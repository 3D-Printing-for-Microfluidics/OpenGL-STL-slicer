from OpenGL.GL import *
from OpenGL.GL import shaders


class OurShaderProgram:
    def __init__(self, vert, frag, **kwargs):
        with open(vert, 'r') as f:
            vert_shader_source = f.read()
        vert_shader = shaders.compileShader(vert_shader_source, GL_VERTEX_SHADER)
        with open(frag, 'r') as f:
            frag_shader_source = f.read()
        frag_shader = shaders.compileShader(frag_shader_source, GL_FRAGMENT_SHADER)
        self.id = shaders.compileProgram(vert_shader, frag_shader, **kwargs)
        
    def use(self):
        glUseProgram(self.id)
        
    def delete(self):
        glDeleteProgram(self.id)
        
    def setInt(self, name, value):
        glUniform1i(glGetUniformLocation(self.id, name), int(value))
        
    def setMat4(self, name, arr):
        glUniformMatrix4fv(glGetUniformLocation(self.id, name), 1, GL_FALSE, arr)
        
    def get_uniform_location(self, name):
        return glGetUniformLocation(self.id, name)
