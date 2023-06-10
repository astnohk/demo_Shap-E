from __future__ import annotations

import numpy as np

import torch
from tqdm.auto import tqdm

from shap_e.diffusion.sample import sample_latents
from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
from shap_e.models.download import load_model, load_config
from shap_e.util.collections import AttrDict
from shap_e.models.nn.camera import DifferentiableCameraBatch, DifferentiableProjectiveCamera
from shap_e.models.transmitter.base import Transmitter, VectorDecoder
from shap_e.rendering.torch_mesh import TorchMesh


def create_pan_cameras(size: int, device: torch.device) -> DifferentiableCameraBatch:
    origins = []
    xs = []
    ys = []
    zs = []
    for theta in np.linspace(0, 2 * np.pi, num=20):
        z = np.array([np.sin(theta), np.cos(theta), -0.5])
        z /= np.sqrt(np.sum(z**2))
        origin = -z * 4
        x = np.array([np.cos(theta), -np.sin(theta), 0.0])
        y = np.cross(z, x)
        origins.append(origin)
        xs.append(x)
        ys.append(y)
        zs.append(z)
    return DifferentiableCameraBatch(
        shape=(1, len(xs)),
        flat_camera=DifferentiableProjectiveCamera(
            origin=torch.from_numpy(np.stack(origins, axis=0)).float().to(device),
            x=torch.from_numpy(np.stack(xs, axis=0)).float().to(device),
            y=torch.from_numpy(np.stack(ys, axis=0)).float().to(device),
            z=torch.from_numpy(np.stack(zs, axis=0)).float().to(device),
            width=size,
            height=size,
            x_fov=0.7,
            y_fov=0.7,
        ),
    )

@torch.no_grad()
def decode_latent_mesh(
    xm: Union[Transmitter, VectorDecoder],
    latent: torch.Tensor,
) -> TorchMesh:
    decoded = xm.renderer.render_views(
        AttrDict(cameras=create_pan_cameras(2, latent.device)),  # lowest resolution possible
        params=(xm.encoder if isinstance(xm, Transmitter) else xm).bottleneck_to_params(
            latent[None]
        ),
        options=AttrDict(rendering_mode="stf", render_with_direction=False),
    )
    return decoded.raw_meshes[0]


class shap_e_wrapper:

    def __init__(
        self,
        guidance_scale: float = 3.0,
    ):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        print('creating base model...')
        self.xm = load_model('transmitter', device=device)
        self.model = load_model('text300M', device=device)
        self.diffusion = diffusion_from_config(load_config('diffusion'))

        self.batch_size = 1

    def sample(
        self,
        prompt: str,
        guidance_scale: float = 15.0
    ):
        # Produce a mesh (with vertex colors)
        latents = sample_latents(
            batch_size=self.batch_size,
            model=self.model,
            diffusion=self.diffusion,
            guidance_scale=guidance_scale,
            model_kwargs=dict(texts=[prompt] * self.batch_size),
            progress=True,
            clip_denoised=True,
            use_fp16=True,
            use_karras=True,
            karras_steps=64,
            sigma_min=1e-3,
            sigma_max=160,
            s_churn=0,
        )
        decoded = decode_latent_mesh(self.xm, latents[0])
        mesh = decoded.tri_mesh()

        return mesh



if __name__ == '__main__':
    shap_e = shap_e_wrapper()
    # Set a prompt to condition on.
    prompt = 'a red motorcycle'

    mesh = shap_e.sample(prompt)

