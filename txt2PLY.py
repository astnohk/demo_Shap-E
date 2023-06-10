from __future__ import annotations

import os

from util import txt2mesh

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', help='Prompt', type=str, default='a red motorcycle')
    parser.add_argument('--output', help='Output XYZ filepath (*.xyz)', type=str, default='pc.xyz')
    args = parser.parse_args()

    shap_e = txt2mesh.shap_e_wrapper(guidance_scale=3.0)
    # Set a prompt to condition on.

    mesh = shap_e.sample(args.prompt)

    # Write the mesh to a PLY file to import into some other program.
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'wb') as f:
        mesh.write_ply(f)

