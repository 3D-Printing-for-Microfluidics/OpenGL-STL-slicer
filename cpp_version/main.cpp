#include <glad/glad.h>
// suppress documentation warning from glfw3.h
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wdocumentation"
#include <GLFW/glfw3.h>
#pragma clang diagnostic pop

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

#include <iostream>
#include <sstream>
#include <string>
#include <iomanip>
#include <vector>

#include "include/shader.h"
#include "vertex.h"
#include "printer.h"
#include "util.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "include/stb_image_write.h"

#define EPSILON 0.0001
GLfloat layer;

const unsigned int SCR_WIDTH = 500;
const unsigned int SCR_HEIGHT = int(SCR_WIDTH * float(printer_resolution.y) / float(printer_resolution.x));

void framebuffer_size_callback(GLFWwindow* window, int width, int height);
void processInput(GLFWwindow *window);
void loadMesh(const char* stl, size_t* p_num_of_verts, std::vector<GLfloat>* p_bounds, GLfloat* p_total_thickness);
void draw(Shader* shader, GLfloat height);
void prepareSlice();
void renderSlice(Shader* shader, GLfloat height, const char* filename);

GLuint VAO, vertVBO, maskVAO, maskVBO, slice_fbo, slice_tex, slice_buf;
size_t num_of_verts;
std::vector<GLfloat> bounds; // bounds = {xmin, xmax, ymin, ymax, zmin, zmax}
GLfloat total_thickness;

int main(int argc, char* argv[])
{
    // glfw: initialize and configure
    // ------------------------------
    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

#ifdef __APPLE__
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE); // uncomment this statement to fix compilation on OS X
#endif

    // glfw window creation
    // --------------------
    GLFWwindow* window = glfwCreateWindow(SCR_WIDTH, SCR_HEIGHT, "STL Slicer", NULL, NULL);
    if (window == NULL)
    {
        std::cout << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return -1;
    }
    glfwMakeContextCurrent(window);
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);

    // tell GLFW to capture our mouse
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_NORMAL);

    // glad: load all OpenGL function pointers
    // ---------------------------------------
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress))
    {
        std::cout << "Failed to initialize GLAD" << std::endl;
        return -1;
    }

    Shader sliceShader("shaders/slice.vert", "shaders/slice.frag");
    loadMesh(argv[1], &num_of_verts, &bounds, &total_thickness);
    prepareSlice();
    layer = atof(argv[2]);

    int i = 0;
    GLfloat height = 0.0f; // slice height
    while(!glfwWindowShouldClose(window))
    {
        processInput(window);
        
        if(height >= total_thickness-EPSILON) {
            break;
        } else {
            height += layer;
            i++;
        }
        
        // draw slice in low resolution
        draw(&sliceShader, height-EPSILON);
        
        // render slice in printer's full resolution
        std::ostringstream filename;
        filename << "slices/out" << std::setw( 4 ) << std::setfill('0') << i-1 << ".png";
        renderSlice(&sliceShader, height-EPSILON, filename.str().c_str());
        
        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    // optional: de-allocate all resources once they've outlived their purpose:
    // ------------------------------------------------------------------------
    glDeleteVertexArrays(1, &VAO);
    glDeleteBuffers(1, &vertVBO);
    glDeleteVertexArrays(1, &maskVAO);
    glDeleteBuffers(1, &maskVBO);

    glfwTerminate();
    return 0;
}

// process all input: query GLFW whether relevant keys are pressed/released this frame and react accordingly
// ---------------------------------------------------------------------------------------------------------
void processInput(GLFWwindow *window)
{
    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS)
        glfwSetWindowShouldClose(window, true);
}

// glfw: whenever the window size changed (by OS or user resize) this callback function executes
// ---------------------------------------------------------------------------------------------
void framebuffer_size_callback(GLFWwindow* window, int width, int height)
{
    // make sure the viewport matches the new window dimensions; note that width and 
    // height will be significantly larger than specified on retina displays.
    glViewport(0, 0, width, height);
}

// load all the vertices and normal into GPU memory, and return bound box
// ----------------------------------------------------------------------
void loadMesh(const char* stl, size_t* p_num_of_verts, std::vector<GLfloat>* p_bounds, GLfloat* p_total_thickness)
{
    std::vector<Vertex> vertices;
    std::vector<Normal> normals;
    getVertices(&vertices, &normals, stl);
    *p_num_of_verts = size_t(vertices.size());
    *p_bounds = find_min_max(vertices);
    *p_total_thickness = (*p_bounds)[5] - (*p_bounds)[4];

    glGenVertexArrays(1, &VAO);
    glGenBuffers(1, &vertVBO);
    glBindVertexArray(VAO);
    glBindBuffer(GL_ARRAY_BUFFER, vertVBO);
    glBufferData(GL_ARRAY_BUFFER, vertices.size()*3*sizeof(GLfloat), vertices.data(), GL_STATIC_DRAW);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), (void*)0);
    glEnableVertexAttribArray(0);
    glBindVertexArray(0);

    GLfloat maskVert[] = {
        0.0f, 0.0f, 0.0f,
        printer_resolution.x*pixel, 0.0f, 0.0f,
        printer_resolution.x*pixel, printer_resolution.y*pixel, 0.0f,
        
        0.0f, 0.0f, 0.0f,
        printer_resolution.x*pixel, printer_resolution.y*pixel, 0.0f,
        0.0f, printer_resolution.y*pixel, 0.0f,
    };

    glGenVertexArrays(1, &maskVAO);
    glGenBuffers(1, &maskVBO);
    glBindVertexArray(maskVAO);
    glBindBuffer(GL_ARRAY_BUFFER, maskVBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(maskVert), &maskVert, GL_STATIC_DRAW);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), (void*)0);
    glEnableVertexAttribArray(0);
    glBindVertexArray(0);
}

