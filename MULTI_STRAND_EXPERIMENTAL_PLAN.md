# Experimental Tool — Multi-Strand: upgrade plan

Status: **Phases A–E implemented.**
Phase A as built: Off / Wound Array modes, count 1–8, step override, per-strand Z and radial
offset, coincidence guard, strand readout, Coiled Basket `k·N` fuse check (pulled forward from B),
`path.strands` in Design JSON (absent → Off). Verified: Off, and Wound Array with N = 1,
reproduce the pre-change build exactly (tris, weighted vertex checksum, bbox to 9 dp) on Torus
Knot, Coiled Basket, Möbius and Custom Path; every path builds at N = 2, 3, 5.
Phase B as built:
- Pinch caps each ring against other strands through a grid spatial hash
  (`forEachCrossStrandPair`). Test: Torus (2,3), 3 strands, Ø 4.4 cm, closest approach 3.16 cm
  → 1 fused solid with Pinch off, 3 separate solids with it on.
- Extra cleaning boxes cross-strand contact zones through `overlapBoxesCore`, the grouping
  routine factored out of `overlapBoxes`. Test: 0 zones found per strand vs 1 zone across strands.
- The coincidence guard now runs on the bare centrelines before rings are built, so a duplicate
  strand can never pinch its twin to nothing.
- Colour by Strand: `part_k = rest ∩ S_k`. The last part is intersected too: taking "whatever
  is left" instead left 735 open edges of coincident-surface slivers. It runs through the
  existing colour pipeline (`colourLayerActive`, worker, banner, exports) and `colourByStrand`
  is saved in the JSON.
- Test: every part has 0 open edges and is one connected piece, and the part volumes sum exactly
  to the pot volume (1787.226 cm³).
- Single-strand output is still identical to the original, including with Pinch and hollow +
  Extra cleaning (Custom Path and Möbius).

Phase C as built:
- **Cable mode** (`buildCableSweep`) offsets each strand in the guide's own frames. The frame
  code was split into `startFrame` and `sweepFramesFromPoints` with unchanged arithmetic.
  - It builds on every path, including Lissajous and Custom.
  - A fractional Twists value or a spacing of 0 is refused, and the design builds as one strand
    with the reason shown.
  - New finding: a cable kinks where the guide bends tighter than spacing + profile radius
    (`cableKinks`, `minBendRadius`). The status line and readout warn about it. Example:
    Lissajous has a 1.33 cm bend, so 1 cm spacing with a 0.8 cm profile warns and 0.4 cm does not.
- **Counter-wind** mirrors strands 2, 4, … before the start frame is chosen, so the tubes still
  face outward (both walls have positive volume). The two families still merge where they cross,
  as expected until phase E, and the readout says so.
- **Alternate Strand Profile Scale** scales strands 2, 4, … Pinch reach and the aggregate
  profile radius use the larger of the two sizes.
- **Expression mode** gives Custom Path `strand`, `strands` and `sp` in scope, always set to
  0, 1, 0 outside this mode.
  - Built-in paths are compiled exactly as before.
  - The default equations don't use `sp`, so extra strands are correctly left out with a hint.
  - Adding `+ sp/a` to the angle gives 2, 3 and 5 distinct strands.
- New JSON fields: `counterWind`, `cableD`, `cableT`, `altScale`. Older files load with the
  defaults.
- Single-strand output is still identical to the original on Custom Path, Torus Knot,
  Lissajous and Möbius, both plain and with Pinch or hollow + Extra cleaning.

Phase D as built:
- **Per-strand grids.** `buildPatternParts` / `buildPatternPartsOrFallback` take the strand set
  `S` and build one pattern grid per strand. `u` runs 0 → 1 along each strand, and `v` uses the
  whole piece's height range, so horizontal bands line up across strands.
- **Unions.** Each state's prism is the union of that state's prism on every strand, including
  the `all` cutter. The trim is the union of every strand's inset solid.
- **Buried skins.** With strands overlapping (3.15 cm closest approach vs 4 cm Ø), 0 of 3,037
  sampled colour vertices sat deeper than the colour depth inside any strand.
