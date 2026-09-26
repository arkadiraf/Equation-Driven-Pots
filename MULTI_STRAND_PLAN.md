# Multi-Strand Weaving — implementation plan

Status: **not implemented**. This is a spec for later work on `EquationDrivenWovenPots.html`.
Named to match the `WOVEN_COLOR_LAYER_PLAN.md` convention the code already references (see the
Dual Pattern Color Layer comment in the source).

## Why

Every path in the library sweeps **one closed strand**. A Turk's head knot is one cord, so the
single-strand paths are legitimate — but a basket is dozens of strands interlacing, and nothing in
the tool can express that. Adding a ninth single-strand path extends the library by one; adding a
strand count multiplies it: a 3-strand Torus Knot is a real braid, a 4-strand Coiled Basket is a
proper coiled vessel, a 6-strand Flower Ring is a woven crown.

This is the one change that would make the project's name literally true.

## What exists today

The build chain in `buildMesh(cfg, scale)`:

```
R = buildRings(cfg)                  one sweep: frames[steps], outer/inner rings, centers,
                                     prox, rGrid, profile, rot, minZ/maxZ, profileMaxR
outer  = buildWallSolid(R.outer, R)  union of pieces of `ringsPerPiece` rings each
inner  = buildWallSolid(R.inner, R)  (hollow only)
overlapBoxes + buildTrueCavityPatch  (extraClean only)
result = outer - inner, then plane cuts, drain holes, vase cavity
cleanDebris
patternParts = buildPatternPartsOrFallback(cfg, R, result, depthCm)
                 ├─ buildInsetSolid(cfg, R, depthCm)
                 └─ buildPatternGrid(cfg, R, depthCm)     ← Nu = R.steps, Nt = R.resR
plateParts   = buildPlateMesh(cfg, outer, zLo)
```

Two facts decide the shape of this work:

- **`buildWallSolid` splits the sweep into pieces short enough that no single piece contains both
  arms of a self-crossing** (`ringsPerPiece`, derived from `prox.minCrossArc`), then unions them.
  Crossings therefore resolve as exact booleans between separate pieces.
- **`buildPatternGrid` is built from `R.frames`**, indexed `iu` over one sweep, with `u` meaning
  "fraction along the path". The entire colour layer, the surface texture and the `u` coordinate
  assume a single continuous sweep. This is the real work in the feature.

## What comes for free

Because these all operate on the merged solid or on the printed silhouette rather than on the
sweep parameterisation:

- Plane cuts (Bottom/Top Cut), bottom thickness, drain holes, vase-insert cavity.
- `cleanDebris`.
- **The base plate.** `buildPlateMesh` traces the solid's cross-section, already handles several
  disjoint loops, and since the edge-walking fix it no longer collapses onto an inner loop when
  the slice vertices are sparse — which is exactly the situation many strands create.
- STL and 3MF export (they consume the merged solid plus the parts list).

## Design decisions

### 1. How a strand is generated — recommend t-offset

> **Superseded — see `MULTI_STRAND_EXPERIMENTAL_PLAN.md`.** A `t` offset on a closed curve only
> moves the start point; every copy traces the same locus (verified: Hausdorff distance 0 on all
> built-in paths). Use a Z rotation of `2π/(g·N)`, where `g` is the path's rotational symmetry
> order, or the Cable mode.

Offset each copy along the curve: strand `k` samples `t + k · period / N`.

Works for every path including Custom, needs no per-path knowledge, and for a wound path it
naturally offsets both the azimuth and the undulation phase (a `(p,q)` torus knot shifted by
`2π/N` in `t` rotates by `2πp/N` and shifts the wave by `2πq/N`). Add an optional second knob —
an extra rotation about the axis, or a z-shift — for designs where the t-offset alone puts the
strands too close.

**Pitfall, and it has a precedent here.** If the offset maps the curve onto itself, all N strands
are the *same* curve and the union receives N coincident tubes — the same failure class as the
period/retrace bug fixed in the `pathLib` refactor (Torus Knot with `gcd(p,q) > 1`, even Möbius
half-twists). Guard it: sample the curve at the offset and compare to the unoffset curve; if they
coincide within a tolerance, reduce N or refuse. Report it through the existing `warn` /
`getPathNote` mechanism rather than silently changing the number the user typed — same principle
as the Coiled Basket fuse advisory and the Flower Ring weave advisory.

### 2. Piece splitting stays per-strand

`ringsPerPiece` exists so no piece contains both arms of a **self**-crossing. Two different
strands are already in different pieces, so a cross-strand crossing needs nothing extra — the
union resolves it. Keep `computeRingProximity` per-strand and leave the splitting alone.

