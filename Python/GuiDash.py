import math
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from dash import Dash, html, dcc, Input, Output, State, callback
import plotly.graph_objects as go


@dataclass
class MeshConfig:
    output_path: str = "eqPot.obj"
    scale_factor: float = 10.0
    z_length: float = 10.0
    wall_thickness: float = 0.35
    bottom_thickness: float = 0.5
    hole_radius: float = 0.5


class EquationMeshExporter:
    def __init__(self, config: MeshConfig):
        self.cfg = config

    def eval_r(self, equation, z, theta):
        safe_globals = {
            "math": math, "z": z, "theta": theta, "pi": math.pi,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "min": min, "max": max, "abs": abs, "pow": pow, "sqrt": math.sqrt,
        }
        return float(eval(equation, {"__builtins__": {}}, safe_globals))

    def build_mesh_data(self, equation, zs, ts):
        vertices = []
        faces = []

        def add_v(x, y, z):
            vertices.append((
                x * self.cfg.scale_factor,
                y * self.cfg.scale_factor,
                z * self.cfg.scale_factor
            ))
            return len(vertices)

        outer_rings, inner_rings = [], []

        for iz in range(zs + 1):
            z_out = self.cfg.z_length * iz / zs
            z_in = self.cfg.bottom_thickness + (self.cfg.z_length - self.cfg.bottom_thickness) * iz / zs
            o_ring, i_ring = [], []

            for it in range(ts):
                theta = 2 * math.pi * it / ts
                r_out = self.eval_r(equation, z_out, theta)
                r_in = self.eval_r(equation, z_in, theta) - self.cfg.wall_thickness

                if r_out <= 0:
                    raise ValueError(f"Outer radius <= 0 at z={z_out:.3f}")

                r_in = max(r_in, 0.001)

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

        return np.array(vertices), np.array(faces) - 1

    def save_obj(self, filename, vertices, faces):
        with open(filename, "w", encoding="utf-8") as f:
            f.write("o EquationPot\n")
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")


def parse_resolution(text):
    vals = [int(x.strip()) for x in text.split(",")]
    if len(vals) != 2: raise ValueError("Format: 30, 60")
    return vals


def make_figure(verts=None, faces=None, title="Preview"):
    fig = go.Figure()
    if verts is not None and len(verts) > 0:
        mesh = go.Mesh3d(
            x=verts[:, 0], y=verts[:, 1], z=verts[:, 2],
            i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
            opacity=1.0, color="burlywood", flatshading=True
        )
        fig.add_trace(mesh)
    
    fig.update_layout(
        title=title, template="plotly_dark",
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z", aspectmode="data"),
        margin=dict(l=0, r=0, t=50, b=0),
    )
    return fig


DEFAULT_EQ = "5 * (1 + 0.22 * cos(5 * theta + pi * z / 10))"

# Style for high-contrast inputs
INPUT_STYLE = {
    "width": "100%", "marginBottom": "10px", 
    "color": "black", "backgroundColor": "white",
    "border": "1px solid #ccc", "borderRadius": "4px", "padding": "4px"
}

app = Dash(__name__)
app.title = "Pot Designer"

app.layout = html.Div(
    style={
        "display": "grid", "gridTemplateColumns": "360px 1fr", "gap": "16px",
        "padding": "16px", "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#111", "minHeight": "100vh", "color": "#f5f5f5",
    },
    children=[
        html.Div(
            style={"background": "#1b1b1b", "padding": "16px", "borderRadius": "12px"},
            children=[
                html.H2("Pot Controls"),
                html.Label("File Name"),
                dcc.Input(id="file-name", value="my_pot.obj", type="text", style=INPUT_STYLE),

                html.Label("Radial Equation"),
                dcc.Textarea(id="equation", value=DEFAULT_EQ, style={**INPUT_STYLE, "height": "90px"}),

                html.Label("Height (cm)"),
                dcc.Input(id="height", value=10.0, type="number", style=INPUT_STYLE),

                html.Label("Wall Thickness (cm)"),
                dcc.Input(id="wall", value=0.35, type="number", style=INPUT_STYLE),

                html.Label("Bottom Thickness (cm)"),
                dcc.Input(id="bottom", value=0.5, type="number", style=INPUT_STYLE),

                html.Label("Hole Radius (cm)"),
                dcc.Input(id="hole", value=0.5, type="number", style=INPUT_STYLE),

                html.Label("Preview Res (Z, Theta)"),
                dcc.Input(id="preview-res", value="30, 60", type="text", style=INPUT_STYLE),

                html.Label("Export Res (Z, Theta)"),
                dcc.Input(id="export-res", value="100, 200", type="text", style=INPUT_STYLE),

                html.Button("Generate & Export", id="generate-btn", n_clicks=0,
                            style={"width": "100%", "padding": "12px", "backgroundColor": "#2ecc71", "color": "black", "fontWeight": "bold", "border": "none", "borderRadius": "6px"}),

                html.Div(id="status", style={"marginTop": "14px", "whiteSpace": "pre-wrap", "color": "#2ecc71"}),
            ],
        ),
        html.Div(
            style={"background": "#1b1b1b", "padding": "12px", "borderRadius": "12px"},
            children=[
                dcc.Graph(id="preview-graph", figure=make_figure(title="Waiting..."), style={"height": "88vh"})
            ],
        ),
    ],
)


@callback(
    Output("preview-graph", "figure"),
    Output("status", "children"),
    Input("generate-btn", "n_clicks"),
    State("file-name", "value"),
    State("equation", "value"),
    State("height", "value"),
    State("wall", "value"),
    State("bottom", "value"),
    State("hole", "value"),
    State("preview-res", "value"),
    State("export-res", "value"),
    prevent_initial_call=True,
)
def generate_mesh(n_clicks, file_name, equation, height, wall, bottom, hole, preview_res, export_res):
    try:
        if not file_name.endswith(".obj"): file_name += ".obj"
        pz, pt = parse_resolution(preview_res)
        ez, et = parse_resolution(export_res)

        cfg = MeshConfig(
            output_path=file_name,
            z_length=float(height),
            wall_thickness=float(wall),
            bottom_thickness=float(bottom),
            hole_radius=float(hole),
        )

        exporter = EquationMeshExporter(cfg)

        # Export High-Res
        verts_hi, faces_hi = exporter.build_mesh_data(equation, ez, et)
        exporter.save_obj(file_name, vertices=verts_hi, faces=faces_hi) # FIXED THE PARAMETER NAMES HERE

        # Generate Preview Low-Res
        verts_lo, faces_lo = exporter.build_mesh_data(equation, pz, pt)
        fig = make_figure(verts_lo, faces_lo, title=f"Preview: {file_name}")

        status = f"Success!\nSaved to: {Path(file_name).resolve()}"
        return fig, status

    except Exception as e:
        return make_figure(title="Error"), f"Error: {e}"


if __name__ == "__main__":
    app.run(debug=True)