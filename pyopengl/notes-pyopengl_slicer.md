# 7/22/21

2018 MacBook Pro laptop. 

Install packages:

    $ brew install glfw
    ==> Upgrading glfw
    3.2.1 -> 3.3.4
    
    (anaconda_py38)
    $ pip install glfw
    Collecting glfw
    Successfully installed glfw-2.1.0
    
    (anaconda_py38)
    $ pip install PyOpenGL
    Successfully installed PyOpenGL-3.1.5
    
    (anaconda_py38)
    $ pip install numpy-stl
    Collecting numpy-stl
    Successfully installed numpy-stl-2.16.0 python-utils-2.5.6

Run app:

    (anaconda_py38)
    $ python app_pyopengl.py ../example.stl 0.01
    app_pyopengl.py:93: DeprecationWarning: tostring() is deprecated. Use tobytes() instead.
      vertVBO = vbo.VBO(data=our_mesh.vectors.astype(GLfloat).tostring(), usage='GL_STATIC_DRAW', target='GL_ARRAY_BUFFER')
    app_pyopengl.py:114: DeprecationWarning: tostring() is deprecated. Use tobytes() instead.
      maskVBO = vbo.VBO(data=maskVert.tostring(), usage='GL_STATIC_DRAW', target='GL_ARRAY_BUFFER')

Fix deprecated methods:

    (anaconda_py38)
    $ python app_pyopengl.py ../example-pyramid.stl 0.5

Everything seems to work fine.

---
# 7/24/21

## How prevent OpenGL window from displaying?

1 - Comment out line 60: 

    # draw(sliceShader, height-EPSILON)  
     
Effect: window displays and flashes red fill color.

2 - Also comment out line 64:

    # glfw.swap_buffers(window)
    
Effect: window displays and is uniformly & unchangingly black.

3 - Also comment out line 65:

    # glfw.poll_events()
    
Same as 2 above the first time I tried it, but then every other time no window appeared.