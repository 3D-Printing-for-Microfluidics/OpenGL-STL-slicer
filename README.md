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
$ cd pyqt5
$ python app_qt.py <stl file> <layer thickness in mm>
```

or

```
$ cd pyopengl
$ python app_pyopengl.py <stl file> <layer thickness in mm>
```

## To install on Windows

Steps:  
  - Install Python Anaconda   
  - Install Pip   
  - Install Dependencies   
  - Configure settings  
  - Test installation   


### Install Python Anaconda 

Follow the installation instructions found <b>[here](https://conda.io/docs/user-guide/install/windows.html)</b>. Use the Anaconda installer, not the Miniconda installer.  

#### Add Python to Windows PATH

To be able to run Python directly from a Windows PowerShell or Command line, add it to PATH as follows:  

* Type "system" in the Windows Start menu
* Open the "System" option that will show up from Control Panel
* Click on "Advanced system settings" on the left 
* Click on "Environment Variables" near the bottom of the new window 
* Select the "PATH" variable in the <b>bottom</b> list of environment variables
* Click "Edit"
* Click "New". This should add a new PATH entry below the others
* Add the file path to your Python installation location (eg. "C:/Users/Anaconda/")
* Click OK on each window as you exit


### Install pip

Pip is a python package manager, and is the easiest way to install the package dependencies found in the slicer software. If you use Python, you probably already have pip installed. If so, skip this step. 

Pip may come in Anaconda by default now. Go to the folder where you installed Anaconda, and if pip.exe is in the Scripts folder, skip to the verify pip installation step below. You may still have to add the Scripts folder to PATH.  

The easiest way to install pip ia as follows: 

  * Save <b>[get-pip.py](https://bootstrap.pypa.io/get-pip.py)</b> somewhere on your computer 
  * Open a command prompt window and navigate to the folder containing get-pip.py  
    * This is easily done by holding shift and clicking in the folder where you downloaded get-pip.py and selecting "Open PowerShell window here"   
  * Run "python get-pip.py". This will install pip

#### Verify pip installation
To verify your pip installation, type "pip freeze". If you don't get errors you are good. You should see a list of installed Python Packages with their versions, like this: 

	C:\Users\Anaconda>pip freeze  
	antiorm==1.1.1  
	enum34==1.0    
	requests==2.3.0  
	virtualenv==1.11.6  

If this fails, you may need to add the Scripts folder (with pip in it) to your PATH. The process is the same as detailed above in "Add Python to Windows PATH", except you will give it the folder path to the "Scripts" folder inside your Python directory. This was "C:\Users\Anaconda\Scripts" for me. Run "pip freeze" again to see if it works now.     

### Install Dependencies

Install all software dependencies as follows: 

  * Go to the folder with the slicing software you want to use. The best version is the <b>pyqt5</b> version. 
  * Open a shell window in that folder 
    * Again, this is easily done by holding shift and clicking in the folder and selecting "Open PowerShell window here"
  * Run "pip install -r req_qt.txt". This will install all the required packages listed in the text file

## Acknowlegement

The algorithm used here is from [Matt Keeter](https://github.com/mkeeter). Here are his [Javascript version](https://github.com/Formlabs/hackathon-slicer) and his [explanation](http://www.mattkeeter.com/projects/dlp/).



