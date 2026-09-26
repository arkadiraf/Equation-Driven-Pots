# Pot Designer Agent

Operational guide for `EquationDrivenPotDesigner.html` — **every model mode of that tool**:
glass-insert vase holders (`structure.modelMode = "vase"`), planters (`"pot"`) and planters with a
saucer (`"potplate"`). One tool, one instruction set; the woven tube app has its own guide,
`WOVEN_DESIGNER_AGENT.md`.

This sits **on top of** `EquationGeneratorPrompt.txt`, which remains the source of truth for the
JSON schema, the preset names and the equation library. Nothing here repeats that. What follows is
the part that is not written down anywhere else: how to drive the tool, what to measure, what
silently goes wrong, and the thresholds a design has to clear before it ships. It was learned
building the vases **Verdant Spiral Bloom**, **Crown Splash Ovoid**, **Gyroid Magma Flare**,
**Gyroid Ember Column** and **Archipelago Contour Vase** (2026-09-17) and the spherical pots
**Caldera Atlas Orb**, **Ironclad Tortoise Planter**, **Red Cap Overalls Planter** and **Wildfire
Drake Planter** with saucers (2026-09-18).

Scope: the vase path was exercised in both coordinate systems; the pot path only as spherical pot
+ spherical saucer. Notes on the cylindrical pot path are from reading the code only and are
marked as such.

Line numbers refer to `EquationDrivenPotDesigner.html` in the working tree of 2026-09-17/18
(around commit `287bf30`). They drift — grep the function name instead of trusting the number.

---

## 1. What the tool builds

| | Vase mode | Pot / potplate mode |
|---|---|---|
| Body | solid sculpture hollowed by a straight bore | thin printed shell |
| Cavity | vertical bore for a real glass, independent of the silhouette | radial offset of the base silhouette |
| Binding constraint | wall between the bore and the carved outer surface | true (not radial) shell wall, and overhang on both faces |
| Spherical `v` runs to | a fixed 175° | `sphBotCut` (the drain ring) |
| Drain | none | the open ring at `sphBotCut` (spherical) / `cylDrain` (cylindrical) |

### 1.1 Vase mode: a solid body around a glass

Not a thin-walled printed vessel. It is a **solid sculptural body hollowed out to accept a real
glass vase** that the user drops in after printing. Everything follows from that:

- The **cavity is a straight vertical bore**, radius `vaseBaseDiameter/2 + insertOffsetMm/10`,
  rising from `bottomThickness` and continuing to the rim (`vaseHoleRadiusAtHeight`, ~L5141).
  It does **not** follow the outer silhouette.
- The binding constraint on every design is **wall thickness between that bore and the carved
  outer surface**. Design decisions that look purely aesthetic (an equator pinch, a deep
  texture, a narrow rim opening) are really wall-thickness decisions.
- Ignored in vase mode, but still emit valid values: `wall`, `cylDrain` (gated on `cfg.isPot`
  at L7012; the other call site at L6429 early-returns for non-pot), `sphBotCut` (forced to
  175°).
- Distortion is applied to the bore too (§7).

**Never ship without measuring the wall.** The first vase reviewed had a **−0.6 mm** minimum wall
— the bore broke out through the rim — and nothing in the UI said so.

### 1.2 Pot mode: a thin shell

A **thin printed shell**, not the solid body of vase mode. Everything below follows from how
`buildSphericalShell` (L5339) builds the two surfaces:

- **The inner surface is a radial offset of the base silhouette only.** `rIn = rBase − wall`
  (L5380). The texture is added to the outer surface and *never* to the inner one. So the local
  wall is `wall + texInt × texture`.
- **The texture must be ≥ 0 everywhere.** Any negative texture value eats into the wall. Loading
  Gyroid Magma Flare's signed `tanh(…)` texture (range ±0.98, intensity 0.34) into pot mode with a
  4 mm wall leaves **0.66 mm** at the valleys. Rewrite such fields as outward-only, e.g.
  `0.5*(1 + tanh(k*G))`, or as sums of `(1 + tanh(…))` steps (§10.6).
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
  equations has to be derived from that (§9.4).
- **Foot skirt:** rows with `phi ≥ sphBotFlatten` are clamped to the bed plane even when their
  natural height is above it (L5387). If `r(sphBotFlatten) < R`, this leaves a short vertical
  skirt at the foot, `(R − r)·|cos(sphBotFlatten)|` tall (2.2 mm on Caldera). It is vertical, so
  it costs no overhang, but colour must stop above it.
- `base.height` is inert in spherical mode (same as vase, §4).
- *(Cylindrical, from code only:)* the drain is `cylDrain` and the bottom closure is appended by
  `appendCylindricalDrainClosure`. The cylindrical pot also forces the bottom row to core colour
  (`forceCoreBottomRow`). None of this was exercised.
- `"potplate"` adds a saucer built from the pot's own settings (§9.5).

---

## 2. Harness: driving the app headlessly

A local server plus the built-in browser gives full programmatic control and puts exports
straight on disk with the filenames you want.

```python
# serve project dir; POST /__save/<name> writes into an output folder;
# GET /__scratch/<file> serves helper scripts (http.server subclass with CORS, ~50 lines)
```

Then in the page:

```js
// exports land on disk instead of the browser download folder
window.downloadBlob = async function (blob, filename) {
  const r = await fetch('http://127.0.0.1:8733/__save/' + encodeURIComponent(filename),
                        { method: 'POST', body: blob });
  return await r.text();
};
```

