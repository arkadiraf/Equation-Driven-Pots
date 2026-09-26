# TODO — body-first preview, colour layer in the background

Status: **done for `EquationDrivenWovenPots.html`** (2026-09-26). Still to do: the same idea for
`EquationDrivenPotDesigner.html` (`renderConfigToScene`), and the optional draft switch (plan 7).

## What shipped (woven app)

- `buildMesh(cfg, scale, { colors: false })` builds the body only (same remesh, uncoloured plate);
  `runPreview` shows it at once and never starts a colour build. Edits are debounced 300 ms.
- The colour layer runs in a **module Web Worker made from a Blob**: it imports three (maths) and
  `manifold-3d` from the CDN, then evaluates the page's own `<script id="woven-core">`, so the
  geometry code is literally the same and no separate `woven-core.js` split was needed (which
  also keeps the page a single file). Parts come back as transferred typed arrays. One worker per
  build (fresh WASM heap); a spare boots while the banner is Idle so a press starts at once.
- Banner (top-left of the viewer): Idle "Render colours" → Working "Rendering colours… mm:ss ·
  stage · Cancel" → Hidden. Geometry edits cancel (`worker.terminate()`); the 4 colour pickers
  recolour in place. If a worker cannot start, the same build runs on the page (plan 8 stop-gap).
- Exports reuse the finished build (keyed on the config minus colours) or start the worker build
  themselves and write the file when it lands. `await renderColours()` for headless runs.
- Per-stage timings of every worker build: console table + `window.lastColourTimings`.

## Results (2026-09-26, H2C design files from `3dModels/Woven`)

| | Before: whole build, page frozen | After: body on the page | Colours in the worker |
|---|---|---|---|
| Cinquefoil Wicker Planter | 67 s (Bambu export) | **4.7 s** | ~65 s, max main-thread stall 13 ms |
| Earthworm Tangle Vase | ~60 s (Bambu export) | ~2.5 s | ~44 s |

Bambu 3MF `3D/Objects/object_*.model` SHA-256 before/after: **identical** for both designs. A
geometry edit 8 s into the Cinquefoil colour build cancelled it and returned the banner to Idle.
The alien trial config was not saved anywhere, so it was not rerun; cancel is `terminate()`, which
stops a worker regardless of what it is doing.

Profile (worker, seconds) — the booleans dominate, then the JS edge/prism stages:

| Stage | Cinquefoil | Earthworm |
|---|---|---|
| body (rings, wall, cuts, debris) | 6.2 | 2.4 |
| colour inset solid | 2.1 | 1.4 |
| colour grid | 0.1 | 0.0 |
| colour edges (`buildSmoothPatternMeshes`) | 11.8 | 1.5 |
| colour prisms (`toSolid` + prism ⊖ inset) | 9.6 | 2.4 |
| colour booleans (result ∩ / ⊖ prisms) | 35.5 | 36.2 |

Next speed-ups, if wanted: a draft preview (refine 0 / stepped edges) and fewer booleans in the
multi-state path (one `split` per state instead of intersect + a separate all-states subtract).

---


## Problem

Every edit rebuilds the whole model — body CSG, the Dual Pattern Color Layer and the saucer — in
one synchronous call on the main thread (`runPreview` → `buildMesh`). The colour layer dominates,
and the page is frozen until it finishes:

| Design (woven app) | Mesh | Body only | Body + colours |
|---|---|---|---|
| Cinquefoil Wicker Planter | 1500 × 140 | ~7 s | 83–93 s |
| Earthworm Tangle Vase | 3200 × 32 | ~5–9 s | ~70 s |
| Alien vase trial (645 colour grooves + gyroid veins, refine 2) | 5200 × 28 | ~4 s | **> 7 min, never returned** — the tab had to be closed |

While it runs, nothing responds: sliders, orbiting, even closing the tab. Designing the *body*
(path, profile, cuts, texture) is the part that needs fast iteration, and it is the cheap part.

## Goal

1. Any edit shows the **body** (base colour, texture included) within a few seconds.
2. The colour layer builds **only when the user asks for it**, by pressing a banner, so body
   iterations never start a colour build they don't need.
3. Once started, it builds **in the background** while the banner says so; the page stays usable.
4. A newer edit **cancels** the in-flight colour build and puts the banner back to its start state.
5. Exports are **bit-identical** to today's (hash `3D/Objects/object_*.model` before/after).

