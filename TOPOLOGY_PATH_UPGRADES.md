# Topology Path Upgrades — Review and Proposal

Status: **proposal; not implemented**  
Primary target: `EquationDrivenWovenPots.html`  
Related design note: `MULTI_STRAND_PLAN.md`

## Purpose

The current topology-path system is a strong base: paths are expressed as `x(t)`, `y(t)` and
`z(t)`, path-specific parameters are data-driven, traversal periods can be calculated from those
parameters, closed-loop sweep frames are twist-corrected, Custom Path designs round-trip through
Design JSON, and exact CSG handles self-intersections.

The next upgrades should make those mathematical paths easier to see, safer to edit, and capable
of producing genuinely woven multi-strand structures. Adding more single-strand presets before
those foundations are improved would expand the list without fixing the main limitations observed
in the live application.

## Executive recommendation

Implement the work in this order:

1. **Topology Preview and Fit View** — make the selected centerline visible independently of the
   final thick vessel mesh.
2. **Path validation and typed parameters** — report expression, closure and cusp problems before
   CSG runs.
3. **Arc-length-aware sampling** — distribute mesh resolution according to distance and curvature,
   not only the equation parameter.
4. **True multi-strand generation** — use spatial or local-frame offsets, not a closed curve's
   parameter offset.
5. **Alternating over/under crossings** — add a crossing mode that reads as an actual weave.
6. **New path families and a visual preset gallery** — expand the library after the core can show
   and validate them properly.

## Findings from the live application

### 1. The shipped geometry hides much of the selected topology

The default profile equation is `3.0`, so the circular strand has a radius of 3 cm. The default
Path Diameter is 5 cm, which gives `rx = 2.5 cm`. The strand is therefore thicker than the base
path radius before the path's own amplitude is considered.

This produces an attractive solid vessel, but several mathematically different paths merge into
similar bulbous forms:

- Torus Knot and Spherical Knot are difficult to distinguish at a glance.
- Flower Ring and Braided Loop lose much of their crossing structure.
- Lissajous Tangle reads as a lobed vessel instead of a free three-dimensional tangle.
- Möbius Curve and Coiled Basket remain more recognizable because their global silhouettes differ
  more strongly.

When Lissajous Tangle was tested in Object mode with the profile reduced from `3.0` to `0.6`, its
topology immediately became legible. This should not require destructively changing the intended
final strand thickness.

**Recommendation:** add a lightweight **Topology Preview** that draws the centerline or a thin
temporary tube without running the complete shell, pattern and plate CSG pipeline. Also display a
read-only ratio such as:

```text
maximum profile radius / base path radius
```

Warn when this ratio is high enough that separate arms are expected to merge extensively. An
optional relative profile scale can be added later, but it should not silently rewrite a custom
profile equation.

### 2. One global design is not a suitable demonstration preset for every path

Switching Topology Path currently changes the path parameters and default Y rotation, but retains
the Torus Knot's profile, cuts, plate, colour masks, thickness and other global settings. During the
live review the unchanged default configuration removed the following debris components:

| Path | Debris shells removed |
|---|---:|
| Coiled Basket | 8 |
| Flower Ring | 32 |
| Möbius Curve | 21 |
| Lissajous Tangle | 17 |

These counts are not automatically geometry failures, but they show that path selection is not the
same thing as selecting a complete, representative preset.

**Recommendation:** allow each `pathLib` row to declare an optional `recommendedGeometry` object:

- path diameter and Z scale;
- profile preset/equation;
- model mode and useful cut percentages;
- default orientation;
- recommended plate strategy;
- optional self-intersection handling;
- camera hint, if one is ever required.

Expose this through an **Apply Recommended Geometry** button. Merely changing the selected path
must not overwrite settings the user has already edited.

### 3. The camera only fits the first generated model

`runPreview()` calls `fitCameraToObject()` only while `hasFitCamera` is false. A later path or scale
change can therefore leave the model tiny, oversized or poorly framed. This was visible immediately
after switching Lissajous Tangle to a thin profile.

**Recommendation:**

