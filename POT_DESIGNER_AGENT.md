# Pot Designer Agent

Operational guide for producing **planters** with `EquationDrivenPotDesigner.html`
(`structure.modelMode = "pot"` or `"potplate"`).

This is the companion to `VASE_DESIGNER_AGENT.md` and sits on top of `EquationGeneratorPrompt.txt`,
which remains the source of truth for the JSON schema, preset names and equation library. The
headless harness, the "verify with the app's own functions" approach, the gyroid recipes and the
seam rules in the vase guide all apply unchanged — read that first. This file covers only what is
different for a pot, and the traps found while building **Caldera Atlas Orb**, **Ironclad Tortoise
Planter** and **Red Cap Overalls Planter** (spherical pots + saucers, 2026-09-18).

Scope: the spherical pot + spherical saucer path was exercised end to end. Notes on the
cylindrical path are from reading the code only and are marked as such.

Line numbers refer to `EquationDrivenPotDesigner.html` in the working tree of 2026-09-18
(commit `287bf30` plus local edits). They drift — grep the function name.

---

## 1. What a pot-mode body actually is

A **thin printed shell**, not the solid body of vase mode. Everything below follows from how
`buildSphericalShell` (L5339) builds the two surfaces:

- **The inner surface is a radial offset of the base silhouette only.** `rIn = rBase − wall`
  (L5380). The texture is added to the outer surface and *never* to the inner one. So the local
  wall is `wall + texInt × texture`.
- **The texture must be ≥ 0 everywhere.** Any negative texture value eats into the wall. Loading
  Gyroid Magma Flare's signed `tanh(…)` texture (range ±0.98, intensity 0.34) into pot mode with a
  4 mm wall leaves **0.66 mm** at the valleys. Rewrite such fields as outward-only, e.g.
  `0.5*(1 + tanh(k*G))`, or as sums of `(1 + tanh(…))` steps (§6).
- **Pattern depth is clamped to `wall − 0.2 mm`** (`maxDepthCm`, L3486), using the *nominal* wall,
  not the local one.
- `uniformShell` only exists for cylindrical (L3494); spherical always uses the radial offset.
- **Floor:** the outer surface is flattened at `flatBottomY = R·cos(sphBotFlatten)` (uses `cfg.R`,
  exactly as in vase mode) and the inner surface is clamped at `flatBottomY + bottomThickness`
  (L5350).
- **Drain hole:** a pot's phi sweep stops at `sphBotCut` (`sphericalPhiEnd`, L3615), and the ring
  left open there *is* the drain. Diameter ≈ `2·r·sin(sphBotCut)`: 176° on R = 8 gives a
  **1.05 cm** hole. `sphBotCut ≥ ~179.7°` is treated as a solid pole — no drain.
- **`v` runs to `sphBotCut`, not to a fixed 175° as in vase mode:**
  `v = (phi − sphBotCut) / (sphTopCut − sphBotCut)`. The foot sits at
  `v_flat = (sphBotFlatten − sphBotCut) / (sphTopCut − sphBotCut)`. Every `v` gate in the
  equations has to be derived from that (§5.2).
- **Foot skirt:** rows with `phi ≥ sphBotFlatten` are clamped to the bed plane even when their
  natural height is above it (L5387). If `r(sphBotFlatten) < R`, this leaves a short vertical
  skirt at the foot, `(R − r)·|cos(sphBotFlatten)|` tall (2.2 mm on Caldera). It is vertical, so
  it costs no overhang, but colour must stop above it.
- `base.height` is inert in spherical mode (same as vase).
- *(Cylindrical, from code only:)* the drain is `cylDrain` and the bottom closure is appended by
  `appendCylindricalDrainClosure`. The cylindrical pot also forces the bottom row to core colour
  (`forceCoreBottomRow`). None of this was exercised this session.

---

## 2. Harness differences from the vase guide

Everything in `VASE_DESIGNER_AGENT.md` §2–3 applies. In addition:

**Load a design without building it.** `applyAIJson()` finishes with `updatePreview()` (L3064),
which schedules a full mesh build. For analysis sweeps, stub it out:

