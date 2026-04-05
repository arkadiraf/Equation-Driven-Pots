# Equation-Driven Pots

Equation-Driven Pots is a math-based 3D design project for generating printable pots, vessels, plates, and related forms from equations.

Instead of sculpting a shape manually, the project defines geometry through sampled mathematical fields in cylindrical or spherical coordinates. That makes it possible to design objects by controlling radial form, texture, color masks, field modifiers, and spatial distortions with equations.

## Live unified GUI

The main browser tool is now the unified **Equation Driven Pot Designer**, available here:

[Equation Driven Pot Designer](https://arkadiraf.github.io/Equation-Driven-Pots/)

![Equation Driven Pot Designer](https://github.com/arkadiraf/Equation-Driven-Pots/blob/main/Images/EquationDrivenPotDesigner.jpg?raw=true)

This all-in-one GUI brings the current browser workflow together in a single interface. It includes:

- cylindrical and spherical coordinate modes
- base scaffold libraries
- structural geometry controls
- surface texture controls
- dual color-mask pattern logic
- plate and pot+plate generation
- STL and multi-part 3MF export
- two experimental math tools:
  - **Field Modifier**
  - **Field Distortion**

The current unified GUI exposes those experimental tools directly in the sidebar as separate sections after the core pot workflow, so they can be layered on top of the main design rather than used as a completely separate app.

## Core idea

For cylindrical designs, the main shape is sampled from a field such as:

```text
r = f(theta, z, v, R)
```

For spherical designs, the main shape is sampled from a field such as:

```text
r = f(theta, phi, v, R)
```

Where:

- `theta` is the angle around the object
- `z` is the sampled vertical coordinate in cylindrical mode
- `phi` is the polar coordinate in spherical mode
- `v` is the normalized vertical progression from `0` to `1`
- `R` is the base radius parameter

The project then builds printable geometry such as outer walls, inner walls, bottoms, drainage openings, and closed shells from those sampled fields.

## Unified browser workflow

The current browser workflow is built around four main design layers:

### 1. Base scaffold

The base scaffold defines the main silhouette of the form.

This can be:
- geometric
- floral
- folded
- nonlinear
- interference-based

Examples include polygonal sections, petal blooms, rounded-square scaffolds, layered harmonic growth, wrapped modular panels, and nonlinear compressed forms.

### 2. Structural geometry

The structural layer turns the field into an actual printable object.

This includes:
- designed figure mode
- functional pot mode
- functional plate mode
- pot + plate mode
- wall thickness
- bottom thickness
- drainage controls
- spherical cut settings
- plate height and plate sizing controls

This is where the project shifts from pure surface design into usable 3D-printable objects.

### 3. Surface texture

Texture is applied as a separate field on top of the base scaffold.

Conceptually:

```text
final radius = base radius + texture displacement
```

This separation keeps the main silhouette and the surface relief independent. One equation can define the vessel body while another adds ribs, weave, terracing, nonlinear compression, or carved interference.

### 4. Dual pattern color layer

Two mask equations define up to four printable color states:

- neither pattern
- pattern A only
- pattern B only
- overlap of A and B

This allows the GUI to produce more structured multi-color results without requiring the base form itself to become overly complex.

## Experimental math tools

The unified GUI now includes two experimental design layers that push the project beyond static equation-defined surfaces.

### Field Modifier

The **Field Modifier** changes where a field is sampled before it is evaluated.

In its current form, the main idea is:

```text
theta' = theta + strength * M(theta, z, v)
```

and the selected field is then evaluated using the modified coordinate.

This allows effects such as:

- twist drift
- crown rotation
- petal migration
- diagonal braid motion
- rim-localized activity
- regional modifier windows

Field modifiers are useful when the shape should still behave like a pot, but the sampled structure should drift, rotate, fold, or migrate through the body.

### Field Distortion

The newer **Field Distortion** layer works differently.

Instead of changing where the field is sampled, it changes where the generated body exists in world space after the field has already been evaluated.

Conceptually:

```text
x' = x + Dx
y' = y + Dy
z' = z + Dz
```

This opens up more physical and sculptural behaviors such as:

- wind bend
- gravity sag
- swirl and vortex motion
- torsion in the `x-z` plane
- crown turning
- local pressure dents
- hand-formed asymmetry

In the current unified GUI, distortion presets are grouped by type such as:

- wind
- gravity
- swirl
- torsion
- pressure
- custom

That is an important expansion of the project. The design process is no longer limited to changing radial equations alone. The project now supports both **field-based shape generation** and **post-field spatial deformation** inside the same browser tool.

## Why the experimental tools matter

The two experimental tools expand the project in two different directions:

- **Field Modifier** changes the sampled coordinates used by the field.
- **Field Distortion** changes the generated body in world XYZ space.

Field modifiers are ideal for:
- rotational drift
- petal motion
- remapped symmetry
- region-aware field behavior

Field distortions are ideal for:
- wind-like lean
- fluid twist
- torsion
- pressure and denting
- more tactile or physically suggestive deformations

Together, they move the project from “equation-defined pots” toward a broader system of **equation-driven 3D design** while still keeping printability and object function central.

## Main browser tools

The repository currently centers on a small set of browser tools:

### [Equation Driven Pot Designer](./JavaScript/EquationDrivenPotDesigner.html)

The current all-in-one browser GUI.

**Purpose**
- unified cylindrical and spherical workflow
- textured equation-driven design
- dual-mask color logic
- structural pot / plate / pot+plate generation
- experimental field modifier and field distortion layers
- STL and multi-part 3MF export

### [Textured Pot Designer](./JavaScript/TexturedPotDesigner.html)

The stable browser-based textured pot designer.

**Purpose**
- cylindrical and spherical pot design in one interface
- separate base and texture equations
- practical and stable workflow for printable forms

### [Quad Color Pot Designer](./JavaScript/QuadColorPotDesignerMobile.html)

The browser-based color-pattern workflow that introduced layered mask logic.

**Purpose**
- combine base shape, texture, and two mask equations
- produce four printable color states from two fields
- explore multi-material / multi-color styling

### [Sweep Designer](./JavaScript/SweepDesigner.html)

The guided sweep workflow for more path-driven 3D forms.

**Purpose**
- create swept forms with more explicit path/profile logic
- serve as a bridge toward Fusion-based reconstruction and CAD continuation

## Python and Fusion scripts

The repository still includes the earlier Python and Fusion tools that formed the basis of the project.

These remain useful as reference implementations, alternate workflows, and foundations for future extensions:

- command-line pot generation
- Tkinter GUI
- Dash web interface
- PyVista preview GUI
- Fusion 360 MathSweep Studio

The browser tools are now the main public-facing workflow, but the Python and Fusion scripts still show how the project evolved and remain useful for experimentation and reconstruction workflows.

## Equation generator prompt

The repository also includes an AI prompt file that helps turn a design description into equations for the pot-design GUIs:

[EquationGeneratorPrompt.txt](./EquationGeneratorPrompt.txt)

This prompt can help users describe the kind of pot or form they want and receive implementation-ready equations for the relevant interface.

## How the project has evolved

The browser side of the project has gradually expanded in layers:

1. equation-defined radial pot generation
2. unified cylindrical + spherical workflows
3. texture displacement
4. dual-mask color logic
5. nonlinear field equations
6. field modifiers
7. field distortion
8. structural plate and pot+plate generation in the unified GUI

That progression matters because the project is still fundamentally math-based. Even as the forms become more complex, the workflow remains centered on sampled mathematical fields rather than manual sculpting.

## Output

The current browser tools support:

- STL export
- multi-part 3MF export

These outputs can be opened in tools such as:

- PrusaSlicer
- Cura
- Blender
- MeshLab
- other modeling or slicing tools

## Design and print notes

For better results:

- keep wall thickness appropriate for your nozzle and material
- avoid equations that create negative or near-zero radii
- increase angular resolution for sharp high-frequency detail
- keep modifier and distortion strengths moderate unless intentionally exploring extreme forms
- inspect multi-part exports carefully when combining pots and plates
- prototype smaller prints first before scaling up

## Why this project

Equation-Driven Pots treats mathematics as a direct design medium.

It is not just about describing forms mathematically after the fact. The equations are the design process itself. The newer unified GUI extends that idea further by combining stable printable vessel generation with more experimental field-based and distortion-based workflows in a single browser interface.
