# Equation-Driven Bowls / Lamp — Review & Implementation Plan

Target file: `EquationDrivenBowlsOptimized.html` (~2,930 lines, single-file app).
Reference implementation: `EquationDrivenPotDesignerOptimized.html` — the pot designer already received the
expression compiler, numeric-key mesh hygiene, progressive preview, noise helpers, and printability readouts.
**Most of Phase A below is a transplant from that file, not new engineering.** Copy the named functions, then
adapt the thin integration layer around them.

Implementation notes for the executing session:
- Make a git checkpoint commit before starting (git lives at
  `%LOCALAPPDATA%\GitHubDesktop\app-*\resources\app\git\cmd\git.exe` — not on PATH).
- No browser/node tooling is available in this environment. Verify statically after every phase:
  brace/paren balance over the `<script>` block, duplicate `const`/`let`/`function` declaration scan,
  and a whitelist cross-check of every preset equation (the pot session's method; see the project memory
  `session-environment-notes`). Beware the Read-tool artifact that displays `/` as `\` — confirm with Grep
  before "fixing" any suspicious backslash.

---

## 1. Review — current state

The bowls app is **further along** than the pot designer was before its optimization pass. Already present
and good: 23 openwork strut styles (including Gray–Scott reaction-diffusion, Game of Life, gyroid/Schwarz P/D
TPMS, quasicrystal, maze, Truchet), a printability flood-fill that removes disconnected openwork islands,
lamp mode (base cord hole), a solid-liner diffuser wall with transparent preview, a ring stand exported as a
separate body, and full design-JSON round-trip. The mesh hygiene chain (weld → orient by signed volume →
manifold validation) is the same proven design as the pot's.

**Findings, ranked by impact:**

1. **Raw `eval()` per sample** — `evalForm` (line ~1228) and `evalMask` (~1236) are the pot designer's
   pre-optimization evaluators. At the default 200×300 resolution one preview evaluates the form equation
   ~60k times (each `eval` re-parsing the string), plus 2 mask evals per wall cell when masks are non-trivial.
   Same injection exposure through loaded design JSON. The compiled-expression fix is already written in the
   pot file.
2. **Voronoi is the default style and is O(seeds) per query, twice.** `buildPattern`'s voronoi closure scans
   all ~160 seeds for nearest, then scans **again** for the edge distance — ~19M distance ops per preview at
   default resolution. Since seeds come from a jittered grid (jitter ≤ 0.5 cell), the nearest seeds are always
   within ±2 grid cells of the query — an exact, simple neighborhood lookup. `phyllotaxis` has the same flaw
   (linear scan over up to 2,000 seeds per query) and the same fix: seeds are ordered in `s`, so only a small
   index window around the query's band position can contain a hole.
3. **String-keyed hot maps** — `makePool.vid` (per-vertex string key at build time), `cleanupMesh` welding,
   `orientMeshConsistently`/`validateMesh` edge maps: all the pot's pre-fix versions.
4. **No draft preview, no build reuse** — 30 ms debounce, then a full 200×300 rebuild on the main thread per
   keystroke; `exportSTL`/`export3MF` rebuild from scratch even when nothing changed since the preview.
5. **Silent equation failure** — a typo renders a plain bowl (`catch → R`) with no message; masks silently
   return −1. The pot's red-outline + status-message pattern applies directly.
6. **Missing math** — no `atan2/sinh/cosh/tanh/hypot` aliases and none of the noise family
   (`cnoise/fbm/ridged/worley/phyllo`), so the pot's newer mask presets (Marble Veins, Voronoi Pebbles, …)
   cannot run here yet.
7. **Bug: stale panel list in `applyDesignConfig`** (~line 2797). Its hard-coded settings-panel array is
   missing `schwarzp, schwarzd, honeycomb, trabecular, truchet, quasicrystal, maze, scales, star, greekkey`
   (all present in `onPatternStyleChange` ~line 2952). Loading a design that uses one of those styles hides
   its settings panel. Fix: extract ONE shared `PATTERN_PANEL_IDS` const used by both.
8. Minor: DoubleSide everywhere despite consistent orientation; three.js r128 CDN pin (offline fragility);
   `signedVolume` already computed by `validateMesh` but never surfaced as a material estimate.

---

## 2. Phase A — Port the pot designer's optimization layer

Copy from `EquationDrivenPotDesignerOptimized.html`, adapting names where noted.

### A1. Expression compiler
Port the whole block: `EXPR_MATH_NAMES`/`EXPR_MATH_VALUES`, `validateExprSource` (+ forbidden-syntax regex),
`exprCache`, `getCompiledExpr` (with the `.bind()` trick), `compileExpr`.
- **Form scope** = `['theta','z','phi','v','R']` — used by `evalForm`.
- **Mask scope** = form scope + the derived names `evalMask` already exposes:
  `radiusDev, texPosNorm, texNorm, radiusNorm, outerDeviation, textureFill` (keep computing them exactly as
  the current `evalMask` does from `formR`; pass them as arguments to the compiled function).
- Rewire `evalForm`/`evalMask` to compiled lookups with identical fallback semantics (R / −1).
- Also port the alias block (`atan2, sinh, cosh, tanh, hypot`) and the **entire noise-helper section**
  (`mulberry32` already exists here — dedupe, keep one; `getSimplexPerm`, `rawSimplex3`, `cnoise`, `fbm`,
  `ridged`, `worleyHashComponent`, `worley3`, `worley`, `phyllo`) and add all names to the whitelist.
- Error surfacing: port `.expr-error` CSS + `refreshExpressionCompileStatus` with specs for the three
  textareas (`equation`, `patternEquation1`, `patternEquation2`); call it inside `updatePreview` and show the
  first error via `setStatus(..., 'error')`.

### A2. Numeric keys / mesh hygiene
- `cleanupMesh`: port the spatial-hash welding (quantized triple + numeric hash + bucket verify), the
  `Int32Array` remap, and the numeric tri-dedup trie. **Keep the bowls extras**: `triangleColorIndices` AND
  `triLayer` arrays must survive the port (the pot version has no `triLayer`).
- `orientMeshConsistently` / `validateMesh`: `min*vertexCount+max` numeric edge keys (drop-in).
- `makePool.vid`: replace the string key with the same quantize-hash-bucket approach (Q=1e4 grid as today).

### A3. Pattern-query hot spots (bowls-specific, not in the pot)
- **Voronoi**: store seeds in their grid layout (`seedAt(cx, cy)` from the existing `cols/rows` loop, before
  jitter wrap). Query: derive the query's cell `(qx, qy)`, examine seeds in cells `qx±2, qy±2` (θ-wrapped in
  x, clamped in y) — exact because jitter ≤ 0.5 cell. Compute nearest + Voronoi edge distance from that ≤25-
  candidate set exactly as the current two loops do over all seeds.
- **Phyllotaxis**: hole `i` sits at `sv = bandS0 + bandH*(i+0.5)/N`. For a query at `s`, only indices within
  `ceil(holeR / (bandH/N)) + 1` of `((s−bandS0)/bandH)*N − 0.5` can contain it; loop that window only.
- Acceptance: default voronoi preview visually identical (same seeds, same jitter — do not touch the RNG call
  order) and noticeably faster; a quick way to confirm equivalence statically is that the seed-generation
  loop is untouched and only the query loop changed.

### A4. Responsiveness + reuse
- Port draft preview: `getInteractivePreviewConfig` clamping `resV ≤ 80`, `resT ≤ 120` during rapid input
  (bowls defaults are 200×300 — the draft matters more here than in the pot), `RAPID_INPUT_WINDOW_MS`/
  `FULL_RES_SETTLE_MS`, split `updatePreview` → `renderConfigToScene(cfg, isDraft)`, append " | draft preview"
  to the status line during the draft pass.
- Port `memoizedMeshBuild` (single-entry, `JSON.stringify(cfg)` key) and wrap the `buildMeshData` /
  `buildRingMeshData` calls in `updatePreview`, `exportSTL`, `export3MF`. Exports right after a preview then
  reuse the mesh.

### A5. Readouts (cheap wins)
- Material estimate: `validateMesh` already returns `signedVolume` (cm³). Status line gains
  `~X cm3 / ~Y g PLA` (ρ=1.24). For ring base add its volume too.
- Strut-width sanity: when the active style's `*Thickness` input (cm) is below 0.08 (≈2 perimeters of a
  0.4 mm nozzle), append a `warn` note — struts thinner than that tend to vanish in slicing. This is a pure
  UI check on cfg, no geometry sampling needed.
- Optional (port if time allows): the pot's Auto Resolution checkbox adapted to the single form equation.

---

## 3. Phase B — New openwork styles for the lamp project

These are new `buildPattern` branches + a settings panel each + entries in `patternStyle` select,
`styleNameMap`, `patternDescs`, `onPatternStyleChange`'s panel list, `resetParameters` defaults, and
`DESIGN_VALUE_IDS`. **Forgetting the last one silently breaks design-JSON round-trip — treat that list as the
save-file contract.** All randomness must go through `mulberry32(seed)`.

Light is the design driver: an openwork lamp projects its pattern onto walls, so styles are chosen for the
shadows they cast, not just the surface look.

### B1. `worleycrackle` — Worley Crackle (stone-crack web)
Infinite, non-repeating crack web — the organic upgrade of the current seeded voronoi.
Strut where `F2 − F1 < half` using hashed per-cell feature points (no seed array): reuse
`worleyHashComponent` on integer cell coords of the unrolled `(u, s)` plane (θ-wrapped in u), examining the
3×3 cell neighborhood for the two nearest feature distances. Params: `crackleDensity` (cells around),
`crackleThickness` (cm), `crackleSeed`.

### B2. `caustic` — Caustic Web (light-through-water)
Strut where `abs(fbm(theta, s/bandH·k, …)) < level` — a flowing organic web whose shadows look like pool
caustics. Use the ported `fbm` on the cylinder embedding (seam-free by construction). Params: `causticScale`
(θ×v frequency), `causticLevel` (web thickness, ~0.06–0.15), `causticOctaves` (2–4), `causticSeed`.

### B3. `slits` — Ray Slits / Louvers
Classic lampshade: arrays of capsule-shaped slots that project crisp light rays. A slot is
`distance to a tilted segment in (u,s) cm-space < slitWidth/2` → **hole** (return false inside). Segments:
`slitCount` columns × `slitRows` staggered rows; each segment centered in its cell, length
`slitLength × rowHeight`, tilted `slitTilt` degrees from vertical (`segDist` already exists at line ~927).
Params: `slitCount`, `slitRows`, `slitWidth` (mm→cm /10 like the others), `slitLength` (0–1), `slitTilt` (°).

### B4. `halftone` — Halftone Glow (equation-driven light gradient) — **the signature feature**
Staggered hex grid of round holes (reuse the honeycomb center layout) whose **radius is driven by the
Pattern A mask equation** sampled at each hole center: bright where the mask is high, dark where low —
turning the existing mask system into a light-intensity image. Implementation: at closure-build time,
precompute each cell center's mask value with the compiled `evalMask` (map `s → v` via the band), normalize
per-build to [0,1] (`tanh` soften optional), hole radius = `holeMin + (holeMax − holeMin) × value`; query =
inside-nearest-hole test over the 3×3 neighborhood. With Pattern A = `-1` fall back to constant mid radius.
Params: `htDensity`, `htMinHole` (mm), `htMaxHole` (mm). Suggest presets to pair: any of the ported noise
masks, `sin(pi*v)` (bright equator), or `exp(-(pow(theta - pi,2) + 8*pow(v-0.55,2))*1.6)` (glow spot).
Safety: clamp max radius to 0.45 × cell spacing so webs between holes never pinch below one extrusion width.

### B5. `constellation` — Constellation (star map with connecting lines)
Seeded scatter of star holes in 2–3 sizes plus thin slot "chords" joining each star to its 1–2 nearest
neighbors — a night-sky pendant. Build time: place `starCount` jittered-grid points (θ-wrapped), assign radii
by rank (`rng()` thresholds: ~15% large, 35% medium, 50% small), connect each to its nearest neighbor (+2nd
with probability 0.4) storing segments once (dedupe `i<j`); query = inside any star circle OR within
`lineWidth/2` of any segment (θ-wrapped u distance) → hole. Keep `starCount ≤ ~120` so the O(points+segments)
query stays cheap, or bucket like B1. Params: `constCount`, `constMaxStar` (mm), `constLineW` (mm), `constSeed`.

### Tier 2 — additional styles (implement after B1–B5 land and their integration pattern is proven)

Tier 2 reuses machinery Tier 1 already builds: bucketed segment/point queries (B5), hashed cell features
(B1), and the compiled mask sampler (B4). Every style below states which of those it leans on.

### B7. `kumiko` — Kumiko Asanoha (Japanese hemp-leaf lattice)
The traditional shoji-lampshade craft, and the best "structured elegance" option in the set. An equilateral
triangular lattice with spokes from each triangle's centroid to its three corners. Implementation is fully
analytic (no arrays): three line families in unrolled `(u,s)` space — horizontals at `rowH = (circ/cols)·√3/2`
spacing plus the two ±60° diagonal families, each distance computed like the existing `star` style's
`lineD`/`diagD` helpers with slope √3; then locate the containing half-triangle from folded cell coordinates
and add `segDist` to its three centroid spokes. `cols` must be an integer (it already is — it's the density
input) so the pattern wraps seamlessly. Params: `kumikoDensity` (triangle columns around), `kumikoThickness`
(mm). Light note: casts the classic six-pointed asanoha star shadows; recommend liner OFF (crisp shadows).

### B8. `veins` — Branching Veins (leaf-skeleton growth)
Organic branching struts grown upward from the solid base — a leaf-skeleton or lightning-tree lamp.
Build time: start `veinRoots` tips evenly spaced (θ-jittered) on the band's bottom edge; iteratively extend
each tip by a fixed `ds` step with seeded θ-wander; at each step a tip splits with probability
`veinSplitProb` (cap total segments ≈ 3,000; kill tips that leave the band top). Record segments with a
per-generation width taper `w = veinThickness · 0.82^generation` (floor at 0.08 cm — printable). Query:
bucketed `segDist` (grid cell = max segment length, θ-wrapped) against per-segment half-widths.
Params: `veinRoots`, `veinSplitProb`, `veinWander`, `veinThickness` (mm, trunk), `veinSeed`.
Structural bonus: every strut is connected to the base *by construction*, so the island flood-fill should
remove zero cells — a cheap self-check that the growth code is right.

### B9. `foam` — Soap Foam (merged bubble holes)
Seeded disks punched as holes; overlapping disks merge into organic multi-lobed openings like soap foam.
Build time: place `foamCount` candidate centers on a jittered grid (θ-wrapped); radius per disk
`rMin + (rMax − rMin)·pow(rng(), 1.5)` (biased small); **reject** any candidate whose gap to an already
accepted disk is below `foamWeb` (guarantees every web strut ≥ the printable minimum — no post-hoc pinch
checks needed). Query: bucketed signed distance `sd = min_i(dist_i − r_i)`; material where `sd > 0`.
Params: `foamCount`, `foamMinHole`/`foamMaxHole` (mm), `foamWeb` (mm), `foamSeed`.

### B10. `ripples` — Ripple Interference (point-source moiré)
Two to four point sources emit circular waves; material follows the interference field's nodal web —
concentric-ring moiré that reads beautifully in cast light. Purely analytic, zero precomputation:
`W = Σ_k sin(2π·d_k/λ)` with `d_k` = θ-wrapped distance in `(u,s)` cm-space to pole `k` (poles seeded at
jittered positions across the band); material where `|W| < rippleWidth · K`. The nodal bands automatically
connect to base and rim wherever they cross the band edges; the island flood-fill catches the rare closed
loop that doesn't. Params: `rippleSources` (2–4), `rippleWavelength` (cm), `rippleWidth` (0.05–0.4),
`rippleSeed`.

### B11. `spirograph` — Spirograph Band (cycloid loops)
A single looping cycloidal curve wound around the band — spirograph rosettes as one continuous ribbon strut.
Parametric curve in `(u,s)`: `u(t) = circ·(k·t/(2π)) + b·sin(m·t)`, `s(t) = mid + c·cos(n·t)` for
`t ∈ [0, 2π)`, with integer wrap count `k` so it closes seamlessly; loops appear when `b·m` exceeds the
linear advance. Build time: sample ~4,000 points into a polyline, bucket segments; query = bucketed
`segDist < spiroThickness/2`. Params: `spiroWraps` (k), `spiroLobes` (m; set n = m unless a second input is
wanted), `spiroLoop` (b, cm), `spiroHeight` (c, 0–1 of band), `spiroThickness` (mm).
Note: a lone ribbon that never touches base/rim would be entirely removed by the flood-fill — default
`spiroHeight` 0.9 so the loops graze both solid bands.

### B12. `gradientcells` — Gradient Cells (mask-driven Voronoi density)
The halftone idea applied to cell *size*: Voronoi web whose cell density follows the Pattern A mask —
small dense cells (dim) where the mask is high, large open cells (bright) where it's low. Build time:
rejection-sample seeds — draw ~4× `gcCount` jittered-grid candidates, keep each with probability
`0.15 + 0.85·pow(maskNorm, gcContrast)` (mask sampled via the compiled `evalMask`, normalized per-build)
until `gcCount` kept or candidates exhausted; then run the same bucketed edge-distance query as B1/A3.
With Pattern A = `-1`, falls back to uniform density (plain crackle). Params: `gcCount`, `gcThickness` (mm),
`gcContrast` (0.5–3), `gcSeed`. Pairs with the same mask presets as B4 — one mask can drive matching
halftone and cell-density designs.

### B13. Stretch styles (only if the above land cleanly — one-line specs)
- `fractalcurve` — panelized Hilbert corridor: P panels around the body, each filled by an order-3/4 Hilbert
  polyline scaled to the panel (endpoints at the panel's base edge so every corridor roots to the solid
  base); bucketed segDist. A `dragon` variant via L-system iteration is decorative but relies on the
  flood-fill for support.
- `web` — spiderweb: radial spokes + sagging catenary threads between adjacent spokes
  (`cosh` tie-in; per-row, per-pair analytic sag curve, distance by coarse polyline).
- `girih` — Islamic strapwork from a periodic decagon/bowtie template tile; high effort, keep last.

### B14. Port the pot's mask presets (colors, not geometry)
Once A1 lands, append to `patternPresets`: Marble Veins, Voronoi Pebbles, Leopard Rosettes, Crackle Mortar,
Lightning Filaments, Phyllotaxis Dot Grid, Shoreline Split, Noise Islands, Sunburst Medallion, Halo Ring
(copy the `eq` strings verbatim from the pot file's `patternPresets`; they only use whitelisted names and are
seam-safe). They also become the natural drivers for B4's halftone and B12's gradient cells.

---

## 4. Phase C — Lithophane Glow Band (wall-thickness light modulation)

The other half of lamp light-play: instead of holes, vary **wall thickness** so light glows through thin
regions (lithophane principle: thin = bright). Only meaningful for `style: solid` (or solid + liner).

- New controls (own collapsible section, hidden unless style = solid): checkbox `glowEnabled`; textarea
  `glowEquation` `L(θ, z|φ, v)` (compiled via A1, form scope); `glowMin` / `glowMax` wall thickness (mm,
  defaults 0.6 / 2.4); the band limits reuse Solid Base / Solid Rim.
- Implementation in `buildShell`: when active, for rows inside the band modulate the **inner** grid only:
  `ri = ro − clamp(glowMax − (glowMax − glowMin) · Lnorm, glowMin, glowMax)/10` where `Lnorm` is the
  compiled `L` value normalized per-build to [0,1] over the sampled band (two passes: sample+min/max, then
  build). Outer surface stays clean; all light shaping happens on the cavity side. `I2`/liner logic is
  bypassed (glow implies solid style).
- Status line: append `glow ON | wall 0.6-2.4mm`; print note in the section's desc-text: white/natural
  filament, 100% infill or spiral-ready solid walls, LED bulbs only (no heat).
- Add `glowEnabled` to `DESIGN_CHECK_IDS`; `glowEquation`, `glowMin`, `glowMax` to `DESIGN_VALUE_IDS`.
- Preset pack for `glowEquation` (small select like the profile presets): `0.5 + 0.5*cnoise(theta, v, 3, 4, 11)`
  (clouds), `0.5 + 0.5*sin(6*theta)*sin(pi*v)` (lantern panels), `fract(theta*3/(2*pi))`→ use
  `0.5+0.5*cos(3*theta)` instead (smooth), `1 - worley(theta, v, 8, 8, 5)` (glowing cells),
  `0.5 + 0.5*sin(3*theta + 5*fbm(theta, v, 3, 4, 4, 9))` (marble glow).

---

## 5. Phase D — Lamp hardware niceties (small, high-value)

- **Pendant rim holes**: checkbox + `hangCount` (default 3) + `hangHole` (mm) + `hangInset` (cm below rim).
  Implemented as forced hole cells in the occupancy pass (like lamp mode's base hole but through the wall):
  circular holes at `v` near the rim band, equally spaced in θ, punched through `occ` before meshing (and
  exempt from the island flood-fill seeds). For solid style, punch through the shell quads by skipping cells
  inside the hole circles — the per-cell occupancy meshing already closes the cut faces.
- **Fix the `applyDesignConfig` stale panel list** (finding 7): single shared `PATTERN_PANEL_IDS` const.
- Bump `applyDesignConfig`'s tolerance for new fields: it already ignores unknown ids — new controls just
  need to be in the two arrays.

---

## 6. Suggested execution order & acceptance

| Step | Contents | Acceptance (static + manual once a browser is available) |
|---|---|---|
| 1 | A1 compiler + aliases + noise + error surfacing | no `eval(` left outside comments; whitelist covers every preset eq in the file; typo in form equation shows red outline note |
| 2 | A2 numeric keys, A3 voronoi/phyllo neighborhoods | balance + dupe-scan clean; seed RNG call order untouched |
| 3 | A4 draft preview + memoized builds, A5 readouts | export after preview reuses build (log it); status shows cm³/g |
| 4 | Fix stale panel list (D, finding 7) | one shared const, both call sites use it |
| 5 | B1–B5 (Tier 1 styles) + B14 mask port | every new style: manifold B:0 N:0 at defaults, entry in ALL six integration points (select, panel, descs, styleNameMap, resetParameters, DESIGN_VALUE_IDS); islands flood-fill still runs on them |
| 5b | B7–B12 (Tier 2 styles), in listed order | same six-point integration + manifold criteria as step 5; B8 additionally: island flood-fill removes 0 cells at defaults (growth is base-rooted by construction) |
| 6 | C lithophane glow | solid bowl w/ glow: manifold clean; wall never < glowMin anywhere (sampled check) |
| 7 | D pendant holes | holes punched, mesh manifold, holes survive island removal |

Per-style manifold spot-check matrix (after 5/5b): cylindrical + spherical × {worleycrackle, caustic, slits,
halftone (with and without mask), constellation, kumiko, veins, foam, ripples, spirograph, gradientcells
(with and without mask)} × {liner on, liner off} × lamp mode on.

## 7. Risks & conventions

- **`DESIGN_VALUE_IDS` / `DESIGN_CHECK_IDS` are the save-file contract** — every new input goes in, and old
  design JSONs must still load (new fields default from the HTML `value=` attributes when absent).
- Determinism: all new styles must be seed-reproducible (`mulberry32` only); same JSON → identical STL bytes.
- The strut closure signature is `(theta, s, x, y, z)` — world coords are only passed for TPMS-style volume
  patterns; none of the new styles (B1–B12) need the world coords — `(theta, s)` only.
- Holes vs struts: `buildPattern` closures return **true = material**. B3/B4/B5/B9 are hole-based: return
  `!insideHole`. The island flood-fill then guarantees nothing floats; leave it enabled for all new styles.
- Solid liner interplay: hole-based styles look best with the liner ON (glow through the diffuser); keep the
  existing `linerDefaultStyles` mechanism and add `caustic`, `halftone`, `constellation`, `foam`,
  `ripples`, and `gradientcells` to it (`kumiko`, `veins`, `slits`, `spirograph` default liner-off: their
  appeal is the crisp cast shadow, which a diffuser softens away).
- Keep the app single-file; no new external dependencies.
