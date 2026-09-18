# Vase Designer Agent

Operational guide for producing **glass-insert vase holders** with
`EquationDrivenPotDesigner.html` (`structure.modelMode = "vase"`).

This sits **on top of** `EquationGeneratorPrompt.txt`, which remains the source of truth for
the JSON schema, the preset names and the equation library. Nothing here repeats that. What
follows is the part that is not written down anywhere else: how to drive the tool, what to
measure, what silently goes wrong, and the thresholds a design has to clear before it ships.

Line numbers refer to `EquationDrivenPotDesigner.html` as of the commit that added this file.
They drift — grep the function name instead of trusting the number.

---

## 1. What a vase-mode design actually is

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

**Never ship without measuring the wall.** The first design reviewed this session had a
**−0.6 mm** minimum wall — the bore broke out through the rim — and nothing in the UI said so.

---

## 2. Harness: driving the app headlessly

A local server plus the built-in browser gives full programmatic control and puts exports
straight on disk with the filenames you want.

```python
# serve project dir; POST /__save/<name> writes into an output folder
# (full script lives in the session scratchpad; ~40 lines, http.server subclass with CORS)
```

Then in the page:

```js
// exports land on disk instead of the browser download folder
window.downloadBlob = async function (blob, filename) {
  const r = await fetch('http://127.0.0.1:8733/__save/' + encodeURIComponent(filename),
                        { method: 'POST', body: blob });
  return await r.text();
};

// programmatic config load — same path as the LOAD DESIGN .JSON button
document.getElementById('aiJsonInput').value = JSON.stringify(cfg, null, 2);
applyAIJson();
await new Promise(r => setTimeout(r, 15000));   // large meshes are slow; wait generously
```

`downloadViewportImage()`, `exportMultiPart3MF()` and `downloadCurrentSettingsJson()` all route
through `downloadBlob`, so one override captures everything.

**Viewing renders:** you cannot see an image returned from JS. Save the PNG to disk, downscale
it ~3× with PIL, and `Read` the small copy. Full-size 1980×1800 renders are wasteful to read.

**Camera:** the renderer only re-aims `controls.target` on rebuild; it never moves the camera.
Set `camera.position` yourself and back off further than the bounding sphere suggests — the
near face of the object is a full radius closer to the camera than the centre, and that is what
crops first.

---

## 3. Verify with the app's own functions, not a rebuild

This is the single biggest time saver. Write DOM fields, call `getConfig()`, then evaluate with
the app's real evaluators. No mesh build, so a full parameter sweep costs seconds instead of
minutes — and because it is the same code the exporter runs, the numbers are trustworthy.

```js
const cfg = getConfig();
evalFieldWithModifier(cfg.eq,    cfg, theta, z, phi, v, cfg.R, false, 'base');     // L3658
evalFieldWithModifier(cfg.texEq, cfg, theta, z, phi, v, 0,     true,  'texture');
vaseHoleRadiusAtHeight(cfg, heightAboveBase);                                      // L5141
applyDistortionPoint(cfg, {x, y, z}, theta, z, phi, v);                            // L3694
memoizedMeshBuild(buildMultipartMeshes, cfg);   // only when you need mesh validation
```

Sweep 100–500 candidate parameter sets against hard constraints, filter, then render only the
survivors. Tuning by eye through full rebuilds is the slow path.

### Measuring minimum wall

Build an outer profile per theta, then walk **uniform heights** through the cavity and
interpolate the outer radius where the profile crosses each height. Do not compare
parameter-space samples directly — in spherical mode the outer surface height is
`r(phi)·cos(phi)`, which is not monotonic once relief is applied.

### Measuring overhang

Bin the **world-space** outer boundary by (height row, world-angle) and take `d(radius)/d(height)`
between consecutive rows. Slope > 1 is past 45°.

Two traps, both of which produced garbage before I caught them:
- **Exclude the flat-bottom clamp.** Clamped points share one height, so the slope divides by
  ~0 and reports a spurious 90°. The flat base is the print bed, not an overhang.
- **Do not filter by `Δy > ε` on the parametric profile.** Relief makes `y(phi)` non-monotonic,
  so that filter throws away nearly every sample and the percentages become meaningless.

---

## 4. Distortion will break the glass fit — except one case

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

## 5. Geometry by coordinate system

### Cylindrical

Straightforward: body is `r(theta, z)` over `z ∈ [0, h]`, flat base at `z = 0`.

- Glass top sits at `bottomThickness + vase.height`. Set `base.height` to that plus the collar
  you want. A 2–3 cm collar reads well; flush (±2 mm) also works.
