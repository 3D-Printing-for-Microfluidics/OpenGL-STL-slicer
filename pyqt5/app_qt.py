import sys
import glob
import json
import numpy as np
from stl import mesh
from PIL import Image
from pathlib import Path
from PyQt5 import QtGui, QtCore, QtWidgets
from ctypes import c_float, c_uint, sizeof

GLfloat = c_float
GLuint = c_uint

EPSILON = 0.00001

app = None


class Window(QtGui.QOpenGLWindow):
    def __init__(
        self,
        stlFilename,
        layerThickness,
        imageWidth,
        imageHeight,
        pixelPitch,
        sliceSavePath,
        progress_handle,
        *args,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)

        self.setTitle("STL Slicer")

        self.vertVAO, self.vertVBO = 0, 0
        self.maskVAO, self.maskVBO = 0, 0
        self.numOfVerts = 0
        self.bounds = dict()
        self.totalThickness = 0.0
        self.currentLayer = 0
        self.height = 0

        self.stlFilename = stlFilename
        self.layerThickness = layerThickness
        self.imageWidth = imageWidth
        self.imageHeight = imageHeight
        self.pixelPitch = pixelPitch
        self.sliceSavePath = sliceSavePath
        self.progress_handle = progress_handle

    def initializeGL(self):
        self.gl = self.context().versionFunctions()

        self.shaderProg = QtGui.QOpenGLShaderProgram()
        self.shaderProg.create()
        self.shaderProg.addShaderFromSourceFile(
            QtGui.QOpenGLShader.Vertex, "shaders/slice.vert"
        )
        self.shaderProg.addShaderFromSourceFile(
            QtGui.QOpenGLShader.Fragment, "shaders/slice.frag"
        )
        self.shaderProg.link()

        self.loadMesh()

        self.proj = QtGui.QMatrix4x4()
        self.proj.setToIdentity()
        self.proj.ortho(
            0,
            self.imageWidth * self.pixelPitch,
            0,
            self.imageHeight * self.pixelPitch,
            -self.totalThickness,
            self.totalThickness,
        )

        self.model = QtGui.QMatrix4x4()
        self.model.setToIdentity()
        self.model.translate(0, 0, self.totalThickness + EPSILON)

        self.sliceFbo = QtGui.QOpenGLFramebufferObject(self.imageWidth, self.imageHeight)
        self.sliceFbo.setAttachment(QtGui.QOpenGLFramebufferObject.CombinedDepthStencil)

    def loadMesh(self):
        # Get information about our mesh
        ourMesh = mesh.Mesh.from_file(self.stlFilename)
        self.numOfVerts = ourMesh.vectors.shape[0] * 3
        self.bounds = {
            "xmin": np.min(ourMesh.vectors[:, :, 0]),
            "xmax": np.max(ourMesh.vectors[:, :, 0]),
            "ymin": np.min(ourMesh.vectors[:, :, 1]),
            "ymax": np.max(ourMesh.vectors[:, :, 1]),
            "zmin": np.min(ourMesh.vectors[:, :, 2]),
            "zmax": np.max(ourMesh.vectors[:, :, 2]),
        }
        self.totalThickness = self.bounds["zmax"] - self.bounds["zmin"]

        #######################################
        # make VAO for drawing our mesh
        self.vertVAO = QtGui.QOpenGLVertexArrayObject()
        self.vertVAO.create()
        self.vertVAO.bind()

        self.vertVBO = QtGui.QOpenGLBuffer(QtGui.QOpenGLBuffer.VertexBuffer)
        self.vertVBO.create()
        self.vertVBO.bind()
        self.vertVBO.setUsagePattern(QtGui.QOpenGLBuffer.StaticDraw)
        data = ourMesh.vectors.astype(GLfloat).tostring()
        self.vertVBO.allocate(data, len(data))
        self.gl.glVertexAttribPointer(
            0, 3, self.gl.GL_FLOAT, self.gl.GL_FALSE, 3 * sizeof(GLfloat), 0
        )
        self.gl.glEnableVertexAttribArray(0)

        self.vertVBO.release()
        self.vertVAO.release()
        #######################################

        # a mask vertex array for stencil buffer to subtract
        maskVert = np.array(
            [
                [0, 0, 0],
                [self.imageWidth * self.pixelPitch, 0, 0],
                [
                    self.imageWidth * self.pixelPitch,
                    self.imageHeight * self.pixelPitch,
                    0,
                ],
                [0, 0, 0],
                [
                    self.imageWidth * self.pixelPitch,
                    self.imageHeight * self.pixelPitch,
                    0,
                ],
                [0, self.imageHeight * self.pixelPitch, 0],
            ],
            dtype=GLfloat,
        )

        #######################################
        # make VAO for drawing mask
        self.maskVAO = QtGui.QOpenGLVertexArrayObject()
        self.maskVAO.create()
        self.maskVAO.bind()

        self.maskVBO = QtGui.QOpenGLBuffer(QtGui.QOpenGLBuffer.VertexBuffer)
        self.maskVBO.create()
        self.maskVBO.bind()
        self.maskVBO.setUsagePattern(QtGui.QOpenGLBuffer.StaticDraw)
        data = maskVert.tostring()
        self.maskVBO.allocate(data, len(data))
        self.gl.glVertexAttribPointer(
            0, 3, self.gl.GL_FLOAT, self.gl.GL_FALSE, 3 * sizeof(GLfloat), 0
        )
        self.gl.glEnableVertexAttribArray(0)

        self.maskVBO.release()
        self.maskVAO.release()
        #######################################

    def paintGL(self):
        if self.height >= self.totalThickness - EPSILON:
            app.exit(0)
        else:
            self.height += self.layerThickness
            self.currentLayer += 1
            self.draw()
            self.renderSlice()
            self.update()
            if self.progress_handle is not None:
                self.progress_handle(
                    "Slicing STL",
                    self.currentLayer,
                    self.totalThickness // self.layerThickness + 1,
                )

    def draw(self):
        self.gl.glViewport(0, 0, self.size().width(), self.size().height())
        self.gl.glEnable(self.gl.GL_STENCIL_TEST)
        self.gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_STENCIL_BUFFER_BIT)
        self.vertVAO.bind()
        self.shaderProg.bind()

        self.model.translate(0, 0, -self.layerThickness)
        self.shaderProg.setUniformValue("proj", self.proj)
        self.shaderProg.setUniformValue("model", self.model)

        self.gl.glEnable(self.gl.GL_CULL_FACE)
        self.gl.glCullFace(self.gl.GL_FRONT)
        self.gl.glStencilFunc(self.gl.GL_ALWAYS, 0, 0xFF)
        self.gl.glStencilOp(self.gl.GL_KEEP, self.gl.GL_KEEP, self.gl.GL_INCR)
        self.gl.glDrawArrays(self.gl.GL_TRIANGLES, 0, self.numOfVerts)

        self.gl.glCullFace(self.gl.GL_BACK)
        self.gl.glStencilOp(self.gl.GL_KEEP, self.gl.GL_KEEP, self.gl.GL_DECR)
        self.gl.glDrawArrays(self.gl.GL_TRIANGLES, 0, self.numOfVerts)
        self.gl.glDisable(self.gl.GL_CULL_FACE)

        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT)
        self.maskVAO.bind()
        self.gl.glStencilFunc(self.gl.GL_NOTEQUAL, 0, 0xFF)
        self.gl.glStencilOp(self.gl.GL_KEEP, self.gl.GL_KEEP, self.gl.GL_KEEP)
        self.gl.glDrawArrays(self.gl.GL_TRIANGLES, 0, 6)
        self.gl.glDisable(self.gl.GL_STENCIL_TEST)
        self.shaderProg.release()

    def renderSlice(self):
        self.sliceFbo.bind()
        self.gl.glViewport(0, 0, self.imageWidth, self.imageHeight)
        self.gl.glEnable(self.gl.GL_STENCIL_TEST)
        self.gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_STENCIL_BUFFER_BIT)
        self.vertVAO.bind()
        self.shaderProg.bind()

        self.shaderProg.setUniformValue("proj", self.proj)
        self.shaderProg.setUniformValue("model", self.model)

        self.gl.glEnable(self.gl.GL_CULL_FACE)
        self.gl.glCullFace(self.gl.GL_FRONT)
        self.gl.glStencilFunc(self.gl.GL_ALWAYS, 0, 0xFF)
        self.gl.glStencilOp(self.gl.GL_KEEP, self.gl.GL_KEEP, self.gl.GL_INCR)
        self.gl.glDrawArrays(self.gl.GL_TRIANGLES, 0, self.numOfVerts)

        self.gl.glCullFace(self.gl.GL_BACK)
        self.gl.glStencilOp(self.gl.GL_KEEP, self.gl.GL_KEEP, self.gl.GL_DECR)
        self.gl.glDrawArrays(self.gl.GL_TRIANGLES, 0, self.numOfVerts)
        self.gl.glDisable(self.gl.GL_CULL_FACE)

        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT)
        self.maskVAO.bind()
        self.gl.glStencilFunc(self.gl.GL_NOTEQUAL, 0, 0xFF)
        self.gl.glStencilOp(self.gl.GL_KEEP, self.gl.GL_KEEP, self.gl.GL_KEEP)
        self.gl.glDrawArrays(self.gl.GL_TRIANGLES, 0, 6)
        self.gl.glDisable(self.gl.GL_STENCIL_TEST)

        image = self.sliceFbo.toImage()
        # makes a QComboBox for different Image Format,
        # namely Format_Mono, Format_MonoLSB, and Format_Grayscale8
        image = image.convertToFormat(QtGui.QImage.Format_Grayscale8)
        fullpath = Path(self.sliceSavePath) / "out{:04d}.png".format(self.currentLayer)

        image.save(str(fullpath))
        self.sliceFbo.release()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            app.exit(0)
        event.accept()


