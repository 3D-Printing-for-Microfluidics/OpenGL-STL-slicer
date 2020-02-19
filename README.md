# STL slicer using OpenGL #

Slice STL files to black-and-white png images that are used in stereolithographic 3D printing.

To use `app_pyopengl.py`, make sure [glfw](http://www.glfw.org/download.html) is installed. Mac users can use `brew` to install it.

![GUI Example](/pyqt5/gui.png)

# To install on Windows

Steps:
  - Install Python Anaconda (Python 3.7.3)
  - Create and activate virtual environment
  - Install dependencies

## Install Python Anaconda

Follow the installation instructions found <b>[here](https://conda.io/docs/user-guide/install/windows.html)</b>. Be sure to get Python 3.7.3. Be sure to check the box to add it to your path.

## Create and Activate Virtual Environment

In a shell of your coice:

```
# install virtualenv
pip install virtualenv
# create new virtual environment named 'env'
python -m virtualenv env
# activate the virtual environment
.\env\Scripts\activate
# install all dependencies
pip install -r .\req.txt
```

When you want to use the slicer, you will have to activate the virtual environment again with

```
# activate virtual environment
.\env\Scripts\activate
# run slicer with the GUI
python slicer_gui.py
```

# Acknowlegement

The algorithm used here is from [Matt Keeter](https://github.com/mkeeter). Here are his [Javascript version](https://github.com/Formlabs/hackathon-slicer) and his [explanation](http://www.mattkeeter.com/projects/dlp/).