```js
function loadCfgNoBuild(json) {
  const saved = window.updatePreview;
  window.updatePreview = () => {};
  try {
    document.getElementById('aiJsonInput').value = JSON.stringify(json);
    applyAIJson();
  } finally { window.updatePreview = saved; }
  return getConfig();
}
```

**Build on demand, synchronously:** `renderConfigToScene(getConfig(), false)` (L6816). At
260 × 400 the pot takes ~5 s and the saucer another ~6 s.

**Keep helper scripts on disk, not inline.** Add a `GET /__scratch/<file>` route to the save
server and load the scripts with `(0, eval)(await fetch('/__scratch/analyzer.js').then(r => r.text()))`.
Re-fetch after every edit. It is far easier than pasting 200 lines into each JS call.

**The browser JS tool times out at ~45 s.** A pot + saucer export (JSON, pot 3MF, then saucer
3MF) takes 17–30 s plus file writes, so awaiting it inside one call can time out. Start
`exportMultiPart3MF()` without awaiting it, return, then poll the output folder from the shell
until the plate file stops growing.

**Filenames.** `downloadCurrentSettingsJson()` → `<Name>.json`; `exportMultiPart3MF()` →
`<Name>_Pot_multipart.3mf` followed by `<Name>_Plate.3mf` (the saucer is exported inside the same
call when `modelMode = "potplate"`).

**Viewport for renders.** `resize_window` to 1500 × 1100 gives a 2096 × 2200 snapshot from
`downloadViewportImage()`. Trim the flat background with PIL before packaging.

---

## 3. What to measure on a pot

Sample the outer and inner surfaces exactly as `buildSphericalShell`'s pot branch does (code in
the appendix). Then:

### Wall — measure the true wall, not the radial one

The radial wall is `wall + texInt × texture` and looks fine everywhere. The **true** wall — the
distance from each inner vertex to the nearest outer vertex in a ±7-cell window — is thinner
wherever the silhouette slopes steeply against the radius, because the offset is radial, not
normal. `true ≈ radial × cos(tilt)`.

A rim collar is exactly such a slope. Sweep on Caldera (`R*(1 − 0.08*sin²φ + A*exp(−(φ−c)²·W))`):

| Collar A / W / c | Radial wall | True wall min | Inner > 45° |
|---|---|---|---|
| 0.24 / 22 / 0.62 | 4.2 mm | 3.01 mm @ φ 44° | 0 % |
| 0.24 / 22 / 0.62 | 4.8 mm | 3.47 mm | 0 % |
| 0.22 / 12 / 0.60 | 4.8 mm | **3.95 mm** | **0 %** ← shipped |
| 0.16 / 12 / 0.66 | 4.8 mm | 4.22 mm | 0.69 % |
| 0.14 / 10 / 0.70 | 4.8 mm | 4.37 mm | 2.02 % |

A weaker collar thickens the wall but brings back inner overhang (below). Widen the Gaussian
(lower `W`) before you lower its amplitude.

### Overhang — check both surfaces

A pot has two printed faces, and they fail in different places:

- **Inner surface:** the inside of a sphere's closing top faces down. With a plain sphere the
  inner lean at the rim is `90° − sphTopCut`, so a 38° top cut starts at **52°**. A rim collar
  that turns the upper wall near-vertical removes it completely (table above).
- **Outer surface:** below the equator, a plain sphere leans `phi − 90°`, so everything between
  135° and `sphBotFlatten` is past 45°. Measured on an early Caldera body: flatten 142° → **1.3 %**
  from the silhouette alone; flatten **135° → 0 %**, and the footprint widens from 9.5 to 10.9 cm.

Use `n.y < −cos 45°` on area-weighted triangles; orient outer normals away from the sphere centre
and inner normals toward it; skip cells whose four corners are all on the clamped bed plane.

**Locate before you fix.** Bin the offending triangles by (phi, theta), not by phi alone. On
Ironclad the 0.66 % at φ ≈ 80° looked like plate bevels. Softening the bevels and the relief fade
changed nothing. Binning by theta put every hit at θ = 45° + k·90°, φ 75–76°: the bottom edge of
the four hatch frames.

