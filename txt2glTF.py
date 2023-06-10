import os

from util import txt2mesh
from util import gltf_util



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', help='Prompt', type=str, default='a red motorcycle')
    parser.add_argument('--output', help='Output glTF filepath (*.glb or *.gltf)', type=str, default='mesh.glb')
    args = parser.parse_args()

    shap_e = txt2mesh.shap_e_wrapper()
    # Set a prompt to condition on.

    mesh = shap_e.sample(args.prompt)

    # Write the mesh to a PLY file to import into some other program.
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    gltf_util.write_gltf(args.output, mesh)

