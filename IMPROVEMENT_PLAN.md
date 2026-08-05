# Equation-Driven Pots — Code Review & Implementation Plan

Target file: `EquationDrivenPotDesignerOptimized.html` (~5,040 lines, single-file app).
Prepared for implementation in phases. Each phase is self-contained and testable; do them in order — Phase 0 unlocks the perf headroom everything else depends on.

---

## 1. Code review — current state

**Architecture (as-is):**
- Single HTML file. Three.js r128 + OrbitControls + JSZip from CDN.
- Math pipeline per sample: base equation `r(θ,z/φ,v)` → texture displacement `T(...)·intensity` → modifier (θ-remap) → world-XYZ distortion field.
- Shell building: outer rows → Laplacian smoothing (`laplacianSmoothRows`) → uniform-wall inner rows via meridional normal offset (`buildUniformCylindricalInnerRows`) → 3-layer sample (outer / pattern-depth / inner).
- Dual-pattern coloring via cell occupancy grids (2 radial layers × resV × resT), connected-component split, per-state watertight meshes (`buildMultipartMeshes`).
- Mesh hygiene: weld (`cleanupMesh`), consistent orientation by signed volume (`orientMeshConsistently`), manifold validation (`validateMesh`). This part is genuinely solid.
- Export: binary STL (×10 cm→mm), multi-part 3MF with color groups.

**Main findings, ranked by impact:**

1. **`eval()` per sample point** (`secureEval` line ~4050, `evalDistortionExpr`, `evaluatePatternValue`). At default 120×180 resolution one preview run performs roughly 150k–300k `eval()` calls (base + texture per node, 4 evals per cell mid, 2 pattern evals per cell, modifier eval nested inside each field eval, 3 distortion evals per point × outer/inner). Each call re-parses the source string. This is the single biggest cost — compiling each expression once with `new Function` is a 1–2 order-of-magnitude win.
2. **Everything runs on the main thread** behind a 30 ms debounce. Typing in an equation box freezes the UI for the whole rebuild. No cancellation: a stale rebuild always completes.
3. **Duplicate pipelines**: `generateCylindrical`/`generateSpherical` (STL path) reimplement phases 1–7 of `buildCylindricalShell`/`buildSphericalShell` (preview path). Every export re-evaluates all fields from scratch.
4. **Wasted work in the STL path**: `generateCylindrical` calls `chooseColor` per outer node (2 pattern evals each) — STL discards colors entirely.
5. **String-keyed hot maps**: vertex welding (`cleanupMesh`), edge maps (`orientMeshConsistently`, `validateMesh`), occupancy component keys — all build template strings per lookup. Quantized-integer keys are much faster and GC-friendlier.
6. **Layering violation**: `cleanupMesh` calls `getConfig()` (DOM reads) deep inside the geometry pipeline to fetch the palette. Pass the palette in.
7. **Suspicious gate** in `exportMultiPart3MF`: `if (blockingIssues.length > 50)` — export is blocked only when there are more than *fifty* manifold problems. Looks like a debugging leftover for `> 0`. Confirm intent with the author before "fixing", but flag it.
8. **`secureEval` is not secure** — it's raw `eval`. Fine for a local tool, but the "AI Assistance" flow encourages pasting third-party JSON whose equation strings execute as arbitrary JS. The Phase 0 compiler with a token whitelist fixes speed *and* this injection vector at once.
9. **Silent per-sample fallback** (`catch → return R`) hides typos: a broken equation renders a plain cylinder with no error. Compile-time validation with a visible per-field error message is a big UX win.
10. **`side: THREE.DoubleSide` everywhere** despite meshes being consistently oriented — doubles fragment work; FrontSide should suffice after `orientMeshConsistently`.
11. **Pattern boundaries are cell-quantized** — color regions have staircase edges at pattern-grid resolution.
12. Missing convenience aliases in equation scope: `cosh`, `sinh`, `tanh`, `atan2`, `hypot` (all exist on `Math`).