- **Strand variables.** `strand` and `strands` are in the pattern and texture scope (0 and 1 on a
  single strand), and the smooth-edge re-evaluation carries them too. Test: `strand == 1`
  coloured only the second strand (352/352 samples nearest it).
- **Failure messages name the strand**, e.g. "mask A on strand 3 …".
- **Depth clamp** uses the thinnest strand (the alternate scale).
- **Colour by Strand and the pattern masks are mutually exclusive**, with Colour by Strand taking
  priority.
- Single-strand colour builds (smooth and stepped, Torus and Custom, with a coloured plate) are
  part-for-part identical to the original: every part's triangle count and checksum match.
- Edge check: no multi-strand part has an odd edge incidence, so there are no holes. Even counts
  above 2 are separate inserts touching along edges; single-strand builds show the same, since
  that is how the existing inserts meet.
- Cost: about 3× a single strand for 3 strands (smooth edges, 200 steps: 14 s vs 5 s). The
  worker build at 200 steps took 8.9 s.

Phase E as built: Crossings = Merge | Alternating over/under (Multi-Strand only), with clearance
(mm), transition length (cm) and starting parity.
- **`findCrossings`.** It clusters close point pairs (across strands and within one strand)
  and refines each cluster to segment-to-segment closest points. Pairs running within 30° of
  parallel are contacts, not crossings, and are left to merge, e.g. the Coiled Basket turns that
  must fuse into a wall.
- **`solveCrossingOrder`.** One unknown per crossing, with parity edges between consecutive
  passages along each strand, 2-coloured by BFS. Constraints broken by odd loops are counted
  and reported.
- **`displaceCrossings`.** It lifts each passage along n = tA × tB, oriented outward, by exactly
  enough to clear.
  - The lift is held flat over a plateau of `need / (2·sin(θ/2))`, then eased out with a cosine.
    A plain cosine bump let 75° crossings touch about 1 cm off-centre: closest approach was
    2.12 cm vs 2.4 cm Ø.
  - Each lift is capped at 45% of the gap to the next passage. A shortened lift is reported
    only when it actually cost clearance.
- **Achieved clearance** is measured segment to segment over each crossing's whole lifted
  zone.
- Test results:

  | Design | Merge | Alternating |
  |---|---|---|
  | Counter-wound Torus, 2 strands | 1 solid | 2 solids, 12 crossings, clearance ≥ 1.0 mm, `+-+-+-…` on each strand |
  | Counter-wound Torus, 4 strands | 1 solid | 4 solids, 48 crossings, clearance ≥ 1.0 mm |
  | Counter-wound, 3 strands | — | 6 odd-loop conflicts reported, plus the clearance shortfall |
  | Flat Custom rosette (loops within one strand) | — | 12 of 24 crossings are within one strand, 0 conflicts; clears at r ≤ 0.5 cm |

  Starting parity B flips every crossing. The new fields round-trip in Design JSON, and older
  files load as Merge.

Known pre-existing issue (not multi-strand): in Object mode a fully enclosed cavity is removed by
`cleanDebris`, because the cavity shell has negative volume, so a hollow closed loop builds solid.
Target: `EquationDrivenWovenPots.html`
Supersedes: §1 "How a strand is generated" of `MULTI_STRAND_PLAN.md`
Builds on: `TOPOLOGY_PATH_UPGRADES.md` ("Multi-strand correction and design", Phases 4–5)

## 1. Review of the two existing documents

**`MULTI_STRAND_PLAN.md`** gets the pipeline analysis right: per-strand piece splitting, the
plate/cuts/export coming for free, the unioned `all` cutter for the pattern base, and the
bit-for-bit `strands = 1` requirement all still hold. Its generation method does not work.
Strand `k` sampling `t + k·period/N` traces the **same locus** as strand 0, so every
copy is coincident. This was checked numerically on every built-in path, and the symmetric
Hausdorff distance between the two copies is 0.000 in every case.

**`TOPOLOGY_PATH_UPGRADES.md`** catches that error and proposes Cable, Axial Array and
Expression modes. The Axial Array proposal has the same failure in a different place: a naive
`360°/N` rotation about Z is also a self-map for many paths. The fix is below.

### The missing rule: rotational symmetry order `g`

