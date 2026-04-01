import math
from dataclasses import dataclass

@dataclass
class MeshConfig:
    output_path: str = "manifold_pot.obj"
    object_name: str = "EquationPot"
    scale_factor: float = 10.0 

    # The equation now has access to min and max
    radial_equation: str = (
        "5 + 1 * ("
        "min(max(1-abs(z-1),0),1)*cos(3*theta) + "
        "min(max(1-abs(z-3),0),1)*cos(5*theta) + "
        "min(max(1-abs(z-5),0),1)*cos(7*theta) + "
        "min(max(1-abs(z-7),0),1)*cos(9*theta) + "
        "min(max(1-abs(z-9),0),1)*cos(11*theta))"
    )
    
    # Dimensions (in cm)
    z_length: float = 10.0
    wall_thickness: float = 0.35
    bottom_thickness: float = 0.5 
    hole_radius: float = 0.5

    # Resolution
    z_sections: int = 80
    theta_sections: int = 120

class EquationMeshExporter:
    def __init__(self, config: MeshConfig):
        self.cfg = config
        self.vertices = []
        self.faces = []

    def eval_r(self, z, theta):
        # FIX: Added min, max, and abs to the safe_globals dictionary
        safe_globals = {
            "math": math, 
            "z": z, 
            "theta": theta, 
            "pi": math.pi, 
            "sin": math.sin, 
            "cos": math.cos,
            "min": min,
            "max": max,
            "abs": abs,
            "pow": pow,
            "sqrt": math.sqrt         
        }
        return float(eval(self.cfg.radial_equation, {"__builtins__": {}}, safe_globals))

    def add_v(self, x, y, z):
        s = self.cfg.scale_factor
        self.vertices.append((x * s, y * s, z * s))
        return len(self.vertices)

    def add_f(self, a, b, c):
        self.faces.append((a, b, c))

    def build_mesh(self):
        ts = self.cfg.theta_sections
        zs = self.cfg.z_sections
        
        # 1. Generate Vertex Rings
        outer_rings = [] 
        for iz in range(zs + 1):
            z = self.cfg.z_length * iz / zs
            ring = []
            for it in range(ts):
                theta = 2 * math.pi * it / ts
                r = self.eval_r(z, theta)
                ring.append(self.add_v(r * math.cos(theta), r * math.sin(theta), z))
            outer_rings.append(ring)

        inner_rings = [] 
        for iz in range(zs + 1):
            z = self.cfg.bottom_thickness + (self.cfg.z_length - self.cfg.bottom_thickness) * iz / zs
            ring = []
            for it in range(ts):
                theta = 2 * math.pi * it / ts
                r_in = self.eval_r(z, theta) - self.cfg.wall_thickness
                ring.append(self.add_v(r_in * math.cos(theta), r_in * math.sin(theta), z))
            inner_rings.append(ring)

        # Hole rings
        hole_bot = []
        hole_top = []
        for it in range(ts):
            theta = 2 * math.pi * it / ts
            hole_bot.append(self.add_v(self.cfg.hole_radius * math.cos(theta), self.cfg.hole_radius * math.sin(theta), 0))
            hole_top.append(self.add_v(self.cfg.hole_radius * math.cos(theta), self.cfg.hole_radius * math.sin(theta), self.cfg.bottom_thickness))

        # 2. Build Faces
        for it in range(ts):
            it1 = (it + 1) % ts
            for iz in range(zs):
                self.add_f(outer_rings[iz][it], outer_rings[iz+1][it], outer_rings[iz+1][it1])
                self.add_f(outer_rings[iz][it], outer_rings[iz+1][it1], outer_rings[iz][it1])
            for iz in range(zs):
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
            for v in self.vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in self.faces:
                f.write(f"f {face[0]} {face[1]} {face[2]}\n")
        print(f"Manifold OBJ exported: {self.cfg.output_path}")

if __name__ == "__main__":
    exporter = EquationMeshExporter(MeshConfig())
    exporter.export()