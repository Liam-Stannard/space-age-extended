"""The engine's asteroid shader, for previews: Factorio's data/core/graphics/shaders/asteroid.frag
ported line for line to numpy (checked by shading promethium's own maps, which come out as the
game draws them: red crystal, grey crust, the red rim on the east/west edges).

shade(colour, normal, rough, sd, angle) -> RGBA float image, premultiplied like the framebuffer.
What it does not reproduce: GPU bilinear/mip sampling at the drawn scale (we shade at texture
resolution and then downsample the lit result), the shadow pass, the space background's
parallax and any post-processing; vOpacity is 1.
"""
import numpy as np

PROMETHIUM = dict(normal_strength=1.2, light_width=0.3, brightness=0.3, specular_strength=2.5,
                  specular_power=1.5, specular_purity=0.1, sss_contrast=0, sss_amount=0.15,
                  lights=[((1, 1, 1), (0.75, 0.22, -1)), ((0.2, 0, 0), (0.5, 0, 0.95))],
                  ambient_light=(0, 0, 0))   # space-age/prototypes/entity/asteroid.lua 140-161

# T03's change, as previewed here: the same shading with the rim light blue -- #1F63FF scaled
# so its strongest channel is the red rim's 0.2. A proposal for the coder, not a decision.
RIM_BLUE = dict(PROMETHIUM, lights=[((1, 1, 1), (0.75, 0.22, -1)),
                                    ((0x1F / 255 * 0.2, 0x63 / 255 * 0.2, 0.2), (0.5, 0, 0.95))])


def shade(colour, normal, rough, sd, angle=0.0, premul=True):
    c = colour.astype(float) / 255
    if premul:   # sprites without premul_alpha=false are premultiplied at load
        c[..., :3] *= c[..., 3:4]
    nimg = normal.astype(float) / 255
    rimg = rough.astype(float) / 255
    sss_col = rimg[..., :3]
    roughness = rimg[..., 3]
    n = np.zeros(c.shape[:2] + (3,))
    n[..., 0] = nimg[..., 0] * 2 - 1
    n[..., 1] = nimg[..., 1] * 2 - 1
    n[..., 2] = np.sqrt(np.clip(1 - n[..., 0] ** 2 - n[..., 1] ** 2, 0, 1))
    up = np.array([0, 0, 1.0])
    n = up + (n - up) * sd['normal_strength']
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    ca, sa = np.cos(-angle), np.sin(-angle)
    rn = np.stack([n[..., 0] * ca + n[..., 1] * sa, -n[..., 0] * sa + n[..., 1] * ca, n[..., 2]], -1)
    lw = sd['light_width']
    illum = np.zeros_like(rn); diff = np.zeros_like(rn); spec_t = np.zeros_like(rn)
    view = np.array([0, 0, -1.0])
    for col, d in sd['lights']:
        col = np.array(col, float); d = np.array(d, float); d /= np.linalg.norm(d)
        L = -d
        ndl = (rn * L).sum(-1)
        lighting = np.maximum(0, ndl + lw)
        diff += col * lighting[..., None] * sd['brightness']
        # GLSL reflect(I, N) = I - 2 dot(N, I) N, called as reflect(rotated_normal, -lightDirection)
        I = rn; N = L
        refl = I - 2 * (I * N).sum(-1)[..., None] * N
        sp = (np.maximum(0, (refl * view).sum(-1) + lw) * (1 - roughness)) ** sd['specular_power']
        spec_col = c[..., :3] + (1 - c[..., :3]) * sd['specular_purity']
        spec_t += spec_col * sp[..., None] * sd['specular_strength'] * col
        illum += col * np.maximum(-1, ndl + lw)[..., None]
    sss = np.clip(2 - illum - sd['sss_contrast'], 0, 1) * sd['sss_amount']
    rgb = (spec_t + diff + np.array(sd['ambient_light'])) * c[..., :3]
    rgb = rgb + np.clip(sss_col * sss, 0, 1)
    k = np.clip((c[..., 3] - 0.9) * 10, 0, 1)[..., None]
    return np.concatenate([rgb * k, c[..., 3:4] * k], -1)   # alpha as blended: premultiplied out


def over(img, bg):
    """composite the shader output (premultiplied, alpha-blended) over a background colour"""
    a = img[..., 3:4]
    return np.clip(img[..., :3] + np.array(bg, float) / 255 * (1 - a), 0, 1)