A path wound around Z with `g`-fold rotational symmetry maps onto itself under a rotation of
`2π/g`. Rotated copies are therefore distinct only within one `2π/g` sector, so the evenly
spaced strand step is

```text
Δφ = 2π / (g · N)
```

Measured Hausdorff distances between copies (cm), with rx = 10 and zA = 10, for N = 3:

| Path (params)            | g | rotate 2π/g | t-offset P/3 | rotate 2π/(gN) | naive 2π/N |
|--------------------------|---|------------:|-------------:|---------------:|-----------:|
| Torus Knot (2,3)         | 3 | 0.000 | 0.000 | **6.93** | **0.00 ✗** |
| Torus Knot (3,5)         | 5 | 0.000 | 0.000 | 4.38 | 4.38 |
| Flower Ring n=5, weave .3| 5 | 0.000 | 0.000 | 4.55 | 4.55 |
| Braided Loop n1=3        | 3 | 0.000 | 0.000 | **8.31** | **0.00 ✗** |
| Braided Loop n1=4        | 1 | 0.000 | 0.000 | 6.27 | 6.27 |
| Möbius h=1               | 1 | 0.000 | 0.000 | 9.74 | 9.74 |
| Möbius h=3               | 3 | 0.000 | 0.000 | **8.18** | **0.00 ✗** |
| Coiled Basket k=8        | 1 | 0.000 | 0.000 | 1.50 | 1.50 |

The **shipped default design (Torus Knot 2,3) with 3 strands and a naive 120° step produces
three coincident tubes**. That is the most likely first test anyone runs, so the symmetry rule is
required.

For torus-type paths, `2π/(gN)` evenly spaced strands form the classical torus link
`T(Np, Nq)`: N interleaved copies of the knot on the same torus. They cross one another with
the same over/under radial offset (`amp`) that the single knot already uses. The weave
therefore comes from the path itself, and no extra crossing logic is needed for the first
version.

## 2. Where it lives in the UI

Add a new collapsible section with the same visual convention as the Pot Designer's experimental
tools (`EquationDrivenPotDesigner.html:977`, highlighted title):

```
Base Scaffold
Structural Geometry
Vase Insert
Base Plate
Surface Texture
Dual Pattern Color Layer
▶ Experimental Tool – Multi-Strand      ← new, collapsed, OFF by default
Mesh Resolution
```

It is placed after the colour layer because it constrains it (see §6), and before Mesh
Resolution because strand count is the biggest driver of build cost.

### Controls

| Control | Type | Default | Shown for |
|---|---|---|---|
| Strand Mode | select: `Off`, `Wound Array`, `Cable`, `Expression` | Off | always |
| Strand Count (N) | integer 1–8 | 3 | mode ≠ Off |
| Symmetry step | read-only: "g = 3 → 40.0° per strand" | — | Wound Array |
| Rotation Step Override (°) | number, blank = auto | blank | Wound Array |
| Z Offset per Strand (cm) | number | 0 | Wound Array |
| Radial Offset per Strand (cm) | number | 0 | Wound Array |
| Counter-Wind Alternate Strands | checkbox | off | Wound Array (phase C) |
| Cable Spacing d (cm) | number | 1.0 | Cable |
| Cable Twists per Loop | **integer** | 6 | Cable |
| Alternate Strand Profile Scale | number | 1.0 | mode ≠ Off (phase C) |
| Colour by Strand | checkbox | off | mode ≠ Off (phase B) |
| Strand readout | text: min cross-strand clearance, suggested max profile radius, coincidence status | — | mode ≠ Off |

`Expression` mode is enabled only while Topology Path = Custom Path in the first release. It adds
`strand`, `strands` and `sp` (`2π·strand/strands`) to the path expression scope, so the equations
decide where the phase goes.

Path-specific advisories stay in the existing `warn`/`getPathNote` mechanism, following the
project rule that a typed number is never silently changed:

- Coiled Basket fuse check uses effective turns `k·N` (an N-start coil fuses N times sooner).
- Wound Array with a user override that is a multiple of `2π/g` → "strand j coincides with
  strand 0 — use a step that is not a multiple of 360/g°".
- Cable with a non-integer twist → blocked, because the strand would not close.

## 3. Strand generation modes