`downloadViewportImage()`, `exportMultiPart3MF()`, `exportBambuStudio3MF()` and
`downloadCurrentSettingsJson()` all route through `downloadBlob`, so one override captures
everything.

**Load a design without building it.** `applyAIJson()` (the LOAD DESIGN .JSON path) finishes
with `updatePreview()` (L3064), which schedules a full mesh build. For analysis sweeps, stub it:

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
260 × 400 a pot takes ~5 s and its saucer another ~6 s. (Loading with the real `updatePreview`
and waiting ~15 s also works, but is slower and less predictable.)

**Keep helper scripts on disk, not inline.** Load them with
`(0, eval)(await fetch('/__scratch/analyzer.js').then(r => r.text()))` and re-fetch after every
edit. It is far easier than pasting 200 lines into each JS call.

**The browser JS tool times out at ~45 s.** A pot + saucer export (JSON, pot 3MF, then saucer
3MF) takes 17–30 s plus file writes, so awaiting it inside one call can time out. Start the export
without awaiting it, return, then watch the output folder from the shell until the last file stops
growing.

**Filenames.** `downloadCurrentSettingsJson()` → `<Name>.json`; `exportMultiPart3MF()` →
`<Name>_Pot_multipart.3mf` (`buildExportStemForKind`, L4890), followed by `<Name>_Plate.3mf` when
`modelMode = "potplate"`; `exportBambuStudio3MF()` → a single Bambu Studio project (§13).

**Viewing renders:** you cannot see an image returned from JS. Save the PNG to disk, downscale
it ~3× with PIL, and `Read` the small copy. Full-size renders are wasteful to read.
`resize_window` to 1500 × 1100 gives a 2096 × 2200 snapshot from `downloadViewportImage()`; trim
the flat background with PIL before packaging.

**Camera:** the renderer only re-aims `controls.target` on rebuild; it never moves the camera.
Set `camera.position` yourself and back off further than the bounding sphere suggests — the
near face of the object is a full radius closer to the camera than the centre, and that is what
crops first.

---

## 3. Verify with the app's own functions, not a rebuild

This is the single biggest time saver. Write DOM fields (or `loadCfgNoBuild`), call
`getConfig()`, then evaluate with the app's real evaluators. No mesh build, so a full parameter
sweep costs seconds instead of minutes — and because it is the same code the exporter runs, the
numbers are trustworthy.

```js
const cfg = getConfig();
evalFieldWithModifier(cfg.eq,    cfg, theta, z, phi, v, cfg.R, false, 'base');     // L3658
evalFieldWithModifier(cfg.texEq, cfg, theta, z, phi, v, 0,     true,  'texture');
vaseHoleRadiusAtHeight(cfg, heightAboveBase);                                      // L5141
applyDistortionPoint(cfg, {x, y, z}, theta, z, phi, v);                            // L3694
evaluatePatternValue(cfg.patternEq1, ...);                                         // masks
memoizedMeshBuild(buildMultipartMeshes, cfg);   // only when you need mesh validation
```

Sweep 100–500 candidate parameter sets against hard constraints, filter, then render only the
survivors. Tuning by eye through full rebuilds is the slow path. The appendix has the spherical pot
analyser built this way.

---

## 4. Geometry by coordinate system

### Cylindrical

Straightforward: body is `r(theta, z)` over `z ∈ [0, h]`, flat base at `z = 0`.

- Vase: the glass top sits at `bottomThickness + vase.height`. Set `base.height` to that plus the
  collar you want. A 2–3 cm collar reads well; flush (±2 mm) also works.
- Vase wall = `min over (theta, v) of r − cavityRadius`, only above `bottomThickness`.
- **Much friendlier for overhang** than spherical — walls are near-vertical, so relief rarely
  tips past 45°. Typical measured: 0.1–0.2 % with a gyroid, 0 % with smooth terrain.

### Spherical

Several things that are not obvious:

- **`base.height` is inert.** The body is driven entirely by `baseRadius` and the phi sweep;
  `cfg.h` is only read on the cylindrical path. Emit a sensible number anyway.
- `phiStart = sphTopCut`. `phiEnd` is fixed at **175°** in vase mode (`sphericalPhiEnd`, L3615 —
  `sphBotCut` is ignored) and is `sphBotCut` in pot mode (§1.2).
- `v = (phi − phiEnd) / (phiStart − phiEnd)`, so **v = 1 at the top cut**. A feature centred at a
  phi *above* `sphTopCut` is sliced off. (A reviewed vase centred its crown at `phi = 0.4`
  with a 32.5° cut — that peak sat at **v = 1.067**, entirely outside the body, so only the
  Gaussian tail was visible as thin fins.)
- `flatBottomY = cfg.R * cos(sphBotFlatten)` (L5349) — uses **`cfg.R`, not the evaluated
  radius**, so the base plane does not move when you reshape the silhouette.
- Footprint diameter = `2·R·sin(sphBotFlatten)`. 150° gives a narrow foot; **130–140° is much
  more stable**, widens the body where a vase's cavity floor sits, and (135°) removes a pot's
  lower-body overhang (§5.3).

**Vase: the spherical rim is almost always the binding wall constraint.** A sphere tall enough to
cradle a 13 cm glass is inherently narrow at the height of the glass mouth. The fix is a flare
term with a **positive baseline**, not just lobes:

```
+ (c0 + c1*max(0, cos(N*theta))) * exp(-pow(phi - PT, 2) * W)
```

