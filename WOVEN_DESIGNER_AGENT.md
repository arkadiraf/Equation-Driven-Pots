# Woven Designer Agent

Operational guide for producing **woven / knotted planters and glass-insert vase holders** with
`EquationDrivenWovenPots.html`.

It is the companion to `POT_DESIGNER_AGENT.md` (the guide for `EquationDrivenPotDesigner.html`,
all its modes). The woven app is a different engine (a swept tube built with exact CSG, not a body
of revolution), so most of the Pot Designer's geometry notes do **not** carry over — but the working method does: drive the app
headlessly, measure with the app's own functions, and verify the exported file rather than the
status line. What follows is what was learned building **Cinquefoil Wicker Planter** (a fat-tube
planter), **Earthworm Tangle Vase** (a thin-tube vase holder, §6b) and **Xeno Claw Pod Vase**
(§6c), 2026-09-18, the first designs in `3dModels/Woven`.

Line numbers refer to `EquationDrivenWovenPots.html` at commit `5d21e0a`. They drift — grep the
function name.

---

## 1. What a woven pot actually is

A **tube** with cross-section radius `r(theta)` (the profile equation) swept along a closed path
`x(t), y(t), z(t)` (`pathLib`, L470). Everything follows from `buildMesh` (L1819):

- **Solid first, then shell.** The sweep is cut into pieces short enough that no piece contains
  both arms of a crossing (`ringsPerPiece`), and `Manifold.union` merges them. Wherever the path
  crosses itself the tube is merged exactly — no stitching.
- **Hollow only when Fill % < 100.** `doHollow = fillPct < 100` (L2871). The JSON's
  `structure.wallThickness` drives it (`onShellThickChange` re-derives Fill %). The cavity is the
  union of the tube offset inward by the wall — **the soil lives inside the knotted tube**.
- **A fat tube makes a planter.** With a thin tube each top arc is its own opening and the soil is
  a knotted hose. When the tube radius is comparable to the path radius, the arms passing near
  the axis merge into one central cavity and the top arcs merge into one lobed opening. Cinquefoil:
  path radius 2.55 cm, amplitude 4.0, tube radius 2.6 → the five inner arms at radius 1.45 cm
  overlap into a central cavity with the floor and drain under it.
- **Pot cut.** `zLo = minZ + bottomCut% · (maxZ − minZ)` and the same for `zHi` (L1854), where
  `minZ/maxZ` are the extremes of the **textured outer rings of the full uncut tube**. Floor =
  `bottomThickness` above `zLo`. `buildDrainHoles` drills one hole per floor region.
- **Texture moves both walls.** `rGrid` carries the displacement and the cavity is
  `r − wallThickness` of the *textured* radius (L895), so the shell stays uniform: a negative
  texture does **not** thin the wall (the opposite of Pot Designer guide §1.2). The cavity gets the
  relief too.
- **Pattern depth** is clamped to `min(depthMm, wall − 0.2 mm, 0.45 · profileMax)` (L1883).
- **Saucer.** `buildPlateMesh` traces the outer silhouette at `zLo`, offsets by `offsetCm`, lofts a
  dish. It sits under the **foot**, not the belly: Cinquefoil's saucer is 16.0 × 15.8 cm under a
  17.5 × 18.1 cm pot. That is expected.

---

## 2. Harness

Same idea as the Pot Designer guide §2, with these differences:

- **One download sink.** Every exporter calls `download(content, name)` (L3658). Override
  `window.download` to POST the blob to a local save server.
- **Body first, colours on request.** Edits (debounced 300 ms) rebuild only the **body** on the
  page (`buildMesh(cfg, 1, { colors: false })`, ~2–6 s). The colour layer is built by a Web
  Worker running the page's own `#woven-core` script, only when the viewer banner ("Render
  colours") is pressed or an export needs it. A geometry edit cancels it; colour-picker edits
  just recolour the meshes on screen. See `RENDER_PIPELINE_TODO.md`.
- **Load without building:** stub `window.updatePreview`, put the JSON in `#designJsonInput`, call
  `applyDesignJson()`. **Build the body synchronously:** `runPreview()`. **Colours:**
  `await renderColours()` resolves with the full scale-1 geometry (and swaps it into the view);
  it rejects if a newer edit cancels it. The page stays responsive meanwhile, so an awaiting JS
  call can poll `colourJob` / `window.lastColourTimings` (per-stage seconds of the last worker
  build). A full synchronous page build is still `buildMesh(readCfg(), 1.0)` → `geo` plus
  `geo.userData.patternParts / plateParts`.
