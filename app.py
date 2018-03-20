import glfw
from OpenGL.GL import *
from OpenGL.arrays import vbo
import platform
import os
from stl import mesh
import numpy as np
from PIL import Image

from shader import OurShaderProgram
from printer import printer
import util

EPSILON = 0.0001
SCR_WIDTH = 500
SCR_HEIGHT = 500

class params:
    VAO, vertVBO, maskVAO, maskVBO = 0, 0, 0, 0
    num_of_verts = 0
    bounds = dict()
    total_thickness = 0.


class slice:
    fbo, tex, buf = 0, 0, 0


def start_slicing_stl(stl_filename, layer_thickness, slice_save_path):
    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    
    if platform.system() == 'Darwin': # for Mac OS
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
        
    window = glfw.create_window(SCR_WIDTH, SCR_HEIGHT, 'STL Slicer', None, None)
    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
    
    loadMesh(stl_filename)
    glBindVertexArray(params.maskVAO)
    slicer_folder = os.path.dirname(os.path.abspath(__file__))
    sliceShader = OurShaderProgram(os.path.join(slicer_folder, 'shaders', 'slice.vert'), 
                                   os.path.join(slicer_folder, 'shaders', 'slice.frag'))
    prepareSlice()
    
    i, height = 0, 0.
    while not glfw.window_should_close(window):
        processInput(window)
        
        if height >= params.total_thickness - EPSILON:
            break
        else:
            height += layer_thickness
            i += 1
        
        draw(sliceShader, height-EPSILON)
        renderSlice(sliceShader, height-EPSILON, os.path.join(slice_save_path, 'out{:04d}.png'.format(i-1)))
        
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    glfw.terminate()


def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)


def processInput(window):
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, GL_TRUE)


def loadMesh(stl):
    # Get information about our mesh
    our_mesh = mesh.Mesh.from_file(stl)
    params.num_of_verts = our_mesh.vectors.shape[0] * 3
    params.bounds = {
        'xmin': np.min(our_mesh.vectors[:,:,0]),
        'xmax': np.max(our_mesh.vectors[:,:,0]),
        'ymin': np.min(our_mesh.vectors[:,:,1]),
        'ymax': np.max(our_mesh.vectors[:,:,1]),
        'zmin': np.min(our_mesh.vectors[:,:,2]),
        'zmax': np.max(our_mesh.vectors[:,:,2])
    }
    params.total_thickness = params.bounds['zmax'] - params.bounds['zmin']

    # make VAO for drawing our mesh
    params.VAO = glGenVertexArrays(1)
    glBindVertexArray(params.VAO)
    vertVBO = vbo.VBO(data=our_mesh.vectors.astype(GLfloat).tostring(), usage='GL_STATIC_DRAW', target='GL_ARRAY_BUFFER')
    vertVBO.bind()
    vertVBO.copy_data()
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), vertVBO)
    glEnableVertexAttribArray(0)
    glBindVertexArray(0)
    
    # a mask vertex array for stencil buffer to subtract
    maskVert = np.array(
        [[0, 0, 0],
         [printer.resolution_x*printer.pixel, 0, 0],
         [printer.resolution_x*printer.pixel, printer.resolution_y*printer.pixel, 0],
     
         [0, 0, 0],
         [printer.resolution_x*printer.pixel, printer.resolution_y*printer.pixel, 0],
         [0, printer.resolution_y*printer.pixel, 0]], dtype=GLfloat
    )
    
    # make VAO for drawing mask
    params.maskVAO = glGenVertexArrays(1)
    glBindVertexArray(params.maskVAO)
    maskVBO = vbo.VBO(data=maskVert.tostring(), usage='GL_STATIC_DRAW', target='GL_ARRAY_BUFFER')
    maskVBO.bind()
    maskVBO.copy_data()
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), maskVBO)
    glEnableVertexAttribArray(0)
    maskVBO.unbind()
    glBindVertexArray(0)


