# STL slicer using OpenGL #

Slice STL files to black-and-white png images that are used in stereolithographic 3D printer.

## Dependency

* `app_qt.py` - `req_qt.txt`
* `app_pyopengl.py` - `req_pyopengl.txt`

To use `app_pyopengl.py`, make sure [glfw](http://www.glfw.org/download.html) is installed. Mac users can use `brew` to install it. 

## Usage

Change resolution and pixel pitch in `printer.py`, accordingly.

Using `app_qt.py` is recommended, because it is about twice as fast as using `app_pyopengl.py`, and it has less dependencies. 

```
$ python app_qt.py <stl file> <layer thickness in mm>
```

or

```
$ python app_pyopengl.py <stl file> <layer thickness in mm>
```

## Acknowlegement

The algorithm used here is from [Matt Keeter](https://github.com/mkeeter). Here are his [Javascript version](https://github.com/Formlabs/hackathon-slicer) and his [explanation](http://www.mattkeeter.com/projects/dlp/).