- **The browser JS tool times out at ~45 s** and a coloured build at working resolution takes
  40–85 s. Start long work with `runAsync` (below) and check `__job` on a later call, or watch the
  save folder from the shell. Exports reuse a finished colour build of the same geometry
  (byte-identical output); otherwise the export starts the worker build itself and writes the
  file when it arrives, so `runAsync(() => exportBambuStudio3MF())` alone is enough.
- **A hidden Browser pane pauses `requestAnimationFrame`**, which the exporters await
  (`nextPaint`, `BambuExport.nextFrame`) - an export then never starts. Front the pane, or shim
  `window.requestAnimationFrame = cb => setTimeout(() => cb(performance.now()), 16)` in the harness.
- **WASM memory runs out.** After several 2 M-triangle builds in one page, a 1750 × 160 build
  failed with `Build failed: table index is out of bounds` (Manifold out of memory). Colour builds
  now get a fresh worker (and WASM heap) each time, but synchronous `buildMesh` calls on the page
  still share one heap: **reload the page before a batch of big page-side builds.**
- **Keep helpers on disk** and load them with `(0, eval)(await fetch('/__scratch/x.js').then(r =>
  r.text()))` — they are lost on every reload. Session helpers used: `W.load`, `W.build`,
  `W.snap` (offscreen `THREE.WebGLRenderer` render of `scene` from any azimuth/elevation, size
  independent of the pane), `W.overhang`, `W.partAreas`.
- **Palette comparisons need no rebuild.** Each preview mesh's material colour is its state's
  colour. Map colour → state once, then recolour `currentMeshes` and snap each palette.
- **Renders.** The scene's only directional light is a point light fixed at (30, 60, 30), so a
  back view (azimuth ~215°) comes out dull. Add a camera-relative `DirectionalLight` for the
  snapshot (0.15 front, 0.5 back balanced Cinquefoil) and remove it afterwards.
- **Filenames:** `downloadCurrentSettingsJson()` → `<slug>.json`; `exportBambuStudio3MF()` →
  `<slug>.3mf` (slug = lowercase with underscores).

---

## 3. Workflow that worked

1. **Shape first, uncoloured, no saucer** (`equation1/2 = "-1"`, `plate.enabled = false`, mesh
   400 × 48): ~0.5 s a build. Sweep topologies and parameters, render side + top views, and
   measure overhang (§7) for each.
2. **Texture** next, still uncoloured, at a resolution that resolves it.
3. **Colour last**, at working resolution. Compare palettes by recolouring (§2).
4. Measure, export, verify the file (§8).

Shapes tried (pot mode, cut 10–90 %; past-60° share of printed surface, uncoloured):

| Path | Diam / Z / amp / taper | Tube r | Reads as | > 60° |
|---|---|---|---|---|
| Torus (2,3) — app default | 5 / 5 / 3.5 / 0 | 3.0 | trefoil knot, clearest over/under | 0.14 % |
| Torus (2,3) | 5 / 5.5 / 3.5 / −0.12 | 3.0 | rounder trefoil | 0.01 % |
| Torus (2,5) | 5 / 5 / 3.5 / 0 | 3.0 | 5-lobe twisted melon | 0.02 % |
| Torus (2,5) | 5.1 / 5.1 / 4.0 / −0.12 | 2.6 | **5-lobe flower rim, see-through crossings** ← shipped | 0.01 % |
| Torus (2,7) | 5.5 / 5.5 / 4.0 / −0.10 | 2.6 | 7-lobe, dense | 0.08 % |
| Torus (3,5) | 6 / 5 / 4.0 / 0 | 2.4 | twisted column | 1.38 % |
| Torus (3,4) | 6 / 5.5 / 4.2 / −0.10 | 2.6 | lopsided | 0.87 % |

- **Negative `taper`** (−0.1 … −0.12) closes the top and bottom in like an urn and was the single
  best overhang fix: (2,5) went from 1.4 % to 0.9 % past 45° and to 0 % past 60°.
- Raising `amp` above the tube radius opens **see-through gaps** at the crossings, which is what
  makes a fat knot read as woven instead of as a lobed melon.
- `p = 3` knots turn into twisted columns and overhang badly. `p = 2`, odd `q` is the sweet spot.
- Profile `DoublePetal` (oval tube) did not help: the rotation-minimising frame turns the flat
  side along the path, so it reads as a twisted ribbon and overhang rose to 2.9 % at 45°.

---

## 4. Mask and texture variables — what they really mean here

Masks and texture are evaluated with `(theta, u, s, v, x, y, z, R, r, len)`:

| Variable | Meaning | Trap |
|---|---|---|
| `theta` | angle **around the tube**, in the rotation-minimising frame | The frame drifts relative to the world along the path, so a low-frequency theta pattern ("top of the tube") wanders. Use integer frequencies ≥ ~6, which read as uniform |
| `u` | arc-length fraction **along the whole path**, 0 → 1 | Wraps at 1: any `u` frequency must be an **integer number of periods** |
| `s` | sweep-parameter fraction | Not arc length; spacing varies |
| `v` | pattern: world height normalised over the **full uncut tube's** z range | For texture, `v` is the **centreline** height normalised over the centreline range — a different scale. **Gate shared features on `z`, not `v`** |
| `x, y, z` | world position in **cm** (before the ×10 export scale) | The only coordinates that mean the same thing to texture and colour |
| `R`, `r`, `len` | profile radius, actual radius, path length (cm) | |

Seam safety: `theta` and `u` coefficients (in `cos(N*theta + 2*pi*K*u)`) must be integers.

---

## 5. Colour: only three colours reach the skin

**When both masks are active, the base colour never appears on the outer surface.**
`bothPatternsActive` (L2361) switches on "no-neither" mode (`cellState`, L2353;
`emitTriangle`, L2628): wherever `B ≤ 0` the skin is Pattern A's colour **regardless of A**.

| Skin state | Condition | JSON slot |
|---|---|---|
| A colour | `B ≤ 0` (A ignored) | `patternColor1` |
| B only | `B > 0`, `A ≤ 0` | `patternColor2` |
| Overlap | `B > 0`, `A > 0` | `overlapColor` |
| Base | never on the skin | `baseColor` → interior cavity, rim cut face, floor, uncoloured saucer |

Consequences:

- Design the outside in **three** colours and treat the base as the interior / rim / saucer
  colour. Pick it so the rim ring and saucer frame the pattern.
- A's zero line only matters inside `B > 0`. Outside, it still splits polygons but emits no wall.
- **The first layers are never single-colour.** The skin ring at the bed is at least the A colour
  (the core is base). A foot band gated on `B` (below) keeps it to those two colours; the B and
  overlap bodies then start above it (Cinquefoil: 4.4 mm).
- The Pot Designer's four-state square (§5.5 there) collapses to a triangle A–B–overlap. Every
  edge is still a single-mask switch (A↔B and A↔overlap switch B; B↔overlap switches A), so
  three colours may meet at a point. Just never let A's and B's zero lines **run along** each
  other.

**Saucer colouring re-evaluates the pot's masks in the saucer's own coordinates** (`theta` around
the dish, `u` 0 at the centre → 1 at the rim over ~10 cm, `v` up the wall;
`buildPlateColorGrid`, L1652). Tube-scale frequencies turn into sub-millimetre noise there. Set
`plate.applyColoring: false` and let the saucer print in the base colour.

---

## 6. Recipe: plain-weave braid on the tube (over/under, colour + relief)

Two families of helical strands around the tube, crossing at ±45°, with true over/under:

```
a = N*theta + 2*pi*K*u          b = N*theta - 2*pi*K*u
e1 = (cos(a) - c)/(1 - c)       e2 = (cos(b) - c)/(1 - c)      // > 0 on a strand, 0 at its edge
T  = 0.5*(cos(N*theta) + cos(2*pi*K*u))                         // = cos(a/2)*cos(b/2): +1 → family 1 on top
h1 = e1*(1 + L*T)               h2 = e2*(1 - L*T)               // strand heights with the undulation

texture   = max(0, max(h1, h2)) * footRimFade
Pattern A = h1 - h2              // which family is on top
Pattern B = min(max(e1, e2), g*min(z - zFoot, zRim - z))       // on a strand, and not in a band
```

- `T` is periodic for any integer `N`, `K`: no seam, whatever their parity.
- At a crossing `T = ±1` and alternates in a checkerboard; midway along a strand `T = 0`. The top
  family rises by `L`, the lower one dips — a real weave, and the colour edge sits exactly on the
  relief crease `h1 = h2`.
- `A = h1 − h2` is strictly positive along family 1's edge outside crossings (`−e2(1 − LT) > 0`)
  and strictly negative along family 2's, so A's zero line meets B's only at the crossing corners.
  The obvious alternative, `A = min(e1 + δ, max(−e2, T))`, fails: next to a crossing where family
  2 is on top it evaluates to exactly 0 along family 2's edge, i.e. A's zero line runs along B's
  (the coincident-boundary trap, Pot Designer guide §8.2).
