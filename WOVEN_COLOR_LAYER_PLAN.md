# Dual Pattern Color Layer for Woven Pots — Implementation Plan

Goal: bring the Pot Designer's "4. Dual Pattern Color Layer" (two mask equations → four colour
states, colour-layer depth, Smooth Pattern Edges, pattern resolution, multi-part 3MF export) to
`EquationDrivenWovenPots.html`, adapted to a swept tube built with Manifold CSG.

## 1. What the Pot Designer does (reference, `EquationDrivenPotDesigner.html`)

| Piece | Where | Behaviour |
|---|---|---|
| Masks | `chooseColor` 6604, `evaluatePatternValue` 4886 | `A = P₁(θ,z,v,…) > 0`, `B = P₂ > 0`, `state = A + 2·B` → palette `[base, A, B, overlap]` |
| Depth | `getConfig` 3367, `buildLayeredSample` 5237 | Three layers: outer, outer inset by `depth` (clamped to `wall − 0.02 cm`), inner. States 1–3 are inserts between layer 0 and 1; the core (state 0) owns everything else and gets a "socket" under each insert |
| Stepped edges | `buildOccupancies` 5275 | Whole grid cells take a state; exposed cell faces are capped |
| Smooth edges | `buildSmoothColorMeshes` 5765, `contourClipPolygon` 5648, `smoothFieldNearZeroFix` 5545 | Each cell's two triangles are clipped by the linearly-interpolated `fa = 0` then `fb = 0` contours; per state: top fan, underside fan, wall quads only on contour edges; welded (`cleanupMesh`), cracks sealed |
| Resolution | `buildParametricShell` 4927, `getInteractivePreviewConfig` 6405 | Shell built at `max(meshRes, patternRes)`; live preview capped at 64×96 during rapid edits, full res after 300 ms |
| Export | `exportMultiPart3MF` 6951, `meshTo3mfObjectXml` 4406 | One 3MF object per state + an assembly of components; `<m:colorgroup>` with the four colours; JSZip; cm→mm |
| Expressions | `getCompiledExpr` 1158 | `new Function` with an allow-listed identifier scope, cached |
| Cutout mode | `buildSmoothCutoutMesh` 5697 | Masked cells become through-wall holes instead of colour inserts |

## 2. The math for a swept tube

The pot is a tube swept along a closed path with profile `r(θ)`; the natural mask domain is the
sweep's own surface parameters, not `(θ, z)` of a body of revolution.

**Mask scope** (compiled expression arguments, replacing `EXPR_PATTERN_NAMES`):

| Name | Meaning |
|---|---|
| `theta` | angle around the tube, measured in the rotation-minimising frame (`frames[i].n/b`). Continuous across the loop closure thanks to the existing twist correction (`err` spread in `buildSweepFrames`) |
| `u` | position along the path as **normalised arc length** `cumLen[i]/totalLen ∈ [0,1)` — equal spacing along the tube regardless of path speed, so "stripes along the path" stay uniform |
| `s` | raw path parameter `t/maxT` (for equations written against the path formula) |
| `v` | normalised world height of the surface point after rotation, `(z − zMin)/(zMax − zMin)` — gives the Pot Designer's height-based presets unchanged |
| `z, x, y` | world coordinates (cm) of the surface point |
| `R`, `r` | profile radius `r(θ)` before / after the pinch clamp |
| `len` | total path length (cm) — lets a user write bands with an absolute pitch: `cos(2*pi*u*len/2)` = 2 cm bands |

Sampling point for a grid node `(iu, jθ)`: the outer-surface point at parametric position
`(iu/Nu · steps, jθ/Nθ · 2π)` — see §4 for how the radii are obtained.

**Preset adaptation** (same `patternPresets` table shape; keep `type/eq/desc`):

- Basic: `cos(theta)` half-tube split (colour faces outward/inward), `v - 0.5` height split,
  `sin(2*pi*8*v)` height bands, `cos(2*pi*6*u)` rings along the path, `cos(6*theta + 2*pi*3*u)`
  spiral wrap, `sign(cos(4*theta))*sign(cos(2*pi*12*u))` checker.
- Helical / lattice / window / Chladni presets translate by `v → u` (along path) or stay on `v`
  (by height); both readings are useful, so offer a few of each.
- Noise presets (`cnoise`, `fbm`, `worley`, `ridged`, `phyllo`) need the helper functions at
  Pot Designer lines 1326–1420 ported verbatim (they are pure functions of two coordinates and a
  seed) — call them with `(theta, u, …)`.