`c0` flares the whole rim outward (buys wall), `c1` adds petals on top. Centre `PT` at
`sphTopCut` so the feature crests *at* the rim instead of being cut away. On a pot the same kind
of collar fixes the inner overhang at the rim (§5.3), but costs true wall (§5.2).

---

## 5. Measuring

### 5.1 Printer tolerance

**User, 2026-09-18:** on the user's Bambu Lab setup, faces up to **60° from vertical print safely
without supports**, and overhangs **supported at both sides (bridges)** are fine. The acceptance
metric is therefore the share of surface past **60°** (§11). The 45° figures in this guide are
kept as history and as a quality indicator, not as a pass/fail limit. 45° work still pays off
where it is cheap (smoother downward faces), but do not give up a form to reach 0 % at 45°.

For triangles: past 60° means `n_up < −sin 60° ≈ −0.866`; past 45° means `n_up < −0.707`. For a
profile slope `d(radius)/d(height)`: past 45° above 1, past 60° above √3 ≈ 1.73.

### 5.2 Wall

**Vase: wall around the bore.** Build an outer profile per theta, then walk **uniform heights**
through the cavity and interpolate the outer radius where the profile crosses each height. Do not
compare parameter-space samples directly — in spherical mode the outer surface height is
`r(phi)·cos(phi)`, which is not monotonic once relief is applied.

**Pot: measure the true wall, not the radial one.** Sample the outer and inner surfaces exactly as
`buildSphericalShell`'s pot branch does (appendix). The radial wall is `wall + texInt × texture`
and looks fine everywhere. The **true** wall — the distance from each inner vertex to the nearest
outer vertex in a ±7-cell window — is thinner wherever the silhouette slopes steeply against the
radius, because the offset is radial, not normal. `true ≈ radial × cos(tilt)`.

A rim collar is exactly such a slope. Sweep on Caldera (`R*(1 − 0.08*sin²φ + A*exp(−(φ−c)²·W))`):

| Collar A / W / c | Radial wall | True wall min | Inner > 45° |
|---|---|---|---|
| 0.24 / 22 / 0.62 | 4.2 mm | 3.01 mm @ φ 44° | 0 % |
| 0.24 / 22 / 0.62 | 4.8 mm | 3.47 mm | 0 % |
| 0.22 / 12 / 0.60 | 4.8 mm | **3.95 mm** | **0 %** ← shipped |
| 0.16 / 12 / 0.66 | 4.8 mm | 4.22 mm | 0.69 % |
| 0.14 / 10 / 0.70 | 4.8 mm | 4.37 mm | 2.02 % |

A weaker collar thickens the wall but brings back inner overhang (§5.3). Widen the Gaussian
(lower `W`) before you lower its amplitude.

### 5.3 Overhang

**Profile method (vase, outer surface).** Bin the **world-space** outer boundary by (height row,
world-angle) and take `d(radius)/d(height)` between consecutive rows. Two traps, both of which
produced garbage before they were caught:

- **Exclude the flat-bottom clamp.** Clamped points share one height, so the slope divides by
  ~0 and reports a spurious 90°. The flat base is the print bed, not an overhang.
- **Do not filter by `Δy > ε` on the parametric profile.** Relief makes `y(phi)` non-monotonic,
  so that filter throws away nearly every sample and the percentages become meaningless.

**Triangle method (pot, both surfaces).** Use area-weighted triangles on the sampled grids (§5.1
thresholds); orient outer normals away from the sphere centre and inner normals toward it; skip
cells whose four corners are all on the clamped bed plane. A pot has two printed faces, and they
fail in different places:

- **Inner surface:** the inside of a sphere's closing top faces down. With a plain sphere the
  inner lean at the rim is `90° − sphTopCut`, so a 38° top cut starts at **52°**. A rim collar
  that turns the upper wall near-vertical removes it completely (§5.2 table).
- **Outer surface:** below the equator, a plain sphere leans `phi − 90°`, so everything between
  135° and `sphBotFlatten` is past 45°. Measured on an early Caldera body: flatten 142° → **1.3 %**
  from the silhouette alone; flatten **135° → 0 %**, and the footprint widens from 9.5 to 10.9 cm.

**Locate before you fix.** Bin the offending triangles by (phi, theta), not by phi alone. On
Ironclad the 0.66 % at φ ≈ 80° looked like plate bevels. Softening the bevels and the relief fade
changed nothing. Binning by theta put every hit at θ = 45° + k·90°, φ 75–76°: the bottom edge of
the four hatch frames.

**Measure how high each overhanging face sits.** Flared feet reach the bed before
`sphBotFlatten` (§9.7), so the cells where the surface meets the clamp plane produce a ring of
steep slivers. On Red Cap Overalls they were 0.21 % of the surface, but every one topped out
below 0.6 mm, i.e. inside the first three layers, printed straight onto the bed. Report overhang
**above 1 mm** alongside the raw figure: 0 % there.

**Raised features on a downward-facing edge.** A frame 4.5 mm tall with a 2.3 mm outer ramp, 76°
down the body, gave 0.66 %. Dropping it to 3.4 mm, widening the ramp to 3.8 mm and moving the
hatch 4° higher (where the base faces up more) took the whole pot from 0.83 % to 0.08 %. Budget the
ramp from the steepest point of `smoothstep`, which is 1.5 × its average slope.

Relief is usually the bigger lever — see §6.

### 5.4 Colour

- **Coverage:** sample the real phi/v sweep, count the four states area-weighted on the
  **visible** outer surface (exclude clamped cells — the underside), and require each > ~2 %
  (§8.1). Do it numerically before rendering.