def generate_slices(
    stlFilename, layerThickness, imageWidth, imageHeight, pixelPitch, progress_handle=None
):
    stlParentFolder = Path(stlFilename).parent
    sliceSavePath = Path(stlParentFolder) / "slices"

    if not Path(sliceSavePath).exists():
        Path(sliceSavePath).mkdir()

    # Set format here, otherwise it throws error
    # `QCocoaGLContext: Falling back to unshared context.`
    # on Mac when use QOpenGLWidgets
    # https://doc.qt.io/qt-5/qopenglwidget.html#details last paragraph
    custom_format = QtGui.QSurfaceFormat()
    custom_format.setRenderableType(QtGui.QSurfaceFormat.OpenGL)
    custom_format.setProfile(QtGui.QSurfaceFormat.CoreProfile)
    custom_format.setVersion(4, 1)
    custom_format.setStencilBufferSize(8)
    QtGui.QSurfaceFormat.setDefaultFormat(custom_format)

    global app
    app = QtWidgets.QApplication(sys.argv)
    window = Window(
        stlFilename,
        layerThickness,
        imageWidth,
        imageHeight,
        pixelPitch,
        sliceSavePath,
        progress_handle,
    )
    SCR_WIDTH = 640
    SCR_HEIGHT = int(SCR_WIDTH * imageHeight / imageWidth)
    window.resize(SCR_WIDTH, SCR_HEIGHT)
    window.show()

    app.exec_()

    # return sliceSavePath, sys.exit(app.exec_())
    return sliceSavePath