### A. Wound Array (first to ship)

Apply this after sampling and before `cfg.rot`:

```text
Ck(t) = Rz(k·Δφ) · C(t) + (0, 0, k·zOff) + radial(k·rOff)
```

- The existing expressions are untouched, which keeps legacy geometry bit-for-bit safe.
- It covers Torus Knot, Spherical Knot, Coiled Basket, Flower Ring, Braided Loop and Möbius.
- Each `pathLib` row gains an optional `zSymmetry` function:

| Path | `zSymmetry(c)` |
|---|---|
| Torus Knot, Spherical Knot | `abs(q)` (after dividing out `turnsGcd(p,q)`) |
| Flower Ring | `abs(n)` |
| Braided Loop | `gcd(n1, 3)` |
| Coiled Basket | `1` |
| Möbius Curve | `abs(halfTwists)` (odd) |
| Lissajous Tangle | not axis-wound → Wound Array disabled; offer Cable |
| Custom Path | unknown → `1`, protected by the numeric guard below |

### B. Cable (generic, second)

This mode works for any path, including Lissajous and Custom. It uses the frames
`buildSweepFrames` already produces:

```text
Ck(i) = p_i + d·cos(2π·T·u_i + 2πk/N)·n_i + d·sin(2π·T·u_i + 2πk/N)·b_i
```

`u_i = prox.cumLen[i] / prox.totalLen` is already computed in `buildRings`, so this mode does
**not** depend on the arc-length resampling upgrade. Because the frames are closed-loop
twist-corrected, `T` must be an integer. Rope readout: strands touch when
`r > d·sin(π/N)`.

### C. Expression (Custom Path only, third)

Pass the extra scope variables into `compilePathExpr` with a new cache key. The arguments are
appended after the existing ones, so non-Custom paths compile exactly as before.

### Guard used by all modes

Sample each strand's centerline at 256 points and compute a symmetric Hausdorff distance to
every other strand. This is cheap: `O(256²·N²)` is about 2 M distance evaluations at N = 5. If
the distance is below `0.25 · profileMaxR`, report the coincidence and build only the distinct
strands. A cyclic `t` shift cannot pass this test by construction.

## 4. Code changes

1. **Split `buildSweepFrames(cfg)`** into `sampleCenterline(cfg) → pts` and
   `framesFromPoints(pts, steps)`. Strands transform the points and then build their own
   rotation-minimizing frames. Rz is rigid, so for Wound Array the frames can simply be rotated,
   but Cable needs fresh frames.
2. **Add `buildStrandSet(cfg)`**. It returns `[R_0 … R_{N-1}]` (each exactly what `buildRings`
   returns today) plus an aggregate `{minZ, maxZ, profileMaxR, debris, debrisFrac}`. Texture
   `v` uses the **global** Z range so bands line up across strands.
3. **Change `buildMesh`**. Use `outer = union(buildWallSolid(R_k.outer, R_k))` and the same for
   `inner`. Piece splitting stays per strand, as `MULTI_STRAND_PLAN.md` §2 says.
4. **Gate it hard:** `if (!cfg.strands || cfg.strands.mode === 'off' || cfg.strands.count === 1)`
   → the current `buildRings` path, byte for byte. Do not route N = 1 through the new code.
5. **Update `getFullHeightCm`**, which currently calls `buildRings` directly and feeds the cut
   percentages. It must use the strand set when multi-strand is active, or Z-offset strands will
   be cut at the wrong height.
6. **Add Design JSON `path.strands`**, optional:
   `{ mode, count, stepDeg|null, zOffCm, rOffCm, cableD, cableT, altScale, colourByStrand }`.
   `readCfg` reads it and the generic import loop restores it. If it is missing, the result is
   single-strand.

## 5. Status of each downstream feature

| Feature | Multi-strand status |
|---|---|
| Plane cuts, bottom thickness, drain holes, vase cavity | free (operate on merged solid) |
| `cleanDebris` | free |
| Base plate (`buildPlateMesh(outer)`) | free; verify Wound Array Möbius with `plateMode: 'ellipse'` |
| STL / 3MF / Bambu export | free for solid; parts list needs strand states if Colour by Strand |
| Surface texture | works per strand; use global Z range (step 2 above) |
| Pinch (`avoidSelfIntersect`) | **phase B**: cap by cross-strand `minDist` too, via spatial hash |
| Extra cleaning (`overlapBoxes`) | **phase B**: add cross-strand `touching` pairs |
| Dual Pattern Color Layer | **disabled when N > 1 in phase A** (status note), per-strand grids in phase D |
| Colour by Strand | **phase B**; see §6 |