**Measure how high each overhanging face sits.** Flared feet reach the bed before
`sphBotFlatten` (§5.7), so the cells where the surface meets the clamp plane produce a ring of
steep slivers. On Red Cap Overalls they were 0.21 % of the surface, but every one topped out
below 0.6 mm, i.e. inside the first three layers, printed straight onto the bed. Report overhang
**above 1 mm** alongside the raw figure: 0 % there.

**Raised features on a downward-facing edge.** A frame 4.5 mm tall with a 2.3 mm outer ramp, 76°
down the body, gave 0.66 %. Dropping it to 3.4 mm, widening the ramp to 3.8 mm and moving the
hatch 4° higher (where the base faces up more) took the whole pot from 0.83 % to 0.08 %. Budget the
ramp from the steepest point of `smoothstep`, which is 1.5 × its average slope.

### Colour

- Area-weighted coverage of the four states on the **visible** outer surface — exclude clamped
  cells (the underside).
- **Colour on the bed layer:** after export, read `zmin` of every pattern body in the 3MF. On the
  pot it should be > 0, so the first layers print in the base colour only (§5.2).

### Soil volume

The theta-averaged `∫ π ρ_in² dy` of the inner surface. Caldera: 1.53 L.

---

## 4. Overhang comes from the relief fade, not from the cliffs

The vase guide recommends fading relief in at the foot with `smoothstep(a, b, v)`. On a pot
that fade is itself an outward slope, climbing over height on a surface already leaning outward.
With 4 mm of relief it dominated everything else:

| Cliff `k` | Relief | Fade `[0.29, 0.42]` | Fade `[0.29, 0.50]` |
|---|---|---|---|
| 2.5 | 3.2 mm | 0.62 % | 0 % |
| 3.5 | 3.2 mm | 0.82 % | 0.01 % |
| 2.5 | 4.0 mm | 2.41 % | 0 % |
| 3.5 | 4.0 mm | 2.49 % | 0.11 % |

Cliff steepness moved the number by < 0.1 %. **Stretch the fade over the lower third of the
body before you touch depth or steepness.** Colour can still run all the way to the foot.

---

## 5. Traps

### 5.1 A `min()` gate with a small term makes stair-stepped colour edges

Symptom: with `smoothPatternEdges: true`, colour boundaries within ~1.5 cm of the rim came out as
one-cell staircases while everywhere else was smooth.

Cause: the gate `min(mask, 0.945 − v)`. Just below the gate line, `0.945 − v` is tiny (0–0.08),
so on the positive side of every *other* boundary the field is capped at that tiny value. The
smooth-edge contouring (`buildSmoothColorMeshes`, L6021) places each boundary by linear
interpolation, `t = a / (a − b)`. With one side capped near zero the crossing snaps onto the
vertex, and the edge follows the grid.

**Fix:** scale every gate so it is steep compared with the mask field:
`min(mask, 60*(0.945 − v))`. The gate line itself does not move, and the other boundaries
interpolate normally again. The same applies to foot gates such as `60*(v − 0.305)`.

How to tell it apart from geometry aliasing: softening the relief cliffs (`k` 3.5 → 2.5) changed
nothing, while removing the gate made every edge smooth. If a relief change fixes the steps, it
was the geometry; if removing a gate fixes them, it was this.

### 5.2 The foot colour gate must sit above `v_flat`

A gate at `v = 0.29` looks like it stops at the foot, but with `sphBotFlatten = 135°`,
`sphBotCut = 176°` and `sphTopCut = 38°`, `v_flat = 0.297`. The gate is therefore 1° *inside* the
clamped band, and every pattern body reached `z = 0`: a thin coloured ring on the first layer.
Moving it to `0.305` lifted the pattern bodies to `zmin = 3.4 mm`. Always compute `v_flat` from §1
and then confirm with `zmin` in the exported 3MF.

### 5.3 The saucer reuses the pot's masks on its own phi/v sweep

`buildSphericalPlateMultipartMeshes` (L4765) runs the normal multipart builder on
`buildSphericalPlateGenerationConfig` (L4114): top cut = `plateSphTopCut` (95°), flatten =
`plateSphBotFlatten` (250°, so only `R·cos 250° = −0.342 R` clamps the floor), bottom cut forced
to 180°. The pot's pattern equations are evaluated with the saucer's own
`v = (phi − 180°) / (95° − 180°)`, and nothing excludes the flat floor.