- Drop the texture/radius-derived scalars (`texNorm`, `outerDeviation`, …): the woven tool has
  no texture field. Keep the allow-list validation so equations stay `eval`-safe.

At merged crossings the two arms' patterns simply meet along the crease — no special handling.

## 3. Geometry: build the colour layer with CSG, not mesh surgery

Reuse Manifold instead of porting the socket/occupancy meshing. Everything below runs only when
at least one mask is non-trivial (`P ≠ "-1"`) and `depth > 0`.

```
d      = clamp(depthMm/10, 0, min(shellThick − 0.02, 0.45·minRingRadius))
inset  = buildWallSolid(rings at radius r − d)        // same code as the inner wall, offset d
skin   = outer − inset                                 // the outer d-thick skin, exact
M_k    = closed "mask prism" for state k ∈ {1,2,3}     // from the pattern grid, §4/§5
insert_k = M_k ∩ skin                                  // outer & inset faces come from `skin`,
                                                       // boundary walls from the prism
base   = pot − insert_1 − insert_2 − insert_3          // sequential, never union touching inserts
```

- The prism spans radius `r − d − ε … r + ε` (`ε ≈ 0.02 cm`) so none of its faces coincide with
  the skin's faces — exact booleans leave zero-volume shells on coincident faces (see the debris
  work in the current pipeline). Same reason for sequential subtraction: `insert_1 ∪ insert_2`
  would share a wall.
- Pot mode: `insert_k` gets the same `trimByPlane(zLo)/(zHi)` as the body, and the drain-hole
  cylinders are subtracted from inserts too (cheap). Inserts never reach the cavity because
  `d ≤ t − 0.02`.
- Merge mode: parts of arm A's prism that lie inside arm B vanish in `∩ skin`, and the insert
  boundary at a crossing follows the crease exactly.
- Pinch mode: prisms are built from the same clamped radii, so they track the pinch.
- Eligibility: skip grid nodes where `r − d < 0.05` (pinched to a thread) by forcing state 0.
- The existing `cleanDebris` runs on `base` and each insert; extra-cleaning / true-shell logic is
  untouched (it only changes the cavity).

Alternative considered: building inserts on the mesh's own rings (pattern grid = mesh grid, no
`∩ skin`). It saves three intersections but forces coincident faces everywhere and ties pattern
resolution to mesh resolution; not recommended.

## 4. Pattern resolution (independent of mesh resolution)

New inputs **Pattern Path Nodes** `Nu` (default 400) and **Pattern Radial Nodes** `Nθ` (default 48).

- Radii for pattern nodes are **bilinearly interpolated from the mesh rings' clamped radii**
  (`R.outer` already holds them per ring/angle) rather than recomputing proximity at a second
  resolution — keeps prism and skin consistent; the `ε` margin absorbs interpolation error.
- Frames for fractional ring positions: interpolate `p` linearly and `n/b` by normalised lerp
  between neighbouring rings (fine at these spacings); or simply run `buildSweepFrames` with
  `steps = Nu` — both are cheap; interpolation is safer for θ continuity.
- Cost model: `Nu·Nθ` compiled-expression evaluations ×2 (≈20 k → <20 ms), prism triangles
  ≈ `2·cells` per state + walls, and the CSG ops scale with prism size. At 400×48 expect
  +0.5–1.5 s per build with colour on; with masks set to "None" the cost is zero.
- Interactive cap (optional): mirror `getInteractivePreviewConfig` — during rapid edits build
  with `min(N, cap)`, then a full-resolution rebuild after a 300 ms settle. Fits the existing
  coalesced `updatePreview/runPreview` by adding a second timer.

## 5. Smooth Pattern Edges (high quality)

Port, nearly verbatim, from the Pot Designer:

1. `smoothFieldNearZeroFix` — snap near-zero samples to the 4-neighbour mean, then the
   deterministic ±2e-3 nudge (prevents sub-tolerance slivers and duplicate walls).
2. `contourClipPolygon` — Sutherland–Hodgman against `fa ≥ 0 / ≤ 0`, interpolating `fa`, `fb`
   and the point channels `top` (radius `r + ε`) and `bot` (radius `r − d − ε`).