## 6. Colour by Strand: a cheap alternative to per-strand pattern grids

The most-wanted follow-up in `MULTI_STRAND_PLAN.md` is "strand 1 one colour, strand 2 another".
That does not need N pattern grids. The strand solids `S_k` already exist before the union:

```text
part_k = result ∩ S_k − ∪_{j<k} S_j        (first strand wins at merged crossings)
state  = k mod 4                            → reuses the existing 4 colour chips / 3MF states
```

This reuses the existing `{state, positions, indices}` part format (`buildPatternParts` emits
states 0–3), so the 3MF and Bambu exporters need no new filament logic. Colour by Strand and the
Dual Pattern layer are mutually exclusive until phase D. Parts are full-depth bodies, not skins,
which Bambu handles fine as multi-part objects. Record the "first strand wins" choice in the UI
help text, as `MULTI_STRAND_PLAN.md` §3 asks.

## 7. Phasing

| Phase | Scope | Exit criteria |
|---|---|---|
| **A: Wound Array, solid only** | section UI, `zSymmetry`, `buildStrandSet`, union, coincidence guard, strand readout, `getFullHeightCm`, JSON | N=1 bit-for-bit; every wound path builds at N = 2, 3, 5; default Torus Knot at N=3 gives 3 distinct strands |
| **B: Cross-strand integrity and colour** | Pinch/extra-clean cross-strand pairs, Colour by Strand parts, Coiled Basket `k·N` fuse note | no open edges per part; 3MF opens in Bambu Studio 02.05 with N colours |
| **C: Cable and variations** | Cable mode (unlocks Lissajous/Custom), counter-wind alternate strands, alternate profile scale, Expression mode for Custom Path | cable closes at integer T; non-integer T blocked |
| **D: Pattern layer per strand** | N grids, unioned `all` cutter, `strand` in pattern scope, per-strand failure messages | as `MULTI_STRAND_PLAN.md` acceptance tests |
| **E: Alternating over/under** | only needed for counter-wound or Cable-on-self-crossing designs, from `TOPOLOGY_PATH_UPGRADES.md` | — |

Counter-wind (mirroring odd strands, `y → −y`) produces a biaxial "finger-trap" braid. It sits in
phase C and not phase A because its crossings are **not** radially separated by the path's own
`amp`: the two families meet at the same radius and merge. Its readout must say so until phase E
exists.

## 8. Prerequisites from `TOPOLOGY_PATH_UPGRADES.md`

Two items are worth pulling forward because multi-strand makes their absence much worse:

- **Topology Preview (centerline overlay):** N merged thick tubes are even harder to read than
  one. Draw all N centerlines in distinct colours without CSG. This is the fastest way to check
  the symmetry step.
- **Fit View / refit on topology change:** strand count and offsets change the bounding box.

Arc-length resampling, the typed-parameter registry and expression error reporting are **not**
blockers for phases A–C.

## 9. Acceptance tests (additions to `MULTI_STRAND_PLAN.md`)

- Mode Off or N = 1: re-measure and match the default design's triangle count, vertex checksum
  and bbox before starting.
- Torus Knot (2,3), N = 3, auto step → 40°. Pairwise Hausdorff > 0.25·profileMaxR. A forced 120°
  override triggers the coincidence warning.
- Braided Loop n1 = 3 and Möbius h = 3 behave the same way (g = 3).
- Coiled Basket N = 3 reports fuse using 24 effective turns.
- Every pathLib row either builds at N = 2, 3, 5 in its supported modes or has the mode disabled
  with a stated reason (Lissajous → Wound Array disabled).
- Design JSON round-trips `path.strands`; old JSON without it imports unchanged.
- Build time and peak memory recorded at N = 1, 3, 5 (400 steps, 48 radial), with and without
  Colour by Strand.
