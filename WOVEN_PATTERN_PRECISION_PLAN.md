# Precise Pattern Boundaries for the Woven Pots Colour Layer — Plan

**Status (2026-09-16): phases 1–4 implemented and verified — see §8 for results and the two
pitfalls met on the way.**

Goal: remove the "pixelated" look of the Dual Pattern Color Layer boundaries in
`EquationDrivenWovenPots.html` (visible on the default Torus Knot checkerboard) and make the
boundary follow the mask equation's true zero set instead of the sampling grid.

## 1. What is actually wrong (measured on the default config, 400 × 48 grid)

Diagnosed in the browser with a parameter-space classifier (every outer-surface triangle of each
part is mapped back to `(iu, jθ, ρ)` on the tube and compared with the mask state it should have),
volume sums, duplicate/twin-triangle counts, ray probes, and flat-shaded / wireframe macro views
(camera 2.5–6 cm from the surface). Four independent causes, in order of visual weight:

| # | Cause | Where | Evidence | Affects |
|---|---|---|---|---|
| A | **Zero-thickness membranes** left by chained coplanar booleans | `buildPatternParts`: `insert = prism ∩ skin`, then `base = result − insert` | 6 910 base triangles lie *on* the colour tiles (4 514 inward-facing + 2 396 outward-facing = two-sided sheets); 18.9 % of the base's outer-surface area is inside tiles. Volumes still sum exactly (base 261.313 + insert 49.896 = pot 311.207), so the volume checks never saw it | preview (z-fighting sawtooth) **and the exported 3MF base object** |
| B | **Vertex normals averaged across the 90° pocket crease** | `runPreview`: `computeVertexNormals()` on Manifold's shared-vertex output | with flat shading the same geometry has razor-straight edges; with smooth normals every edge gets a soft dark/light "pillow" whose width is whatever sliver Manifold left along the boundary → scalloped, uneven edges | preview only |
| C | **Binary masks can only land on cell midpoints** | `clipPoly.crossing`: `t = fa/(fa−fb)`; with `sign()` the field is ±1 so `t ≡ 0.5` | default `sign(cos(6θ))`: nodes 2, 6, 10 … sit exactly on the zero and read `+`/`−` by floating-point luck (`cos(π/2) = 6e-17`, `cos(3π/2) = −1.8e-16`), so the twelve stripes come out **4,4,4,4,4,3,5,3,5,3,5,4 cells** wide (11.8–19.6 mm for a nominal 15.7 mm); `sign(cos(5θ))` → 5,5,4,5,5,5,5,4,5,5. Along `u` the error is ± half a node (nodes are uniform in `t`, not arc length: 9–16 nodes per ring) | geometry + export |
| D | **Saddle cells cut along the fixed A–C diagonal** | `buildSmoothPatternMeshes` triangulates every cell as (A,B,C),(A,C,D) | all 384 checkerboard corners (12 × 32) get a half-cell (≈ 2 mm) 45° bridge/chamfer: the 1.1 % (insert) / 1.8 % (base) residual "wrong" area is exactly `384 × ¼ cell` | geometry + export |

Cause A is not Manifold misbehaving in general — a minimal flush subtraction (box minus a
top-flush pocket) is clean (16 verts, volume 996, 0 duplicates). It is the *chaining*: the insert's
top face is a re-triangulation of the pot's own facets with FP-computed vertices, and the second
boolean classifies those sub-triangles as marginally inside/outside the pot surface, keeping the
original facet as a membrane over them.

The tube's own faceting (48 radial nodes at r = 3 cm → 3.9 mm flat bands) is a fifth, separate
limit; A–D fix the boundary *within* a facet, which is what looks pixelated today.

## 2. Fix A — membrane-free CSG (prototyped and verified in-page)

Cut the base with a solid that is in **generic position** relative to the pot (top `ε` above the
surface, bottom = inset surface, walls exact planes) instead of with the already-computed insert:

```
inset      = buildInsetSolid(cfg, R, d)               // unchanged
prism_k    = mask prism for state k, radius r − d − ε … r + ε   // unchanged
cutter_k   = prism_k − inset                          // bottom snaps to the inset surface; never coplanar with `result`

single state present:   [insert_1, base] = result.split(cutter_1)   // one evaluation, complementary by construction
several states present: insert_k = result ∩ cutter_k                // each from the pristine `result`, never chained
                        base     = result − cutterAll               // cutterAll = prismAll − inset, where prismAll is
                                                                    // the soup with walls only on state≠0 ↔ state 0 edges
```

