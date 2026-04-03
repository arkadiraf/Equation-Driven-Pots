import math
import os
import re
import random
from dataclasses import dataclass

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


# =========================
# Config
# =========================

@dataclass
class PreviewConfig:
    output_dir: str = "textured_preview_output"
    per_page: int = 30
    total_pots: int = 60
    cols: int = 5
    rows: int = 6
    seed: int = 42
    figure_dpi: int = 220


# =========================
# Libraries from unified textured designer
# =========================

CYLINDRICAL_LIBRARY = {
    "Rounded Square": {
        "eq": "R * pow(pow(abs(cos(theta)), 8) + pow(abs(sin(theta)), 8), -0.125)"
    },
    "Ellipse": {
        "eq": "R / sqrt(pow(cos(theta), 2) + 2.5 * pow(sin(theta), 2))"
    },
    "Square Ripple": {
        "eq": "R * pow(pow(abs(cos(theta)), 8) + pow(abs(sin(theta)), 8), -0.125) * (1 + 0.05 * sin(10 * z))"
    },
    "Elliptical Twist": {
        "eq": "R / sqrt(pow(cos(theta + z/3), 2) + 2.5 * pow(sin(theta + z/3), 2))"
    },
    "5-Petal Flower": {
        "eq": "R * (1 + 0.25 * cos(5 * theta))"
    },
    "Gear-like": {
        "eq": "R * (1 + 0.08 * cos(12 * theta))"
    },
    "Soft Gourd": {
        "eq": "R * (1 + 0.10 * cos(4 * theta) + 0.05 * sin(2 * theta))"
    },
    "Wavy Ceramic": {
        "eq": "R * (1 + 0.08 * cos(3 * theta) + 0.06 * sin(5 * theta))"
    },
    "Pumpkin Rib": {
        "eq": "R * (1 + 0.14 * cos(8 * theta))"
    },
    "Turbine Blade": {
        "eq": "R * (1 + 0.18 * cos(5 * theta + 0.35 * sin(theta)))"
    },
    "Islamic Rosette": {
        "eq": "R * (1 + 0.14 * cos(8 * theta) + 0.06 * cos(4 * theta))"
    },
    "Opening Flower": {
        "eq": "R * (1 + 0.25 * cos(5 * theta)) * (1 + 0.35 * sin(pi * z / 10))"
    },
    "Sharpening Top": {
        "eq": "R * (1 + (0.10 + 0.18 * z / 10) * cos(6 * theta))"
    },
    "Twisted Blossom": {
        "eq": "R * (1 + 0.22 * cos(5 * theta + pi * z / 10))"
    },
    "3-to-6 Petal Morph": {
        "eq": "R * (1 + 0.35 * sin(pi * z / 10)) * (1 + 0.25 * (((10 - z) / 10) * cos(3 * theta) + (z / 10) * cos(6 * theta)))"
    },
    "Fractal Growth": {
        "eq": "R * (1 + (min(max((z-0.0)/2.5, 0), 1) * 0.18 * cos(3 * theta)) + (min(max((z-2.5)/2.5, 0), 1) * 0.15 * cos(6 * theta)) + (min(max((z-5.0)/2.5, 0), 1) * 0.10 * cos(12 * theta)) + (min(max((z-7.5)/2.5, 0), 1) * 0.08 * cos(24 * theta)))"
    },
    "Antenna Migration": {
        "eq": "R * (1 + 0.4 * pow(z / 10.0, 1.5) * abs(cos((2 + 6 * (z / 10.0)) * theta / 2.0)))"
    },
    "Harmonic Oscillator": {
        "eq": "R * (1 + 0.25 * abs(cos(pi * 1.0 * z / 10.0)) * cos(7 * theta))"
    },
    "DNA Helix": {
        "eq": "R * (1 + 0.4 * cos(2 * (theta + (1.2 * sin(2 * pi * z / 10.0)))))"
    },
    "Bloomfold Vase": {
        "eq": "(R-1.0)+1.2*sin(pi*z/10.0)+(0.34+0.42*sin(pi*z/10.0))*(pow(cos(0.5*pi*z/10.0),2)*cos(3*theta)+1.55*pow(sin(pi*z/10.0),2)*cos(6*theta))"
    },
    "Trifold Bloom Vase": {
        "eq": "(R-1.0)+1.2*sin(pi*z/10.0)+(0.34+0.42*sin(pi*z/10.0))*(pow(cos(pi*z/10.0),2)*cos(3*theta)+1.55*pow(sin(pi*z/10.0),2)*cos(6*theta))"
    },
    "DNA Double Helix": {
        "eq": "R + 0.5 * sin(4 * theta + z) + 0.5 * cos(4 * theta - z)"
    },
}

