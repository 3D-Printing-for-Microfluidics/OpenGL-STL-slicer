import os
import PySimpleGUI as sg
from app_qt import generate_slices


# set up frontend GUI

sg.theme('Light Blue 2')

layout = [[sg.Text('STL File', size=(16, 1)), sg.InputText(''), sg.FileBrowse()],
          [sg.Text('Layer Thickness (um)', size=(16, 1)), sg.InputText(default_text=10)],
          [sg.Submit(), sg.Cancel()]]
window = sg.Window('Python STL Slicer', layout)
event, values = window.read()
if event == 'Cancel' or event is None:
    exit()

# cast values appropriately
layer_thickness_um = float(values[1])
path_to_stl = os.path.normpath(values[0])

# create the print file and then exit
output_folder = generate_slices(path_to_stl, layer_thickness_um/1000)

sg.popup('Slices saved to', output_folder, title='Slicing Complete')


window.close()