## Plan

1. **Profile first.** Time the stages inside `buildMesh` / `buildPatternParts` on the three designs
   above: `buildRings`, `buildWallSolid`, cut/cavity booleans, `buildPatternGrid`,
   `buildSmoothPatternMeshes` (JS loops + boundary refinement), `toSolid`/`weldMesh`, the prism ⊖
   inset and result ∩ prism booleans, `getMesh`. The fix below depends on which of these
   dominate; the hang above suggests `buildSmoothPatternMeshes` with many boundaries and refine 2.
2. **Split `buildMesh`** into `buildBody(cfg)` (rings, solids, cuts, drain, vase bore, debris
   clean-up), `buildColorLayer(cfg, R, body)` and `buildPlate(cfg, outer, zLo)`. `runPreview`
   renders `buildBody` immediately in `baseColor`.
3. **Colour layer in a Web Worker.**
   - Move the pure geometry code (path library, `buildRings` and its frame maths, pattern grid,
     smooth/stepped mesh builders, noise helpers, `compilePatternExpr`) into a module
     (`woven-core.js`) imported by both the page and a module worker. It uses only
     `THREE.Vector3/Matrix4`; import three in the worker or replace those with small helpers.
   - The worker loads `manifold-3d` itself (same CDN module), receives the config (plain JSON) plus
     a generation number, rebuilds what it needs, and posts back `{state, positions, indices}`
     parts as transferable typed arrays.
   - Deterministic: same code and inputs in the worker, so the parts match today's output.
4. **Banner — press to render colours.** Colours never start on their own. A small overlay on the
   viewer walks through three states:

   | State | Shown when | Looks like | On click |
   |---|---|---|---|
   | **Idle** | the body has been rebuilt and the colour layer is active (a mask is set and depth > 0) but not rendered for this config | "Render colours" button | start the worker build → *Working* |
   | **Working** | the worker is building colours for the current config | "Rendering colours… 00:23 · Cancel" (elapsed time; a spinner or progress from the worker's phase messages) | Cancel: `worker.terminate()`, fresh worker → *Idle* |
   | **Hidden** | the coloured parts for the current config are on screen, or no colour layer is active | — | — |

   - Any change that alters geometry or masks (a field edit, preset, Design JSON load, page load)
     rebuilds the body, cancels a *Working* build, and shows *Idle*. The coloured preview of the
     old config is replaced by the new body, so what is on screen always matches the form.
   - When the worker answers with the current generation, swap the body mesh for the coloured
     parts and hide the banner until the next change. An older generation's answer is dropped.
   - Colour-only edits (the four colour pickers) do not need a rebuild: recolour the existing
     meshes in place, and keep the banner's state.
5. **Debounce** body rebuilds (~300 ms) so a slider drag rebuilds the body once, not twenty times.
6. **Exports** reuse the finished worker result when the config hash matches. Otherwise pressing an
   export button *is* the request: it starts the worker build itself and shows the banner in the
   *Working* state (no extra click), then writes the file when the parts arrive. Exporting no longer
   freezes the page.
7. Optional: a **"Colours: off / draft / full"** preview switch — draft = stepped edges or
   `boundaryRefine 0` at reduced resolution; exports always use full.
8. Stop-gap if the worker is delayed: ship the banner flow on the main thread first — body
   only on every edit, colours only when the banner is pressed — and yield (`await nextFrame()`)
   between the JS phases of the colour build so the *Working* state can paint. Manifold calls
   themselves cannot be sliced, so the page still pauses during them, but only when asked.

## Done when

- Editing a path parameter on Cinquefoil shows the new body in < 10 s at working resolution and
  **starts no colour build**; the banner shows "Render colours".
- Pressing the banner renders the colours in the background with the *Working* banner; orbiting
  stays smooth; the banner disappears when the coloured model is shown and comes back (*Idle*) on
  the next edit.
- An edit during *Working* cancels that build and returns the banner to *Idle*.
- The alien trial configuration either completes in the worker or can be cancelled without
  closing the tab.
- Exported 3MF object hashes for Cinquefoil and Earthworm are unchanged.
- `WOVEN_DESIGNER_AGENT.md` §2 (harness) is updated: headless runs can await the worker's promise
  instead of polling the save folder.
