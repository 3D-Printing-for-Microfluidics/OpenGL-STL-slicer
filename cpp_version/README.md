## How to setup c++ dependencies on Mac OSX

```
$ brew update
$ brew install glfw3
$ brew install glew
$ brew install glm
$ brew install boost

Go to http://glad.dav1d.de/
    Languate - C/C++
    Specification - OpenGL
    API - gl - 3.3
    Profile - Core
    (Settings not mentioned are not important.)
Click `Generate`
Download `glad.zip`
There are 2 folders in `include`, `KHR` and `glad`. Put then in `\usr\local\include`.

Now all the necessary header files should be in `\usr\local\include`.
The glfw binary is in `\usr\local\Cellar\glfw\3.2.1\lib`.

To compile our OpenGL program, we need to include the header directory and link the binary library and `glad.c`. To do that, use the following command. 

$ g++ -I/usr/local/include -L/usr/local/Cellar/glfw/3.2.1/lib -w -framework OpenGL -lglfw -std=c++11 main.cpp glad.c -o myapp

To run test the slicer, 
$ mkdir slices
$ ./myapp <stl file> <layer thickness in mm>
```