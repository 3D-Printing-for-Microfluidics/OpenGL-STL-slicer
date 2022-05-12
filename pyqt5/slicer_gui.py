import os
import PySimpleGUI as sg
from printer import printer
from app_qt import generate_slices, dice_images

default_overlap = 15

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
            [
                [
                    sg.Combo(
                        [printer.width],
                        default_value=printer.width,
                        key="width",
                        visible=False,
                    )
                ]
            ],
            element_justification="right",
        ),
    ],
    [
        sg.Text("Image Height (px)", key="height_txt", visible=False, size=(16, 1)),
        sg.Column(
            [
                [
                    sg.Combo(
                        [printer.height],
                        default_value=printer.height,
                        key="height",
                        visible=False,
                    ),
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
                    sg.InputText(
                        default_text=default_overlap, key="overlap", visible=False
                    ),
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
                    sg.InputText(
                        default_text=f"{printer.width},{printer.width*2 - default_overlap}",
                        key="xb",
                        visible=False,
                    ),
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
                    sg.InputText(
                        default_text=f"{printer.height},{printer.height*2 - default_overlap}",
                        key="yb",
                        visible=False,
                    ),
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
        x_boundries = [int(i) for i in values["xb"].split(",")]
        y_boundries = [int(i) for i in values["yb"].split(",")]
        overlap = int(values["overlap"])

        # check if stitching boundries are valid
        if bool(values["stitched"]):
            xs = [0]
            invalid = False
            for x in x_boundries:
                if x < width:
                    if xs[-1] == 0:
                        img_width = x - xs[-1]
                    else:
                        img_width = x - (xs[-1] - overlap)
                    if img_width <= printer.width:
                        xs.append(x)
                    else:
                        invalid = True
                else:
                    break
            if xs[-1] == 0:
                img_width = width - xs[-1]
            else:
                img_width = width - (xs[-1] - overlap)
            if img_width <= printer.width:
                xs.append(width)
            else:
                invalid = True
            x_boundries = xs

            if invalid:
                sg.popup(
                    f"X boundries will result in image width greater than {printer.width}"
                )
                continue

            ys = [0]
            invalid = False
            for y in y_boundries:
                if y < height:
                    if ys[-1] == 0:
                        img_height = y - ys[-1]
                    else:
                        img_height = y - (ys[-1] - overlap)
                    if img_height <= printer.height:
                        ys.append(y)
                    else:
                        invalid = True
                else:
                    break
            if ys[-1] == 0:
                img_height = height - ys[-1]
            else:
                img_height = height - (ys[-1] - overlap)
            if img_height <= printer.height:
                ys.append(height)
            else:
                invalid = True
            y_boundries = ys

            if invalid:
                sg.popup(
                    f"Y boundries will result in image height greater than {printer.height}"
                )
                continue

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