- **Colour on the bed layer:** after export, read `zmin` of every pattern body in the 3MF. On a
  pot it should be > 0, so the first layers print in the base colour only (§9.4).

### 5.5 Soil volume (pots)

The theta-averaged `∫ π ρ_in² dy` of the inner surface. Caldera: 1.53 L.

---

## 6. Relief and overhang

`tanh(k·G)` gives plateaus separated by cliffs; `k` controls the cliff steepness, and on a vase
that is what drives overhang — not the depth alone. Fade relief out at the foot with
`* smoothstep(0.02, 0.25, v)` for a clean printable base while the colour still runs to the
bottom.

**On a pot the fade itself is the overhang, not the cliffs.** A fade is an outward slope, climbing
over height on a surface already leaning outward. With 4 mm of relief it dominated everything
else:

| Cliff `k` | Relief | Fade `[0.29, 0.42]` | Fade `[0.29, 0.50]` |
|---|---|---|---|
| 2.5 | 3.2 mm | 0.62 % | 0 % |
| 3.5 | 3.2 mm | 0.82 % | 0.01 % |
| 2.5 | 4.0 mm | 2.41 % | 0 % |
| 3.5 | 4.0 mm | 2.49 % | 0.11 % |

Cliff steepness moved the number by < 0.1 %. **Stretch the fade over the lower third of the
body before you touch depth or steepness.** Colour can still run all the way to the foot.

**Do not hard-terrace elevation.** Elevation maps to *radius*, so every uphill step becomes an
outward shelf — a 90° overhang. Soft terraces (§10.6) are fine.

Reduce relief depth or soften transition sharpness to buy overhang; raise `bottomThickness` or
widen the body to buy wall.

---

## 7. Distortion and the glass fit (vase mode)

`applyDistortionPoint` is applied to the **inner cavity points as well as the outer surface**
(spherical L5401–5402, again at L7236–7237, same pattern in the cylindrical builder). Any bend,
lean, sag or pressure dent warps the bore and the glass no longer fits.

**Torsion about the vertical axis is the exception**, because a rotation maps a circle centred
on the axis onto itself:

```json
"dx": "x*cos(A) - z*sin(A) - x",
"dz": "x*sin(A) + z*cos(A) - z",
"dy": "0", "strength": 1.0, "region": "all", "anchor": "none"
```

where `A` is any function of `v` alone.

**`strength` must be exactly 1.0, `region` "all", `anchor` "none".** `applyDistortionPoint`
computes `factor = strength × regionFactor × anchorFactor` (L3699). For any `f ≠ 1` the map
becomes a *scaled* rotation and the bore radius changes by

```
k = sqrt(1 + 2(1 − cos A)(f² − f))
```

which is < 1 for 0 < f < 1. At `A = 0.75 rad, f = 0.5` the 41.0 mm bore closes to 38.1 mm and
the glass will not go in. `getDistortionRegionFactor('all')` and
`getDistortionAnchorFactor('none')` both return 1 (L3668, L3676) — any other value scales it.

**Always verify on the built rings**, don't trust the algebra:

```js
const pt = applyDistortionPoint(cfg, {x: holeR*Math.cos(th), y: nomY, z: -holeR*Math.sin(th)},
                                th, 0, phi, v);
// max |hypot(pt.x, pt.z) − holeR| over every ring must be 0.0000 mm
```

### Torsion is expensive in overhang

Measured on the same body, same relief: **modifier twist alone 0.12 % of the wall past 45°;
adding the torsion distortion took it to 1.99 %.** Both rotate the surface, but the modifier
remaps theta *before* the fields are sampled, while torsion rotates already-carved geometry, so
the relief climbs far faster at a fixed world angle.

**Prefer the modifier for twist.** Raise `modifier.strength` and drop the distortion entirely —
the visual result is indistinguishable and the print is ~10× cleaner.

---

## 8. Pattern masks and colour layout

### 8.1 Four states, none wasted

Four colour states come from two masks: neither / A only / B only / both. **A mask pair where
one contains the other silently wastes a colour.** A reviewed vase had Pattern A entirely
inside Pattern B — `patternColor1` rendered **nowhere**, and the status line showed
`Pattern B (1), Overlap (14)` with no Pattern A body at all. Measure coverage (§5.4).

Good targets: dominant state 35–60 %, secondary 15–35 %, accents 3–20 %.

Other rules that held up:

- **`smoothPatternEdges: true`** for any curved, diagonal or organic mask. Only leave it false
  for axis-aligned stripes or a draft preview.
- **Outward-only shape terms preserve wall.** `0.11*max(0, cos(6*theta))` never reduces the
  radius, so the wall budget is set by the profile alone. `0.11*cos(6*theta)` costs you 11 % of
  R at every trough. Same trick for ripples: `max(0, sin(7*phi))`.
- **Drive relief and colour from the same field.** When `texture` and the masks share an
  expression, the colour boundary lands exactly on the physical cliff. That coherence is most
  of why the gyroid and terrain designs read well.
- **Write every mask term as a signed distance in millimetres** when combining motifs (§10.7):
  `min`/`max` then combine terms without squashing any boundary (§9.3).
- **Which state lands where:** base fills the recesses, pattern A the raised plateaus. Dark base
  + light plateau reads as carved depth; the reverse looks flat. On a pot, put the colour you want
  on the bed and on the soil side in the base state — the core body is the base colour, so it
  forms the inside wall and the first layers.

