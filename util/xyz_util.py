from typing import TextIO

import numpy as np

from shap_e.rendering.mesh import TriMesh

def write_xyz(
    f: TextIO,
    mesh: TriMesh,
):
    #np.stack([mesh.channels[x] for x in "RGB"], axis=1)
    length = mesh.verts.shape[0]
    # X Y Z R G B
    for l in range(length):
        f.write('{x} {y} {z} {r} {g} {b}\n'.format(
            x=mesh.verts[l, 0],
            y=mesh.verts[l, 1],
            z=mesh.verts[l, 2],
            r=mesh.vertex_channels['R'][l],
            g=mesh.vertex_channels['G'][l],
            b=mesh.vertex_channels['B'][l]))

