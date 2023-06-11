import numpy as np
import json
from shap_e.rendering.mesh import TriMesh

def generate_json(
    mesh: TriMesh,
):
    triangles = np.asarray(mesh.faces, dtype=np.uint16)
    triangles = triangles.tolist()
    #triangles_binary_blob = triangles.flatten().tobytes() # Flatten triangle index [N x 3]
    points = np.asarray(mesh.verts, dtype=np.float32)
    points = points.tolist()
    #points_binary_blob = points.flatten()#.tobytes()
    color = None
    if mesh.has_vertex_colors():
        colors = np.stack([mesh.vertex_channels[x] for x in "RGB"], axis=1)
        colors = np.asarray(colors, dtype=np.float32)
        colors = colors.tolist()
    #colors_binary_blob = colors.flatten().tobytes()

    data = {
        "triangles": {
            "componentType": "UNSIGNED_SHORT",
            "count": len(triangles),
            "type": "SCALAR",
            "target": "ARRAY_BUFFER",
            "buffer": triangles,
        },
        "verts": {
            "componentType": "FLOAT",
            "count": len(points),
            "type": "VEC3",
            "target": "ELEMENT_ARRAY_BUFFER",
            "buffer": points,
        },
        "colors": None
    }
    if colors is not None:
        data["colors"] = {
            "componentType": "FLOAT",
            "count": len(colors),
            "type": "VEC3",
            "max": [1.0, 1.0, 1.0],
            "min": [0.0, 0.0, 0.0],
            "target": "ARRAY_BUFFER",
            "buffer": colors,
        }
    return data

