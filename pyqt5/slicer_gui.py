import os
import PySimpleGUI as sg
from app_qt import generate_slices, dice_images


# set up frontend GUI

sg.theme("Light Blue 2")

layout = [
    [sg.Text("STL File", size=(16, 1)), sg.InputText(""), sg.FileBrowse(key="path")],
    [
        sg.Text("Layer Thickness (um)", size=(16, 1)),
        sg.InputText(default_text=10, key="thickness"),
    ],
    [
        sg.Checkbox(
            "Advanced Options",
            size=(18, 1),
            default=False,
            change_submits=True,
            key="adv_opts",
        )
    ],
    [
        sg.Text("Image Width (px)", key="width_txt", visible=False, size=(16, 1)),
        sg.Column(
            [[sg.Combo([2560], default_value=2560, key="width", visible=False)]],
            element_justification="right",
        ),
    ],
    [
        sg.Text("Image Height (px)", key="height_txt", visible=False, size=(16, 1)),
        sg.Column(
            [
                [
                    sg.Combo([1600], default_value=1600, key="height", visible=False),
                ]
            ],
            element_justification="right",
        ),
    ],
    [
        sg.Text("Pixel Pitch (um)", key="pitch_txt", visible=False, size=(16, 1)),
        sg.Column(
            [
                [
                    sg.Combo(
                        [7.6, 15.2, 3.8], default_value=7.6, key="pitch", visible=False
                    ),
                ]
            ],
            element_justification="right",
        ),
    ],
    [sg.Checkbox("Create stitched images", key="stitched", visible=False)],
    [
        sg.Text("Overlap (px)", key="overlap_txt", visible=False, size=(16, 1)),
        sg.Column(
            [
                [
                    sg.InputText(default_text=15, key="overlap", visible=False),
                ]
            ],
            element_justification="right",
        ),
    ],
    [
        sg.Text("X Boundries (px)", key="xb_txt", visible=False, size=(16, 1)),
        sg.Column(
            [
                [
                    sg.InputText(default_text="2560,5105", key="xb", visible=False),
                ]
            ],
            element_justification="right",
        ),
    ],
    [
        sg.Text("Y Boundries (px)", key="yb_txt", visible=False, size=(16, 1)),
        sg.Column(
            [
                [
                    sg.InputText(default_text="1600,3185", key="yb", visible=False),
                ]
            ],
            element_justification="right",
        ),
    ],
    [sg.Submit(), sg.Cancel()],
]
window = sg.Window("Python STL Slicer", layout)


def progress_handle(title, progress, total):
    sg.one_line_progress_meter(title, progress, total, "key")


while True:
    event, values = window.read()

    if event == "Submit":
        # cast values appropriately
        layer_thickness_um = float(values["thickness"])
        width = float(values["width"])
        height = float(values["height"])
        pixel_pitch_um = float(values["pitch"])
        path_to_stl = os.path.normpath(values["path"])

        # create the print file and then exit
        output_folder = generate_slices(
            path_to_stl,
            layer_thickness_um / 1000,
            width,
            height,
            pixel_pitch_um / 1000,
            progress_handle,
        )

        if bool(values["stitched"]):
            x_boundries = [int(i) for i in values["xb"].split(",")]
            y_boundries = [int(i) for i in values["yb"].split(",")]
            overlap = int(values["overlap"])
            dice_images(
                output_folder,
                width,
                height,
                pixel_pitch_um,
                x_boundries,
                y_boundries,
                overlap,
                progress_handle,
            )

        sg.popup("Slices saved to", output_folder, title="Slicing Complete")

        window.close()
    elif event == "adv_opts":
        window.Element("width").Update(visible=values["adv_opts"])
        window.Element("height").Update(visible=values["adv_opts"])
        window.Element("pitch").Update(visible=values["adv_opts"])
        window.Element("stitched").Update(visible=values["adv_opts"])
        window.Element("overlap").Update(visible=values["adv_opts"])
        window.Element("xb").Update(visible=values["adv_opts"])
        window.Element("yb").Update(visible=values["adv_opts"])
        window.Element("width_txt").Update(visible=values["adv_opts"])
        window.Element("height_txt").Update(visible=values["adv_opts"])
        window.Element("pitch_txt").Update(visible=values["adv_opts"])
        window.Element("overlap_txt").Update(visible=values["adv_opts"])
        window.Element("xb_txt").Update(visible=values["adv_opts"])
        window.Element("yb_txt").Update(visible=values["adv_opts"])
    elif event == "Cancel" or event is None:
        exit()
