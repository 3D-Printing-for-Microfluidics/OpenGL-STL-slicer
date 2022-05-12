import os
import PySimpleGUI as sg
from app_qt import generate_slices


# set up frontend GUI

sg.theme('Light Blue 2')

layout = [[sg.Text('STL File', size=(16, 1)), sg.InputText(''), sg.FileBrowse(key='path')],
          [sg.Text('Layer Thickness (um)', size=(16, 1)), sg.InputText(default_text=10, key='thickness')],
          [sg.Checkbox('Advanced Options', size=(16, 1), default=False, change_submits=True, key='adv_opts')],
          [sg.Text('Image Width (px)', key='width_txt', visible = False, size=(16, 1)), sg.Combo([2560], default_value=2560, key='width', visible = False)],
          [sg.Text('Image Height (px)', key='height_txt', visible = False, size=(16, 1)), sg.Combo([1600], default_value=1600, key='height', visible = False)],
          [sg.Text('Pixel Pitch (um)', key='pitch_txt', visible = False, size=(16, 1)), sg.Combo([7.6,15.2,3.8], default_value=7.6, key='pitch', visible = False)],
          [sg.Submit(), sg.Cancel()]]
window = sg.Window('Python STL Slicer', layout)

while True:
    event, values = window.read()

    if event == 'Submit':
        # cast values appropriately
        layer_thickness_um = float(values['thickness'])
        width = float(values['width'])
        height = float(values['height'])
        pixel_pitch_um = float(values['pitch'])
        path_to_stl = os.path.normpath(values['path'])

        # create the print file and then exit
        output_folder = generate_slices(path_to_stl, layer_thickness_um/1000, width, height, pixel_pitch_um/1000)

        sg.popup('Slices saved to', output_folder, title='Slicing Complete')


        window.close()
    elif event == 'adv_opts':
        window.Element('width').Update(visible=values['adv_opts'])
        window.Element('height').Update(visible=values['adv_opts'])
        window.Element('pitch').Update(visible=values['adv_opts'])
        window.Element('width_txt').Update(visible=values['adv_opts'])
        window.Element('height_txt').Update(visible=values['adv_opts'])
        window.Element('pitch_txt').Update(visible=values['adv_opts'])
    elif event == 'Cancel' or event is None:
        exit()