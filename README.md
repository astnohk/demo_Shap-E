# demo_Shap-E
Simple Demonstration Sample Program for Shap-E.
This is the simple interface for [Shap-E](https://github.com/openai/shap-e) via console or HTTP API without Jupyter Notebook.

## Setup

1. Install Python.
2. Install Shape-E `https://github.com/openai/shap-e` as Python module.
3. Clone this repository.
4. Use `txt2*.py` for one-time generation and `http_txt2mesh.py` for starting HTTP server.


## Local Console

`txt2*.py` can produce a one model file for each runs.
`$ python3 txt2PLY.py --prompt "a boat" --output ./boat.ply`
`$ python3 txt2glTF.py --prompt "a boat" --output ./boat.glb`


## HTTP Server

You can run HTTP server for rendering and distributing generated 3D models as PLY, XYZ or glTF files.
Run `$ python3 http_txt2mesh.py` and GET `/request?prompt=prompt_text&fileformat=FORMAT` or POST simple prompt text to `/request?fileformat=FORMAT` could trigger rendering process on the server.
`FORMAT` will receives `ply`, `xyz` and `glTF`.
Poll at `/getResult` will return 404 or 200 with result file path.
Get the result file by accessing to the received file path as `/file_path`.


## Google Colabolatory

Here is [the sample for Google Colabolatory](ColabSample.ipynb).
1. Create your [ngrok](https://ngrok.com/) account.
2. Copy the sample code on your Colab.
3. Runs the code.