SPHERICAL_LIBRARY = {
    "Dragon Egg": {
        "eq": "R * (1 + 0.08 * cos(10*theta + 8*phi) + 0.08 * cos(10*theta - 8*phi))"
    },
    "Perfect Sphere": {
        "eq": "R"
    },
    "Aerospace Isogrid": {
        "eq": "R * (1 + 0.08 * max(cos(12*theta + 10*phi), cos(12*theta - 10*phi)))"
    },
    "Crown Splash": {
        "eq": "R * (1 + 0.35 * exp(-pow(phi - 0.4, 2) * 20) * max(0, cos(14 * theta)) + 0.05 * sin(phi * 8))"
    },
    "Phased Array Lobe": {
        "eq": "R * (1 + 0.25 * pow(sin(phi), 4) * pow(cos(4*theta), 6) + 0.03 * sin(16*theta)*sin(phi))"
    },
    "Wind Shear Ripples": {
        "eq": "R * (1 + 0.08 * sin(12*theta) * pow(sin(phi), 2) + 0.04 * sin(24*theta - 12*phi) * sin(phi))"
    },
    "Electron Cloud": {
        "eq": "R * (1 + 0.3 * abs(pow(sin(phi), 3) * cos(phi) * sin(3*theta)))"
    },
    "Fibonacci Spirals": {
        "eq": "R * (1 + 0.08 * pow(max(0, sin(13*theta - 8*phi)), 2) + 0.08 * pow(max(0, sin(8*theta + 13*phi)), 2))"
    },
    "Crystalline Geode": {
        "eq": "R * (1 + 0.08 * (abs(sin(5*theta)) + abs(cos(5*theta))) * (abs(sin(4*phi)) + abs(cos(4*phi))))"
    },
    "Gravity Drip": {
        "eq": "R * (1 + 0.2 * exp(phi - 2.5) * cos(12 * theta) * sin(phi))"
    },
    "Overlapping Armor": {
        "eq": "R * (1 + 0.12 * pow(max(0, sin(10*theta - 6*phi)), 2) * sin(phi))"
    },
    "Twisted Hex Vortex": {
        "eq": "R * (1 + 0.15 * cos(6 * (theta + phi*2)))"
    },
    "Ribbed Art Deco": {
        "eq": "R * (1 + 0.15 * pow(cos(8*theta), 4) * sin(phi))"
    },
    "Equatorial Flare": {
        "eq": "R * (1 + 0.4 * exp(-pow(phi-1.57, 2)*10))"
    },
    "Cellular Organic": {
        "eq": "R * (1 + 0.06 * (sin(8*theta)*cos(10*phi) + sin(11*theta)*cos(5*phi)))"
    },
    "Pumpkin Lobes": {
        "eq": "R * (1 + 0.15 * cos(8 * theta))"
    },
    "Woven Basket": {
        "eq": "R * (1 + 0.05 * sin(12 * theta) * cos(8 * phi))"
    },
    "Starfruit": {
        "eq": "R * (1 + 0.25 * cos(5 * theta) * sin(phi))"
    },
    "Hourglass Peanut": {
        "eq": "R * (1 - 0.25 * sin(2 * phi))"
    },
    "Coral Brain": {
        "eq": "R * (1 + 0.08 * sin(10 * theta + 5*phi) * sin(8 * phi))"
    },
}

TEXTURE_PRESETS = {
    "Fine Vertical Ribs": {"eq": "cos(16*theta)"},
    "Twisted Vertical Ribs": {"eq": "cos(14*theta + 4*pi*v)"},
    "Diamond Weave": {"eq": "0.5*cos(10*theta + 8*pi*v) + 0.5*cos(10*theta - 8*pi*v)"},
    "Hex-ish Facets": {"eq": "abs(cos(6*theta))*0.7 + 0.3*cos(10*pi*v)"},
    "Wave Bands": {"eq": "sin(3*theta + 10*pi*v)"},
    "Armor Scales": {"eq": "pow(max(0, sin(12*theta - 10*pi*v)), 2)"},
    "Dragon Dimples": {"eq": "0.7*cos(10*theta + 8*pi*v) * cos(10*theta - 8*pi*v)"},
    "Pebble Dimples": {"eq": "0.7*sin(14*theta)*sin(10*pi*v) + 0.3*sin(23*theta + 7*pi*v)"},
    "Stipple Noise": {"eq": "sin(18*theta)*sin(14*pi*v) + 0.35*sin(31*theta + 9*pi*v)"},
    "Cymatic Ripples": {"eq": "sin(20*theta)*cos(18*pi*v)"},
    "Rosette Engraving": {"eq": "cos(8*theta) + 0.4*cos(4*theta + 6*pi*v)"},
    "Braided Spiral": {"eq": "sin(6*theta + 8*pi*v) + 0.65*sin(6*theta - 8*pi*v)"},
    "Topographic Rings": {"eq": "sin(24*pi*v)"},
    "Lotus Scallops": {"eq": "pow(max(0, cos(8*theta)), 2) * sin(pi*v)"},
}