### 8.2 Pattern A and pattern B must never share a boundary line

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
- When the design's contacts already form the square, no strip is needed. Wildfire Drake:
  orange–cream (belly, claws), cream–yellow (diamonds), yellow–red (flame cores), red–orange
  (flame edges) gave orange 00, cream A, yellow overlap, red B.

**Verify it numerically, not by eye.** Sample both masks on a ~0.3 mm (theta, phi) grid, label each
sample 0–3, and for every sample of state 3 (or 1) find the nearest sample of state 0 (or 2)
within a ±10-cell window. The result is the **narrowest separating strip in millimetres** for each
forbidden pair. Aim for ≥ 1.5 mm, which is more than one mesh cell at 260 × 400.

- Wildfire Drake's first flames had open edges; after the redesign the narrowest red strip
  between a yellow core and the orange body measured 3.97 mm.
- Adding the tail flame brought it to 2.61 mm, still clean.
- A 700 × 1400 check takes ~2 s.

### 8.3 The very top and bottom rows are forced to the base colour

`buildSmoothColorMeshes` (L6021) forces both masks to −1 on the first and last vertex rows so the
rim bezel is a plain base-colour quad. If a colour that needs **both** masks (the overlap state)
runs up to the rim, the first row is a base → overlap transition, the §8.2 case again.

On Red Cap Overalls (red cap = overlap) this left a blue hairline in the top row: its outer face is
~0.02 mm wide, plus two 1.4 mm side walls. It's invisible, below any nozzle width, and every body
stays B:0 N:0, so it was accepted. The ring is inherent whenever the rim colour is two switches
from base (brown–red–blue form a triangle through the forced ring). To avoid it, let the rim
colour be the base state or a single-mask state, as on Caldera and Ironclad.

---

## 9. Traps

### 9.1 "manifold check passed" is not a manifold check

`exportMultiPart3MF` only aborts when **`blockingIssues.length > 50`**. Until 2026-09-26 the status
string then printed "manifold check passed" whenever the core edge-case flag was false, so a model
with 6 boundary edges on the core and 12 on the overlap exported with a green light. It now says
`manifold warnings (N)` and lists them, but it still exports.

**Check the validations directly:**

```js
const parts = memoizedMeshBuild(buildMultipartMeshes, getConfig());
parts.coreValidation.boundaryEdges;                       // must be 0
parts.surfaceGroups.map(p => p.mergedValidation.boundaryEdges);   // all must be 0
```

The preview status line does surface it as `Core B:6 | Overlap B:12` — read it, don't skim it.

**Cause and fix:** holes come from sliver-thin mask regions (and from coincident A/B boundaries,
§8.2), not from undersampling. Thickening the contour mask from `cos(30·H) − 0.75` to `− 0.65`
took every count to zero. Raising resolution from 280×380 to 320×420 made it **worse**, which is
how you tell the two apart.

### 9.2 `smoothPatternEdges` round-trip (fixed)

`getCurrentDesignerConfig` used to omit `patterns.smoothPatternEdges` while `applyAIJson` read
it, so every saved design silently reloaded with stepped edges and rebuilt to different
geometry. Fixed at L2591. **Any JSON written by hand must still include the field** — the loader
defaults it to false.

### 9.3 A `min()` gate with a small term makes stair-stepped colour edges

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

### 9.4 The foot colour gate must sit above `v_flat` (pots)

A gate at `v = 0.29` looks like it stops at the foot, but with `sphBotFlatten = 135°`,
`sphBotCut = 176°` and `sphTopCut = 38°`, `v_flat = 0.297`. The gate is therefore 1° *inside* the
clamped band, and every pattern body reached `z = 0`: a thin coloured ring on the first layer.
Moving it to `0.305` lifted the pattern bodies to `zmin = 3.4 mm`. Always compute `v_flat` from
§1.2 and then confirm with `zmin` in the exported 3MF.

### 9.5 The saucer reuses the pot's masks on its own phi/v sweep

`buildSphericalPlateMultipartMeshes` (L4765) runs the normal multipart builder on
`buildSphericalPlateGenerationConfig` (L4114): top cut = `plateSphTopCut` (95°), flatten =
`plateSphBotFlatten` (250°, so only `R·cos 250° = −0.342 R` clamps the floor), bottom cut forced
to 180°. The pot's pattern equations are evaluated with the saucer's own
`v = (phi − 180°) / (95° − 180°)`, and nothing excludes the flat floor.

On Caldera, **55 % of the saucer's underside came out coloured**: invisible, but four colours on
the first layers.

- There is no clean equation-level fix. For a given phi the pot's `v` and the saucer's `v` differ,
  and no linear gate in (phi, v) passes the pot's lower body while blocking the saucer floor. A
  non-linear discriminator can be built, but it breaks as soon as anyone changes a cut angle. To
  keep colour off the saucer, turn saucer colouring off instead.
- **Choosing and shipping.** Set `plate.applyColoring: false` when the pot's motifs look odd on
  the saucer (a belly or tail copied onto the rim of the dish), or when colour on the first layers
  is unwanted. The JSON then reproduces the plain saucer on reload. To ship both variants, export
  once as the JSON says, then flip the box and call
  `exportPlateAssembly3MF(getConfig(), { filenameStem: '<Name>_Plate_Plain' })` (or `_Plate` for
  the coloured one).

### 9.6 Generated expressions and negative thresholds

String-building `H − ${t}` with `t = −0.58` produces `H - -0.58`. It evaluates correctly, but it is
ugly in the delivered JSON. Rewrite it as `H + 0.58` — in IEEE arithmetic `a − (−b)` is exactly
`a + b`, so the round-trip hash is unaffected (verified).