- add a persistent **Fit View** button;
- automatically refit after Topology Path, Path Diameter, Z-Stretch or Model Type changes;
- do not refit for colour, texture or other changes that do not materially change the bounding box;
- preserve a deliberately manipulated camera unless the new bounds no longer fit the viewport.

### 4. Important path warnings are visually detached from their controls

The Flower Ring warning correctly explains that `Weave * n` must exceed 1 before its angular map
becomes non-monotone. The message is placed in the global status pill at the bottom of the viewer,
where it competes with triangle counts, debris, pattern and plate status.

**Recommendation:** retain the global status summary, but render path-specific warnings directly
below the relevant parameter. When a safe fix is unambiguous, offer a small action such as
**Set minimum interlacing value**.

### 5. Preset names and filenames drift apart

After another topology is selected, Design File Name can remain `Torus Knot`. Update a generated
name automatically while it is still untouched, but preserve any name the user entered manually.

### 6. The parameter panel does not scale well

Lissajous Tangle has six full-width parameter rows. Custom Path adds four more parameters and three
equation fields. Use a two-column grid for short numeric controls, keep equations full width, and
place related parameters in small groups such as Frequency, Phase, Shape and Orientation.

## Core architecture upgrades

### A. Make `pathLib` the actual registry

The source describes path definitions as fully data-driven, but the `<select>` options are also
hard-coded in the HTML. Generate the Topology Path menu from `pathLib` so adding a path really does
require only one registry entry.

A proposed row shape is:

```js
{
    label: "Flower Ring",
    category: "Wound / Rosette",
    description: "A vertically undulating ring with optional angular backtracking.",
    params: [
        { id: "n", label: "Petals", value: 5, step: 1, type: "integer", min: 2 },
        { id: "amp", label: "Amplitude", value: 3, step: 0.1, min: 0 },
        { id: "weave", label: "Weave", value: 0.25, step: 0.05 }
    ],
    x: "...",
    y: "...",
    z: "...",
    period: params => 2 * Math.PI,
    recommendedGeometry: { /* optional */ },
    plateMode: "silhouette"
}
```

Parameter metadata should support:

- `integer`, `float` and possibly `angle` types;
- minimum and maximum values;
- soft recommended ranges distinct from hard limits;
- unit labels;
- inline help;
- a validator or advisory function;
- grouping and display order.

### B. Add a Topology Inspector

Before creating sweep rings, sample the centerline and calculate:

- evaluated traversal period;
- endpoint closure distance;
- endpoint tangent mismatch;
- approximate path length;
- bounding-box dimensions and centre;
- minimum and maximum sampled segment length;
- minimum tangent magnitude and cusp candidates;
- minimum non-local centreline separation;
- approximate crossing/near-contact count;
- maximum profile radius and clearance ratio;
- whether the path is probably a single traversal or a retrace.

Show a concise summary near Topology Path and expose the detailed values in a collapsible inspector.
The same result should feed warnings and export validation instead of every feature independently
recomputing similar facts.

### C. Report expression errors instead of collapsing a coordinate to zero

`compilePathExpr()` currently converts a syntax error into a function that returns zero, and
runtime failures are also reduced to zero by the sampler. This can create a degenerate but
apparently intentional-looking model.

Replace silent fallback with structured results:

```js
{
    ok: false,
    axis: "x",
    source: "...",
    message: "Unexpected token ...",
    sampleT: null
}
```

Runtime validation should sample the compiled function before CSG and report the first non-finite
result with its `t` value. Keep the previous valid preview visible, mark the failing equation, and
disable export until the path is valid.

### D. Validate closure and tangent continuity

The sweep assumes a closed curve, but numeric inputs can violate that assumption even for built-in
paths. HTML `step="1"` does not prevent a fractional value from being typed for `p`, `q`, `k`,
`halfTwists`, `nx`, `ny` or `nz`.

For the chosen period `P`, compare:

```text
|C(P) - C(0)|
angle(C'(P), C'(0))
```

Use a tolerance relative to the path's bounding-box diagonal. A large position error must block
the final sweep rather than letting the ring connection bridge the gap. A large tangent mismatch
should be an explicit kink warning. Integer fields should be validated as integers rather than
silently rounded only inside period calculations.