On Caldera, **55 % of the saucer's underside came out coloured**: invisible, but four colours on
the first layers.

- There is no clean equation-level fix. For a given phi the pot's `v` and the saucer's `v` differ,
  and no linear gate in (phi, v) passes the pot's lower body while blocking the saucer floor. A
  non-linear discriminator can be built, but it breaks as soon as anyone changes a cut angle.
- The real switch is the **Apply Plate Coloring** checkbox (`applyPlateColoring`, L3493). It is
  **not stored in the JSON** and defaults to on. Unticked, the saucer exports in the base colour
  only.
- Ship the default (coloured) saucer so the files match the JSON on reload, and tell the user
  about the toggle.
- The two plate-size readouts disagree slightly: the preview status (`buildPlateMultipartMeshes`)
  said 15.36 cm and the export status (`generatePlate`) said 15.64 cm. Quote the 3MF bounding box
  instead.

### 5.4 Generated expressions and negative thresholds

String-building `H − ${t}` with `t = −0.58` produces `H - -0.58`. It evaluates correctly, but it is
ugly in the delivered JSON. Rewrite it as `H + 0.58` — in IEEE arithmetic `a − (−b)` is exactly
`a + b`, so the round-trip hash is unaffected (verified).

### 5.5 Pattern A and pattern B must never share a boundary line

Symptom: `Core B:153` on the first Ironclad build (200 × 300), with every other check clean.

Cause: a region that goes straight from dark base to white overlap (both masks switch together)
puts A's zero line and B's zero line on the same curve. That happened at the shell-to-band edge
(`A = band`, `B = phi − φ_band`) and at the hatch frames (the same `frame` term in both). The
two-stage clip in `buildSmoothColorMeshes` then cuts along two coincident contours and leaves
degenerate slivers.

**Fix:** let one mask own each edge. Offset B's edge from A's by a few millimetres so an A-only
strip runs between them. On Ironclad that strip is the red outline: band edge `B = phi − (φ_band +
0.03)`, and a hatch frame of `A = D ∈ [0.85, 1.45]` with `B = D ∈ [1.0, 1.3]`. After that, every
body was B:0 N:0 at both 200 × 300 and 260 × 400.

Plan the state layout so that at each edge only **one** mask changes sign. Base → A-only → overlap
is fine; base → overlap directly is not.

**Check it as a graph before writing any equation.** The four states are the corners of a square:
base–A, A–overlap, overlap–B, B–base. Each colour has exactly two neighbours it may touch, and
**no three colours can all touch each other** (a square has no triangles). List which colours
touch in the design, then assign states:

- If a colour needs three neighbours, or three colours form a triangle, break one contact with a
  real strip (≥ 1.5 mm) of a colour that is one switch from both sides.
- On Red Cap Overalls, blue touches red (shirt), brown (shoes) *and* yellow (buttons). Giving each
  button a brown rim broke that: blue → brown rim → yellow, like a brass button's edge. That gave
  brown 00, blue A, red overlap, yellow B.
- Put the colour you want on the bed and on the soil side of the pot in the base state. The core
  body is the base colour, so it forms the inside wall and the first layers.

### 5.6 The very top and bottom rows are forced to the base colour

`buildSmoothColorMeshes` (L6021) forces both masks to −1 on the first and last vertex rows so the
rim bezel is a plain base-colour quad. If a colour that needs **both** masks (the overlap state)
runs up to the rim, the first row is a base → overlap transition, the §5.5 case again.

On Red Cap Overalls (red cap = overlap) this left a blue hairline in the top row: its outer face is
~0.02 mm wide, plus two 1.4 mm side walls. It's invisible, below any nozzle width, and every body
stays B:0 N:0, so it was accepted. The ring is inherent whenever the rim colour is two switches
from base (brown–red–blue form a triangle through the forced ring). To avoid it, let the rim
colour be the base state or a single-mask state, as on Caldera and Ironclad.

### 5.7 Leg lobes reach the bed before `sphBotFlatten`

