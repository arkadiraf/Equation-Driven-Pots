# TODO

## Plate coloring artifacts at low resolution (spherical saucer)

Reported 2026-09-18 while testing the Bambu Lab export with `3dModels/TestModels/4ColorSphere.json`:
a spherical pot + saucer at mesh 30 × 30, with pattern A = "Basic Vertical Split" (`cos(theta)`) and
pattern B = "Basic Horizontal Split" (`v - 0.5`).

The saucer's color split shows odd artifacts at this resolution. They may point to a deeper
problem, not just a coarse mesh. Not investigated yet.

What the exported saucer bodies look like (`4ColorSphere_Plate.3mf`). All four are watertight
(0 boundary / 0 non-manifold edges):

| Body | Height | Radius | Where it sits |
| --- | --- | --- | --- |
| Pattern A | z 0–1.20 mm | r 0–36 mm | A flat disc on the floor, so it prints as the first layers |
| Pattern B | z 0–12.85 mm | r 35–52 mm | Wall plus an outer ring of the floor |
| Overlap | z 0–12.85 mm | r 35–52 mm | Wall plus an outer ring of the floor |

The saucer samples the pot's masks over its own phi/v sweep. As a result, the pot's horizontal split
(`v - 0.5`) lands on the saucer's floor/wall junction, and the vertical split cuts the floor in half.

Where to start:

- `buildSphericalPlateGenerationConfig` and `buildSphericalPlateMultipartMeshes` in
  `EquationDrivenPotDesigner.html`: how the saucer's v and phi are mapped before the masks are
  sampled.
- Related: the Apply Plate Coloring checkbox is ignored on this path (`POT_DESIGNER_AGENT.md` §5.3).

Repro files: `3dModels/TestModels/4ColorSphere.json`, `4ColorSphere_Plate.3mf`,
`4ColorSphere_Pot_multipart.3mf`, and the Bambu Studio project `4ColorSphere.3mf`.
