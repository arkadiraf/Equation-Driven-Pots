# Equation-Driven Pots

**Equation-Driven Pots** is a design and fabrication project for generating functional, 3D-printable plant pots from mathematical equations.

Instead of sculpting a vessel manually, this project defines the outer surface through radius functions such as:

- `r(z, θ)` for cylindrical-coordinate generation
- `r(θ, φ)` for spherical-coordinate generation

where:

- `z` is height along the vertical axis
- `θ` is the angular position around the axis
- `φ` is the polar angle in spherical coordinates
- `r` is the radius at that position

This approach produces printable hollow vessels directly from equations. By changing the math, you can create twisted, ribbed, lobed, symmetric, or highly organic forms while preserving practical features needed for 3D printing.

---

## GUI preview

### PyVista GUI

![PyVista GUI](Images/pyVistaGui.jpg)

### Fusion 360 MathSweep Studio

![Fusion 360 MathSweep Studio](Images/Fusion360Gui.jpg)

---

## HTML tool previews

### Pot Designer HTML

![Pot Designer HTML](Images/PotDesignerHTML.jpg)

### 3D Sweep Designer HTML

![3D Sweep Designer HTML](Images/3DSweepDesignerHTML.jpg)

### Spherical Pot Designer HTML

![Spherical Pot Designer HTML](Images/SphericalPotDesignerHTML.jpg)

### Textured Unified Pot Designer HTML

![Textured Unified Pot Designer](Images/TexturedPotDesigner.jpg)

### Multi-Color Pot Designer HTML