Where the base radius exceeds `R` near the foot (flared legs), the clamp `r·cos(phi) < R·cos(flatten)`
kicks in earlier: at 129° instead of 135° for a +16 % lobe. A phi- or v-based foot gate then
leaves colour on the bed at the legs, or a lopsided sole. Gate on **height above the bed**
instead. `baseFormRadius` is available in pattern equations:

```
foot = (baseFormRadius*cos(phi) - R*(-0.70711) - 0.4)*10     // mm above a 4 mm sole, flatten 135°
```

The constant is `cos(sphBotFlatten)`, so it has to change with the flatten angle. Ironclad's teal
body starts at exactly `z = 4.00 mm` all the way round.

### 5.8 Relief cliffs narrower than a mesh cell alias the geometry

A `tanh(k·(H − t))` step spans roughly `2 / (k·|∇H|)`. A 15-cell gyroid on R = 8 has `|∇H|` up to
~3.3 /cm, so `k = 3.5` gives cliffs ~1.7 mm wide. At 180 × 260 (1.8 mm per theta cell) they alias
onto the grid. 260 × 400 (~1.2 mm) is the working resolution for this scale; that produces
3MFs of ~90 MB each for pot and saucer.

---

## 6. Recipe: colour bands that encode height (hypsometric tint)

Two masks give four colour states, and they can be arranged so the states fall **in height
order**, with no colour wasted. With one elevation field `H` and thresholds `t1 < t2 < t3`:

```
Pattern A = min(H − t1, t3 − H)     // on between t1 and t3
Pattern B = H − t2                  // on above t2
```

| Height band | A | B | State | JSON colour slot |
|---|---|---|---|---|
| `H < t1` (valleys) | 0 | 0 | neither | `baseColor` |
| `t1 < H < t2` | 1 | 0 | A only | `patternColor1` |
| `t2 < H < t3` | 1 | 1 | overlap | `overlapColor` |
| `H > t3` (peaks) | 0 | 1 | B only | `patternColor2` |

Note that the **top** band is `patternColor2` and the **third** band is `overlapColor`.

**Relief on the same thresholds**, so each colour is also one physical terrace up and the colour
edge lands exactly on the cliff (outward only, range 0–1):

```
tex = 0.5*( 0.40*(1 + tanh(k*(H − t1)))
          + 0.35*(1 + tanh(k*(H − t2)))
          + 0.25*(1 + tanh(k*(H − t3))) )
      * smoothstep(v_flat + 0.008, 0.5, v)          // foot fade, §4
      * (1 − smoothstep(0.925, 0.95, v))            // clean rim band
```

Caldera uses `k = 2.5` and intensity 0.40 (4 mm). This is a *soft* terrace. The vase guide's
warning against hard terracing still stands: every uphill step is an outward shelf.

**Thresholds from area-weighted quantiles.** Sample `H` over the unclamped outer surface, weight
each sample by `sin(phi)`, and read `t1, t2, t3` at the band fractions you want. Quantiles
0.32 / 0.60 / 0.85 gave `t = −0.575 / 0.308 / 1.087` and coverage 36 / 26 / 24 / 14 %. The black
rim band adds to the base share, so aim the lowest quantile a little under the target.

**Terrain field.** The Magma Flare gyroid plus seeded fbm drift, which breaks the lattice into
continents and archipelagos:

```
H = sin(X)cos(Y) + sin(Y)cos(Z) + sin(Z)cos(X) + 0.5*fbm(theta, v, 1.6, 2.8, 4, 11)
X = 15 sin(phi)cos(theta)   Y = 10 cos(phi)   Z = 15 sin(phi)sin(theta)
```

`H` spans about ±1.75. Scale on R = 8: `Ah = 12` read as blobby camouflage; **15** read as a map;
17 was busy. For an isotropic fbm, `nsv ≈ 1.8 × nst` on a body this shape.

**Rim band.** Fading the relief and gating the colour over the top ~5 % of `v` gives a plain
band (1.25 cm on Caldera) that frames the map and prints a clean, non-wavy top edge. Remember to
scale the gate (§5.1).

---

## 6b. Recipe: motif pots (armour plates, hatches, markings)

