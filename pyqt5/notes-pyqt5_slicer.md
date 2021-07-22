# 7/22/21

2018 MacBook Pro laptop. 

Install packages:

    $ brew install qt@5
    Warning: qt5 is already installed, it's just not migrated.
    To migrate this formula, run:
      brew migrate qt@5
    Or to force-install it, run:
      brew install qt@5 --force
    $ brew migrate qt@5
    Error: /usr/local/Cellar/qt5 is a symlink
    $ brew install qt@5 --force
    🍺  /usr/local/Cellar/qt@5/5.15.2: 10,688 files, 367.9MB
    Removing: /usr/local/Cellar/qt5/5.12.0... (9,689 files, 318.9MB)
    Error: Not a directory @ dir_s_rmdir - /usr/local/Cellar/qt5
    
    (anaconda_py38)
    $ pip install PyQt5
    Successfully installed PyQt5-5.15.4 PyQt5-Qt5-5.15.2 PyQt5-sip-12.9.0


Run app:

    (anaconda_py38)
    $ python app_qt.py ../example.stl 0.01
    app_pyopengl.py:93: DeprecationWarning: tostring() is deprecated. Use tobytes() instead.
      vertVBO = vbo.VBO(data=our_mesh.vectors.astype(GLfloat).tostring(), usage='GL_STATIC_DRAW', target='GL_ARRAY_BUFFER')
    app_pyopengl.py:114: DeprecationWarning: tostring() is deprecated. Use tobytes() instead.
      maskVBO = vbo.VBO(data=maskVert.tostring(), usage='GL_STATIC_DRAW', target='GL_ARRAY_BUFFER')

Fix deprecated methods:

    (anaconda_py38)
    $ python app_qt.py ../example.stl 0.1

Everything seems to work fine.