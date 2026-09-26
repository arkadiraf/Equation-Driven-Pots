# TODO — buried colour pockets and Colour-by-Strand slivers

Status: **not started** (found 2026-09-26 while checking `torus_knot (1).3mf` / `.json`).
Target: `EquationDrivenWovenPots.html` — `buildPatternParts`, `buildStrandColourParts`.

## 1. Buried colour pockets in the Dual Pattern layer (priority)

### Problem

When the tube overlaps itself heavily, part of one arm's colour skin ends up *inside* another arm.
Where that skin is less than the colour depth below the finished outer surface, the inset trim
(`prism − inset`) keeps it. The skin then prints as a colour island sealed inside the wall:
invisible from outside, but it still costs filament changes and purge.

Signature: the **base** part decomposes into negative-volume components (sealed voids), each one
an exact mirror of a small colour-part piece (e.g. −0.98266 mm³ in Base, +0.98266 mm³ in Pattern A).

### Measured on the reference design (JSON below, pattern layer, current app)

| Build | Sealed pockets | Colour buried | Largest |
|---|---|---|---|
| 3 strands (`wound`, `rOffCm` 1) | 63 | 130.9 mm³ = 4.7% of Pattern A | 16.9 mm³ |
| 1 strand (Multi-Strand off) | 20 | 10.7 mm³ = 0.4% | 5.0 mm³ |

This is **not a multi-strand bug**: the single-strand build has it too. It appears whenever the
profile is large compared with the path spacing. Here the profile radius is 3 cm on a 2.5 cm path
radius, and more strands overlap more. Colour by Strand is unaffected: 0 pockets.

### Plan

After the colour booleans in `buildPatternParts`, in both the single-cutter and multi-cutter
branches:

1. `base.decompose()`; the negative-volume components are the sealed voids.
2. Rebuild the base from its positive components only, which fills every pocket with base
   material.
3. `decompose()` each insert. Drop every piece whose bounding box lies inside a void's bounding
   box (within 1e-5) and whose volume is no larger than that void's. The void's surface IS the
   buried piece's surface, so the match is exact.
4. Sanity check: the dropped volume must equal the filled volume (to ~1e-3 mm³). If not, skip the
   cleanup for that build and say so in the status line, rather than risk deleting real colour.
5. Report it in the status line, e.g. `· 63 buried colour pockets filled`.

Check whether `buildPlatePatternParts` can produce the same thing. The plate does not overlap
itself, so probably not, but verify.

### Done when

- The reference design, as 3 strands and as 1 strand, builds with 0 negative-volume base
  components.
- Base + colour parts still sum to the body's volume.
- The regression suite (`python tests/run_regression.py`) changes only in cases that had pockets.
- A new regression case, "buried pockets", is added: this design, reduced resolution.

## 2. Slivers in Colour by Strand (low priority)

### Problem

`buildStrandColourParts` cuts part *k* as `rest ∩ S_k` after subtracting the earlier strands. The
subtracted surfaces coincide exactly with the finished pot's, so a middle strand can keep a
hair-thin leftover.

The reference design with Colour by Strand on reproduces `torus_knot (1).3mf` exactly (17,654 /
22,224 / 23,376 tris). It has two such pieces in Pattern A:

- 0.025 mm³ (2.4 × 0.56 × 1.6 mm);
- 0.00004 mm³ (0.34 × 0.04 × 0.23 mm).

Both are closed and sit against the neighbouring colour, and both are below line width and layer
height. They are harmless in print, but they are debris in the file.

### Plan

After building the parts, move any connected piece under ~1 mm³ (or < 1e-5 of its part) into the
colour part it touches (union), instead of deleting it. Deleting would leave a void; moving keeps
the parts tiling the pot exactly. Report the count only if it is non-zero.

### Done when

The reference design with Colour by Strand gives Pattern A exactly its 6 real pieces, no sub-mm³
fragments, and the part volumes still sum to the body.

## Reference design

Saved from the app as `torus_knot (1).json`. Its strands block predates phase C, so the newer
fields load with their defaults. Set `"colourByStrand": true` under `path.strands` to reproduce the
3MF.

```json
{"name":"Torus Knot","path":{"type":"Torus Knot","diameter":5,"zStretch":5,"params":{"p":2,"q":3,"amp":3.5,"phase":0,"wave":0,"taper":0},
 "strands":{"mode":"wound","count":3,"stepDeg":null,"zOffCm":0,"rOffCm":1}},
 "profile":{"preset":"Circle","equation":"3.0"},"orientation":{"rotX":0,"rotY":0,"rotZ":0},
 "structure":{"mode":"pot","bottomCutPct":10,"topCutPct":90,"bottomThickness":0.35,"drainHoleDiameter":1,"fillPct":22,"wallThickness":0.35,"avoidSelfIntersect":false,"extraClean":false,"debrisThresholdPct":0.1},
 "plate":{"enabled":true,"applyColoring":true,"offsetCm":1.5,"heightCm":1.5,"wallThickness":0.35,"baseThickness":0.35,"openingAngleDeg":25,"smoothingDeg":10},
 "vase":{"enabled":false,"baseDiameter":3,"topDiameter":4,"height":8,"insertOffsetMm":1,"wallMm":1},
 "texture":{"preset":"Twisted Ribs","equation":"cos(12*theta + 10*pi*u)","intensity":0.15},
 "patterns":{"preset1":"Lightning Filaments","equation1":"ridged(theta, v, 4, 6, 4, 6) - 0.85","preset2":"None (Solid Base Color)","equation2":"-1",
  "baseColor":"#c12e1f","patternColor1":"#0056b8","patternColor2":"#5f4a8b","overlapColor":"#8ab04d","depthMm":1.2,"smoothEdges":true,"boundaryRefine":2},
 "mesh":{"sections":400,"radialRes":48,"patternResU":400,"patternResT":48}}
```

How the pockets were measured: build with `buildMesh(readCfg(), 1, { colors: true })`, weld the
base part's vertices (1e-4 mm), group triangles into connected components, and sum each
component's signed volume. Negative components are sealed voids.
