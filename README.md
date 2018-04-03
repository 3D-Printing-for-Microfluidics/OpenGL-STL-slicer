# STL slicer using OpenGL #

Slice STL files to black-and-white png images that are used in stereolithographic 3D printer.

## Dependency

Make sure [glfw](http://www.glfw.org/download.html) is installed. Mac users can use `brew` to install it. 

## Usage

Change resolution and pixel pitch in `printer.py`, accordingly.

```
$ python app.py <stl file> <layer thickness in mm>
```

## Acknowlegement

The algorithm used here is from [Matt Keeter](https://github.com/mkeeter). Here are his [Javascript version](https://github.com/Formlabs/hackathon-slicer) and his [explanation](http://www.mattkeeter.com/projects/dlp/).