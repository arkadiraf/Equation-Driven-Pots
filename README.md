# Equation-Driven Pots

A Python project for generating functional 3D-printable plant pots from equations in cylindrical coordinates.

Instead of sculpting a pot manually, this project defines the surface mathematically with a radius function:

`r(z, θ)`

where:

- `z` is the height along the vertical axis
- `θ` is the angle around the axis
- `r` is the radius at that position

The result is a printable hollow vessel generated directly from an equation. By changing the equation, you can create twisted, rippled, lobed, symmetric, or highly organic pot shapes while keeping the object functional for 3D printing.

---

## GUI preview

### PyVista GUI

![PyVista GUI](Images/pyVistaGui.jpg)

---


## How it works

The code evaluates a user-defined equation `r(z, θ)` over a sampled grid of height and angle values.  
From that sampled surface, it generates:

- an outer wall
- an inner wall
- a bottom surface
- a drainage hole
- a closed manifold mesh

The mesh is then exported as an `.obj` file, ready for inspection, slicing, and 3D printing.

---

## Features

- Generate pots from mathematical equations
- Export watertight OBJ meshes
- Control wall thickness, bottom thickness, height, and drainage hole size
- Explore different interfaces:
  - command-line generator
  - Tkinter GUI
  - Dash web GUI
  - PyVista preview GUI

---

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/arkadiraf/Equation-Driven-Pots.git
cd Equation-Driven-Pots
```

### 2. Create a Python environment

Recommended: Python 3.10 or newer

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

If you want everything installed:

```bash
pip install numpy dash plotly pyvista
```

> `tkinter` is usually included with standard Python installations.  
> On some Linux systems, you may need to install it separately with your package manager.

---

## Python scripts and required packages

### `Python/Equation Driven Pottery.py`

Basic command-line OBJ generator.

**Purpose**
- Generates a pot mesh directly from a hardcoded equation
- Exports a manifold OBJ file

**Required packages**
- No external packages
- Uses Python standard library only:
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
- Lets you enter the equation and dimensions in a form
- Exports the generated pot as an OBJ file

**Required packages**
- No external pip packages
- Uses Python standard library only:
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
- Generate the OBJ mesh
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

## Example equation

A pot is generated from a radial function such as:

```python
5 * (1 + 0.22 * cos(5 * theta + pi * z / 10))
```

This defines the radius at each point along height and angle, producing a patterned surface that varies as the pot rises.

You can also build more layered forms using piecewise or frequency-mixed expressions such as:

```python
5 * (
    1
    + min(max((z-0.0)/2.5, 0), 1) * 0.18 * cos(3 * theta)
    + min(max((z-2.5)/2.5, 0), 1) * 0.15 * cos(6 * theta)
    + min(max((z-5.0)/2.5, 0), 1) * 0.10 * cos(12 * theta)
)
```

---

## Pot equations

A collection of pot equations is available here:

[Pot Equations Spreadsheet](https://docs.google.com/spreadsheets/d/e/2PACX-1vRYxQRyGNsDuxl4WaNONKAniyfK-77zSTJY7q4plz88dK7fTNcIbU8814u9wOJ2o2BI10GwCpFbcP3U/pubhtml?widget=true&headers=false)

---

## Gallery

Below is a collection of the designs generated using the provided equations. Each model is exported as a high-resolution `.obj` file and a 3D preview.

![Pot Designs Grid](https://github.com/arkadiraf/Equation-Driven-Pots/blob/main/Images/pot_designs_3xn_grid.jpg?raw=true)

---

## Main parameters

The generators expose several parameters that affect both geometry and printability:

- **Radial Equation** — the mathematical definition of the outer form
- **Pot Height** — total height of the object
- **Wall Thickness** — thickness of the vessel walls
- **Bottom Thickness** — thickness of the floor
- **Drainage Hole Radius** — size of the bottom hole
- **Z Sections** — vertical mesh resolution
- **Theta Sections** — angular mesh resolution / smoothness

Higher section counts produce smoother meshes, but also larger files and slower generation.

---

## Output

The scripts export `.obj` files, which can be opened in tools such as:

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
- inspect the OBJ before slicing
- test small versions first before printing full-size pots

---

## Why this project?

Equation-Driven Pots turns mathematics into fabrication.  
It treats equations not just as descriptions, but as design tools for producing real, usable objects.

This makes it possible to explore procedural form, computational design, and digital fabrication in a simple Python workflow.

---

* * *

## Optional AI-assisted direct generation

In addition to the Python scripts in this repository, you can use the included prompt file to ask an AI model to generate a 3D pot mesh directly.

Prompt file:

- [`3dPotGenerator.txt`](./3dPotGenerator.txt)

Tested with:

- Gemini Thinking mode
- ChatGPT Thinking mode

The prompt instructs the model to generate and run Python code that creates a printable `.obj` file, produces a preview image, and returns a downloadable result.

This is useful if you want a fast, portable workflow for one-off pot generation without manually editing the scripts first.

> This prompt-based workflow is experimental and not consistent. Results may vary between models, versions, and runs.

* * *

## License

This repository is licensed under GPL-3.0.