### 9.7 Leg lobes reach the bed before `sphBotFlatten`

Where the base radius exceeds `R` near the foot (flared legs), the clamp `r·cos(phi) < R·cos(flatten)`
kicks in earlier: at 129° instead of 135° for a +16 % lobe. A phi- or v-based foot gate then
leaves colour on the bed at the legs, or a lopsided sole. Gate on **height above the bed**
instead. `baseFormRadius` is available in pattern equations:

```
foot = (baseFormRadius*cos(phi) - R*(-0.70711) - 0.4)*10     // mm above a 4 mm sole, flatten 135°
```

The constant is `cos(sphBotFlatten)`, so it has to change with the flatten angle. Ironclad's teal
body starts at exactly `z = 4.00 mm` all the way round.

### 9.8 Relief cliffs narrower than a mesh cell alias the geometry

A `tanh(k·(H − t))` step spans roughly `2 / (k·|∇H|)`. A 15-cell gyroid on R = 8 has `|∇H|` up to
~3.3 /cm, so `k = 3.5` gives cliffs ~1.7 mm wide. At 180 × 260 (1.8 mm per theta cell) they alias
onto the grid. 260 × 400 (~1.2 mm) is the working resolution for this scale; that produces
3MFs of ~90 MB each for pot and saucer.

### 9.9 Vertical warp

`modifier.equationV` is dangerous on any silhouette with a localised flare: it drags the flare's
Gaussian around in `v`. One vase trial widened the body from 13.4 to 16.8 cm and collapsed the
minimum wall to **0.3 mm**. Leave it `""` unless the silhouette is warp-insensitive.

---

## 10. Equation cookbook

### 10.1 Seam safety

Any `theta` coefficient must be an **integer**, or the expression must be built from
`cos(theta)` / `sin(theta)`. `sin(1.5*theta)` tears at the seam.

### 10.2 Gyroid, spherical

`sin(X)cos(Y) + sin(Y)cos(Z) + sin(Z)cos(X)` evaluated at the surface direction:

```
X = Ah*sin(phi)*cos(theta)    Y = Av*cos(phi)    Z = Ah*sin(phi)*sin(theta)
```

`Ah = Av` is a true isotropic gyroid. **`Av < Ah` stretches cells vertically**, which both suits
a vase and cuts overhang — 15/9 dropped it from 3.2 % to 1.9 % (past 45°) versus 15/15.

### 10.3 Gyroid, cylindrical

```
X = A*cos(theta)    Y = A*sin(theta)    Z = B*v
```

Much easier to tune: **`A` is directly the cell count around the circumference**, `B/(2π)` the
number of vertical periods. `A = 10, B = 13` on a 17 cm column reads well.

### 10.4 Relief shaping

See §6: `tanh(k·G)` plateaus, a long foot fade, no hard terraces.

### 10.5 Noise terrain / "islands"

```
H       = fbm(theta, v, 1.2, 2.2, 4, 17)      // range ≈ [−0.8, 0.8], mean ≈ 0
land    = H − 0.12                             // sea level; 0.12 → ~30 % land
contour = cos(30*H) − 0.65                     // contour lines at even elevation intervals
texture = 0.68*tanh(3.0*(H − 0.12)) + 0.38*H   // shoreline cliff + continuous elevation
```

`st` sets horizontal feature count, `sv` vertical. Because `cos(k·H)` is a function of elevation
alone, bands tighten on slopes and spread on flats — that is what makes it read as a chart.
All noise is seeded and deterministic, so exports are reproducible. (This texture is signed: fine
in vase mode, rewrite it outward-only for a pot, §1.2.)

### 10.6 Colour bands that encode height (hypsometric tint)

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
      * smoothstep(v_flat + 0.008, 0.5, v)          // foot fade, §6
      * (1 − smoothstep(0.925, 0.95, v))            // clean rim band