### E. Resample by arc length

`buildSweepFrames()` currently samples uniformly in `t`. A 400-step numerical check using the
shipped path defaults found these maximum/minimum segment-length ratios:

| Path | Segment-length ratio |
|---|---:|
| Torus Knot | 1.83x |
| Spherical Knot | 7.20x |
| Coiled Basket | 1.67x |
| Flower Ring | 2.86x |
| Braided Loop | 2.96x |
| Möbius Curve | 4.12x |
| Lissajous Tangle | 3.69x |
| Custom looping rosette | 3.87x |

Uniform `t` therefore oversamples slow parts while leaving fast sections relatively coarse. It can
also reduce the reliability of proximity tests because neighbouring rings represent very different
physical distances.

Recommended process:

1. sample the equation at 4-8 times the requested Path Steps;
2. build a cumulative-length table;
3. interpolate `sections + 1` points at equal arc-length targets;
4. optionally add samples in regions with high curvature or low non-local clearance;
5. build rotation-minimizing frames from the resampled points.

Because changing sampling can alter triangle positions and pattern boundaries, store a Design JSON
field such as `samplingMode: "parametric" | "arcLength"`. Existing designs can retain legacy
parametric sampling while new designs default to arc-length sampling.

## Multi-strand correction and design

### Important correction to `MULTI_STRAND_PLAN.md`

The existing plan proposes strand `k` as:

```text
Ck(t) = C(t + k * period / N)
```

For any closed curve with period `P`, this is only a change of starting point:

```text
{ C(t + delta) : 0 <= t < P } = { C(t) : 0 <= t < P }
```

Every copy traverses the same geometric locus. A point-by-point comparison might not identify the
copies as equal because their samples are cyclically shifted, but their swept solids are still
coincident. A `t` offset alone therefore cannot generate multiple strands.

### Recommended strand modes

#### 1. Cable mode — generic and path-independent

Use each centreline's rotation-minimizing frame:

```text
Ck(s) = C(s)
      + d * cos(twist * 2*pi*s + phaseK) * N(s)
      + d * sin(twist * 2*pi*s + phaseK) * B(s)

phaseK = 2*pi*k/N
```

where `s` is normalized arc length, `N/B` are the local normal and binormal, `d` is strand spacing,
and `twist` controls how many times the strands braid around the guide path.

This works for every built-in path and Custom Path without assuming a global axis.

#### 2. Axial array mode — useful for vessel-scale arrangements

Create spatially rotated copies around the global Z axis, with optional radial and Z offsets. This
is appropriate for baskets and crowns, but not every path is axis-centred. Detect coincident copies
using a symmetric nearest-point/Hausdorff-style comparison rather than comparing equal parameter
indices.

#### 3. Expression-controlled mode — maximum flexibility

Expose these values in path-expression scope:

```text
strand       zero-based strand index
strands      total strand count
strandPhase  2*pi*strand/strands
s             normalized arc length, when available
```

Each path can then decide whether strand phase belongs in its winding angle, vertical wave, radial
wave or another term. This produces genuinely distinct curves while keeping Custom Path open-ended.

### Suggested multi-strand UI

- Strand Mode: `Single`, `Cable`, `Axial Array`, `Expression-Controlled`
- Strand Count: integer, default 1
- Strand Spacing: cm
- Cable Twist Count
- Array Rotation Offset
- Array Z Offset
- Alternate Profile Scale: optional later feature
- Expose Strand Index to Pattern Masks

`count = 1` must reproduce the current geometry exactly when legacy sampling is selected.

## True crossing semantics

The current choices are effectively:

- **Merge:** union touching arms into one solid.
- **Pinch:** reduce the profile radius so arms avoid intersection.

Add a third mode:

- **Alternating Over/Under:** assign an ordering to crossing pairs and apply a smooth local
  displacement so one arm passes above/outside while the other passes below/inside.

Suggested controls:

- Crossing Mode: `Merge`, `Pinch`, `Alternating`
- Crossing Clearance: mm
- Transition Length: cm or fraction of path length
- Starting Parity: `A over first` / `B over first`
- Conflict Policy: warn when a closed crossing graph cannot satisfy the requested alternation

The existing non-local proximity data can propose crossing candidates, but candidates should be
refined to closest points on centreline segments. Merely finding nearby sampled rings is not enough
to define stable crossing order.

## Reusable path operators

Several useful shape controls should be applied after the base sampler instead of being duplicated
inside selected equations:

- scale X/Y/Z;
- radial taper or height envelope;
- global twist around Z;
- mirror X/Y/Z;
- phase/start-point rotation;
- bend or squash;
- bounded harmonic/noise displacement;
- normalize or fit to requested width/height;
- centre on bounding box or centroid.

Operators should be ordered, individually enabled, and serialized. The unmodified operator stack
must remain an exact pass-through for backward compatibility.

## Preset additions

### Priority 1: Figure-Eight Knot

This is the most useful missing canonical knot because it is not another member of the torus-knot
family and has an immediately recognizable crossing structure. A suitable starting family is:

```text
x(t) = (rx + amp*cos(2*t)) * cos(3*t)
y(t) = (rx + amp*cos(2*t)) * sin(3*t)
z(t) = zA * sin(4*t)
period = 2*pi
```

### Priority 2: Harmonic/Fourier Knot

Generalize Lissajous Tangle from one cosine per axis to two or three harmonics. Keep the first UI
version constrained to a few understandable amplitudes, frequencies and phases; the Custom Path
editor remains available for unrestricted expressions.

### Priority 3: Superformula Rosette

Use a Gielis/superformula radial function to create rounded polygons, stars and organic floral
forms, combined with a vertical harmonic. It is visually diverse without requiring a new sweep
architecture.

### After multi-strand support

- Turk's Head / Celtic Braid
- Cable Basket
- Linked Rings / Chain Link
- Alternating thick-and-thin cane braid
- Strand-index colour presets

### Long-term special topology

**Möbius Ribbon** should be treated as a real oriented ribbon or band, not only as a tube following
one Möbius boundary curve. It requires deliberate profile orientation/twist semantics and may need
a specialized builder.

## User-interface proposal

### Compact topology header

The current Base Scaffold section is collapsed at startup even though Topology Path is the defining
feature. Keep a compact always-visible header containing:

- selected path name;
- small thumbnail or centreline icon;
- validation state;
- actual overall dimensions;
- Topology Preview and Fit View buttons.

### Visual path gallery

Replace or supplement the plain dropdown with categorized cards:

- **Wound knots:** Torus, Spherical, Figure-Eight
- **Vessel coils:** Coiled Basket
- **Rosettes:** Flower Ring, Braided Loop, Superformula
- **Space curves:** Möbius Curve, Lissajous, Harmonic Knot
- **Custom:** Custom Path

Each card should show a thin-strand thumbnail so differences are visible before the final vessel
profile merges them.

### Naming behavior

Track whether Design File Name is automatic or user-edited:

- selecting a new path updates an automatic name;
- typing in the field marks it user-owned;
- applying recommended geometry may suggest a name but must not overwrite a user-owned one;
- importing JSON always uses the imported explicit name when present.

## Design JSON additions

A possible additive schema is:

```json
{
  "path": {
    "type": "Lissajous Tangle",
    "diameter": 20,
    "zStretch": 10,
    "samplingMode": "arcLength",
    "params": {},
    "strands": {
      "mode": "cable",
      "count": 3,
      "spacingCm": 0.8,
      "twistCount": 6,
      "rotationOffsetDeg": 0,
      "zOffsetCm": 0
    },
    "operators": []
  },
  "crossings": {
    "mode": "alternating",
    "clearanceMm": 1.2,
    "transitionCm": 1.5,
    "startingParity": 0
  }
}
```

All new fields must be optional. Missing fields retain current single-strand, merged-crossing,
legacy-sampling behavior.

## Implementation phases

### Phase 1 — topology visibility and UI correctness

