# Woven Designer Agent

Operational guide for producing **woven / knotted planters** with `EquationDrivenWovenPots.html`.

It is the companion to `POT_DESIGNER_AGENT.md` and `VASE_DESIGNER_AGENT.md`. The woven app is a
different engine (a swept tube built with exact CSG, not a body of revolution), so most of the
Pot Designer's geometry notes do **not** carry over — but the working method does: drive the app
headlessly, measure with the app's own functions, and verify the exported file rather than the
status line. What follows is what was learned building **Cinquefoil Wicker Planter**
(2026-09-18), the first design in `3dModels/Woven`.

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
  texture does **not** thin the wall (the opposite of Pot Designer §1). The cavity gets the relief
  too.
- **Pattern depth** is clamped to `min(depthMm, wall − 0.2 mm, 0.45 · profileMax)` (L1883).
- **Saucer.** `buildPlateMesh` traces the outer silhouette at `zLo`, offsets by `offsetCm`, lofts a
  dish. It sits under the **foot**, not the belly: Cinquefoil's saucer is 16.0 × 15.8 cm under a
  17.5 × 18.1 cm pot. That is expected.

---

## 2. Harness

Same idea as the vase guide §2, with these differences:

- **One download sink.** Every exporter calls `download(content, name)` (L3261). Override
  `window.download` to POST the blob to a local save server.
- **Load without building:** stub `window.updatePreview`, put the JSON in `#designJsonInput`, call
  `applyDesignJson()`. **Build synchronously:** `runPreview()`. Get geometry without touching the
  scene: `buildMesh(readCfg(), 1.0)` → `geo` plus `geo.userData.patternParts / plateParts`.
- **The browser JS tool times out at ~45 s** and a coloured build at working resolution takes
  40–85 s. While a build runs the page's event loop is blocked, so an awaiting call cannot even
  poll. Start the work in `setTimeout`, return immediately, and watch the save folder from the
  shell (a Monitor `until [ -f file ]` loop). A Bambu export takes ~110 s.
- **WASM memory runs out.** After several 2 M-triangle builds in one page, a 1750 × 160 build
  failed with `Build failed: table index is out of bounds` (Manifold out of memory). **Reload the
  page before every big build or export.** The same 1500 × 140 build that is fine in a fresh page
  may fail in a tired one.
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
  (the coincident-boundary trap, Pot guide §5.5).
- **Diamond cells:** `K ≈ N·len / (2π·r_tube)` gives 45° strands. Cinquefoil: `len` = 148.2 cm,
  `r` = 2.6 → `N = 10, K = 90` (8/72 read bolder and coarser). `c = −0.4` gives strands ~7 mm wide
  with ~4.5 mm diamond gaps; `L = 0.5`.
- **Resolution:** ≥ ~14 samples per theta period and ~16 per `u` period — 1500 × 140 for N = 10.
  1000 × 96 for N = 8 read lumpy.
- **Relief:** intensity 0.11 cm (1.1 mm cords, 1.65 mm on top at crossings). The cord edges are
  what add overhang (§7).
- **Bands.** Gate B, and fade the texture, in **world `z`** (§4): a plain foot band and a rim
  "binding" in the A colour. `g = 7` (per cm, on the un-normalised `max(cos) + 0.4`) keeps the gate
  steep compared with the strand field, so the band edge is smooth (Pot guide §5.1). Get `zLo` /
  `zHi` from `buildRings(readCfg())` with the pot settings; the faded texture does not change them
  because the extremes lie inside the fade.

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
| Printed surface past 60° | **< 0.5 %** | User's printer limit; bridged spans (tube ceilings, arches over gaps) are fine. 45° is report-only |
| Boundary / non-manifold edges | **0 / 0** on every body in the exported 3MF | Manifold output, but parse the file anyway |
| Skin colour states | each **> 10 %** of the skin | Only three reach the skin (§5) |
| Pattern B / overlap bodies | start **above the bed** | A-colour foot band |
| Saucer | uncoloured unless the masks are designed for it (§5) | |
| Drain | present | `drainHoleDiameter` > 0 and a floor region under it |
| JSON round trip | reloading the JSON and re-exporting gives identical `3D/Objects/object_*.model` hashes | Root `3dmodel.model` carries the date — hash the object files |
| JSON idempotence | `getCurrentWovenPotConfig()` after loading the JSON equals the file | |

The Bambu Studio command line cannot slice the app's export (partial project config — it
segfaults on this install). Open it in the GUI to slice.

---

## 9. Packaging into `3dModels/Woven`

```
3dModels/Woven/<Design Name With Spaces>/
    Design_Name.3mf     (exportBambuStudio3MF: pot on plate 1, saucer on plate 2, H2C, PLA Basic)
    Design_Name.json    (downloadCurrentSettingsJson)
    Design_Name.png     (render: front + back side by side)
```

Tell the user the image is a render. Re-saving in Bambu Studio adds plate thumbnails.

---

## 10. Reference designs

| Design | Path | Pot W × D × H | Saucer | Wall / floor | > 60° (outer / cavity) | Skin coverage | Pot / saucer (100 % solid) | Mesh | Build / export |
|---|---|---|---|---|---|---|---|---|---|
| Cinquefoil Wicker Planter | Torus (2,5), d 5.1, z 5.1, amp 4.0, taper −0.12, tube 2.6 | 17.5 × 18.1 × 12.3 cm | 16.0 × 15.8 × 1.5 cm | 3.5 / 4.5 mm | 0.48 % (0.20 / 0.28) | teal 40 %, orange 40 %, navy 20 % | 486 g / 89 g | 1500 × 140 | 83–93 s / 110 s, 37.5 MB |

Cinquefoil verification: every body 0 boundary / 0 non-manifold edges in the exported 3MF;
2,777,052 preview triangles on every rebuild; reloading the JSON in a fresh page and re-exporting
gave identical SHA-256 for `3dmodel.model`, both object files and both configs; the JSON is
idempotent through `getCurrentWovenPotConfig()`.

Palette (Bambu PLA Basic): base `#5E43B7` Purple (interior, rim, saucer), A `#0A2989` Blue (gaps,
foot band, rim binding), B `#FF9016` Pumpkin Orange (strand family 2), overlap `#00B1B7`
Turquoise (strand family 1).

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
runAsync(async () => { runPreview(); await snap('front.png', { az: 35, el: 18 }); });
runAsync(() => exportBambuStudio3MF());
```

`snap` renders `scene` with its own `THREE.WebGLRenderer({ preserveDrawingBuffer: true })` and a
`PerspectiveCamera` placed on the bounding sphere of `currentMeshes`, then posts
`canvas.toBlob()` to `/__save/`. Trim the flat `#fafafa` background with PIL before packaging.