```

Caldera uses `k = 2.5` and intensity 0.40 (4 mm). This is a *soft* terrace; the warning against
hard terracing (§6) still stands.

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
scale the gate (§9.3).

### 10.7 Motifs (armour plates, hatches, markings, flames)

Ironclad Tortoise Planter is built from discrete motifs rather than a single field. These
techniques carried it and Wildfire Drake:

**Write every mask term as a signed distance in millimetres.** `(phi − φ₀)·R·10`, `(D − d₀)·10`,
`(w − E)·cell_mm`. Then `min`/`max` combine terms without squashing any boundary (§9.3), and
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

Diamonds (gems) use the same idea: `1 − |dx|/a − |dy|/b` is ≥ 0 inside a rhombus. Its positive
part doubles as a gentle four-facet pyramid for the relief. A hollow (outlined) gem is
`min(outer, −inner)`, with the inner rhombus shrunk by the ring width.

**Flames.** Measure height above a wavy base line, `up = (φ_base(θ) − φ)·R`.

- Tongue profile: a triangle wave raised to a power, `pow(1 − 2|fract(N·θ'/2π) − 0.5|, p)`. That
  gives pointed, concave tongues. A cosine lobe gives rounded blobs that read as waves.
- Flicker: `θ' = θ + c·up + w·sin(k·up + 2θ)` bends the tongues into S-shapes.
- Outer flame: `up < h0 + T·s`. Core: `h0c + Tc·s^q` with `h0c < h0 − margin`, `Tc ≤ T`, `q > 1`.
  Then the core stays at least `margin` below the outer edge vertically, and narrower sideways.
- These are *vertical*-distance fields. On a steep tongue flank they change several millimetres
  per cell sideways, so a relief step of `smoothstep(−1, 1, F)` becomes a sub-cell cliff and
  aliases. Ramp the relief over ~10 mm of `F` (`clamp(F/10, 0, 1)`) instead.

**Curved bands (a tail).** An arc of radius `r` centred at `(r, 0)` in local cm coordinates:
`u = atan2(−ty, r − tx)` runs 0 → π/2 along it, and `|hypot(tx − r, ty) − r|` is the distance
across it. Gate both ends with `u·r` and `(π/2 − u)·r`, taper the width with `u`, and a
`min(band, w − band)` strip gives a coloured outline of width `w` just inside the edge.

---

## 11. Acceptance thresholds

Measure all of these before packaging. Report them.

| Check | Applies to | Target | Notes |
|---|---|---|---|
| Minimum wall around the bore | vase | **≥ 6 mm**, ideally 8 mm | Below 5 mm is fragile in a solid body (§5.2) |
| Cavity roundness after distortion | vase | **0.0000 mm** deviation | Measure with `applyDistortionPoint` (§7) |
| True minimum shell wall | pot | **≥ 3.5 mm** | Measured, not radial (§5.2). The collection's spherical pots use 3.5–5 mm radial walls |
| Texture minimum | pot | **≥ 0** | Otherwise the wall shrinks (§1.2) |
| Surface past 60° (outer; and inner on a pot) | all | **< 0.5 %**, 0 % preferred | The printer's unsupported limit (§5.1). Bridged spans (supported at both ends) are acceptable even past it. Report the figure above 1 mm too |
| Surface past 45° | all | report only | Quality indicator, not a limit |
| Boundary / non-manifold edges | all | **0 / 0** on every body, pot **and saucer** | Read the validations directly (§9.1) — the UI lies about this |
| Four colour states | all | each **> 2 %** | §8.1 |
| Mask layout | all | no edge where A and B switch together | §8.2 |
| Narrowest separating strip | all | **≥ 1.5 mm** for both forbidden pairs | Numerical strip check (§8.2) |
| Pattern bodies `zmin` | pot | **> 0** | First layers print single-colour (§9.4) |
| Drain | pot | present | `sphBotCut` < 179.7° |
| Base sits on Z = 0 | all | yes | Exporter applies printer-flat orientation |
| Round trip | all | identical mesh hashes after reloading the JSON (§13) | pot **and saucer** |

Reduce relief depth or soften transition sharpness to buy overhang; raise `bottomThickness` or
widen the body to buy wall.

---

## 12. Palettes already used

Prefer exact Bambu Lab PLA Basic hexes (see `PLA_Colors.txt`). Pick a combination not already
on this list — or in `WOVEN_DESIGNER_AGENT.md` §10 — so the family stays varied. Columns are in
JSON-slot order.

| Design | Mode | base | pattern A | pattern B | overlap |
|---|---|---|---|---|---|
| Verdant Spiral Bloom | vase | `#482960` Indigo Purple | `#00AE42` Bambu Green | `#EC008C` Magenta | `#FEC600` Sunflower Yellow |
| Crown Splash Ovoid | vase | `#545454` Dark Gray | `#00AE42` Bambu Green | `#BECF00` Bright Green | `#5E43B7` Purple |
| Gyroid Magma Flare | vase | `#0A2989` Blue | `#00B1B7` Turquoise | `#FF6A13` Orange | `#FEC600` Sunflower Yellow |
| Gyroid Ember Column | vase | `#000000` Black | `#E4BD68` Gold | `#9D2235` Maroon Red | `#FF9016` Pumpkin Orange |
| Archipelago Contour Vase | vase | `#0056B8` Cobalt Blue | `#F7E6DE` Beige | `#00B1B7` Turquoise | `#9D432C` Brown |
| Caldera Atlas Orb | pot | `#000000` Black (valleys) | `#C12E1F` Red (lowlands) | `#8E9089` Gray (peaks) | `#847D48` Bronze (highlands) |
| Ironclad Tortoise Planter | pot | `#545454` Dark Gray (shell, rim, sole) | `#C12E1F` Red (seams, outlines, muzzles) | `#0086D6` Cyan (lower body) | `#FFFFFF` Jade White (band, frames, triangles) |
| Red Cap Overalls Planter | pot | `#6F5034` Cocoa Brown (shoes, button rims, interior) | `#0056B8` Cobalt Blue (overalls) | `#FEC600` Sunflower Yellow (button faces) | `#C12E1F` Red (cap, shirt) |
| Wildfire Drake Planter | pot | `#FF9016` Pumpkin Orange (body, interior) | `#F7E6DE` Beige (belly, claws) | `#C12E1F` Red (flames, tail outline) | `#FEC600` Sunflower Yellow (flame cores, gems) |

For Caldera the height order is base → A → overlap → B (§10.6).

---

## 13. Packaging

| Mode | Folder |
|---|---|
| vase | `3dModels/Vases/<Design Name With Spaces>/` |
| pot, potplate | `3dModels/MultiColor/<Design Name With Spaces>/` |

```
<folder>/
    Design_Name.3mf     (Bambu Studio project from exportBambuStudio3MF, printer as the user asks;
                         pot on plate 1, saucer on plate 2)
    Design_Name.json    (downloadCurrentSettingsJson)
    Design_Name.png     (render: front + back side by side)
```

The gallery `.3mf` files are **Bambu Studio projects**. The app's **Download Bambu Lab .3MF**
button (`exportBambuStudio3MF()`) writes one directly, with filament slots already assigned and no
plate thumbnails; re-saving it in Bambu Studio adds the thumbnails. (Older vase entries were
`exportMultiPart3MF` files — `<Name>_Pot_multipart.3mf`, renamed to `<Name>.3mf` — re-saved in
Bambu Studio.) Older `MultiColor` folders also hold `<Name>.jpg` and `<Name>Thumbnail.jpg`: those
are **photos of printed pieces** (3000 × 4000 and 800 × 600) and cannot come from the app. Tell
the user the PNG is a render, so a photo can replace it later.

**Always round-trip verify before calling it done:** reload the delivered JSON with
`applyAIJson()`, re-export, and compare the mesh payload hashes. Zip timestamps differ between
runs, so hash the inner XML, not the `.3mf` file:

```python
z = zipfile.ZipFile(p)
# multipart export: '3D/3dmodel.model'
# Bambu project:    every '3D/Objects/object_*.model' (the root model carries a creation date)
hashlib.sha256(z.read(name)).hexdigest()
```

Also confirm from the 3MF itself: the expected parts (4 colour bodies per object), the 4 expected
colours, `unit="millimeter"`, and that the object stands on `z = 0`. The Bambu Studio command line
on this machine cannot slice the app's Bambu export (partial project config) — slice in the GUI.

---

## 14. Reference designs

### Vases

Dimensions read from the exported 3MF bounding box.

| Design | Coord | Glass (cm) | Body W×H (cm) | Min wall | >45° | Solid mass |
|---|---|---|---|---|---|---|
| Verdant Spiral Bloom | cyl | 9.6 × 17 | 14.7 × 17.5 | 4.5 mm | — | 838 g |
| Crown Splash Ovoid | sph | 8 × 13 | 12.8 × 15.6 | 5.4 mm | — | 719 g |
| Gyroid Magma Flare | sph | 8 × 13 | 13.1 × 16.1 | 8.2 mm | 1.91 % | 1007 g |
| Gyroid Ember Column | cyl | 8 × 13 | 14.8 × 17.0 | 7.9 mm | 0.19 % | 1487 g |
| Archipelago Contour Vase | cyl | 9.6 × 17 | 14.1 × 18.5 | 8.4 mm | 0 % | 1407 g |

Masses are the app's 100 %-solid estimate; at 10–15 % infill expect roughly a quarter of that.
Quote both — the headline number alarms people unnecessarily.

Mesh resolution of 240–280 × 360–400 is enough for fine patterns at these sizes; 3MF files land
between 50 and 140 MB, which the user has confirmed is acceptable.

### Pots

| Design | Coord | R | Top / flatten / bot cut | Pot W × H | Opening | Foot | Wall true (radial) | >45° out / in | Soil | Pot / saucer (100 % solid) |
|---|---|---|---|---|---|---|---|---|---|---|
| Caldera Atlas Orb | sph | 8 | 38° / 135° / 176° | 15.4 × 13.1 cm | 11.0 cm | 10.9 cm | 3.96 mm (4.8) | 0 % / 0 % | 1.5 L | 463 g / 161 g |
| Ironclad Tortoise Planter | sph | 8.5 | 44° / 135° / 176° | 16.8 × 12.6 cm | 12.1 cm | 11.6 cm | 4.18 mm (4.8) | 0.09 % / 0 % | 1.8 L | 497 g / 176 g |
| Red Cap Overalls Planter | sph | 8 | 40° / 135° / 176° | 16.3 × 13.1 cm | 11.5 cm | 11.3 cm | 4.25 mm (4.8) | 0 % above 1 mm (0.21 % raw) / 0 % | 1.65 L | 502 g / 180 g |
| Wildfire Drake Planter | sph | 8 | 40° / 135° / 176° | 16.5 × 12.9 cm | 11.5 cm | 11.1 cm | 4.04 mm (4.8) | 0.18 % above 1 mm, 0 % past 60° / 0 % | 1.67 L | 406 g / 160 g |

Caldera: mesh 260 × 400, pattern depth 1.4 mm, saucer 15.4 × 2.1 cm (spherical plate at 95° /
250°, +0.5 cm). Coverage 38 / 25 / 23 / 14 %. The pot 3MF is 93 MB and the saucer 88 MB.

Ironclad: same mesh, depth and saucer settings; saucer 17.1 × 2.2 cm. Coverage: dark gray 49 %,
red 12 %, teal 27 %, white 11 %. The saucer underside is 27 % coloured. The pot 3MF is 78 MB and
the saucer 71 MB.

Red Cap Overalls: same settings; saucer 16.2 × 2.1 cm. Coverage: blue 48 %, red 35 %, brown 16 %,
yellow 2.1 % (six buttons). The saucer comes out brown and blue, with 10 % of its underside
coloured. The pot 3MF is 78 MB and the saucer 60 MB.

Wildfire Drake: same settings. Coverage: orange 71 %, red 15 %, cream 9 %, yellow 5 %. The pot's
colour bodies start 8 mm above the bed. The 0.18 % overhang sits on the claws, below 2 cm. The pot
3MF is 64 MB, the saucer 54 MB, and a plain `_Plate_Plain` saucer 46 MB (§9.5).

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
// For the 60° pass/fail figure, compare against -Math.sin(Math.PI / 3) (≈ −0.866) instead of -Math.SQRT1_2.
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
`textureFill`/`texPosNorm`; the height-band masks in §10.6 do not need it.