- **Diamond cells:** `K ≈ N·len / (2π·r_tube)` gives 45° strands. Cinquefoil: `len` = 148.2 cm,
  `r` = 2.6 → `N = 10, K = 90` (8/72 read bolder and coarser). `c = −0.4` gives strands ~7 mm wide
  with ~4.5 mm diamond gaps; `L = 0.5`.
- **Resolution:** ≥ ~14 samples per theta period and ~16 per `u` period — 1500 × 140 for N = 10.
  1000 × 96 for N = 8 read lumpy.
- **Relief:** intensity 0.11 cm (1.1 mm cords, 1.65 mm on top at crossings). The cord edges are
  what add overhang (§7).
- **Bands.** Gate B, and fade the texture, in **world `z`** (§4): a plain foot band and a rim
  "binding" in the A colour. `g = 7` (per cm, on the un-normalised `max(cos) + 0.4`) keeps the gate
  steep compared with the strand field, so the band edge is smooth (Pot Designer guide §9.3). Get `zLo` /
  `zHi` from `buildRings(readCfg())` with the pot settings; the faded texture does not change them
  because the extremes lie inside the fade.

---

## 6b. Recipe: thin-tube vase holder (glass insert)

Built for **Earthworm Tangle Vase** (8 × 13 cm glass). A vase holder is the opposite of a planter:
**thin solid tubes** wrapped around a glass cylinder, with the glass visible between them.

**Glass insert.** `vase.enabled: true`, `baseDiameter`/`topDiameter` = glass, `insertOffsetMm: 1`.
`buildVaseInsertCavity` (L1799) subtracts a bore of radius `glass/2 + offset` from `floorZ =
zLo + bottomThickness` straight up through the top. Any tube inside the bore is cut away, so the
fit is guaranteed by CSG either way — but **the user wants the tubes left whole** (2026-09-18):

- **The glass rests on top of the floor tubes; do not let the bore floor cut them.** Measure the
  highest material inside the glass footprint (`hypot(x, y) < bore radius`) on a build with the
  vase disabled, and set `bottomThickness` = that height above `zLo` + ~0.1 mm. The round floor
  tubes then stay round and show through the glass bottom.
- **Minimum base 0.75 cm:** the glass floor sits at least 0.75 cm above the build plate.
- **Side strands clear the bore** (keep the innermost tube surface ≥ bore radius). Check
  `minBoreR` (smallest vertex distance to the axis above the floor): > bore radius means nothing
  was cut. Earthworm (first version) let the inner strands intrude ~1 mm, leaving flat bearing
  strips; that is no longer the house style.

**Solid tubes.** Use `fillPct 100` (no cavity, no drain). On reload the wall re-derives Fill, but
a saved `fillPct` of 100 now overrides that, so a solid design reloads solid whatever its
`wallThickness` (before 2026-09-26 it came back hollow unless the wall was ≥ the tube radius).
Setting `wallThickness` ≥ the tube radius (0.8 for r = 0.7) still works and keeps both fields in agreement.

**Something must be under the glass.** A lattice around a cylinder has no floor. Pull the bottom
turns of the path in through the axis so they form a star under the glass. Custom Path used
(`a` wriggle, `b` weave depth, `c` sweep sharpness; `rx` = strand-cylinder radius, `zA` = half
height):

```
S = sin(5t)
rho = rx + b*cos(5t)*sin(pi*S) - rx*pow(max(0, -S), c)      // weave + floor sweep
phi = 3t + a*sin(15t)                                         // (3,5) winding + wriggle
x = rho*cos(phi)   y = rho*sin(phi)   z = zA*(S + 0.0637*pow(max(0, -S), c))
```

- **(3,5)** puts 10 strands around the glass with crossings at `S = ±0.5` (solve
  `phi1 ≡ phi2, z1 = z2` in the unrolled cylinder: crossings sit at `sin(q t) = ±s*`, here
  `s* = 1/2`). `b*cos(5t)*sin(pi*S/(2 s*))` then puts each strand **over at one crossing row and
  under at the other** — an alternating weave. A plain torus knot always runs ascending strands
  outside, which is two layers, not a weave. Keep `b` < tube radius so crossings fuse (rigid).
- **Floor sweep:** `c` = 30 concentrates the inward sweep in the last ~2 mm of height, so the
  bottom bends lie on the bed instead of arching over it (c = 10 left 2.3 % past 60° in the bottom
  centimetre, c = 32 left 0.95 %).