def draw(shader, height):
    glEnable(GL_STENCIL_TEST)
    glClearColor(0., 0., 0., 1.)
    glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
    glBindVertexArray(params.VAO)
    shader.use()
    
    proj = util.ortho(0, printer.resolution_x*printer.pixel, 
                      0, printer.resolution_y*printer.pixel, 
                      -params.total_thickness, params.total_thickness, GLfloat)
    shader.setMat4("proj", proj)

    model = util.translation([0, 0, params.total_thickness-height], GLfloat)
    shader.setMat4("model", model)

    glEnable(GL_CULL_FACE)
    glCullFace(GL_FRONT)
    glStencilFunc(GL_ALWAYS, 0, 0xFF)
    glStencilOp(GL_KEEP, GL_KEEP, GL_INCR)
    glDrawArrays(GL_TRIANGLES, 0, params.num_of_verts)

    glCullFace(GL_BACK)
    glStencilOp(GL_KEEP, GL_KEEP, GL_DECR)
    glDrawArrays(GL_TRIANGLES, 0, params.num_of_verts)
    glDisable(GL_CULL_FACE)

    glClear(GL_COLOR_BUFFER_BIT)
    glBindVertexArray(params.maskVAO)
    glStencilFunc(GL_NOTEQUAL, 0, 0xFF)
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
    glDrawArrays(GL_TRIANGLES, 0, 6)
    glDisable(GL_STENCIL_TEST)


def prepareSlice():
    slice.fbo = glGenFramebuffers(1)
    slice.tex = glGenTextures(1)
    slice.buf = glGenRenderbuffers(1)

    glBindTexture(GL_TEXTURE_2D, slice.tex);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, printer.resolution_x, printer.resolution_y, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glBindTexture(GL_TEXTURE_2D, 0)


def renderSlice(shader, height, filename):
    glEnable(GL_STENCIL_TEST)
    glViewport(0, 0, printer.resolution_x, printer.resolution_y)
    glBindFramebuffer(GL_FRAMEBUFFER, slice.fbo)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, slice.tex, 0)
    glBindRenderbuffer(GL_RENDERBUFFER, slice.buf)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_STENCIL, printer.resolution_x, printer.resolution_y)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, slice.buf)

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
    glBindVertexArray(params.VAO)
    shader.use()

    proj = util.ortho(0, printer.resolution_x*printer.pixel, 
                      0, printer.resolution_y*printer.pixel, 
                      -params.total_thickness, params.total_thickness, GLfloat)
    shader.setMat4("proj", proj)

    model = util.translation([0, 0, params.total_thickness-height], GLfloat)
    shader.setMat4("model", model)

    glEnable(GL_CULL_FACE)
    glCullFace(GL_FRONT)
    glStencilFunc(GL_ALWAYS, 0, 0xFF)
    glStencilOp(GL_KEEP, GL_KEEP, GL_INCR)
    glDrawArrays(GL_TRIANGLES, 0, params.num_of_verts)

    glCullFace(GL_BACK)
    glStencilOp(GL_KEEP, GL_KEEP, GL_DECR)
    glDrawArrays(GL_TRIANGLES, 0, params.num_of_verts)
    glDisable(GL_CULL_FACE)

    glClear(GL_COLOR_BUFFER_BIT)
    glBindVertexArray(params.maskVAO)
    glStencilFunc(GL_NOTEQUAL, 0, 0xFF)
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
    glDrawArrays(GL_TRIANGLES, 0, 6)
    glDisable(GL_STENCIL_TEST)
    
    data = glReadPixels(0, 0, printer.resolution_x, printer.resolution_y, GL_RED, GL_UNSIGNED_BYTE)
    image = Image.frombytes('L', (printer.resolution_x, printer.resolution_y), data, 
                            'raw', 'L', 0, -1)
    image.save(filename)

    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glDisable(GL_STENCIL_TEST)
    glViewport(0, 0, SCR_WIDTH, SCR_HEIGHT)


def main():
    import sys
    stl_filename = sys.argv[1]
    layer_thickness = float(sys.argv[2])
    temp = os.path.dirname(stl_filename)
    slice_save_path = os.path.join(temp, 'slices')
    if not os.path.exists(slice_save_path):
        os.mkdir(slice_save_path)
    start_slicing_stl(stl_filename, layer_thickness, slice_save_path)


if __name__ == '__main__':
    main()






