- Wall = `min over (theta, v) of r − cavityRadius`, only above `bottomThickness`.
- **Much friendlier for overhang** than spherical — walls are near-vertical, so relief rarely
  tips past 45°. Typical measured: 0.1–0.2 % with a gyroid, 0 % with smooth terrain.

### Spherical

Several things that are not obvious:

- **`base.height` is inert.** The body is driven entirely by `baseRadius` and the phi sweep;
  `cfg.h` is only read on the cylindrical path. Emit a sensible number anyway.
- `phiEnd` is fixed at **175°** for vase mode (`sphericalPhiEnd`, L3615) — `sphBotCut` is
  ignored. `phiStart = sphTopCut`.
- `v = (phi − phiEnd) / (phiStart − phiEnd)`, so **v = 1 at the top cut**. A feature centred at a
  phi *above* `sphTopCut` is sliced off. (The reviewed design centred its crown at `phi = 0.4`
  with a 32.5° cut — that peak sat at **v = 1.067**, entirely outside the body, so only the
  Gaussian tail was visible as thin fins.)
- `flatBottomY = cfg.R * cos(sphBotFlatten)` (L5349) — uses **`cfg.R`, not the evaluated
  radius**, so the base plane does not move when you reshape the silhouette.
- Footprint diameter = `2·R·sin(sphBotFlatten)`. 150° gives a narrow foot; **130–140° is much
  more stable** and also widens the body where the cavity floor sits.

**The spherical rim is almost always the binding wall constraint.** A sphere tall enough to
cradle a 13 cm glass is inherently narrow at the height of the glass mouth. The fix is a flare
term with a **positive baseline**, not just lobes:

```
+ (c0 + c1*max(0, cos(N*theta))) * exp(-pow(phi - PT, 2) * W)
```

`c0` flares the whole rim outward (buys wall), `c1` adds petals on top. Centre `PT` at
`sphTopCut` so the feature crests *at* the rim instead of being cut away.

---

## 6. Acceptance thresholds

Measure all of these before packaging. Report them.

| Check | Target | Notes |
|---|---|---|
| Minimum wall around the bore | **≥ 6 mm**, ideally 8 mm | Below 5 mm is fragile in a solid body |
| Cavity roundness after distortion | **0.0000 mm** deviation | Measure with `applyDistortionPoint` |
| Surface past 45° overhang | **< 1 %**, 0 % preferred | Below ~2 % prints with minor roughness |
| Surface past 60° overhang | **< 0.5 %** | |
| Boundary edges `B` | **0** on every body | See §7 — the UI lies about this |
| Non-manifold edges `N` | **0** | |
| All four colour states | each **> 2 %** | See §8 |
| Base sits on Z = 0 | yes | Exporter applies printer-flat orientation |

Reduce relief depth or soften transition sharpness to buy overhang; raise `bottomThickness` or
widen the body to buy wall.

---

## 7. Traps in the app

### "manifold check passed" is not a manifold check

`exportMultiPart3MF` only aborts when **`blockingIssues.length > 50`** (L7381), and the status
string prints "manifold check passed" whenever the core edge-case flag is false. A model with
6 boundary edges on the core and 12 on the overlap exported with a green light this session.

**Check the validations directly:**

```js
const parts = memoizedMeshBuild(buildMultipartMeshes, getConfig());
parts.coreValidation.boundaryEdges;                       // must be 0
parts.surfaceGroups.map(p => p.mergedValidation.boundaryEdges);   // all must be 0
```

The preview status line does surface it as `Core B:6 | Overlap B:12` — read it, don't skim it.

**Cause and fix:** holes come from sliver-thin mask regions, not from undersampling. Thickening
the contour mask from `cos(30·H) − 0.75` to `− 0.65` took every count to zero. Raising resolution
from 280×380 to 320×420 made it **worse**, which is how you tell the two apart.

### `smoothPatternEdges` round-trip (fixed)

`getCurrentDesignerConfig` used to omit `patterns.smoothPatternEdges` while `applyAIJson` read
it, so every saved design silently reloaded with stepped edges and rebuilt to different
geometry. Fixed at L2591. **Any JSON written by hand must still include the field** — the loader
defaults it to false.

### Export filename

`exportMultiPart3MF` writes `<Name>_Pot_multipart.3mf` (`buildExportStemForKind`, L4890).
Rename to `<Name>.3mf` when packaging.

---

## 8. Pattern masks

Four colour states come from two masks: neither / A only / B only / both. **A mask pair where
one contains the other silently wastes a colour.** The reviewed design had Pattern A entirely
inside Pattern B — `patternColor1` rendered **nowhere**, and the status line showed
`Pattern B (1), Overlap (14)` with no Pattern A body at all.