---

## 2. Phase 0 — Expression compiler (foundation)

**Goal:** replace per-sample `eval` with compiled, cached functions. No behavior change other than speed and error reporting.

Tasks:
1. Add a module-level cache: `const exprCache = new Map(); // source string → compiled fn | Error`.
2. `compileExpr(src, argNames)`:
   - Whitelist-validate tokens first: allow numbers, operators, parens, commas, the known identifiers (`theta z phi v R x y z zs pi sin cos tan asin acos atan atan2 sinh cosh tanh pow min max abs exp sqrt log floor ceil round sign clamp fract smoothstep mod hypot` + Phase 3/4 helpers + pattern-scope helpers `texNorm texPosNorm radiusNorm radiusDev absRadiusDev localRadiusDev outerRadius baseFormRadius outerDeviation textureFill`). Reject anything else (identifiers like `window`, `document`, `fetch`, backticks, `=>`, `[`, `]`).
   - Build with `new Function(...argNames, '"use strict"; return (' + src + ');')`.
   - On compile error, store the Error and surface it (task 5).
3. Replace call sites: `secureEval`, `evalDistortionExpr`, `evaluatePatternValue` keep their signatures but look up compiled functions. Keep the same NaN/∞ → fallback semantics per call.
4. For `evaluatePatternValue`, hoist the per-call closure creation (`outerDeviation`, `textureFill`) out — pass them as arguments to the compiled function (they're part of `argNames`).
5. Error surfacing: when a field's expression fails to compile, outline the corresponding textarea in red and show the message in `#status` (kind `'error'`). A field that compiles but throws at runtime keeps the current silent-fallback behavior.
6. Skip color/pattern evaluation when the consumer discards it: `generateCylindrical`/`generateSpherical` get a `wantColors` flag, false from the STL path.
7. Pass the palette into `cleanupMesh` instead of calling `getConfig()` there.
8. Add `cosh, sinh, tanh, atan2, hypot` aliases next to the existing ones (line ~959) and to the compiler whitelist.

**Acceptance:** default pot preview ≥5× faster (measure with `performance.now()` around `buildMultipartMeshes`); a typo like `cos(6*theta` shows a visible error instead of a silent cylinder; STL/3MF outputs byte-identical geometry (colors aside) vs. before.

---

## 3. Phase 1 — Responsiveness & mesh-pipeline optimization

1. **Web Worker generation** (keep single-file: build the worker from a `Blob` URL wrapping the math + meshing functions, or reuse the same file via `new Worker(URL.createObjectURL(...))`).
   - Main thread sends the plain `cfg` object (it's already DOM-free after `getConfig`); worker returns `{positions: Float32Array, indices: Uint32Array, triangleColorIndices, validation}` per part with transferables.
   - Generation token: bump a counter per request; worker results carrying a stale token are dropped. UI stays live while generating; status shows "Generating…".
2. **Progressive preview:** while a field is being edited (input events < 300 ms apart), clamp to interactive resolution (e.g. `resV ≤ 64`, `resT ≤ 96`); when idle 300 ms, regenerate at full resolution. Exports always use full resolution.
3. **Numeric keys in hot paths:**
   - Welding: quantize to 1e-6 and key with `xi*73856093 ^ yi*19349663 ^ zi*83492791` into a `Map<number, number[]>` bucket (verify exact match within bucket), or pack quantized 21-bit coords into a single number when bounds allow.
   - Edge maps in `orientMeshConsistently`/`validateMesh`: key = `min*N + max` as a number (N = vertex count).
   - Occupancy component flood fill: index = `(k*resV + iv)*resT + it` into a `Uint8Array` visited buffer instead of `Set<string>`.
4. **Typed arrays in shell building:** replace `{x,y,z}` object grids in `buildCylindricalShell`/`buildLayeredSample` with flat `Float64Array` (3 floats per node). Lower priority than 1–3; do it only if profiling still shows GC pressure.
5. **Materials:** after consistent orientation, use `THREE.FrontSide`; keep DoubleSide only as a debug toggle.
6. **Field sample reuse:** cache the last `{configHash → sampled field grids}` so an export immediately after a preview doesn't re-evaluate everything (config hash = JSON of the equation strings + numeric params).

**Acceptance:** UI never freezes > 50 ms during editing at default resolution; dragging a number input feels live; export of a just-previewed design skips field re-evaluation (log it).

---

## 4. Phase 2 — Exotic math, zero infrastructure (preset pack)

These are pure additions to `libraries` / `texturePresets` / `patternPresets` / `modifierPresets` — paste-ready with the current evaluator. Tune amplitudes visually before committing; values below are sane starting points.

### New base scaffolds (cylindrical unless noted)

| Name | Equation | Notes |
|---|---|---|
| Superformula Hex Star | `R * 0.9 * pow(pow(abs(cos(1.5*theta)), 14) + pow(abs(sin(1.5*theta)), 14), -0.125)` | Gielis superformula, m=6, n1=8, n2=n3=14 |
| Superformula Starfish | `R * 0.65 * pow(pow(abs(cos(1.25*theta)), 7) + pow(abs(sin(1.25*theta)), 7), -0.5)` | m=5 closes because n2=n3 (cos↔sin swap invariant) |
| Superformula Morph | `R * ((1-v) * 0.9*pow(pow(abs(cos(1.5*theta)),14) + pow(abs(sin(1.5*theta)),14), -0.125) + v * 0.65*pow(pow(abs(cos(1.25*theta)),7) + pow(abs(sin(1.25*theta)),7), -0.5))` | hex base morphs to 5-star rim |
| Rose Curve (5-petal) | `R * (0.78 + 0.22 * abs(cos(2.5*theta)))` | k=5/2 rose; `abs` restores 2π periodicity |
| Catenary Waist | `R * (0.62 + 0.38 * (exp(2.4*(v-0.5)) + exp(-2.4*(v-0.5))) / (exp(1.2) + exp(-1.2)))` | catenoid-like minimal-surface profile; use `cosh` once aliased |
| Spherical Harmonic Y₃₂ (spherical) | `R * (1 + 0.25 * pow(sin(phi), 2) * cos(phi) * cos(2*theta))` | real spherical harmonic bump field |
| Spherical Harmonic Y₄₄ (spherical) | `R * (1 + 0.2 * pow(sin(phi), 4) * cos(4*theta))` | crown-heavy 4-fold harmonic |

### New textures

| Name | Equation | Notes |
|---|---|---|
| Gyroid Slice | `sin(6*theta)*cos(10*pi*v) + sin(10*pi*v)*cos(3*theta + 4*pi*v) + sin(3*theta + 4*pi*v)*cos(6*theta)` | TPMS gyroid section wrapped on the (θ,v) torus |
| Weierstrass Relief | `0.6*cos(3*theta + 2*pi*v) + 0.3*cos(9*theta - 4*pi*v) + 0.15*cos(27*theta + 8*pi*v) + 0.075*cos(81*theta - 16*pi*v)` | 4-octave a=½, b=3 fractal cascade |
| Chladni Plate | `atan(4*(sin(4*theta)*sin(6*pi*v) + sin(6*theta)*sin(4*pi*v)))` | standing-wave nodal pattern, atan-sharpened |
| Knot-Line Ribbons | `exp(-pow(abs(mod(3*theta - 4*pi*v + pi, 2*pi) - pi), 2) * 6)` | ridge along the (2,3) torus-knot line family |
| Loxodrome Ribbon (spherical) | `exp(-pow(abs(mod(theta - 3*log(tan(max(0.05, phi)/2)) + pi, 2*pi) - pi), 2) * 8)` | constant-bearing rhumb-line spiral on the sphere |

### New pattern masks

| Name | Equation | Notes |
|---|---|---|
| Chladni Windows | `sin(3*theta)*sin(5*pi*v) + sin(5*theta)*sin(3*pi*v)` | classic Chladni nodal split as a 2-color mask |
| Gyroid Mask | `sin(4*theta)*cos(8*pi*v) + sin(8*pi*v)*cos(2*theta + 2*pi*v) + sin(2*theta + 2*pi*v)*cos(4*theta) - 0.2` | organic interlocking regions |

### New modifiers

| Name | Equation | Notes |
|---|---|---|
| Möbius Squeeze | `2*atan(0.35*sin(theta) / (1 - 0.35*cos(theta)))` | conformal Möbius reparametrization of the circle — compresses features toward one side, strength 1.0 |
| Log-Spiral Pace | `0.6*log(0.25 + v)` | twist whose rate follows logarithmic spiral pacing (fast near base) |

**Acceptance:** every new preset renders manifold (B:0 N:0) at default resolution in both preview and 3MF export; each has a one-line `desc` in house style ("Demonstrates …" for basicEffect types).

---

## 5. Phase 3 — Helper-function math (new built-ins)

Adds deterministic, seam-free procedural functions to the equation scope (define once, add to compiler whitelist, document in the AI prompt file).

1. **Seeded simplex noise, cylinder-embedded** — seam-free in θ by construction:
   - `cnoise(theta, v, st, sv, seed)` → 3D simplex sampled at `(st·cos θ, st·sin θ, sv·v)`, range ≈ [-1,1].
   - `fbm(theta, v, st, sv, octaves, seed)` — standard 2·gain=0.5 lacunarity=2 cascade.
   - `ridged(theta, v, st, sv, octaves, seed)` — `1 - |fbm|` ridged multifractal.
   - Implementation: self-contained simplex-3D (~80 lines), permutation table from a mulberry32 PRNG seeded by `seed` (cache per seed).
2. **`worley(theta, v, st, sv, seed)`** — cellular F1 distance on the same cylinder embedding, normalized ~[0,1]. Crackle/leather/hammered surfaces.
3. **`phyllo(theta, v, n, size)`** — golden-angle phyllotaxis bump field: seeds at `θ_k = k·2.39996`, `v_k = k/n`; returns the max Gaussian bump over the few nearest k (solve k from v-band, check ±2 neighbors). Sunflower/pinecone stud fields.
4. Preset pack using them, e.g.:
   - Texture "Hammered Copper": `0.8 - 1.6*worley(theta, v, 9, 9, 7)`
   - Texture "Bark Ridges": `ridged(theta, v, 3, 14, 4, 2)`
   - Texture "Coral fBm Warp": `fbm(theta + 0.6*fbm(theta, v, 4, 6, 3, 5), v, 6, 9, 4, 1)` (domain-warped)
   - Texture "Sunflower Belt": `phyllo(theta, v, 240, 0.05) * exp(-pow(v-0.5,2)*8)`
   - Mask "Noise Islands": `cnoise(theta, v, 3, 4, 11) - 0.15`

**Guardrails:** helpers must be pure and deterministic (same seed → same mesh, always — exports must be reproducible). Keep per-call cost O(octaves); no allocation inside the sample loop.

**Acceptance:** same seed produces byte-identical STL across two runs; noise textures show no seam at θ=0; default-res preview stays under ~1.5× the Phase-1 generation time.

---

## 6. Phase 4 — Bigger features

### 4a. Reaction–diffusion field baker (Gray–Scott)
- New collapsible section "Computed Field". Controls: preset (Coral F=0.0545 k=0.062, Mitosis F=0.0367 k=0.0649, Worms F=0.078 k=0.061), grid (256×256 default, θ-periodic, v-clamped), steps (e.g. 5,000), seed, Bake button.
- Solver runs in the worker (few seconds); result stored as a Float32Array field, bilinearly sampled by a new scope function `field(theta, v)` usable in texture and mask equations (e.g. texture `1.5*(field(theta, v) - 0.35)`).
- Field is saved into the design JSON as base64 (or re-baked from seed+params on load — prefer re-bake, smaller files; solver must then be fully deterministic: fixed iteration order, no `Math.random` beyond the seeded PRNG).

### 4b. Pattern "cutout" mode (perforated lanterns)
- Add a per-pattern mode dropdown: `Color` (current) / `Cutout`.
- Cutout: cells matching the mask are removed from *both* core occupancy layers instead of being assigned a surface state. `buildOccupancyMesh` already emits interior walls at occupancy boundaries, so holes come out watertight for free.
- Safety rails: force-keep the bottom row + solid base cells (reuse `forceCoreBottomRow` / `inSolidBase` logic); warn if cutouts disconnect the shell into floating islands (reuse `splitOccupancyComponents` on the core — if >1 component, show `#generationNotice`).
- This turns the existing color machinery into a lattice/lantern generator — highest wow-per-effort feature in this plan.

### 4c. Printability & material readouts
- **Overhang heatmap**: toggle that vertex-colors faces by downward angle (green < 45°, yellow 45–60°, red > 60°, measured in printer orientation). Status line shows max overhang angle.
- **Material estimate**: `validateMesh` already computes `signedVolume` (cm³). Display "≈ X cm³ ≈ Y g PLA" (ρ=1.24 g/cm³) in the status bar. Nearly free.
- **Min-wall check**: sample outer↔inner distance across the grid; warn when below nozzle-safe threshold (e.g. 0.8 mm).

### 4d. Auto-resolution
- "Auto" checkbox next to Radial Nodes: with compiled expressions, sample `r(θ)` at 2,048 points on 3 rings (v = 0.25/0.5/0.75), compute max |Δr| per step, choose the smallest resT where chord error < 0.05 mm (clamped to [60, 720]); analogous scan in v for resV. Re-run on equation change only (cheap once compiled).

### 4e. Full (θ,v) modifiers
- Current modifier warps θ only (`getModifiedCoords`). Add optional second expression `Mv` warping v (clamped to [0,1], with z recomputed as `v·h` in cylindrical mode), enabling true conformal warps (log-spiral `w = log z`, Möbius on the annulus) and vertical feature migration. Default empty = current behavior; existing designs unaffected.

---

## 7. Phase 5 — Stretch / optional

- **Sub-cell pattern boundaries**: marching-squares the mask sign-change inside cells and split boundary cells' geometry, replacing staircase color edges with smooth curves. Significant meshing work — keep watertightness tests from `validateMesh` as the gate.
- **Quadric decimation on export** (optional toggle): regular grids over-tessellate flat regions; 30–60% triangle reduction at no visual cost.
- **Three.js modernization**: r128 → current module build via import map; or at minimum vendor the three files locally so the app works offline.
- **True 3D-normal shell offset**: `thetaNormalFlag` infrastructure already exists (currently `false`); revisit with the smoothing pipeline for accurate wall thickness on high-curvature lobes.
- Confirm intent of `blockingIssues.length > 50` in `exportMultiPart3MF` (§1 item 7) and tighten if it was a leftover.

---

## 8. Risks & conventions for the implementing session

- `eval` → `new Function` changes scope semantics: compiled functions no longer see page globals. That is *desired*, but every identifier presets use must be an explicit parameter — grep all preset equations for identifiers and cross-check the whitelist before switching over (the preset tables in §4 of the file are the test corpus).
- Keep the app single-file and dependency-free beyond the existing CDN scripts. The worker must be built from a Blob, not a separate file.
- Never regress mesh hygiene: after every phase, spot-check B:0 N:0 for: default pot, spherical pot, pot+plate, vase, a pattern-heavy design, and (after 4b) a cutout design — in both preview status and 3MF export.
- Determinism: any stochastic feature (noise, RD) must be seed-reproducible; exports of the same design JSON must be identical.
- Preserve the design-JSON schema; new fields must be optional with defaults so old files load unchanged.