void draw(Shader* shader, GLfloat height)
{
    glEnable(GL_STENCIL_TEST);
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);
    glBindVertexArray(VAO);
    shader->use();
    
    glm::mat4 proj = glm::ortho(0.0f, printer_resolution.x*pixel, 0.0f, printer_resolution.y*pixel, -total_thickness, total_thickness);
    shader->setMat4("proj", proj);

    glm::mat4 model;
    model = glm::translate(model, glm::vec3(0.0f, 0.0f, total_thickness-height));
    shader->setMat4("model", model);

    glEnable(GL_CULL_FACE);
    glCullFace(GL_FRONT);
    glStencilFunc(GL_ALWAYS, 0, 0xFF);
    glStencilOp(GL_KEEP, GL_KEEP, GL_INCR);
    glDrawArrays(GL_TRIANGLES, 0, num_of_verts);

    glCullFace(GL_BACK);
    glStencilOp(GL_KEEP, GL_KEEP, GL_DECR);
    glDrawArrays(GL_TRIANGLES, 0, num_of_verts);
    glDisable(GL_CULL_FACE);

    glClear(GL_COLOR_BUFFER_BIT);
    glBindVertexArray(maskVAO);
    glStencilFunc(GL_NOTEQUAL, 0, 0xFF);
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP);
    glDrawArrays(GL_TRIANGLES, 0, 6);
    glDisable(GL_STENCIL_TEST);
}

void prepareSlice()
{
    glGenFramebuffers(1, &slice_fbo);
    glGenTextures(1, &slice_tex);
    glGenRenderbuffers(1, &slice_buf);

    glBindTexture(GL_TEXTURE_2D, slice_tex);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, printer_resolution.x, printer_resolution.y, 0, GL_RGBA, GL_UNSIGNED_BYTE, NULL);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glBindTexture(GL_TEXTURE_2D, 0);
}

void renderSlice(Shader* shader, GLfloat height, const char* filename)
{
    glEnable(GL_STENCIL_TEST);
    glViewport(0, 0, printer_resolution.x, printer_resolution.y);
    glBindFramebuffer(GL_FRAMEBUFFER, slice_fbo);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, slice_tex, 0);
    glBindRenderbuffer(GL_RENDERBUFFER, slice_buf);
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_STENCIL, printer_resolution.x, printer_resolution.y);
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, slice_buf);
    
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);
    glBindVertexArray(VAO);
    shader->use();

    glm::mat4 proj = glm::ortho(0.0f, printer_resolution.x*pixel, 0.0f, printer_resolution.y*pixel, -total_thickness, total_thickness);
    shader->setMat4("proj", proj);

    glm::mat4 model;
    model = glm::translate(model, glm::vec3(0.0f, 0.0f, total_thickness-height));
    shader->setMat4("model", model);

    glEnable(GL_CULL_FACE);
    glCullFace(GL_FRONT);
    glStencilFunc(GL_ALWAYS, 0, 0xFF);
    glStencilOp(GL_KEEP, GL_KEEP, GL_INCR);
    glDrawArrays(GL_TRIANGLES, 0, num_of_verts);

    glCullFace(GL_BACK);
    glStencilOp(GL_KEEP, GL_KEEP, GL_DECR);
    glDrawArrays(GL_TRIANGLES, 0, num_of_verts);
    glDisable(GL_CULL_FACE);

    glClear(GL_COLOR_BUFFER_BIT);
    glBindVertexArray(maskVAO);
    glStencilFunc(GL_NOTEQUAL, 0, 0xFF);
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP);
    glDrawArrays(GL_TRIANGLES, 0, 6);
    glDisable(GL_STENCIL_TEST);

    GLchar data[printer_resolution.x * printer_resolution.y];
    glReadPixels(0, 0, printer_resolution.x, printer_resolution.y, GL_RED, GL_UNSIGNED_BYTE, data);
    stbi_write_png(filename, printer_resolution.x, printer_resolution.y, 1, data, printer_resolution.x);

    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glDisable(GL_STENCIL_TEST);
    glViewport(0, 0, SCR_WIDTH, SCR_HEIGHT);
}


