Ironclad Tortoise Planter is built from discrete motifs rather than a single field. Four
techniques carried it:

**Write every mask term as a signed distance in millimetres.** `(phi − φ₀)·R·10`, `(D − d₀)·10`,
`(w − E)·cell_mm`. Then `min`/`max` combine terms without squashing any boundary (§5.1), and
widths read directly as print sizes.

**Exact hexagonal plates.** The sum of three cosines, or of three triangle waves, does *not* tile.
It leaves triangular gaps at the junctions instead of even seams. Instead, take the hexagonal
distance to the nearest centre of two offset rectangular grids:

```
u = theta*Nu/(2*pi)                 s = (phi − phi0)*Ks
dxA = u − round(u)                  dyA = s − 1.732*round(s/1.732)
dxB = u − 0.5 − round(u − 0.5)      dyB = s − 0.866 − 1.732*round((s − 0.866)/1.732)
hex(dx,dy) = max(abs(dx), max(abs(0.5*dx + 0.866*dy), abs(0.5*dx − 0.866*dy)))
E = 0.5 − min(hex(dxA,dyA), hex(dxB,dyB))        // 0 on the seam … 0.5 at the plate centre
```

`E` is continuous (checked on a 500² grid) and is the true distance to the plate edge in cell
units, so:

- seams are `(w − E)·cell_mm`;
- `c·E` alone gives a six-facet pyramid on each plate (the faceted armour);
- adding `smoothstep(0.02, 0.14, E)` gives a bevelled edge.

`Nu` must be an integer. Set `Ks ≈ R / (plate pitch)` so the plates are regular at mid-body.

**Repeated square features.** `q = mod(theta, pi/2) − pi/4` gives four sectors; then
`hx = q·R·sin(phi)` and `hy = (phi − φh)·R` in cm, and `D = max(|hx|, |hy|)` is a square radius.
Frames, ports and bosses are all ranges of `D`. Round bosses use `hypot(hx ∓ a, hy)`.

**Polygon markings.** Triangles as the `min` of half-planes in the same local frame, e.g. pointing
up: `min(a − ty, (ty + a)·k − |tx − xc|)`. Offset `q` by `pi/4` to centre them on the legs
instead of between them.

---

## 7. Acceptance thresholds for pots

| Check | Target | Notes |
|---|---|---|
| True minimum wall | **≥ 3.5 mm** | Measured, not radial (§3). The collection's spherical pots use 3.5–5 mm radial walls |
| Texture minimum | **≥ 0** | Otherwise the wall shrinks (§1) |
| Outer surface past 45° | **< 1 %**, 0 % preferred | Flatten ≤ 135° and a long relief fade usually reach 0 |
| Inner surface past 45° | **< 1 %** | Driven by the top cut; a collar fixes it |
| Boundary / non-manifold edges | **0 / 0** on every body, **pot and saucer** | Read the validations directly, as in the vase guide §7 |
| Four colour states | each **> 2 %** | |
| Mask layout | no edge where A and B switch together | Put an A-only (or B-only) strip between base and overlap (§5.5) |
| Pot pattern bodies `zmin` | **> 0** | First layers print single-colour |
| Drain | present | `sphBotCut` < 179.7° |
| Round trip | identical `3D/3dmodel.model` hash for **pot and saucer** | |

---

## 8. Palettes used (pots)

| Design | base | pattern A | overlap | pattern B |
|---|---|---|---|---|
| Caldera Atlas Orb | `#000000` Black (valleys) | `#C12E1F` Red (lowlands) | `#847D48` Bronze (highlands) | `#8E9089` Gray (peaks) |
| Ironclad Tortoise Planter | `#545454` Dark Gray (shell, rim, sole) | `#C12E1F` Red (seams, outlines, muzzles) | `#FFFFFF` Jade White (band, frames, triangles) | `#0086D6` Cyan (lower body) |
| Red Cap Overalls Planter | `#6F5034` Cocoa Brown (shoes, button rims, interior) | `#0056B8` Cobalt Blue (overalls) | `#C12E1F` Red (cap, shirt) | `#FEC600` Sunflower Yellow (button faces) |

For Caldera the columns are in height order (§6 recipe). Also check the vase guide's table so the family
stays varied.

