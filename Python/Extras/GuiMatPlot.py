import math
import tkinter as tk
from tkinter import messagebox
from dataclasses import dataclass
import os
import numpy as np

# 3D Engines
import pyvista as pv 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.widgets import Button

@dataclass
class MeshConfig:
    output_path: str = "pot_design.obj"
    scale_factor: float = 10.0  
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
        """Generates the high-resolution OBJ file for 3D printing/rendering."""
        ts, zs = self.cfg.theta_sections, self.cfg.z_sections
        vertices, faces = [], []

        def add_v(x, y, z):
            vertices.append((x * self.cfg.scale_factor, y * self.cfg.scale_factor, z * self.cfg.scale_factor))
            return len(vertices)

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

        h_bot, h_top = [], []
        for it in range(ts):
            theta = 2 * math.pi * it / ts
            h_bot.append(add_v(self.cfg.hole_radius * math.cos(theta), self.cfg.hole_radius * math.sin(theta), 0))
            h_top.append(add_v(self.cfg.hole_radius * math.cos(theta), self.cfg.hole_radius * math.sin(theta), self.cfg.bottom_thickness))

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

        with open(self.cfg.output_path, "w") as f:
            f.write(f"o {os.path.basename(self.cfg.output_path)}\n")
            for v in vertices: f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces: f.write(f"f {face[0]} {face[1]} {face[2]}\n")

# --- VISUALIZATION FUNCTIONS ---

def show_low_res_preview(exporter, preview_res=(20, 36)):
    """
    Generates a fast Matplotlib preview with fixed axes and a Reset button.
    """
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection='3d')
    plt.subplots_adjust(bottom=0.2)

    zs_count, ts_count = preview_res
    z_vals = np.linspace(0, exporter.cfg.z_length, zs_count)
    theta_vals = np.linspace(0, 2 * np.pi, ts_count)
    
    # Draw the outer surface
    for i in range(len(z_vals) - 1):
        for j in range(len(theta_vals) - 1):
            z0, z1 = z_vals[i], z_vals[i+1]
            t0, t1 = theta_vals[j], theta_vals[j+1]
            
            pts = []
            for curr_z, curr_t in [(z0, t0), (z0, t1), (z1, t1), (z1, t0)]:
                r = exporter.eval_r(curr_z, curr_t)
                pts.append([r * math.cos(curr_t), r * math.sin(curr_t), curr_z])
            
            poly = Poly3DCollection([pts], alpha=0.5, facecolor='tan', edgecolor='saddlebrown', linewidths=0.2)
            ax.add_collection3d(poly)

    def set_view_limits():
        ax.set_xlim(-7.5, 7.5)
        ax.set_ylim(-7.5, 7.5)
        ax.set_zlim(0, max(10, exporter.cfg.z_length))
        ax.set_title("Quick Preview (Fixed -7.5 to 7.5)")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

    set_view_limits()

    # Add the "Fit to Screen" (Reset) Button
    ax_button = plt.axes([0.4, 0.05, 0.2, 0.06]) 
    btn_reset = Button(ax_button, 'Fit to Screen', color='#ecf0f1', hovercolor='#bdc3c7')

    def reset_view(event):
        set_view_limits()
        ax.view_init(elev=20, azim=-35) # Standard 3D angle
        plt.draw()

    btn_reset.on_clicked(reset_view)
    plt.show()

def show_with_pyvista(filename, z_max=10.0):
    """High-quality inspection of the saved file."""
    mesh = pv.read(filename)
    plotter = pv.Plotter(title="PyVista High-Res Viewer")
    plotter.set_background("ghostwhite")
    
    plotter.add_mesh(mesh, color="tan", smooth_shading=True, specular=0.5)
    plotter.show_grid(bounds=[-7.5, 7.5, -7.5, 7.5, 0, z_max])
    plotter.add_axes()
    plotter.show()

# --- GUI APPLICATION ---

class EquationPotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Equation Pot Designer")
        self.root.geometry("550x600")

        # Default complex equation
        default_eq = ("5 * (1 + (min(max((z-0.0)/2.5, 0), 1) * 0.18 * cos(3 * theta)) + "
                      "(min(max((z-2.5)/2.5, 0), 1) * 0.15 * cos(6 * theta)) + "
                      "(min(max((z-5.0)/2.5, 0), 1) * 0.10 * cos(12 * theta)) + "
                      "(min(max((z-7.5)/2.5, 0), 1) * 0.08 * cos(24 * theta)))")

        self.fields = [
            ("Output Filename", "my_pot_design.obj"),
            ("Radial Equation", default_eq),
            ("Pot Height (cm)", "10.0"),
            ("Wall Thickness (cm)", "0.35"),
            ("Floor Thickness (cm)", "0.5"),
            ("Drainage Hole Radius (cm)", "0.5"),
            ("Z Complexity (File)", "100"),
            ("Theta Smoothness (File)", "180"),
        ]

        self.entries = {}
        for label, default in self.fields:
            f = tk.Frame(root); f.pack(fill="x", padx=20, pady=5)
            tk.Label(f, text=label, width=22, anchor="w").pack(side="left")
            ent = tk.Entry(f); ent.insert(0, str(default)); ent.pack(side="right", expand=True, fill="x")
            self.entries[label] = ent

        # Buttons
        tk.Button(root, text="1. QUICK PREVIEW (MATPLOTLIB)", command=lambda: self.run_process("mpl"), 
                  bg="#2980b9", fg="white", font=('Arial', 10, 'bold'), height=2).pack(pady=10, padx=20, fill="x")

        tk.Button(root, text="2. BUILD & SAVE HIGH-RES (PYVISTA)", command=lambda: self.run_process("pv"), 
                  bg="#2c3e50", fg="white", font=('Arial', 10, 'bold'), height=2).pack(pady=5, padx=20, fill="x")

        self.status = tk.Label(root, text="Ready", fg="gray"); self.status.pack(pady=10)

    def run_process(self, mode):
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
                z_sections=int(self.entries["Z Complexity (File)"].get()),
                theta_sections=int(self.entries["Theta Smoothness (File)"].get())
            )

            exporter = EquationMeshExporter(cfg)

            if mode == "mpl":
                self.status.config(text="Opening Quick Preview...", fg="orange")
                self.root.update()
                show_low_res_preview(exporter)
                self.status.config(text="Preview Closed", fg="gray")
            else:
                self.status.config(text=f"Exporting {filename}...", fg="blue")
                self.root.update()
                exporter.build_and_save()
                self.status.config(text=f"SUCCESS: {filename} saved!", fg="green")
                show_with_pyvista(filename, z_max=cfg.z_length)

        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong:\n{str(e)}")
            self.status.config(text="Process failed", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = EquationPotApp(root)
    root.mainloop()