`skin = result − inset` disappears. `Manifold.prototype.split` exists in manifold-3d 3.5.3
(checked); keep an `intersect` + `subtract` fallback.

Measured with a monkey-patched `buildPatternParts` on the default config:

| | current | membrane-free |
|---|---|---|
| base triangles lying on tiles | 6 910 (18.9 % of area) | 0 beyond the saddle bridges (1.8 %, symmetric with the insert's 1.1 %) |
| base + insert volume vs pot | +0.001 % | +0.002 % |
| status | NoError | NoError |
| build time (2 runs) | 3 226 / 5 131 ms | **1 530 / 1 532 ms** |
| flat-shaded macro view | sawtooth teeth every cell | straight edges; only D's corner chamfers remain |

Why the multi-state recipe does not re-introduce the problem: inserts share walls with each other
only through *exact* input planes (the same welded prism points), never through faces one boolean
computed and another one has to classify. `prismAll` comes from the same clipped polygons by
skipping wall emission on edges between two non-zero states; do **not** `Manifold.union` the
cutters (opposite-facing coincident walls — the situation that produced the piece-cap debris).

## 3. Fix B — crease-aware preview normals (prototyped)

Replace `computeVertexNormals()` for the pattern parts (and the plain pot, whose merged crossings
are real creases too) with per-corner normals that average only the incident faces within a crease
angle (40°: tube facets are 7.5° / ~3° apart and stay smooth; the 1.2 mm pocket walls are 90° and
stay sharp). Output a non-indexed geometry with a `normal` attribute; exports are untouched.

Verified visually together with Fix A at 6 cm: crisp, straight edges, no scallops, tube still
smooth. The naive prototype (string-keyed position map) took 1.4 s on 190 k triangles — the
production version should build the vertex→faces adjacency from the index buffer (Manifold output
is already welded), O(F), expected < 200 ms. Optional: only run it when pattern parts exist.

## 4. Fix C — root-refined crossings

Give every polygon vertex its parametric position `(iu, jθ)` (fractional after D) and give
`clipPoly` a `refine(a, b, key)` callback: bisect the compiled mask along the edge in parameter
space (10 iterations → 1/1000 of a cell), evaluating with linearly interpolated `theta`, `u`, `s`,
world point (chord between the two endpoints' surface points) and `v` from its `z`. Use the result
as `t` for the `top` / `bot` / `fa` / `fb` lerps. Works for smooth and discontinuous masks alike
(`sign`, `floor`, `mod`, thresholds), needs no preset rewrites, converges to the jump for step
functions, and only runs on edges whose endpoints differ in sign (5 568 boundary cells of 19 200
here → a few tens of thousands of extra expression evaluations, far below the CSG cost).

Details:
- The `fb` clip runs on the output of the `fa` clip, whose vertices may lie mid-triangle; bisection
  between two arbitrary points in the same (convex) grid triangle is still a 1-D search.
- Wrap-around edges (`jθ = Nθ−1 → 0`, `iu = Nu−1 → 0`) must interpolate in the unwrapped domain.
- Keep `nearZeroFixWrap` (its ±2e-3 nudge now moves a boundary by ≤ 1e-3 cell); if bisection cannot
  bracket (an endpoint exactly 0) fall back to the current linear `t`.
- Expected result for the default: twelve stripes of 4.000 cells; rings of exactly 1/32 of the path
  length.

## 5. Fix D — adaptive subdivision of boundary cells

In `buildSmoothPatternMeshes`, before clipping, split any cell whose four corner states are not all
equal into 2 × 2 sub-cells (mask re-evaluated at the new nodes through the same sampler as
`buildPatternGrid`; `top` / `bot` for sub-nodes are lerps *within the grid triangle they fall in*,
so they stay `ε` off the flat facet), recursively to level `k` for sub-cells that still straddle a
boundary. Then clip each sub-triangle exactly as today (with C applied). `k = 2` shrinks the
checkerboard chamfer from ~2 mm to ~0.5 mm, `k = 3` to ~0.25 mm — below print resolution — while
touching only boundary cells (29 % at level 1, far fewer at deeper levels). Prism triangle count
grows ~20–40 %; the CSG operands barely change because the pot mesh is untouched.

UI: one number input "Boundary Refinement" (0–3, default 2) in the Dual Pattern Color Layer
section, saved/loaded in the design JSON (`patterns.boundaryRefine`).

## 6. Phases

1. **Membrane-free CSG** (§2, ~30 lines): rewrite the part assembly in `buildPatternParts`; drop
   `skin`; single-state `split` path and multi-state path; keep `cleanDebris` on each part.
2. **Crease normals** (§3, ~40 lines): `computeCreaseNormals(geometry, 40)` used in `runPreview`.
3. **Root-refined crossings** (§4, ~50 lines): parametric vertex data + `refine` callback in
   `clipPoly`; thread the compiled masks and the sampler through `grid`.
4. **Adaptive subdivision** (§5, ~80 lines + 1 input): sub-cell sampler, recursion, JSON field,
   default config updated.
5. **Defaults**: consider Pattern Radial Nodes 96 for the demo config once 1–4 are in (halves the
   facet width; measure the CSG cost before changing it).

## 7. Verification (reuse the in-page diagnostics from this investigation)

- Membrane counter: parameter-space classification of every part's outer-surface triangle →
  "wrong-state" area must equal the saddle residual (≈ 0 after D) for base and inserts alike.
- `dupVerts` / twin-triangle stats per part; `status() === 'NoError'`; base + inserts volume =
  uncoloured pot within 0.01 %.
- Stripe-width audit on the default (`sign(cos(6θ))` → all 4.00 cells; `sign(cos(5θ))` → 4.80).
- Flat-shaded and crease-shaded macro screenshots at ~6 cm from the surface: no teeth, no scallops.
- 3MF round trip through DOMParser as before; open in the slicer and confirm no "non-manifold" /
  zero-thickness warnings on the base object.
- Timing on the default config stays at or below the current build (~1.5–2 s expected).
- Regression set: pinch mode, object mode, solid fill, Surface Texture on, two masks with crossing
  boundaries (Half-Split × Height-Bands), stepped-edge mode (behaviour unchanged).

Note: Manifold booleans are lazy — timing individual ops with `performance.now()` reads 0 ms;
measure whole builds via the status line.

## 8. Implementation notes and results (2026-09-16)

What landed in `EquationDrivenWovenPots.html`:

- `buildPatternParts`: cutters `prism_k − inset`; one state → `result.split(cutter)`; several →
  inserts cut from the pristine pot, base carved by the merged `all` prism. `skin` removed.
  `toSolid` catches Manifold's constructor throw ("Not manifold") per pool.
- `buildCreaseGeometry` (40°) replaces `computeVertexNormals()` in `runPreview` for the pattern
  parts and the plain pot.
- `buildPatternGrid` returns the sampling context; `lerpRec` records; `clipPoly(..., ctx)` with
  `ctx.refine` (14 dyadic bisection steps, clamped to [1/512, 1−1/512]).
- `buildSmoothPatternMeshes(grid, refineLevel)`: per-cell uniform subdivision (saddle → 2^L,
  single-contour cell → 2), shared edge tables per grid edge, centroid fans for hanging vertices,
  `all` pool. Stepped builder gets the `all` pool too.
- UI "Boundary Refinement (0–3)" → `cfg.boundaryRefine`, JSON `patterns.boundaryRefine`, default 2.

Two pitfalls (both surfaced only with two masks — a single mask never exercises the other field):

1. Sampling the *other* field on the mask at a crossing breaks the linear-over-the-triangle
   invariant: a convex polygon can then see four `fb` sign changes and the two sides of that contour
   disagree on where it runs → "Not manifold". The other field stays the plain lerp.
2. Nudging that lerp away from zero destroys the exact 0 at a vertex that lies on both contours
   (lerp of two zeros), so `emitState` no longer attaches the `fa` walls there → orphan wall quads.

Results (default torus-knot checkerboard unless noted):

| check | before | after |
|---|---|---|
| base triangles lying on tiles | 6 910 (18.9 % of area) | 0 |
| boundary vs analytic zero set | midpoint-snapped (stripes 3–5 cells) | mean offset 0.02 mm, max 0.7 mm (level-2 corner chamfer) |
| base + inserts vs pot volume | +0.001 % | −0.0004 % |
| page-load build | 1.9–5.1 s | 2.6–3.2 s (refine 2); 1.65 s (0); 3.0 s (3) |
| triangles in parts | 200 k | 308 k |
| regression set | — | two masks (refine 0/2/3), checkerboard × rings, pinch, object, texture, stepped: 0 bad edges, volumes within 0.01 %, no console errors |
| JSON round trip | — | `boundaryRefine` exported and re-applied |

Phase 5 (Pattern Radial Nodes 96 by default) was not applied — the tube's own 3.9 mm facets remain
the visible limit at the macro scale; raising it costs CSG time roughly linearly.