- **Flat base (cut 35 % of the tube height):** the lift `flat*pow(max(0,-S), c)` with
  `flat = 0.05/(1 − 0.95^c)` levels the whole sweep (`S` from −0.95 to −1) to within 0.6 mm.
  Sample the path (`makePathSampler(readCfg())`), take the highest centreline z over `S ≤ −0.95`
  (`zc`), put the cut at `zCut = zc − r + 0.35·2r = zc − 0.3 r`, and set
  `bottomCutPct = 100·(zCut − minZ)/(maxZ − minZ)` using `buildRings(cfg)` with the final
  texture. Every floor spoke is then cut by ≥ 35 % of its height, which leaves a flat contact
  ≥ 95 % of the tube width (`2r·√(1 − 0.3²)`) while keeping 1.3 r of height. A 50 % cut (the
  first rule, Earthworm v1) gives the full width but costs height; the user settled on 35 % so the
  base keeps enough tube. Levelling the sweep took Earthworm's bed contact from 12 cm² (25 % cut on
  an unlevelled sweep) to 66 cm², and the bottom centimetre from 0.95 % to 0.01 % past 60°.
- **Base height:** the floor tubes stand `1.3 r` tall after a 35 % cut, so `r ≥ 0.58 cm` gives the
  0.75 cm minimum base. For thinner strands, thicken only the bottom with a texture term such as
  `k*(1 − smoothstep(zLo + 0.9, zLo + 1.8, z))`.
- **Height:** holder top = `zA + r` (+ relief); glass top = `zLo + bottomThickness + glass height`.
  Choose `zA` so they match (flush) or so the worms rise a little above the rim.
- **Top cut 100 %:** the top turns become rounded hairpins instead of a flat rim. Their undersides
  are small bridged arches (0.8 % past 60° — acceptable).
- **`t` sampling is uniform, arc length is not.** The floor sweep is traversed several times faster
  than the strands, so it gets several times fewer rings. Keep fine `u` detail off it (gate on `z`).

**Features along the tube use `len`.** `len` (path length, cm) is in scope, so distances along the
path are exact in millimetres: `abs(mod(K*u + 0.5, 1) − 0.5)*len*10/K` is the distance to the
nearest of `K` rings. Choose `K` (integer) for the pitch; it adapts if the path length changes.
The worm skin:

```
SAD = 9 − abs(mod(7*u, 1) − 0.5)*len/0.7          // > 0 within 9 mm of 7 saddle (clitellum) centres
GRV = 0.55 − abs(mod(474*u + 0.5, 1) − 0.5)*len/47.4    // > 0 within 0.55 mm of 474 segment grooves
Pattern A = SAD + 0.8                                   // 0.8 mm offset: A's edge never runs on B's
Pattern B = min(max(GRV, SAD), 10*(z − zLo − 0.25))     // grooves + saddles, off in the bottom 2.5 mm
texture   = max((0.5 − 0.5*cos(2*K*pi*u))*(1 − w), 1.35*w) * smoothstep(zLo+0.05, zLo+0.55, z),
            w = smoothstep(−1.5, 1.5, SAD)              // sinusoidal segments, smooth raised saddle
```

States (no-neither): body = A colour, grooves = B only, saddles = overlap, core = base (the flat
base, the floor under the glass and the bore cut faces). Seven saddles on a 5-fold path land at
seven different heights, which looks natural. Sinusoidal segments keep the ripple slope under
~23°; a sharper `sqrt(|sin|)` profile makes every ring's lower wall a > 60° ledge. Segment relief
still costs overhang on the shallower strand undersides: 0.4 mm → +0.24 %, 0.5 mm → +0.37 %,
0.6 mm → +0.69 % past 60°.

**Resolution:** grooves need ~7 rings per 4.5 mm segment along the fastest part of the strand:
3200 sections for a 213 cm path; `radialRes` 32 is enough for rings (they are `u`-only).
2.7 M preview triangles, ~70 s.

### Colour cost — what makes a coloured build hang

The colour layer, not the body, is the expensive part (`RENDER_PIPELINE_TODO.md`). Measured on
the alien holder at quarter resolution (1800 × 12 = 21.6 k cells; the body alone is 47 k
triangles and 0.6 s):

| Colour layout | Refine | Colour-part triangles | Time |
|---|---|---|---|
| 461 black grooves + world-gyroid green veins + tips | 1 | 1.78 M | 48 s |
| gyroid veins + tips only | 1 | 1.26 M | 24 s |
| grooves + tips only | 1 | 0.85 M | 12 s |
| two helical stripes (black edge + green core) + tips | 1 | 1.56 M (raw prisms 1.2 M) | 19 s |
| same stripes | **0** | raw prisms 0.52 M | — |

- Cost scales with **cells × boundaries per cell**, and **no-neither mode emits every cell** into a
  colour prism (the whole skin is coloured), so there is a floor of ~24 triangles per cell even
  with simple patterns.
