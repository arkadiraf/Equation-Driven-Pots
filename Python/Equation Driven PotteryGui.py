import math
import tkinter as tk
from tkinter import messagebox
from dataclasses import dataclass
import os

@dataclass
class MeshConfig:
    output_path: str = "pot_design.obj"
    scale_factor: float = 10.0  # mm to cm scaling
    radial_equation: str = ""
    z_length: float = 10.0
    wall_thickness: float = 0.35
    bottom_thickness: float = 0.5 
    hole_radius: float = 0.5 
    z_sections: int = 100
    theta_sections: int = 180

class EquationMeshExporter:
    def __init__(self, config: MeshConfig):
        self.cfg = config

    def eval_r(self, z, theta):
        """Safely evaluates the radial equation string."""
        safe_globals = {
            "math": math, "z": z, "theta": theta, "pi": math.pi,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "min": min, "max": max, "abs": abs, "pow": pow, "sqrt": math.sqrt
        }
        try:
            return float(eval(self.cfg.radial_equation, {"__builtins__": {}}, safe_globals))
        except Exception as e:
            raise ValueError(f"Equation Error: {e}")

    def build_and_save(self):
        """Generates the manifold mesh and writes directly to an OBJ file."""
        ts, zs = self.cfg.theta_sections, self.cfg.z_sections
        vertices = []
        faces = []

        def add_v(x, y, z):
            vertices.append((x * self.cfg.scale_factor, y * self.cfg.scale_factor, z * self.cfg.scale_factor))
            return len(vertices)

        # 1. Generate Vertex Rings
        outer_rings, inner_rings = [], []
        for iz in range(zs + 1):
            z_out = self.cfg.z_length * iz / zs
            z_in = self.cfg.bottom_thickness + (self.cfg.z_length - self.cfg.bottom_thickness) * iz / zs
            
            o_ring, i_ring = [], []
            for it in range(ts):
                theta = 2 * math.pi * it / ts
                r_out = self.eval_r(z_out, theta)
                r_in = self.eval_r(z_in, theta) - self.cfg.wall_thickness
                o_ring.append(add_v(r_out * math.cos(theta), r_out * math.sin(theta), z_out))
                i_ring.append(add_v(r_in * math.cos(theta), r_in * math.sin(theta), z_in))
            outer_rings.append(o_ring)
            inner_rings.append(i_ring)

        # 2. Hole Rings
        h_bot, h_top = [], []
        for it in range(ts):
            theta = 2 * math.pi * it / ts
            h_bot.append(add_v(self.cfg.hole_radius * math.cos(theta), self.cfg.hole_radius * math.sin(theta), 0))
            h_top.append(add_v(self.cfg.hole_radius * math.cos(theta), self.cfg.hole_radius * math.sin(theta), self.cfg.bottom_thickness))

        # 3. Build Manifold Faces
        for it in range(ts):
            it1 = (it + 1) % ts
            for iz in range(zs):
                faces.append((outer_rings[iz][it], outer_rings[iz+1][it], outer_rings[iz+1][it1]))
                faces.append((outer_rings[iz][it], outer_rings[iz+1][it1], outer_rings[iz][it1]))
                faces.append((inner_rings[iz][it], inner_rings[iz][it1], inner_rings[iz+1][it1]))
                faces.append((inner_rings[iz][it], inner_rings[iz+1][it1], inner_rings[iz+1][it]))
            faces.append((outer_rings[zs][it], inner_rings[zs][it], inner_rings[zs][it1]))
            faces.append((outer_rings[zs][it], inner_rings[zs][it1], outer_rings[zs][it1]))
            faces.append((outer_rings[0][it], h_bot[it1], h_bot[it]))
            faces.append((outer_rings[0][it], outer_rings[0][it1], h_bot[it1]))
            faces.append((inner_rings[0][it], h_top[it], h_top[it1]))
            faces.append((inner_rings[0][it], h_top[it1], inner_rings[0][it1]))
            faces.append((h_bot[it], h_bot[it1], h_top[it1]))
            faces.append((h_bot[it], h_top[it1], h_top[it]))

        # 4. Save to Disk
        with open(self.cfg.output_path, "w") as f:
            f.write(f"o {os.path.basename(self.cfg.output_path)}\n")
            for v in vertices: f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces: f.write(f"f {face[0]} {face[1]} {face[2]}\n")

# --- SIMPLIFIED GUI ---
class SimplePotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fast Pot Generator")
        self.root.geometry("550x450")

        # Default Multi-frequency equation
        default_eq = ("5 * (1 + (min(max((z-0.0)/2.5, 0), 1) * 0.18 * cos(3 * theta)) + "
                      "(min(max((z-2.5)/2.5, 0), 1) * 0.15 * cos(6 * theta)) + "
                      "(min(max((z-5.0)/2.5, 0), 1) * 0.10 * cos(12 * theta)) + "
                      "(min(max((z-7.5)/2.5, 0), 1) * 0.08 * cos(24 * theta)))")

        self.fields = [
            ("Output Filename", "pot_design_v1.obj"),
            ("Radial Equation", default_eq),
            ("Pot Height (cm)", "10.0"),
            ("Wall Thickness (cm)", "0.35"),
            ("Floor Thickness (cm)", "0.5"),
            ("Drainage Hole Radius (cm)", "0.75"),
            ("Complexity (Z-Sections)", "100"),
            ("Smoothness (Theta-Sections)", "180"),
        ]

        self.entries = {}
        for label_text, default in self.fields:
            frame = tk.Frame(root)
            frame.pack(fill="x", padx=20, pady=5)
            tk.Label(frame, text=label_text, width=22, anchor="w").pack(side="left")
            ent = tk.Entry(frame)
            ent.insert(0, str(default))
            ent.pack(side="right", expand=True, fill="x")
            self.entries[label_text] = ent

        self.btn = tk.Button(root, text="BUILD 3D MODEL", command=self.generate, 
                             bg="#2c3e50", fg="white", font=('Arial', 11, 'bold'), height=2)
        self.btn.pack(pady=20, padx=20, fill="x")

        self.status = tk.Label(root, text="Ready to export", fg="gray")
        self.status.pack()

    def generate(self):
        try:
            filename = self.entries["Output Filename"].get().strip()
            if not filename.lower().endswith(".obj"): filename += ".obj"

            cfg = MeshConfig(
                output_path=filename,
                radial_equation=self.entries["Radial Equation"].get(),
                z_length=float(self.entries["Pot Height (cm)"].get()),
                wall_thickness=float(self.entries["Wall Thickness (cm)"].get()),
                bottom_thickness=float(self.entries["Floor Thickness (cm)"].get()),
                hole_radius=float(self.entries["Drainage Hole Radius (cm)"].get()),
                z_sections=int(self.entries["Complexity (Z-Sections)"].get()),
                theta_sections=int(self.entries["Smoothness (Theta-Sections)"].get())
            )

            self.status.config(text=f"Generating {filename}...", fg="blue")
            self.root.update()

            exporter = EquationMeshExporter(cfg)
            exporter.build_and_save()

            self.status.config(text=f"SUCCESS: {filename} saved!", fg="green")
            messagebox.showinfo("Success", f"File '{filename}' generated successfully.\nLocation: {os.getcwd()}")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status.config(text="Generation failed", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimplePotApp(root)
    root.mainloop()