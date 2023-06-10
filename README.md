# demo_Shap-E
Simple Demonstration Sample Program for Shap-E.
This is the simple interface for [Shap-E](https://github.com/openai/shap-e) via console or HTTP API without Jupyter Notebook.

## Setup

1. Install Python.
2. Install Shape-E `https://github.com/openai/shap-e` as Python module.
3. Clone this repository.
4. Use `txt2*.py` for one-time generation and `http_txt2*.py` for starting HTTP server.


## HTTP Server

You can run HTTP server for rendering and distributing generated 3D models as PLY, XYZ or glTF files.
GET `/request?prompt=prompt_text` or POST simple prompt text to `/request` could trigger rendering process on the server.
Poll at `/getResult` will return 404 or 200 with result file path.
Get the result file by accessing to the received file path as `/file_path`.