---

## 9. Packaging into `3dModels/MultiColor`

Existing folders contain `<Name>.3mf`, `<Name>.json`, `<Name>.jpg` and `<Name>Thumbnail.jpg`. The
**jpgs are photos of printed pieces** (3000 × 4000 and 800 × 600), and those `.3mf` files are
**Bambu Studio projects the user re-saved** (pot and saucer on two build plates, with slicer
metadata). Neither can be produced from the app, so deliver:

```
3dModels/MultiColor/<Design Name With Spaces>/
    Design_Name.3mf          (renamed from *_Pot_multipart.3mf)
    Design_Name_Plate.3mf    (the saucer, exactly as exported)
    Design_Name.json         (from downloadCurrentSettingsJson)
    Design_Name.png          (render: front + back side by side)
```

Tell the user the image is a render, so a photo can replace it later.

---

## 10. Reference designs

| Design | Coord | R | Top / flatten / bot cut | Pot W × H | Opening | Foot | Wall true (radial) | >45° out / in | Soil | Pot / saucer (100 % solid) |
|---|---|---|---|---|---|---|---|---|---|---|
| Caldera Atlas Orb | sph | 8 | 38° / 135° / 176° | 15.4 × 13.1 cm | 11.0 cm | 10.9 cm | 3.96 mm (4.8) | 0 % / 0 % | 1.5 L | 463 g / 161 g |

| Ironclad Tortoise Planter | sph | 8.5 | 44° / 135° / 176° | 16.8 × 12.6 cm | 12.1 cm | 11.6 cm | 4.18 mm (4.8) | 0.09 % / 0 % | 1.8 L | 497 g / 176 g |

| Red Cap Overalls Planter | sph | 8 | 40° / 135° / 176° | 16.3 × 13.1 cm | 11.5 cm | 11.3 cm | 4.25 mm (4.8) | 0 % above 1 mm (0.21 % raw) / 0 % | 1.65 L | 502 g / 180 g |

Caldera: mesh 260 × 400, pattern depth 1.4 mm, saucer 15.4 × 2.1 cm (spherical plate at 95° /
250°, +0.5 cm). Coverage 38 / 25 / 23 / 14 %. The pot 3MF is 93 MB and the saucer 88 MB.

Ironclad: same mesh, depth and saucer settings; saucer 17.1 × 2.2 cm. Coverage: dark gray 49 %,
red 12 %, teal 27 %, white 11 %. The saucer underside is 27 % coloured. The pot 3MF is 78 MB and
the saucer 71 MB.

Red Cap Overalls: same settings; saucer 16.2 × 2.1 cm. Coverage: blue 48 %, red 35 %, brown 16 %,
yellow 2.1 % (six buttons). The saucer comes out brown and blue, with 10 % of its underside
coloured. The pot 3MF is 78 MB and the saucer 60 MB.

Baseline of other spherical pots in `MultiColor` (read from six of their JSONs): R 5–12.5, radial
wall 0.35–0.5 cm, bottom 0.35–0.85 cm, top cut 25–38°, flatten 150–155°, bottom cut 173–178°,
saucer 95° / 250° with +0.5 cm. Caldera's 135° flatten is deliberately lower than any of them,
to reach 0 % overhang.

---

## Appendix: spherical pot analyser

The core of the in-page analyser used for Caldera. It relies only on the app's own globals
(`evalFieldWithModifier`, `applyDistortionPoint`, `sphericalPhiEnd`, `evaluatePatternValue`).