**Always measure coverage numerically before rendering:**

```js
// sample the real phi/v sweep, count the four states, require each > ~2%
```

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

---

## 9. Equation cookbook

### Seam safety

Any `theta` coefficient must be an **integer**, or the expression must be built from
`cos(theta)` / `sin(theta)`. `sin(1.5*theta)` tears at the seam.

### Gyroid, spherical

`sin(X)cos(Y) + sin(Y)cos(Z) + sin(Z)cos(X)` evaluated at the surface direction:

```
X = Ah*sin(phi)*cos(theta)    Y = Av*cos(phi)    Z = Ah*sin(phi)*sin(theta)
```

`Ah = Av` is a true isotropic gyroid. **`Av < Ah` stretches cells vertically**, which both suits
a vase and cuts overhang — 15/9 dropped it from 3.2 % to 1.9 % versus 15/15.

### Gyroid, cylindrical

```
X = A*cos(theta)    Y = A*sin(theta)    Z = B*v
```

Much easier to tune: **`A` is directly the cell count around the circumference**, `B/(2π)` the
number of vertical periods. `A = 10, B = 13` on a 17 cm column reads well.

### Relief shaping

`tanh(k·G)` gives plateaus separated by cliffs; **`k` controls the cliff steepness, and that is
what drives overhang** — not the depth alone. Fade relief out at the foot with
`* smoothstep(0.02, 0.25, v)` for a clean printable base while the colour still runs to the
bottom.

### Noise terrain / "islands"

```
H       = fbm(theta, v, 1.2, 2.2, 4, 17)      // range ≈ [−0.8, 0.8], mean ≈ 0
land    = H − 0.12                             // sea level; 0.12 → ~30 % land
contour = cos(30*H) − 0.65                     // contour lines at even elevation intervals
texture = 0.68*tanh(3.0*(H − 0.12)) + 0.38*H   // shoreline cliff + continuous elevation
```

`st` sets horizontal feature count, `sv` vertical. Because `cos(k·H)` is a function of elevation
alone, bands tighten on slopes and spread on flats — that is what makes it read as a chart.
All noise is seeded and deterministic, so exports are reproducible.

**Do not hard-terrace elevation.** On a vase, elevation maps to *radius*, so every uphill step
becomes an outward shelf — a 90° overhang.

### Vertical warp

`modifier.equationV` is dangerous on any silhouette with a localised flare: it drags the flare's
Gaussian around in `v`. One trial widened the body from 13.4 to 16.8 cm and collapsed the
minimum wall to **0.3 mm**. Leave it `""` unless the silhouette is warp-insensitive.

---

## 10. Palettes already used

Prefer exact Bambu Lab PLA Basic hexes (see `PLA_Colors.txt`). Pick a combination not already
on this list so the family stays varied.

| Design | base | pattern A | pattern B | overlap |
|---|---|---|---|---|
| Verdant Spiral Bloom | `#482960` Indigo Purple | `#00AE42` Bambu Green | `#EC008C` Magenta | `#FEC600` Sunflower Yellow |
| Crown Splash Ovoid | `#545454` Dark Gray | `#00AE42` Bambu Green | `#BECF00` Bright Green | `#5E43B7` Purple |
| Gyroid Magma Flare | `#0A2989` Blue | `#00B1B7` Turquoise | `#FF6A13` Orange | `#FEC600` Sunflower Yellow |
| Gyroid Ember Column | `#000000` Black | `#E4BD68` Gold | `#9D2235` Maroon Red | `#FF9016` Pumpkin Orange |
| Archipelago Contour Vase | `#0056B8` Cobalt Blue | `#F7E6DE` Beige | `#00B1B7` Turquoise | `#9D432C` Brown |

Remember which state each colour lands on: **base fills the recesses, pattern A the raised
plateaus.** Dark base + light plateau reads as carved depth; the reverse looks flat.

---

## 11. Packaging

```
3dModels/Vases/<Design Name With Spaces>/
    Design_Name_With_Underscores.3mf     (renamed from *_Pot_multipart.3mf)
    Design_Name_With_Underscores.json
    Design_Name_With_Underscores.png
```

**Always round-trip verify before calling it done:** reload the delivered JSON with
`applyAIJson()`, re-export, and compare the `3D/3dmodel.model` payload hash. Zip timestamps
differ between runs, so hash the inner XML, not the `.3mf` file.

```python
hashlib.sha256(zipfile.ZipFile(p).read('3D/3dmodel.model')).hexdigest()
```

Also confirm from the 3MF itself: 4 objects + assembly, the 4 expected colours in the
colorgroup, `unit="millimeter"`, and `zmin == 0`.

---

## 12. Reference designs

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