- Topology Preview centreline/thin-tube overlay
- Fit View button and conditional automatic refit
- automatic-versus-user filename tracking
- inline path warnings
- two-column parameter layout
- thin-strand thumbnails or an initial gallery

This phase should not modify exported geometry.

### Phase 2 — registry, validation and inspector

- generate the dropdown/gallery from `pathLib`
- typed parameter metadata and bounds
- expression compile/runtime errors
- closure and tangent checks
- path metrics and crossing candidates
- export blocking for invalid paths

### Phase 3 — arc-length sampling

- oversampling and cumulative-distance lookup
- equal-distance interpolation
- optional curvature refinement
- `samplingMode` compatibility field
- regression fixtures for both modes

### Phase 4 — multi-strand solid geometry

- Cable mode first
- Axial Array second
- expression scope variables
- coincidence/near-duplicate detection
- solid-only output initially; report that colour layers are temporarily disabled when necessary

### Phase 5 — crossing, pattern and cleaning integration

- cross-strand proximity for Pinch and Extra Cleaning
- alternating over/under mode
- one pattern grid per strand
- `strand` available to pattern equations
- unioned all-mask cutter and per-strand failure reporting

### Phase 6 — new path pack and polish

- Figure-Eight, Harmonic/Fourier and Superformula paths
- path-specific recommended geometry
- gallery thumbnails and example Design JSON files
- README screenshots and documentation

## Acceptance tests

### Backward compatibility

- Current features off plus `samplingMode = "parametric"` reproduce the shipped default model's
  triangle count, vertex checksum and bounding box.
- Existing Design JSON files import without new required fields.
- Exported configurations round-trip with all new path, strand and crossing fields.

### Validation

- A malformed expression identifies the failing axis and never silently substitutes zero.
- A non-closing Custom Path is rejected with its measured closure gap.
- Fractional integer-only winding parameters are rejected or explicitly normalized before build.
- A path with a zero tangent reports a cusp instead of producing collapsed sweep frames.

### Sampling

- Arc-length mode keeps adjacent segment lengths within a defined tolerance on every shipped path,
  except where curvature refinement intentionally adds smaller segments.
- No preset has fewer samples in a high-curvature region than legacy parametric sampling at the
  same nominal Path Steps.
- `u` remains monotone and covers exactly 0 to 1 around each strand.

### Multi-strand

- Strand count 1 is identical to the single-strand baseline.
- Counts 2, 3 and 5 build successfully for every supported strand mode.
- Distinct strands have a non-zero symmetric nearest-point distance before their intended
  crossings; cyclic parameter shifts cannot pass the distinctness test.
- Pinch and Extra Cleaning account for cross-strand contacts when enabled.
- No exported pool has an open edge after welding.

### UI

- Fit View frames every preset after large scale and profile changes.
- A manually entered design name survives topology changes.
- An automatic name follows topology changes.
- Path-specific warnings appear next to the responsible parameter and remain summarized globally.
- Topology Preview responds quickly enough for parameter exploration without waiting for full CSG.

### Printability and performance

- Recommended geometry for each path builds in both Object and Pot modes without an unexpected CSG
  failure.
- Debris removal counts are recorded for every recommended preset and investigated when unusually
  high.
- Minimum printable clearance and minimum wall/profile radius are reported using user-configurable
  printer thresholds.
- Build time and peak memory are recorded for 1, 3 and 5 strands at 400 path steps and 48 radial
  points, with and without pattern colour layers.

## Immediate, low-risk improvements

The following changes provide value before the larger geometry work begins:

1. Add Fit View.
2. Update automatic filenames when the path changes.
3. Move path warnings beneath their controls.
4. Give Flower Ring and Braided Loop separate Flat and Interlaced recommended values.
5. Generate the path dropdown from `pathLib`.
6. Add path descriptions and recommended ranges.
7. Add a centreline overlay using the already available sampler.
8. Correct the Lissajous documentation: its integer-frequency cosine bounding box is centred on
   the origin over a complete traversal; ellipse plate mode may still be appropriate because of
   the cross-section topology, not because the curve is inherently off-centre.

These changes improve discoverability and correctness without changing the production mesh or file
formats.