def dice_images(
    sliceSavePath,
    imageWidth,
    imageHeight,
    pixelPitch,
    x_boundries,
    y_boundries,
    overlap,
    progress_handle=None,
):

    dicedSavePath = Path(sliceSavePath) / "diced_images"
    fullSavePath = Path(sliceSavePath) / "full_sized_images"

    if not Path(dicedSavePath).exists():
        Path(dicedSavePath).mkdir()
    if not Path(fullSavePath).exists():
        Path(fullSavePath).mkdir()

    images = glob.glob(str(sliceSavePath / "*.png"))
    image_count = len(images)
    for i, image_path in enumerate(images):
        image_path = Path(image_path)
        filename = image_path.stem
        extention = image_path.suffix
        img = np.array(Image.open(image_path))

        last_x = 0
        for j, x in enumerate(x_boundries):
            x = int(x)
            if x == 0:
                continue
            last_y = 0
            for k, y in enumerate(y_boundries):
                y = int(y)
                if y == 0:
                    continue
                sub_img = img[last_y:y, last_x:x]
                sub_img = Image.fromarray(sub_img).convert("L")
                sub_img.save(dicedSavePath / f"{filename}_stitch_x{j}_y{k}{extention}")
                last_y = y - overlap
            last_x = x - overlap

        image_path.replace(fullSavePath / f"{filename}{extention}")
        if progress_handle is not None:
            progress_handle("Dicing images", i + 1, image_count)

    with open(sliceSavePath / "stitching_info.json", "w") as file:
        info = {
            "pixel_pitch": pixelPitch,
            "x_boundries": x_boundries,
            "y_boundries": y_boundries,
            "overlap": overlap,
        }
        json.dump(info, file)


if __name__ == "__main__":
    stlFilename = sys.argv[1]
    layerThickness = float(sys.argv[2])
    generate_slices(stlFilename, layerThickness)