This corrects a cost estimate made before the code was checked: proximity is **N·O(steps²)**, not
O((N·steps)²). At 4 strands and 400 sections that is ~640k pairs, not 2.6M.

Cross-strand proximity is only needed by two optional features:

- **Pinch mode** (`avoidSelfIntersect`): the radius reduction should back off from other strands,
  not just from the strand's own arms — otherwise strands interpenetrate in the one mode whose
  entire purpose is that they do not.
- **Extra cleaning** (`extraClean` / `overlapBoxes`): overlap zones between strands need boxing
  too, or thin blades survive between arm cavities at cross-strand merges.

Both default to off. Compute cross-strand pairs lazily, only when one of them is enabled, and use
a spatial hash rather than the O(n²) double loop if it proves slow.

### 3. Pattern layer — N grids, concatenated parts

Build one grid per strand and concatenate the resulting parts. `u` then runs 0→1 along **each
strand**, which is the right semantics anyway: a pattern should repeat per strand rather than
smear once across the whole basket.

Care is needed in `buildPatternParts`, which currently does two different things with its prisms:

- **Inserts** are `result ∩ cutter`. Per-strand prisms can stay per-strand here. Note that at a
  crossing, strand A's prism will also carve strand B's surface where they overlap — that is
  arguably correct (the colour band continues across the merge) but it is a visible design
  decision, so make it deliberately and write down which way it went.
- **The base** is `result − (all-masks prism − insetSolid)`. This must subtract the **union of
  every strand's `all` prism**, not each one in turn against a shrinking base, or the base gets
  carved N times and the pattern states stop being disjoint.

`buildInsetSolid(cfg, R, depthCm)` is also per-strand and will need the same union treatment.

The failure reporting added alongside the smooth-edge fix should be extended to name the strand:
`mask B dropped on strand 3 (…)` is far more useful than the un-numbered message.

### 4. UI, config and JSON

The strand count applies to every path, so it does not belong in a `pathLib` row's `params`. Put
it with the Geometric Basis controls, next to Path Diam and Z-Stretch:

- `strands` — integer, default **1**
- `strandOffset` — the extra rotation/z-shift knob, default **0**

Both read in `readCfg`, exported under `path` in the Design JSON, imported by the existing generic
loop. **Default 1 must reproduce today's geometry bit-for-bit** — the same property maintained
through the `pathLib` refactor, the `phase`/`wave` additions and the `weave` additions, verified
each time by triangle count, vertex checksum and bounding box on the shipped default design.

## Suggested phasing

1. **Solid only.** `strands` + t-offset, N sweeps unioned, pattern layer disabled when `strands > 1`
   (report it in the status line). Proves the geometry, the coincidence guard and the performance
   envelope. The plate should work untouched — confirm it does.
2. **Pinch and extra-clean cross-strand awareness.** Both optional features, both currently off by
   default, so they can land separately.
3. **Pattern layer.** N grids, unioned `all` cutter, per-strand failure messages. The largest piece.
4. **Polish.** `strandOffset`, presets that show the feature off, README and gallery entries.

## Acceptance tests

Mirror the checks used for the previous changes in this file:

- `strands = 1` reproduces the shipped default design bit-for-bit (307,738 tris, vertex checksum
  −3733.018338, bbox to 9 decimals as of this writing — re-measure before starting, since the
  default design may have changed).
- Every path in `pathLib` builds at `strands` 2, 3 and 5 with no CSG error.
- The coincidence guard fires on a deliberately degenerate case and does **not** fire on a healthy
  one.
- No pool in the pattern pass has an open edge: weld each pool and histogram edge incidence — every
  edge must have exactly 2 incident triangles. This is the check that found the smooth-edge bug and
  it should be run per strand.
- Base plate contour: no adjacent-bin jump larger than the current worst case across the library,
  and the rim never sits inside the traced silhouette.
- Design JSON round-trips byte-identically with `strands` set.
- Build time at `strands = 4`, 400 sections, colour layer on, recorded and judged acceptable before
  the feature ships.

## Open questions

- Should strands be allowed **different profiles** (e.g. alternating thick and thin canes)? Cheap
  once N sweeps exist, and visually powerful, but it multiplies the config surface.
- Should the colour masks be able to address the strand index (a `strand` variable in the pattern
  expression scope) so strand 1 can be one colour and strand 2 another? This is probably the single
  most-wanted follow-up and is easy once N grids exist — worth reserving the variable name now.
- Is a `strands` count enough, or is an explicit **offset list** wanted, so strands can be placed
  unevenly? Start with the even count; an explicit list can be added later without breaking it.