3. `emitTriangle` — clip each cell triangle by `fa` then `fb` → polygons for states 3, 1, 2, 0.
4. `emitState` — for states 1–3: fan `top`, fan `bot` (reversed), wall quads **only** on polygon
   edges whose endpoints both have `|fa| < eps` or `|fb| < eps`, skipping zero-length edges.
   State 0 emits nothing (the base comes from the CSG subtraction) — simpler than the Designer.
5. Weld by position (port the hash-bucket part of `cleanupMesh`, ~40 lines), drop degenerate
   triangles, `sealSmoothContourCracks` optional. Feed to `new Manifold(new Mesh(...))`,
   check `status()`; on failure skip that state and show a status warning.

Differences from the Designer: the `(u, θ)` grid wraps in both directions, so there are no
forced state-0 boundary rings and no separate end caps — every region is closed by its own
contour walls. Winding is known at construction (outward top, inward bottom, walls consistent),
so no `orientMeshConsistently` pass is needed.

**Off (stepped)**: each cell quad takes its corner-majority / centre state; walls on cell edges
whose neighbour has a different state. Same weld → one closed prism per state.

## 6. Preview and export

- Preview: `base` + up to three insert meshes as separate `THREE.Mesh` objects with the palette
  colours (`MeshStandardMaterial`), replacing the single mesh; status line adds the present
  states and triangle counts.
- **EXPORT .3MF (MULTI-COLOR)**: port `colorGroupColorXml`, `meshTo3mfObjectXml`, the content
  types/rels boilerplate and the assembly-with-components layout (lines 6992–7057); objects
  `Base` (colour 0), `Pattern A` (1), `Pattern B` (2), `Overlap` (3). Add
  `https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js`. Scale ×10 (cm→mm) like the
  STL export. No `rotateMeshForPrinterCoordinates`: that maps Y-up to Z-up, and woven pots are
  already Z-up.
- STL/OBJ exports stay as they are (single uncoloured solid = `base ∪ inserts`, i.e. today's pot).
- Bambu palette picker: optional later port (`BAMBU_PALETTE_TARGET_IDS`, `pickBambuColor`).

## 7. Cutout mode (optional, cheap with CSG)

`pot − M_full` where `M_full` spans `r − t − ε … r + ε` over masked cells/polygons; then
`decompose()` and warn when the lattice breaks into several bodies (the Designer's
`disconnectedIslands` check).

## 8. UI additions (`readCfg` fields in brackets)

New collapsible section **Dual Pattern Color Layer** after Structural Geometry: Pattern Mode
[`patternMode`], Pattern A/B preset selects + descriptions, mask textareas [`patternEq1/2`],
four colour inputs [`baseColor, patternColor1, patternColor2, overlapColor`], Color Layer Depth
mm [`patternDepthCm` clamped], Smooth Pattern Edges checkbox [`smoothPatternEdges`], Pattern
Path Nodes / Pattern Radial Nodes [`patternResU, patternResT`], and the 3MF export button.
All fields call `updatePreview()`.

## 9. Phases

1. **Core** (~250 lines): compiled mask expressions with the new scope; pattern-grid sampling
   with interpolated radii/frames; stepped prisms; `skin/insert/base` CSG assembly; coloured
   preview. Deliverable: colour states visible, manifold parts, pinch/merge/pot/object modes.
2. **Smooth edges** (~150 lines): §5 port; verify no zero-volume shells and that
   `insert_k.status() === 'NoError'` across the preset set.
3. **3MF export** (~120 lines): §6; verify in the slicer that the four bodies nest without gaps
   (they share exact faces by construction).
4. **Polish** (optional): noise helpers + full preset table, cutout mode, interactive resolution
   cap, Bambu palette, per-state triangle counts in the status line.

## 10. Risks and checks

- Coincident faces → the `ε` margins and sequential subtraction are load-bearing; if a build
  reports debris > 0 with colour on, look here first.
- Depth vs. wall: clamp `d ≤ t − 0.02` and `≤ 0.45·r` at pinched rings; report the clamp in the
  status line like the Designer's "Depth clamped to …".
- Prism validity: weld tolerance `1e-6 cm` (Designer value); degenerate cells at pinched rings
  must be dropped before welding.
- Loop closure: `theta` continuity relies on the twist correction; `u` wraps at the grid edge —
  test a spiral preset (`cos(6*theta + 2*pi*3*u)`) for a visible seam at ring 0.
- Performance: measure with the status timer; the Extra-cleaning switch and the colour layer are
  independent costs, both opt-in.