[Multi-Color Pot Designer GUI](https://github.com/arkadiraf/Equation-Driven-Pots/blob/main/JavaScript/MultiColorPotDesigner.html)

![Multi-Color Pot Designer GUI](https://github.com/arkadiraf/Equation-Driven-Pots/blob/main/Images/MultiColorPotDesigner.jpg?raw=true)

---

## How it works

The tools evaluate a user-defined equation over a sampled grid and convert that surface into printable geometry.

For cylindrical designs, the main form is defined by:

`r(z, θ)`

For spherical designs, the form is defined by:

`r(θ, φ)`

From the sampled surface, the tools generate printable geometry such as:

- an outer wall
- an inner wall
- a bottom surface
- drainage holes
- closed manifold meshes for export

Depending on the tool, the resulting geometry can be exported as `.obj`, `.stl`, or multi-part `.3mf` for inspection, slicing, and fabrication.

---

## Features

- Generate printable pots directly from mathematical equations
- Support both cylindrical and spherical equation-driven workflows
- Control wall thickness, bottom thickness, height, and drainage-hole size
- Explore multiple interfaces for different workflows:
  - command-line generator
  - Tkinter desktop GUI
  - Dash web GUI
  - PyVista preview GUI
  - browser-based HTML pot designer
  - browser-based spherical pot designer
  - browser-based sweep designer
  - Fusion 360 parametric sweep reconstruction script
  - unified textured pot designer
  - multi-color pot designer
- Export printable geometry in `.obj` and `.stl`
- Export multi-part `.3mf` assemblies for color-separated workflows
- Keep the repository lightweight while hosting representative previews and tools in one place

---

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/arkadiraf/Equation-Driven-Pots.git
cd Equation-Driven-Pots
```

### 2. Create a Python environment

Recommended: Python 3.10 or newer.

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install packages

If you want the main Python tools available in one environment:

```bash
pip install numpy dash plotly pyvista
```

> `tkinter` is usually included with standard Python installations.  
> On some Linux systems, you may need to install it separately through your package manager.

---

## Python scripts and required packages

### `Python/Equation Driven Pottery.py`

Basic command-line OBJ generator.

**Purpose**

- Generates a pot mesh directly from a hardcoded equation
- Exports a manifold OBJ file

**Required packages**

- No external packages
- Uses only the Python standard library:
  - `math`
  - `dataclasses`

**Run**

```bash
python "Python/Equation Driven Pottery.py"
```

---

### `Python/Equation Driven PotteryGui.py`

Simple desktop GUI built with Tkinter.

**Purpose**

- Lets you enter the equation and dimensions through a form
- Exports the generated pot as an OBJ file

**Required packages**

- No external pip packages
- Uses the Python standard library:
  - `math`
  - `tkinter`
  - `dataclasses`
  - `os`

**Run**

```bash
python "Python/Equation Driven PotteryGui.py"
```

---

### `Python/GuipyVista.py`

Desktop GUI with PyVista-based 3D preview.

**Purpose**

- Generate an OBJ mesh
- Open a rendered preview in a PyVista viewer

**Required packages**

- External:
  - `pyvista`
- Standard library:
  - `math`
  - `tkinter`
  - `dataclasses`
  - `os`

**Install**

```bash
pip install pyvista
```

**Run**

```bash
python "Python/GuipyVista.py"
```

---

### `Python/GuiDash.py`

Browser-based interface using Dash and Plotly.

**Purpose**

- Enter an equation in a web app
- Preview the pot in 3D
- Export a higher-resolution OBJ file

**Required packages**

- External:
  - `numpy`
  - `dash`
  - `plotly`
- Standard library:
  - `math`
  - `os`
  - `dataclasses`
  - `pathlib`

**Install**

```bash
pip install numpy dash plotly
```

**Run**

```bash
python "Python/GuiDash.py"
```

Then open the local Dash address shown in the terminal.

---

### [`Python/Fusion360/3d MathSweep Studio.py`](./Python/Fusion360/3d%20MathSweep%20Studio.py)

Fusion 360 script for reconstructing equation-driven swept geometry directly inside Fusion.

**Purpose**

- Rebuild a 3D swept form in Fusion 360 from a mathematical path and a base profile
- Make the design easier to inspect, edit, and continue modeling as native Fusion geometry
- Provide a more CAD-friendly workflow than importing a mesh from the sweep designer

This tool is useful when the goal is to continue working with editable CAD geometry instead of a lightweight imported mesh.

**How to add it in Fusion 360**

1. Open **Fusion 360**
2. Go to **Utilities**
3. Open **Add-Ins**
4. Open **Scripts and Add-Ins**
5. Click **+ New Script**
6. Copy or place `3d MathSweep Studio.py` into the created script folder
7. Return to **Scripts and Add-Ins**, select the script, and run it

**Notes**

- The script is heavier on Fusion 360 than the mesh-based workflow
- More complex profiles and higher section counts can noticeably slow generation
- The Fusion workflow is best when editable CAD geometry is more important than speed

**Required packages**

- No external pip packages
- Runs inside Fusion 360's Python environment
- Uses Fusion API modules such as:
  - `adsk.core`
  - `adsk.fusion`
  - `math`
  - `traceback`

---

## HTML / JavaScript tools

### [`JavaScript/PotDesigner.html`](./JavaScript/PotDesigner.html)

Browser-based pot designer for creating printable 3D pots directly in HTML and JavaScript.

**Purpose**

- Works similarly to the Python pot generator
- Lets you adjust the pot equation and geometry in the browser
- Exports the generated design as OBJ or STL

---

### [`JavaScript/SphericalPotDesigner.html`](./JavaScript/SphericalPotDesigner.html)

Browser-based spherical-coordinate pot designer for creating printable pots from equations of the form `r(θ, φ)`.

**Purpose**

- Design pots using spherical coordinates instead of cylindrical coordinates
- Explore forms that are easier to describe with `r(θ, φ)` than with `r(z, θ)`
- Preview the generated shape directly in the browser
- Export the generated design for downstream 3D modeling and printing workflows

This tool extends the project beyond height-based radial pot design and opens up a broader design space for equation-driven vessels.

---

### [`JavaScript/SweepDesigner.html`](./JavaScript/SweepDesigner.html)

Browser-based 3D sweep designer for creating guided swept forms.

**Purpose**

- Build more complex 3D swept shapes interactively
- Export the generated design as OBJ or STL
- Use the output as a starting point for more intricate pot designs

---

### [`JavaScript/TexturedPotDesigner.html`](./JavaScript/TexturedPotDesigner.html)

Browser-based unified pot designer for creating printable pots from both cylindrical and spherical coordinate systems, with optional surface texture applied directly to the outer shell.

**Purpose**

- Combine cylindrical and spherical pot design in one interface
- Switch between equation systems within a single tool
- Add external texture displacement on top of the base pot form
- Preview the generated shape directly in the browser
- Export the generated design as STL

**Texture variables**

The unified textured designer uses a base-form equation together with a texture displacement equation.

The base form defines the main pot shape, and the texture equation adds or subtracts small surface offsets on the outside of the pot.

Common variables used in the tool:

- `r` — final radius at a point on the surface
- `T` — texture displacement amount
- `θ` — angular position around the pot
- `z` — height in cylindrical mode
- `φ` — polar angle in spherical mode
- `v` — normalized vertical position from `0.0` to `1.0`

Conceptually, the textured version behaves like:

`final radius = base radius + texture displacement`

This keeps the vessel form and the surface relief separate, allowing one equation to control the overall shape while another controls the visible texture.

---

### [`JavaScript/MultiColorPotDesigner.html`](https://github.com/arkadiraf/Equation-Driven-Pots/blob/main/JavaScript/MultiColorPotDesigner.html)

Browser-based multi-color pot designer for creating printable pots with equation-driven base geometry, external texture, and separable color regions.

**Purpose**

- Combine cylindrical and spherical pot generation in one browser-based tool
- Preview equation-driven pot geometry live in 3D
- Generate multi-color pots by splitting the model into a base body and a pattern body
- Export a slicer-friendly multi-part `.3mf` assembly for color assignment in supported slicers
- Export `.stl` for single-mesh workflows

**Capabilities**

- Supports both coordinate systems in one interface:
  - cylindrical extrusion using `r(θ, z, v)`
  - spherical wrapping using `r(θ, φ, v)`
- Includes preset libraries for:
  - base scaffold equations
  - external surface texture equations
  - color pattern masks
- Lets you define:
  - base-form equations
  - texture-displacement equations
  - pattern-mask equations
- Supports functional pot geometry such as:
  - wall thickness
  - flat or thickened bottom regions
  - drainage holes
- Includes controls for:
  - base color
  - pattern color
  - pattern depth
  - mesh resolution
  - pattern resolution
- Includes responsive mobile scaling while preserving the desktop layout

**Pattern logic**

The Multi-Color Pot Designer separates the object into a base body and a pattern body using a mathematical pattern mask. This makes it possible to turn selected parts of the outer surface into a second printable part for multi-color slicing workflows.

The pattern system supports:

- texture-based selection using the raised share of the external texture
- outer-envelope selection using a cylindrical or spherical reference envelope
- direct custom equations written in the pattern mask field

**Output**

The tool supports:

- `.3mf` export for multi-part color workflows
- `.stl` export for standard mesh workflows

The multi-part workflow is intended for slicers that can import multiple parts as one object and allow each part to be assigned to a different filament.

---

## Example equations

A cylindrical pot can be generated from a radial function such as:

```python
5 * (1 + 0.22 * cos(5 * theta + pi * z / 10))
```

This defines the radius at each point along height and angle, producing a patterned surface that changes as the pot rises.

You can also build layered forms using piecewise or frequency-mixed expressions such as:

```python
5 * (
    1
    + min(max((z-0.0)/2.5, 0), 1) * 0.18 * cos(3 * theta)
    + min(max((z-2.5)/2.5, 0), 1) * 0.15 * cos(6 * theta)
    + min(max((z-5.0)/2.5, 0), 1) * 0.10 * cos(12 * theta)
)
```

A spherical pot can be generated from an equation of the form:

```python
r(theta, phi)
```

which defines the radius as a function of azimuthal angle and polar angle.

---

## Pot equations

A collection of equations is available here:

[Pot Equations Spreadsheet](https://docs.google.com/spreadsheets/d/e/2PACX-1vRYxQRyGNsDuxl4WaNONKAniyfK-77zSTJY7q4plz88dK7fTNcIbU8814u9wOJ2o2BI10GwCpFbcP3U/pubhtml?widget=true&headers=false)

The spreadsheet includes both cylindrical and spherical equations.

---

## Gallery

### Cylindrical pot designs

![Pot Designs Grid](https://github.com/arkadiraf/Equation-Driven-Pots/blob/main/Images/pot_designs_3xn_grid.jpg?raw=true)

### Spherical design summary

![Spherical Design Summary](Images/spherical_design_summary.jpg)

Example 3D models for the spherical designer are hosted on Thingiverse to keep the repository lightweight:

[Equation-Driven Pots on Thingiverse](https://www.thingiverse.com/thing:7327538)

---

## Main parameters

The generators expose several parameters that affect both geometry and printability:

- **Radial Equation** — the mathematical definition of the outer form
- **Pot Height** — total height of the object
- **Wall Thickness** — thickness of the vessel walls
- **Bottom Thickness** — thickness of the floor
- **Drainage Hole Radius** — size of the bottom hole
- **Z Sections** — vertical mesh resolution
- **Theta Sections** — angular mesh resolution and smoothness
- **Phi Sections** — polar sampling resolution for spherical designs

Higher section counts produce smoother meshes, but they also increase file size and generation time.

---

## Output

The scripts and HTML tools export `.obj` files, and the HTML tools also support `.stl` output.

The Multi-Color Pot Designer additionally supports multi-part `.3mf` export for color-separated workflows.

These files can be opened in tools such as:

- Blender
- MeshLab
- PrusaSlicer
- Cura
- other 3D modeling or slicing software

---

## 3D printing notes

For best results:

- keep wall thickness large enough for your nozzle and material
- avoid equations that produce negative or near-zero radii
- use higher angular resolution for sharp ripples or high-frequency patterns
- inspect the mesh before slicing
- test small versions before printing full-size pots

---

## Why this project?

Equation-Driven Pots turns mathematics into fabrication.

It treats equations not only as descriptions, but as design tools for producing real, usable objects. The project brings together procedural form, computational design, digital fabrication, browser-based interactive design, and CAD reconstruction in a practical workflow.

---

## Optional AI-assisted direct generation

In addition to the Python and HTML tools in this repository, you can also use AI to generate a 3D pot mesh directly.

**AI workflows**

- feed the Python pot-generation scripts to a capable AI model
- use the included prompt file: [`3dPotGenerator.txt`](./3dPotGenerator.txt)

**Tested with**

- Gemini Thinking mode
- ChatGPT Thinking mode

The prompt-based workflow instructs the model to generate and run Python code that creates a printable `.obj` file, produces a preview image, and returns a downloadable result.

This is useful when you want a fast, portable workflow for one-off pot generation without manually editing the scripts first.

> This workflow is experimental and may produce inconsistent results depending on the model, version, and run.

---

## License

This repository is licensed under GPL-3.0.