# =========================
# Utilities
# =========================

def sanitize(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", str(name)).strip()


def safe_eval(eq, theta=0.0, z=0.0, phi=0.0, v=0.0, R=5.0):
    safe = {
        "__builtins__": {},
        "math": math,
        "pi": math.pi,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "pow": pow,
        "sqrt": math.sqrt,
        "abs": abs,
        "min": min,
        "max": max,
        "exp": math.exp,
        "theta": theta,
        "z": z,
        "phi": phi,
        "v": v,
        "R": R,
    }
    try:
        value = float(eval(eq, safe, {}))
        if not math.isfinite(value):
            return R
        return value
    except Exception:
        return R


def choose_texture_intensity(texture_name: str, rng: random.Random) -> float:
    if "Engraving" in texture_name or "Rings" in texture_name:
        return rng.uniform(0.08, 0.16)
    if "Dimples" in texture_name or "Noise" in texture_name:
        return rng.uniform(0.10, 0.18)
    if "Scales" in texture_name or "Weave" in texture_name:
        return rng.uniform(0.12, 0.20)
    return rng.uniform(0.10, 0.22)


# =========================
# Geometry sampling
# =========================

def build_cylindrical_surface(shape_eq, texture_eq, R, H, tex_intensity,
                              z_res=34, t_res=48):
    quads = []
    z_vals = np.linspace(0.0, H, z_res)
    t_vals = np.linspace(0.0, 2 * math.pi, t_res, endpoint=False)

    for i in range(len(z_vals) - 1):
        for j in range(len(t_vals)):
            j1 = (j + 1) % len(t_vals)

            corners = []
            for cur_z, cur_t in [
                (z_vals[i], t_vals[j]),
                (z_vals[i], t_vals[j1]),
                (z_vals[i + 1], t_vals[j1]),
                (z_vals[i + 1], t_vals[j]),
            ]:
                v = cur_z / H if H != 0 else 0.0
                r_base = safe_eval(shape_eq, theta=cur_t, z=cur_z, v=v, R=R)
                disp = safe_eval(texture_eq, theta=cur_t, z=cur_z, v=v, R=0.0)
                r = max(0.15, r_base + disp * tex_intensity)
                x = r * math.cos(cur_t)
                y = r * math.sin(cur_t)
                corners.append([x, y, cur_z])

            quads.append(corners)

    return quads


def build_spherical_surface(shape_eq, texture_eq, R, tex_intensity,
                            phi_start_deg=22, phi_end_deg=174,
                            p_res=34, t_res=48):
    quads = []

    phi_start = math.radians(phi_start_deg)
    phi_end = math.radians(phi_end_deg)

    phi_vals = np.linspace(phi_start, phi_end, p_res)
    t_vals = np.linspace(0.0, 2 * math.pi, t_res, endpoint=False)

    min_z = float("inf")
    raw_quads = []

    for i in range(len(phi_vals) - 1):
        for j in range(len(t_vals)):
            j1 = (j + 1) % len(t_vals)

            quad = []
            for cur_phi, cur_t in [
                (phi_vals[i], t_vals[j]),
                (phi_vals[i], t_vals[j1]),
                (phi_vals[i + 1], t_vals[j1]),
                (phi_vals[i + 1], t_vals[j]),
            ]:
                v = (cur_phi - phi_start) / (phi_end - phi_start) if phi_end != phi_start else 0.0
                r_base = safe_eval(shape_eq, theta=cur_t, phi=cur_phi, v=v, R=R)
                disp = safe_eval(texture_eq, theta=cur_t, phi=cur_phi, v=v, R=0.0)
                r = max(0.15, r_base + disp * tex_intensity)

                x = r * math.sin(cur_phi) * math.cos(cur_t)
                y = r * math.sin(cur_phi) * math.sin(cur_t)
                z = r * math.cos(cur_phi)

                min_z = min(min_z, z)
                quad.append([x, y, z])

            raw_quads.append(quad)

    # shift so base sits near z=0 like the cylindrical previews
    for quad in raw_quads:
        shifted = []
        for x, y, z in quad:
            shifted.append([x, y, z - min_z])
        quads.append(shifted)

    return quads


# =========================
# Rendering
# =========================

def render_pot_preview(ax, pot):
    ax.set_facecolor("#f8f6f2")

    if pot["system"] == "Cyl":
        quads = build_cylindrical_surface(
            pot["shape_eq"],
            pot["texture_eq"],
            pot["R"],
            pot["H"],
            pot["tex_intensity"],
        )
        z_max = pot["H"]
        xy_lim = 8.5
    else:
        quads = build_spherical_surface(
            pot["shape_eq"],
            pot["texture_eq"],
            pot["R"],
            pot["tex_intensity"],
        )
        z_max = 11.0
        xy_lim = 8.5

    poly = Poly3DCollection(
        quads,
        facecolor="tan",
        edgecolor="saddlebrown",
        linewidth=0.10,
        alpha=0.84,
    )
    ax.add_collection3d(poly)

    ax.set_xlim(-xy_lim, xy_lim)
    ax.set_ylim(-xy_lim, xy_lim)
    ax.set_zlim(0, z_max)

    ax.view_init(elev=23, azim=-58)
    try:
        ax.set_box_aspect((1, 1, 1.2))
    except Exception:
        pass

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.grid(False)
    ax.set_axis_off()

    title = f"{pot['system']} | {pot['shape_name']} | {pot['texture_name']}"
    ax.set_title(title, fontsize=7, pad=3)


def stitch_pages(pots, cfg: PreviewConfig):
    os.makedirs(cfg.output_dir, exist_ok=True)

    pages = []
    for page_idx in range(2):
        start = page_idx * cfg.per_page
        end = start + cfg.per_page
        page_pots = pots[start:end]

        fig = plt.figure(figsize=(16, 20), facecolor="white")
        fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.97, wspace=0.08, hspace=0.14)

        for i, pot in enumerate(page_pots, start=1):
            ax = fig.add_subplot(cfg.rows, cfg.cols, i, projection="3d")
            render_pot_preview(ax, pot)

        fig.suptitle(
            f"Equation-Driven Pots — Textured Unified Designer — Page {page_idx + 1}",
            fontsize=18,
            y=0.992,
        )

        out_path = os.path.join(cfg.output_dir, f"textured_pots_page_{page_idx + 1}.jpg")
        plt.savefig(out_path, dpi=cfg.figure_dpi, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        pages.append(out_path)

    return pages


# =========================
# Pot combination generation
# =========================

def build_random_pot_set(cfg: PreviewConfig):
    rng = random.Random(cfg.seed)

    all_combos = []

    for shape_name, shape_data in CYLINDRICAL_LIBRARY.items():
        for tex_name, tex_data in TEXTURE_PRESETS.items():
            all_combos.append({
                "system": "Cyl",
                "shape_name": shape_name,
                "shape_eq": shape_data["eq"],
                "texture_name": tex_name,
                "texture_eq": tex_data["eq"],
            })

    for shape_name, shape_data in SPHERICAL_LIBRARY.items():
        for tex_name, tex_data in TEXTURE_PRESETS.items():
            all_combos.append({
                "system": "Sph",
                "shape_name": shape_name,
                "shape_eq": shape_data["eq"],
                "texture_name": tex_name,
                "texture_eq": tex_data["eq"],
            })

    if cfg.total_pots > len(all_combos):
        raise ValueError("Requested more unique pots than available unique shape+texture+system combinations.")

    chosen = rng.sample(all_combos, cfg.total_pots)

    pots = []
    for combo in chosen:
        pot = dict(combo)

        if pot["system"] == "Cyl":
            pot["R"] = rng.uniform(4.2, 5.8)
            pot["H"] = rng.uniform(8.5, 11.5)
        else:
            pot["R"] = rng.uniform(4.6, 5.8)
            pot["H"] = 10.0

        pot["tex_intensity"] = choose_texture_intensity(pot["texture_name"], rng)
        pots.append(pot)

    return pots


# =========================
# Main
# =========================

if __name__ == "__main__":
    cfg = PreviewConfig()

    os.makedirs(cfg.output_dir, exist_ok=True)

    pots = build_random_pot_set(cfg)
    pages = stitch_pages(pots, cfg)

    print("Generated unique textured pot preview pages:")
    for page in pages:
        print(" -", page)

    print("\nEach tile title is:")
    print("System | Shape | Texture")
    print("\nNo duplicate shape+texture+system combinations were used.")