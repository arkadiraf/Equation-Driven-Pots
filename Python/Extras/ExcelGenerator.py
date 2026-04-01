import math
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from dataclasses import dataclass

@dataclass
class MeshConfig:
    output_path: str = ""
    object_name: str = ""
    scale_factor: float = 10.0 
    radial_equation: str = ""
    z_length: float = 10.0
    wall_thickness: float = 0.35
    bottom_thickness: float = 0.5 
    hole_radius: float = 0.5
    z_sections: int = 80
    theta_sections: int = 120

class EquationMeshExporter:
    def __init__(self, config: MeshConfig):
        self.cfg = config
        self.vertices = []
        self.faces = []

    def eval_r(self, z, theta):
        safe_globals = {
            "math": math, "z": z, "theta": theta, "pi": math.pi, 
            "sin": math.sin, "cos": math.cos, "min": min,
            "max": max, "abs": abs, "pow": pow, "sqrt": math.sqrt         
        }
        try:
            return float(eval(self.cfg.radial_equation, {"__builtins__": {}}, safe_globals))
        except:
            return 5.0  # Default radius if equation fails

    def add_v(self, x, y, z):
        s = self.cfg.scale_factor
        self.vertices.append((x * s, y * s, z * s))
        return len(self.vertices)

    def add_f(self, a, b, c):
        self.faces.append((a, b, c))

    def build_mesh(self):
        ts, zs = self.cfg.theta_sections, self.cfg.z_sections
        
        # Generate Vertex Rings
        outer_rings = [] 
        for iz in range(zs + 1):
            z = self.cfg.z_length * iz / zs
            ring = [self.add_v(self.eval_r(z, 2*math.pi*it/ts) * math.cos(2*math.pi*it/ts), 
                               self.eval_r(z, 2*math.pi*it/ts) * math.sin(2*math.pi*it/ts), z) for it in range(ts)]
            outer_rings.append(ring)

        inner_rings = [] 
        for iz in range(zs + 1):
            z = self.cfg.bottom_thickness + (self.cfg.z_length - self.cfg.bottom_thickness) * iz / zs
            ring = [self.add_v((self.eval_r(z, 2*math.pi*it/ts) - self.cfg.wall_thickness) * math.cos(2*math.pi*it/ts), 
                               (self.eval_r(z, 2*math.pi*it/ts) - self.cfg.wall_thickness) * math.sin(2*math.pi*it/ts), z) for it in range(ts)]
            inner_rings.append(ring)

        hole_bot = [self.add_v(self.cfg.hole_radius * math.cos(2*math.pi*it/ts), self.cfg.hole_radius * math.sin(2*math.pi*it/ts), 0) for it in range(ts)]
        hole_top = [self.add_v(self.cfg.hole_radius * math.cos(2*math.pi*it/ts), self.cfg.hole_radius * math.sin(2*math.pi*it/ts), self.cfg.bottom_thickness) for it in range(ts)]

        # Build Faces
        for it in range(ts):
            it1 = (it + 1) % ts
            for iz in range(zs):
                self.add_f(outer_rings[iz][it], outer_rings[iz+1][it], outer_rings[iz+1][it1])
                self.add_f(outer_rings[iz][it], outer_rings[iz+1][it1], outer_rings[iz][it1])
                self.add_f(inner_rings[iz][it], inner_rings[iz][it1], inner_rings[iz+1][it1])
                self.add_f(inner_rings[iz][it], inner_rings[iz+1][it1], inner_rings[iz+1][it])
            self.add_f(outer_rings[zs][it], inner_rings[zs][it], inner_rings[zs][it1])
            self.add_f(outer_rings[zs][it], inner_rings[zs][it1], outer_rings[zs][it1])
            self.add_f(outer_rings[0][it], hole_bot[it1], hole_bot[it])
            self.add_f(outer_rings[0][it], outer_rings[0][it1], hole_bot[it1])
            self.add_f(inner_rings[0][it], hole_top[it], hole_top[it1])
            self.add_f(inner_rings[0][it], hole_top[it1], inner_rings[0][it1])
            self.add_f(hole_bot[it], hole_bot[it1], hole_top[it1])
            self.add_f(hole_bot[it], hole_top[it1], hole_top[it])

    def export(self):
        self.build_mesh()
        with open(self.cfg.output_path, "w") as f:
            f.write(f"o {self.cfg.object_name}\n")
            for v in self.vertices: f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in self.faces: f.write(f"f {face[0]} {face[1]} {face[2]}\n")

def save_preview_image(config, img_path):
    """Generates a JPG preview using Matplotlib."""
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Low resolution for faster image generation
    z_res, t_res = 30, 40
    z_vals = np.linspace(0, config.z_length, z_res)
    theta_vals = np.linspace(0, 2 * np.pi, t_res)
    
    exporter = EquationMeshExporter(config)
    
    for i in range(len(z_vals) - 1):
        for j in range(len(theta_vals) - 1):
            z_slice = [z_vals[i], z_vals[i], z_vals[i+1], z_vals[i+1]]
            t_slice = [theta_vals[j], theta_vals[j+1], theta_vals[j+1], theta_vals[j]]
            pts = []
            for cur_z, cur_t in zip(z_slice, t_slice):
                r = exporter.eval_r(cur_z, cur_t)
                pts.append([r * math.cos(cur_t), r * math.sin(cur_t), cur_z])
            ax.add_collection3d(Poly3DCollection([pts], color='tan', edgecolor='saddlebrown', alpha=0.8, lw=0.1))

    ax.set_xlim(-8, 8); ax.set_ylim(-8, 8); ax.set_zlim(0, 10)
    ax.set_title(config.object_name)
    plt.savefig(img_path, dpi=100)
    plt.close()

def sanitize(name):
    return re.sub(r'[\\/*?:"<>|]', "", str(name))

if __name__ == "__main__":
    # 1. Setup Folders
    for folder in ["3dModels", "images"]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # 2. Load Data
    excel_file = "Pot Design Equations.xlsx"
    df = pd.read_excel(excel_file)
    
    print(f"Starting batch process for {len(df)} designs...")

    # 3. Iterate and Generate
    for _, row in df.iterrows():
        design_name = str(row['Design Name']).strip()
        equation = row['Unified Python Equation: r(θ,z)']
        
        if not design_name or pd.isna(equation): continue
        
        safe_name = sanitize(design_name)
        obj_path = os.path.join("3dModels", f"{safe_name}.obj")
        img_path = os.path.join("images", f"{safe_name}.jpg")

        cfg = MeshConfig(
            output_path=obj_path,
            object_name=safe_name,
            radial_equation=str(equation)
        )

        # Export OBJ
        exporter = EquationMeshExporter(cfg)
        exporter.export()

        # Export Image
        save_preview_image(cfg, img_path)
        print(f"Done: {design_name}")

    print("\nAll files generated successfully in /3dModels and /images")