```js
// Outer + inner world grids, mirroring buildSphericalShell's pot branch.
function buildGrids(cfg, NV, NT) {
  const solid = cfg.isPot && cfg.sphBotCut >= Math.PI - 0.005;
  const phiEnd = sphericalPhiEnd(cfg, solid);
  const phiStart = Math.min(Math.max(cfg.sphTopCut, 0.001), phiEnd - 0.001);
  const flatY = cfg.R * Math.cos(cfg.sphBotFlatten);
  const floorY = flatY + Math.max(0.05, cfg.bottomThickness || cfg.w || 0.1);
  const G = { O: [], I: [], CL: [], PH: [], VV: [], NV, NT, floorY };
  for (let iv = 0; iv <= NV; iv++) {
    const phi = phiStart + (phiEnd - phiStart) * iv / NV, v = (phi - phiEnd) / (phiStart - phiEnd);
    const o = [], n = [], c = [];
    for (let it = 0; it < NT; it++) {
      const th = 2 * Math.PI * it / NT;
      const rB = evalFieldWithModifier(cfg.eq, cfg, th, 0, phi, v, cfg.R, false, 'base');
      const tx = evalFieldWithModifier(cfg.texEq, cfg, th, 0, phi, v, 0, true, 'texture');
      const rO = Math.max(0.1, rB + tx * cfg.texInt), rI = Math.max(0.08, rB - cfg.w);
      let oY = rO * Math.cos(phi), iY = rI * Math.cos(phi), clamped = false;
      if (phi >= cfg.sphBotFlatten || oY < flatY) { oY = flatY; clamped = true; }
      if (iY < floorY) iY = floorY;
      o.push(applyDistortionPoint(cfg, { x: rO * Math.sin(phi) * Math.cos(th), y: oY, z: -rO * Math.sin(phi) * Math.sin(th) }, th, 0, phi, v));
      n.push(applyDistortionPoint(cfg, { x: rI * Math.sin(phi) * Math.cos(th), y: iY, z: -rI * Math.sin(phi) * Math.sin(th) }, th, 0, phi, v));
      c.push(clamped);
    }
    G.O.push(o); G.I.push(n); G.CL.push(c); G.PH.push(phi); G.VV.push(v);
  }
  return G;
}

// True wall: nearest outer vertex to each inner vertex, K-cell window.
function trueWall(G, K = 7) {
  let best = Infinity;
  for (let iv = 0; iv <= G.NV; iv++) for (let it = 0; it < G.NT; it++) {
    const p = G.I[iv][it];
    if (p.y <= G.floorY + 1e-6) continue;           // floor = bottomThickness
    for (let dv = -K; dv <= K; dv++) {
      const jv = iv + dv; if (jv < 0 || jv > G.NV) continue;
      for (let dt = -K; dt <= K; dt++) {
        const q = G.O[jv][(it + dt + G.NT) % G.NT];
        best = Math.min(best, Math.hypot(p.x - q.x, p.y - q.y, p.z - q.z));
      }
    }
  }
  return best;                                        // cm
}

// Area fraction past 45°; outward = true for the outer surface, false for the cavity.
// Grid coordinates are pre-shift, so the sphere centre is the origin.
function overhang45(G, grid, outward) {
  let tot = 0, bad = 0;
  const tri = (a, b, c) => {
    const u = [b.x - a.x, b.y - a.y, b.z - a.z], w = [c.x - a.x, c.y - a.y, c.z - a.z];
    const n = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]];
    const len = Math.hypot(...n); if (len < 1e-10) return;
    const m = [(a.x + b.x + c.x) / 3, (a.y + b.y + c.y) / 3, (a.z + b.z + c.z) / 3];
    let s = Math.sign(n[0] * m[0] + n[1] * m[1] + n[2] * m[2]) || 1; if (!outward) s = -s;
    tot += len / 2; if (s * n[1] / len < -Math.SQRT1_2) bad += len / 2;
  };
  for (let iv = 0; iv < G.NV; iv++) for (let it = 0; it < G.NT; it++) {
    const j = (it + 1) % G.NT;
    if (G.CL[iv][it] && G.CL[iv + 1][it] && G.CL[iv][j] && G.CL[iv + 1][j]) continue; // bed face
    tri(grid[iv][it], grid[iv + 1][it], grid[iv + 1][j]);
    tri(grid[iv][it], grid[iv + 1][j], grid[iv][j]);
  }
  return 100 * bad / tot;
}
```

Colour coverage uses the same grid: evaluate `evaluatePatternValue(cfg.patternEq1 / 2, …)` at
each cell centre, weight by the two triangles' area, and keep clamped cells in a separate "bed
face" bucket. Pass a `stats` object (`texMin`, `texMax`, `texPosMax`, …) if the masks use
`textureFill`/`texPosNorm`; the height-band masks in §6 do not need it.