- `boundaryRefine` subdivides every cell where two boundaries meet. Two boundaries 1 mm apart
  (a stripe's black edge and green core) put *every* stripe cell through refinement: level 1
  more than doubled the prisms. Use **refine 0** unless the design has sharp corners that need it.
- The full-resolution version of the first layout (5200 × 28, refine 2) ran > 7 minutes and never
  returned; the tab had to be closed. **Time a quarter-resolution build first** and scale by the
  cell count before starting a full one.
- Prefer long, simple boundaries (bands, stripes along the tube) over many small islands (3D noise
  or gyroid veins sampled on thin tubes).

---

## 6c. Recipe: alien claw pod (bronze + bright green)

Built for **Xeno Claw Pod Vase**: the §6b holder family with an alien silhouette and a skin that
stays cheap to colour.

**Path** — same terms as §6b plus an egg bulge and top claws (`q = 7`, 14 strands):

```
S = sin(7t)
rho = rx + b*cos(7t)*sin(pi*S) + 1.6*cos(7t)^2 − rx*pow(max(0,−S), c) + 2.4*pow(max(0,S), 8)
z   = zA*(S + 0.0637*pow(max(0,−S), c)) + 2.2*pow(max(0,S), 8)
phi = 3t + a*sin(21t)
```

- `Bg*(1 − S²)` (= `1.6*cos²`) bulges the cage into an egg around the glass and keeps every
  strand ≥ 5 mm off it, so nothing is cut by the bore (`minBoreR` 4.53 cm). It vanishes at
  `S = ±1`, so the floor sweep still reaches the axis.
- `H*pow(max(0,S), m)` lifts each top turn into a claw and `F*pow(max(0,S), m)` flares it
  outward: `H 2.2, F 2.4, m 8` gives claws 1.9 cm above the glass rim leaning out like opening
  egg petals. Small `H` (2 cm at `m 24`) only makes taller hairpins. The claws cost nothing in
  overhang (0.06 % past 60° above 11 cm).
- (3,7) has crossings at `S = ±0.5` like (3,5) (the `crossRows(p, q)` helper solves
  `tau = pi/2 + pi*j + (q/p)*pi*m` for `sin(tau)`), so the same `sin(pi*S)` weave alternates.
  (4,5) and (4,7) give three rows (±0.71, 0); (2, q) a single row at mid-height.

**Skin** — relief ribs (7 mm pitch, `u`-only, not coloured) and **two helical glow stripes** along
each tentacle, black edge + green core, plus green claw tips:

```
STR = abs(mod(theta/pi + 54*u + 0.5, 1) − 0.5)*18.85      // mm to the nearest of 2 stripes (r = 0.6)
Pattern A = max(1.5 − STR, 10*(z − zTip) + 0.8)            // green core (1.5 mm) and claw tips
Pattern B = min(max(2.7 − STR, 10*(z − zTip)), 10*(z − zLo − 0.25))
texture   = ((0.5 − 0.5*cos(2K*pi*u))*(1 − w) + 1.4*w)*footFade,  w = smoothstep(−0.5, 0.5, 2.7 − STR)
```

`theta/pi + 54*u` stays seam-safe (2 stripes around, 54 twists along the loop). The raised
stripe makes each tentacle read as a cable with a glowing conduit.

**Three filaments for four roles.** `assignFilaments` (bambu-export.js) gives one slot per
distinct colour, so a colour may fill two JSON slots: base = A = Bronze `#847D48`, B = Black,
overlap = Bright Green `#BECF00`. With the core bronze, **the first layers print in one colour**
(the bed ring is the A colour, §5).

**What did not work:** 461 coloured groove rings plus world-gyroid green veins (the first idea)
was far too expensive to colour (§6b colour cost) — the full build never returned. Keep the ribs as
relief and put colour on a few long boundaries.

---

## 7. Measuring

- **Overhang on the uncoloured build.** The coloured parts have internal interfaces (each colour
  body's inner face against the base body) that are not printed surfaces but face every way. On
  Cinquefoil the coloured parts said 1.64 % past 60°; the real printed surface is 0.48 %. Rebuild
  with both masks `"-1"` at the same resolution and measure `geo` (area-weighted, faces on the bed
  plane skipped, `n.z < −sin 60°`).
- **Outer vs cavity:** classify each overhanging face by whether its normal points away from or
  towards the nearest centreline point (`buildRings(cfg).centers`). Cinquefoil: 0.20 % outer (arches
  over the see-through gaps and a ring at the foot), 0.28 % cavity (the tube ceilings — arches,
  supported both sides). The bare form was 0.01 %; the cord relief adds the rest.
- **Coverage:** `W.partAreas` over the colour bodies. Each insert's area ≈ 2 × its skin area, so the
  ratios between states 1–3 are the skin coverage.
- **Volume:** signed tetrahedron sum over each closed body. Mass = cm³ × 1.24 g (PLA, 100 % solid).
- **Wall:** uniform by construction (§1); the nominal wall is the true wall away from crossings.
  In merge mode thin blades can remain where two arm cavities nearly touch — check a cross
  section (`W.snap` with a clipping plane; `THREE.Plane` keeps `n·p + c ≥ 0`, so look at the kept
  half from the cut side). `extraClean` replaces them with a true offset if needed.

---

## 8. Acceptance thresholds

| Check | Target | Notes |
|---|---|---|
| Printed surface past 60° | **< 0.5 %** outside bridged spans and the bottom 1 cm | User's printer limit. Bridged spans (tube ceilings, arches over gaps, hairpin tops) are fine. 45° is report-only. Report the figure per height band (`W.ohBands`: 0–1 cm, body, top) |
| Overhang within ~1 cm of the bed | allowed, **optional supports** | **Woven designs only:** the slicer may add supports that touch the build plate (Bambu: *Support → On build plate only*). Say in the hand-off when a design needs them. They are an option, not a substitute for the flat base below |
| Flat base | every bed contact is a **flat cut through 35 % of the tube height** (≥ 35 % everywhere) | User requirement for woven designs: a flat surface on the build plate, ≥ 95 % of the tube width, while keeping height in the base tubes. Design the lowest parts of the path to sit at one height, then cut 0.3 r below their centreline (§6b) |
| Glass on uncut tubes (vase holders) | `bottomThickness` = highest material inside the glass footprint + ~0.1 mm; `minBoreR` > bore radius | The glass rests on the floor tubes, which stay round and visible through it; no strand is trimmed by the bore (§6b) |
| Minimum base (vase holders) | glass floor **≥ 0.75 cm** above the build plate | User requirement |
| Boundary / non-manifold edges | **0 / 0** on every body in the exported 3MF | Manifold output, but parse the file anyway |
| Skin colour states | each **> 10 %** of the skin | Only three reach the skin (§5) |
| Pattern B / overlap bodies | start **above the bed** | A-colour foot band |
| Saucer | uncoloured unless the masks are designed for it (§5) | |
| Drain (planters) | present | `drainHoleDiameter` > 0 and a floor region under it. Vase holders are solid tubes and need none |
| JSON round trip | reloading the JSON and re-exporting gives identical `3D/Objects/object_*.model` hashes | Root `3dmodel.model` carries the date — hash the object files |
| JSON idempotence | `getCurrentWovenPotConfig()` after loading the JSON equals the file | |

The Bambu Studio command line cannot slice the app's export (partial project config — it
segfaults on this install). Open it in the GUI to slice.

---

## 9. Packaging into `3dModels/Woven`

```
3dModels/Woven/<Design Name With Spaces>/
    Design_Name.3mf     (exportBambuStudio3MF: pot on plate 1, saucer (if any) on plate 2, H2C, PLA Basic)
    Design_Name.json    (downloadCurrentSettingsJson)
    Design_Name.png     (render: front + back side by side)
```

Tell the user the image is a render. Re-saving in Bambu Studio adds plate thumbnails.

---

## 10. Reference designs

| Design | Path | Pot W × D × H | Saucer | Wall / floor | > 60° (outer / cavity) | Skin coverage | Pot / saucer (100 % solid) | Mesh | Build / export |
|---|---|---|---|---|---|---|---|---|---|
| Cinquefoil Wicker Planter | Torus (2,5), d 5.1, z 5.1, amp 4.0, taper −0.12, tube 2.6 | 17.5 × 18.1 × 12.3 cm | 16.0 × 15.8 × 1.5 cm | 3.5 / 4.5 mm | 0.48 % (0.20 / 0.28) | teal 40 %, orange 40 %, navy 20 % | 486 g / 89 g | 1500 × 140 | 83–93 s / 110 s, 37.5 MB |
| Earthworm Tangle Vase (v2) | Custom (3,5) worm path (§6b), rx 5.45, zA 6.72, a 0.16, b 0.55, c 30, tube 0.7 | 13.1 × 13.3 × 14.0 cm, glass 8 × 13 cm | — | solid tubes / glass floor 9.7 mm on uncut tubes | 1.40 % (0.39 bottom 1 cm / 0.13 body / 0.88 hairpin arches) | pink 73 %, maroon 21 %, brown 6 % | 391 g | 3200 × 32, refine 2 | 63 s (3.3 M triangles) / ~120 s, 44.3 MB |
| Xeno Claw Pod Vase | Custom (3,7) egg + claws (§6c), rx 5.3, zA 6.57, a 0.08, b 0.55, c 30, tube 0.6 | 16.3 × 16.1 × 15.8 cm, glass 8 × 13 cm | — | solid tubes / glass floor 8.6 mm on uncut tubes | 0.14 % (0.08 bottom 1 cm / 0.00 body / 0.06 claws) | bronze 67 %, black 12 %, green 21 % | 435 g | 3300 × 24, refine 0 | 23–26 s / ~60 s, 24.9 MB |

Cinquefoil verification: every body 0 boundary / 0 non-manifold edges in the exported 3MF;
2,777,052 preview triangles on every rebuild; reloading the JSON in a fresh page and re-exporting
gave identical SHA-256 for `3dmodel.model`, both object files and both configs; the JSON is
idempotent through `getCurrentWovenPotConfig()`.

Palette (Bambu PLA Basic): base `#5E43B7` Purple (interior, rim, saucer), A `#0A2989` Blue (gaps,
foot band, rim binding), B `#FF9016` Pumpkin Orange (strand family 2), overlap `#00B1B7`
Turquoise (strand family 1).

Earthworm v2 (the 35 % cut, glass-on-tubes and clear-bore rules; v1 used a 54 % cut, a 4.5 mm
floor cutting the spokes and 1 mm bearing strips): one connected body; every body 0 / 0 edges in
the 3MF; nothing cut by the bore (`minBoreR` 4.198 cm); holder top level with the glass rim;
63 cm² flat bed contact; ring and saddle bodies start 2.3 mm above the bed; identical object
hashes after a JSON reload. Palette: base `#6F5034` Cocoa Brown (flat base), A `#F55A74` Pink
(body), B `#9D2235` Maroon Red (segment grooves), overlap `#9D432C` Brown (saddles). The 35 % cut
leaves more of the round tube near the bed than the 54 % cut did (0.39 % vs 0.19 % past 60° in
the bottom centimetre): optional build-plate supports (§8).

Xeno verification: one connected body; 0 / 0 edges; `minBoreR` 4.53 cm; claws 1.9 cm above the
glass rim; 62.6 cm² bed contact; black and green bodies start 2.25 mm above the bed and the first
layers are bronze only; identical object hashes after a JSON reload; three filaments (Bronze,
Black, Bright Green).

---

## Appendix: harness essentials

Save server (Python, run from anywhere; serves the project and writes into `./out`):

```python
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def do_GET(s):                                   # /__scratch/<file> -> helper scripts
        if s.path.startswith('/__scratch/'): ...serve os.path.join(SCRATCH, basename)...
        else: super().do_GET()
    def do_POST(s):                                  # /__save/<name> -> OUT/<name>
        data = s.rfile.read(int(s.headers['Content-Length']))
        open(os.path.join(OUT, basename(unquote(s.path[8:]))), 'wb').write(data)
http.server.ThreadingHTTPServer(('127.0.0.1', 8733), H).serve_forever()
```

In the page (`http://127.0.0.1:8733/EquationDrivenWovenPots.html`):

```js
window.download = async (content, name) =>             // every exporter lands in ./out
  (await fetch('/__save/' + encodeURIComponent(name),
               { method: 'POST', body: content instanceof Blob ? content : new Blob([content]) })).text();

function load(json) {                                  // same path as LOAD DESIGN .JSON, no rebuild
  const saved = window.updatePreview; window.updatePreview = () => {};
  try { document.getElementById('designJsonInput').value = JSON.stringify(json); applyDesignJson(); }
  finally { window.updatePreview = saved; }
}

function runAsync(fn) {                                // long builds: return now, watch ./out
  window.__job = { done: false };
  setTimeout(async () => { try { __job.result = await fn(); } catch (e) { __job.error = String(e); }
                           __job.done = true; }, 50);
}
runAsync(async () => { runPreview(); await renderColours(); await snap('front.png', { az: 35, el: 18 }); });
runAsync(() => exportBambuStudio3MF());                // starts the colour worker itself if needed
```

`snap` renders `scene` with its own `THREE.WebGLRenderer({ preserveDrawingBuffer: true })` and a
`PerspectiveCamera` placed on the bounding sphere of `currentMeshes`, then posts
`canvas.toBlob()` to `/__save/`. Trim the flat `#fafafa` background with PIL before packaging.
