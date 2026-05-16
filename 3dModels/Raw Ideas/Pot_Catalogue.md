# Equation Driven Pot — Full Catalogue (150 Designs)

---

## BATCH 1 — Pots 1–10 (Quiet to Noisy)

| # | File | Character | Shape | Texture | Colors | Active Systems |
|---|------|-----------|-------|---------|--------|----------------|
| 1 | Zen_Stone_Vessel.json | **Dead quiet** | Shoulder bulge with gentle base taper | None | Single warm stone `#8c8075` | Base only |
| 2 | Linen_Ridge_Bowl.json | **Very calm** | Wide flared bowl | Soft horizontal bands, fade upward | Linen + dark earth | Base + texture + 1 pattern |
| 3 | Moss_Weave_Planter.json | **Calm but textured** | Classic planter taper with foot bead | Diamond weave | Moss green + dark earth + light moss | Base + weave + 2 patterns |
| 4 | Hex_Column_Planter.json | **Geometric, clean** | Soft hexagonal column with mild taper | Hard saturated facet edges | Slate blue + gold + pale blue rim | Base + texture + 2 patterns |
| 5 | Twisted_Terracotta_Urn.json | **Mid — organic motion** | 5-lobe petal body with mid-bulge | Twist ribs following the lobes | Terracotta tones | Base + texture + 2 patterns + twist modifier |
| 6 | Petal_Orb_Pod.json | **Mid — floral/spherical** | Spherical 5-petal form, egg-asymmetric | Petal surface relief | Rose + violet + petal gold | Spherical + texture + 2 patterns + petal modifier |
| 7 | Lattice_Lantern.json | **Intricate but controlled** | Hex column with harmonic overtone bulge | Honeycomb relief | Deep navy + gold + rust | Base + honeycomb + hex windows + outer deviation + modifier |
| 8 | Chromatic_Bloom.json | **Vibrating multi-color** | Fourier multi-harmonic bloom silhouette | Moiré interference | Deep purple + hot pink + cyan + yellow | Base + moiré texture + double helix + moiré windows + braided drift |
| 9 | Storm_Vortex_Planter.json | **Very active, electric** | 2-frequency swirling body | Arc carving + rib interference | Near-black + electric blue + green + orange | Base + texture + 2 patterns + braided drift + swirl distortion |
| 10 | Hypno_Spiral_Vessel.json | **Maximum chaos** | 4-harmonic Fourier body | Triple-frequency moiré extreme | Deep violet + magenta + cyan + yellow | Base + texture + moiré windows + double helix + braided drift + torsion distortion |

---

## BATCH 2 — Pots 11–20 (Exploring New Equations)

| # | File | New Technique | Shape Logic | Key Color Story |
|---|------|--------------|-------------|-----------------|
| 11 | Carved_Obsidian_Column.json | **ATan fluting** — `atan(6·cos(...))` creates compressed faces with sharp trough edges; **Crown Rotation** modifier concentrates rim twist | Column tapers gently, flutes drift diagonally with height | Near-black obsidian + silver edge highlights |
| 12 | Coral_Scallop_Vase.json | **8-lobe body** modulated by `sin(πv)` — lobes bloom through the mid-body and fade at base/rim; arc carving aligned to the lobes | Bulging lobed vase form with slight rim lift | Coral red + ocean blue + pale salmon |
| 13 | Hourglass_Wind_Planter.json | **Strong waist pinch** with symmetric flare at both base and rim; **Wind Lean distortion** bends the form diagonally as if caught mid-gust | Double-bell hourglass, bent by wind | Pale sky blue + steel blue diagonal stripes |
| 14 | Superellipse_Modern_Pot.json | **Superellipse cross-section** `pow(|cos|^8 + |sin|^8, -0.125)` — faces near-flat, corners gently convex; near-zero texture for a pristine minimal look | Square-ish column with soft geometry | Off-white + warm grey — pure modernist |
| 15 | Dragon_Egg_Orb.json | **Crossing diagonal scales** on a sphere `cos(10θ+8φ) + cos(10θ-8φ)` — the two waves interfere to form lozenge-shaped scales; pattern matches the scale geometry | Spherical egg with equatorial fullness | Deep forest green + rich gold scale highlights |
| 16 | Folded_Panel_Column.json | **Folded mod panels** `cos(8·abs(mod(θ+πv, π/4) - π/8))` — 8 helically-drifting accordion panels; moiré interference texture + diagonal drift modifier warps the grid | Industrial faceted column with slowly rotating seams | Deep teal navy + sea green + amber gold |
| 17 | Rim_Vortex_Bowl.json | **Rim Vortex distortion** — tangential offset `(-sin(θ), 0, cos(θ))·pow(v,1.6)` spirals the rim outward as if spun; texture density increases toward the rim | Extreme flared bowl with a spinning rim | Pale ice blue + dusty steel, deep navy at overlap |
| 18 | Pulsing_Frequency_Vase.json | **Beating ring frequencies** — two close wave periods (18π and 25π in v, 27π in texture) create standing-wave beat envelopes; slight theta offset makes rings subtly helical | Elegant tall vase — quiet geometry, color pattern does the work | Near-black + fire red + bright yellow + white flash at beats |
| 19 | Desert_Barrel_Cactus_Pot.json | **Side Pressure Dent** distortion — localized Gaussian dent `exp(-θ²·7)·exp(-(v-0.55)²·22)` creates a rock-pressed indentation on one face | Fat 10-lobe barrel with a dented side | Cactus green + dark forest + desert sand + bright gold rim |
| 20 | Interference_Lantern_Orb.json | **Spherical lattice windows** from `cos(8θ)·cos(6φ)` product — creates a true grid of diamond windows on the sphere surface; torsion distortion gently rotates the upper half | Spherical form with equatorial fullness and a twisted crown | Deep violet + vivid purple + electric cyan + yellow flash |

---

## BATCH 3 — Pots 21–50 (30 Unique Explorations)

### Silhouette-Driven

| # | File | Silhouette Logic |
|---|------|-----------------|
| 21 | Soft_Egg_Pod.json | Spherical egg `R·(1+0.16cosφ−0.08cos2φ)` — tapers toward south pole, blooms toward north. Single cream glaze, upper half tinted taupe. Utterly quiet. |
| 22 | Pinched_Neck_Vase.json | Three-Gaussian compound silhouette: fat belly at v=0.38, dramatic neck pinch at v=0.72, slight rim flare above — a classic gourd-neck vase form built from pure math. |
| 23 | Beveled_Octagon_Tower.json | 8-sided `cos(8θ)` polygon with atan-sharpened face edges, slight taper. Charcoal + antique gold face/corner contrast. |
| 24 | Bamboo_Segment_Column.json | `sin²(3.5πv)` creates periodic constrictions — 3.5 bamboo-node segments at irregular spacing for an organic feel. Pattern highlights the node rings in dark green. |
| 25 | Gourd_Planter.json | Fat belly Gaussian at v=0.30 (peak 1.5R), neck-pinch Gaussian at v=0.72 — pure gourd form. Diamond weave texture. Burnt orange palette. |
| 49 | Hourglass_Pinch_Pod.json | Spherical: `−0.22sin²φ` constricts the equator — widest at poles, narrowest at the waist. Produces a pinched ring shape when the sphere is cut top and bottom. Pale blue palette. |

### Texture-Driven

| # | File | Texture Strategy |
|---|------|----------------|
| 26 | Dense_Rib_Tower.json | 20 vertical ribs at full intensity — the ribbing IS the pot. `textureFill` highlights peaks in pale blue on a dark navy body. |
| 27 | Woven_Spiral_Basket.json | Tight 12-strand diamond weave with a twist modifier rotating the weave grid as it rises. Pattern selects both raised peaks and crossing nodes. Natural basket palette. |
| 28 | Scalloped_Shell_Vase.json | 3-lobe body with arc carving aligned to the lobe frequency — carved arcs follow the petal geometry. Outer deviation adds a third color at protrusions. Shell ivory + coral. |
| 29 | Knurled_Grip_Cylinder.json | 18-strand ultra-tight diamond weave creates machined knurling. Near-black metal with bright peak highlights. Industrial. |
| 30 | Topographic_Rings_Planter.json | Two beat-frequency band masks (16π and 32π in v) create major and minor topographic contour lines. Pattern colors the elevation bands independently. |

### Pattern-Driven

| # | File | Pattern Concept |
|---|------|----------------|
| 31 | Harlequin_Diamond_Vase.json | Two diagonal stripe masks `sin(8πv±4θ)` — where both select you get diamonds, where neither you get base color. Four distinct regions: red, yellow, blue, white. |
| 32 | Flame_Torch_Vase.json | Vertical gradient lifts from black through ember to orange; a diagonal modifier shifts flame tongues laterally as they rise. Fire color builds bottom to top. |
| 45 | Raku_Fire_Bowl.json | Moiré near-frequency crackle `sin(16θ+12πv)+sin(17θ−12πv)` selected as a pattern mask — crackle lines appear in fire-red against near-black. Raku ceramic palette. |
| 48 | Marble_Column_Planter.json | Two slow beating vein patterns `sin(8πv±nθ)` with different winding numbers simulate the angular drift of marble veining. Clean white body, grey/warm veins. |

### Modifier-Driven

| # | File | Modifier Strategy |
|---|------|-----------------|
| 33 | Barley_Twist_Column.json | `sin(3πv)` twist at strength 0.80 — the strongest twist in the collection. The hexagonal faces and rib texture visibly spiral up the column. |
| 34 | Braided_Rope_Vessel.json | Braided drift modifier at 0.35 applied to all layers simultaneously. Diagonal interference texture + crossing double-helix pattern together create a convincing braided rope appearance. |
| 43 | Nautilus_Shell_Vase.json | Petal migration modifier `sin(2πv)+0.3sin(5θ)` causes the 5-lobe body and arc-carved channels to drift angularly as they climb — the spiral grows as you look up. |

### Distortion-Driven

| # | File | Distortion Concept |
|---|------|-------------------|
| 35 | Leaning_Tower_Planter.json | Basic Bend: `0.26·pow(v,1.5)` at strength 0.55 — deliberate architectural lean. The vertical split pattern shows the lean direction as two-tone. |
| 36 | Gravity_Sag_Bowl.json | Basic Sag: `dy=−0.20·pow(v,1.8)` at strength 0.55 on a trumpet-flared bowl — the rim droops downward as if the clay is still wet. Surreal olive/yellow palette. |
| 37 | Double_Dent_Barrel.json | `−sign(x)·cos⁸(θ)·Gaussian(v)` dents both ±x faces simultaneously — like the barrel was squeezed from two sides. Symmetric physics deformation. |
| 38 | Torsion_Spire.json | Torsion at strength 0.70 — the strongest torsion in the collection. The tall column visibly rotates around its own axis, turning helical ribs into a corkscrew. |
| 40 | Volcanic_Crater_Bowl.json | Combined distortion: off-axis Gaussian pressure dent + gravity sag in one equation set (custom type). The bowl sags AND has a meteor-impact dent on one face. |

### Complex Multi-System

| # | File | All-System Concept |
|---|------|-------------------|
| 39 | Circuit_Board_Column.json | Octagonal column + honeycomb texture + moiré window pattern + outer deviation + diagonal modifier. PCB green + solder gold. Reads like a circuit trace pattern. |
| 41 | Crystal_Shard_Planter.json | 7-sided ATan base at high gain (12× vs standard 6×) creates very sharp crystal facets. Matching atan texture reinforces edge sharpness. Ice blue + bright facet white. |
| 42 | Ocean_Wave_Planter.json | Lobed base varies with `sin(2πv)` — the lobes pulse in and out twice vertically. Interference texture + two angular pattern masks create distinct wave crest regions. |
| 44 | Northern_Lights_Column.json | Two independent moiré window masks at different wave numbers create overlapping aurora curtains. Braided drift modifier shifts the curtain pattern. Polar palette. |
| 46 | Honeycomb_Beeswax_Tower.json | Pure honeycomb from hex `max()` in base, texture, AND both pattern masks simultaneously — every layer is hexagonal. Beeswax amber gradient. |
| 47 | Plasma_Field_Vase.json | Three incommensurate frequencies (7, 11, 3 angular / 4, 3, 8 vertical) interfere directly in the base radius equation — the silhouette itself pulses with plasma energy. |
| 50 | Fractal_Bloom_Supreme.json | 5-harmonic Fourier base + triple-frequency moiré texture + two crossing pattern masks + braided drift modifier + torsion distortion at maximum resolution (240×200). The densest configuration in the collection. |

---

---

## BATCH 4 — Pots 51–100 (New Preset Library Explorations)

### Polygon Silhouettes (New Cross-Sections)

| # | File | Shape Equation | Key Effect | Colors |
|---|------|---------------|------------|--------|
| 51 | Elliptical_Column_Planter.json | Wide Oval `R/√(1.9cos²θ + 0.7sin²θ)` — broad ellipse cross-section with gentle taper | Alternating ribs `cos(10θ)+0.35cos(20θ)` add rhythmic texture | Warm buff + chocolate |
| 52 | Tall_Oval_Vase.json | Tall Oval `R/√(0.72cos²θ + 1.85sin²θ)` — narrow ellipse with shoulder pinch at v=0.7 | Shoulder ribs `cos(12θ)·exp(−(v−0.72)²·18)` | Sage green + olive |
| 53 | Shield_Profile_Bowl.json | Shield Profile `R·(1+0.14cosθ−0.08cos2θ)·(1+0.30·v^1.8)` — D-shaped cross-section, flares toward rim | Ripple rings + dual pattern split by cosθ and sinπv | Cobalt + cream + gold |
| 54 | Blunt_Triangle_Column.json | Blunt Triangle `R·(1+0.24cos3θ)` — strong 3-face geometry with Crown Rotation rim twist | Meridian atan carving `atan(8cos3θ)` aligned to triangle faces | Charcoal + gold |
| 55 | Barrel_Oval_Planter.json | Barrel Oval `R/√(1.45cos²θ + 0.82sin²θ)·(1+0.10sinπv)` — ellipse with mid-body bulge | Basket crosshatch weave `sin(10θ+8πv)·sin(10θ−8πv)` | Warm tan + espresso |
| 56 | Rounded_Rectangle_Trough.json | Rounded Rectangle superellipse `pow(|cos/1.25|^6 + |sin/0.82|^6, 1/6)^−1` — wide shallow trough | Crown terraces `floor(5·(0.5+0.5·sin(12πv)))/5` | Concrete grey palette |
| 57 | Soft_Pentagon_Tower.json | Progressively sharpening pentagon `(1+0.12cos5θ)·(1+(0.05+0.10v^1.4)·atan(4cos5θ))` — faces harden upward | Atan rib texture follows pentagon | Sand + sienna |
| 58 | Pillow_Square_Pot.json | Pillow Square `pow(|cosθ|^6 + |sinθ|^6, −1/6)·(1+0.08sinπv)` — cushion square with belly bulge | Stepped weave `cos(8θ+floor(10v)·π/5)` — phase steps with height | Indigo + cream |

### Bloomfold / Petal Morph (z-based Lobes)

| # | File | Shape Logic | Color |
|---|------|-------------|-------|
| 59 | Bloomfold_Vase.json | Full Bloomfold equation — 3→6 lobe morph driven by `cos(0.5πz/10)²` and `sin(πz/10)²` cross-fade weights. Crown interference texture. Gentle torsion modifier 0.22. | Burgundy + rose |
| 60 | Petal_Morph_Vase.json | `(1+0.35sin(πz/10))·(1+0.25·(((10−z)/10)·cos3θ + (z/10)·cos6θ))` — explicitly lerps from 3-petal to 6-petal as z rises. Petal migration modifier. | Forest green + lime |
| 61 | Twisted_Trifold_Bloom.json | Bloomfold with helical phase offset `θ − πz/15` — the entire lobe pattern rotates as it climbs. Domain Warp Ribs texture. Counter-diagonal drift modifier. | Deep navy + cobalt |
| 62 | Nested_Warp_Blossom.json | Domain-warped petal `cos(5·(θ + 0.18sin(3πv) + 0.07sin(11θ)))` — nested warp inside the petal frequency. ATan Braid texture. Rosette drift modifier. | Violet + silver |

### Antenna / DNA / Harmonic (z-Physics Equations)

| # | File | Key Equation | Effect |
|---|------|-------------|--------|
| 63 | Antenna_Migration_Tower.json | `R·(1+0.40·(z/10)^1.5·abs(cos((2+6z/10)·θ/2)))` — lobe count and amplitude both grow with height. Body Swirl Window modifier. | Charcoal + chrome |
| 64 | DNA_Double_Helix_Vase.json | `R + 0.5sin(4θ+z) + 0.5cos(4θ−z)` — two counter-rotating helices sum to create a braided cross-section. Braided drift modifier. Separate red/blue strand patterns. | Black + vivid red + blue |
| 65 | Harmonic_Oscillator_Vase.json | `R·(1+0.25·abs(cos(πz/10))·cos7θ)` — standing wave envelope: lobes appear, vanish, appear again vertically. Patterns select node vs. antinode zones. | Navy + silver |
| 66 | Fractal_Growth_Column.json | 4 z-gated harmonics — cos3θ, cos5θ, cos7θ, cos11θ each activated via clamp() in sequential v-bands. Quasi-interference texture. | Warm brass + bronze |
| 93 | Harmonic_Beats_Vase.json | `R·(1+0.30·abs(cos(1.5πz/10))·cos(8·(θ+πz/20)))` — fractional frequency creates beating nodes; 8-lobe cross-section slowly rotates as it climbs. Body swirl modifier. | Bronze + sienna |

### Domain Warp / ATan / Nonlinear Textures

| # | File | Nonlinear Technique | Colors |
|---|------|-------------------|--------|
| 67 | Domain_Warp_Rib_Planter.json | Domain Warp Ribs `cos(12·(θ+0.12sin(6πv)+0.05sin(9θ)))` — ribs warp laterally with a v-driven phase drift and self-referential angular warp. Rosette drift modifier. | Terracotta + clay |
| 68 | Terraced_Contour_Bowl.json | `floor(6·(0.5+0.5·sin(16πv)))/6` — terrain-terraced bands on a flared bowl; both pattern masks use the floor function to select geological elevation zones. | Stone + earth strata |
| 69 | Log_Ripple_Vase.json | `log(1+4·abs(sin(12θ+10πv)))` — logarithmic compression creates sharp bright ridges with wide dark valleys. Feather sweep modifier. | Midnight + gold |
| 70 | Saturated_Moire_Tower.json | `atan(5·(sin18θ+sin19θ))` — near-integer frequencies saturated through atan. Maximum resolution 240×180. Quasi drift modifier. | Charcoal + orange + white |
| 71 | Diamond_Carve_Planter.json | `abs(cos(8θ+6πv)) + abs(cos(8θ−6πv))` — dual-diagonal absolute carving creates a true diamond grid across the surface. | Deep teal + silver |
| 72 | ATan_Braid_Column.json | `atan(8·(sin(6θ+8πv) + 0.6sin(11θ−7πv)))` — two-frequency braid compressed through atan. Cymatic sweep modifier. Maximum resolution 240×180. | Bronze + copper |
| 96 | Nonlinear_Chevron_Vase.json | Chevron Fold base + `atan(6·(abs(sin(6θ+8πv)) − 0.5·abs(sin(6θ−8πv))))` — absolute-value subtraction creates directional chevron pointing, texture emphasizes the asymmetry. Chevron drift modifier. | Navy + gold |

### Interference / Quasi-Crystal Patterns

| # | File | Interference Strategy | Colors |
|---|------|----------------------|--------|
| 73 | Quasi_Helix_Window_Vessel.json | Fourier Bloom base + quasi-helix window pattern `cos(5θ+8πv)+0.7cos(8θ−√2·7πv)−0.25` — irrational winding ratio prevents repetition. Interference drift modifier. | Indigo + violet |
| 74 | Crisp_Window_Tower.json | `smoothstep(0.18,0.22,sin(6θ+8πv)+0.55sin(11θ−5πv))−0.5` — razor-thin crisp windows. Max resolution 240×180. Cross-diagonal weave modifier. | Gunmetal + silver |
| 75 | Equatorial_Arc_Belt_Bowl.json | `asin(0.98sin8θ)·exp(−(v−0.5)²·30)` — arcsin creates flat-topped equatorial bands in a Gaussian belt. No modifier — the pattern does the work. | Ocean blue |
| 76 | ATan_Gate_Bands_Vase.json | `atan(7·(sin(7θ+8πv)+0.35cos(3θ−6πv)))` — two-component atan gate. Upper Bloom Twist modifier concentrates at rim. | Rose + magenta |
| 94 | Phase_Drift_Shell_Vase.json | `R·(1+0.12cos(5θ+πv+0.4sin(2πv))+0.05cos(11θ−2πv))` — embedded phase warp `0.4sin(2πv)` makes the spiral accelerate then decelerate. Quasi drift modifier. | Space black + electric blue |
| 95 | Braided_Spiral_Orb_Pot.json | Spherical `cos(8θ+10φ)+cos(8θ−10φ)+0.03cos16θ` — two counter-spiraling waves interfere to create braid cross-sections on a sphere. Cymatic sweep modifier. | Navy + teal |
| 98 | Moire_Orb_Pot.json | Spherical `cos(12θ+9φ)+cos(13θ−9φ)` — one-apart angular frequencies create rolling moiré on sphere. Vortex Turn torsion distortion `0.20·v^1.7`. Max resolution 240×180. | Violet + pink |
| 99 | Irrational_Weave_Orb.json | Spherical `cos(9θ+√2·7φ)+cos(14θ−√3·5φ)` — both irrational winding ratios prevent any pattern repeat. Product texture `cos·cos`. Gentle torsion + Crown Rotation XYZ distortion. | Copper + gold |

### Lobe-Evolution / Progressive Forms

| # | File | Progression Logic | Colors |
|---|------|-----------------|--------|
| 77 | Progressive_Lobe_Tower.json | `R·(1+0.22·atan((2+6v)·cos6θ))` — atan gain parameter grows from 2 at base to 8 at rim; lobes transition from barely visible to sharply defined. | Sand + stone |
| 78 | Spiral_Triple_Helix_Vessel.json | `(R+2.0sin(πz/10))·(1+0.20cos(3θ+πz/10))` — radius pulses AND lobes rotate simultaneously as z rises. Twist drift modifier 0.30. | Plum + rose gold |
| 79 | Petal_Belt_Vessel.json | `R·(1+0.18cos6θ·exp(−(v−0.55)²·18))` — 6 petals appear only in a Gaussian belt at the body's mid-height; completely smooth above and below. Minimal ivory + sage. | Ivory + sage |
| 80 | Lotus_Crown_Planter.json | `R·(1+0.10cos6θ·exp(−(v−0.88)²·40))` — 6 petals emerge only near the rim. Lotus Crown modifier `exp(−(v−0.88)²·55)·sin8θ` strength 0.30. potplate mode. | Ivory + forest + gold |
| 97 | Stepped_Crown_Phase_Column.json | `R·(1+(0.05+0.16·exp(−(v−0.85)²·60))·cos(6θ+floor(8v)·π/8))` — 8 stepped phase jumps with a bright crown flare. Shoulder Window modifier. | Charcoal + cyan |

### Wind / Gravity / Pressure Distortions

| # | File | Distortion Concept | Colors |
|---|------|-------------------|--------|
| 81 | Gusted_Wind_Tall_Vase.json | Gusted Wind: `dx = v^1.8·(0.7+0.3sin4θ)` at strength 0.45 — the lean is uneven around the perimeter, so the pot bends AND twists slightly. | Sky blue |
| 82 | Diagonal_Sag_Bowl.json | Diagonal Sag: `dx=0.10·Gauss(v−0.7)`, `dy=−0.16·Gauss(v−0.7)`, `dz=0.06sin3θ·Gauss(v−0.7)` — triaxial sag creates a diagonal gravitational droop at a specific height band. | Amber + olive |
| 83 | Crown_Eddy_Orb.json | Crown Eddy: swirl `dx=−0.14z·Gauss(v−0.86)`, `dz=0.14x·Gauss(v−0.86)` plus `dy` lift — the rim orbits slightly while also floating upward. Spherical form. | Midnight + violet |
| 86 | Palm_Press_Organic.json | Palm Press pressure: `dx=−0.45·exp(−(θ−π/10)²·7)·exp(−(v−0.55)²·14)` — localized off-axis dent as if a palm was pressed against one side. | Sandy beige |
| 87 | Sway_Wave_Planter.json | Sway Wave: `dx=0.12sin(3πv)`, `dy=0.02sin(2πv)` — sinusoidal sway creates an S-curve lean that reverses direction twice with height. | Dusty pink |

### Fluid Twist / Torsion Distortions

| # | File | Torsion Strategy | Colors |
|---|------|-----------------|--------|
| 84 | Fluid_Twist_Column.json | Fluid Twist XYZ: `cos(0.25sin(2πv) + 0.15exp(−(v−0.75)²·18))` — the twist angle is a sum of a full-body sinusoid and a shoulder Gaussian, producing complex twist profile. Quasi-crystal base. | Charcoal + gold |
| 85 | Counter_Twist_Column.json | Counter Twist: `0.18sin(2πv)` torsion — twist reverses direction: bottom leans one way, top leans back. Woven interference base reinforces crossing pattern. | Navy + cobalt |

### Spherical Specials

| # | File | Spherical Concept | Colors |
|---|------|-----------------|--------|
| 88 | Fibonacci_Spirals_Orb.json | `pow(max(0,sin(13θ−8φ)),2) + pow(max(0,sin(8θ+13φ)),2)` — two Fibonacci-ratio spirals, each `max(0,·)²` so they only add, never cancel. Diagonal petal sweep modifier. | Ochre + rust + gold |
| 89 | Coral_Brain_Orb.json | `sin(10θ+5φ)·sin(8φ)` — product of angular and meridian waves creates coral-like folded ridges on a sphere. Petal ripple modifier. | Ocean blue + coral |
| 90 | Bell_Orb_Pod.json | `R·(1+0.22sin^1.6φ − 0.16cosφ)` — bell-curve equatorial swell with slight north-taper. Quiet spherical pod. | Burgundy + rose + cream |
| 91 | Aerospace_Isogrid_Orb.json | `max(cos(12θ+10φ), cos(12θ−10φ))` — max() selects the higher of two crossing diagonal families, creating an isogrid triangle lattice on sphere. Gentle torsion modifier. | Aerospace grey + orange |
| 92 | Crown_Splash_Orb.json | `0.35·exp(−(φ−0.4)²·20)·max(0,cos14θ)` — 14 splash jets frozen at the crown. Crown Rotation modifier 0.35. | Teal + cyan |
| 100 | Absolute_Pinnacle.json | Spherical Quasi-Lattice `R·(1+0.12sin²φ)·(1+0.06cos(10θ+√2·8φ)+0.06cos(15θ−√3·6φ)+0.03cos(20θ+4φ))`. Audio Ripple Shell texture `sin16θ·cos18φ + 0.4sin(24θ−10φ) + 0.3cos(30θ+14φ)`. Multi-direction flower modifier. Fluid Twist XYZ distortion. Max resolution 200×200. The most complex design in the collection. | Black + gold + cyan + white |

---

---

## BATCH 5 — Pots 101–150 (New Math Frontiers)

### Exotic Silhouettes (Limaçon, Rose, Star, Squircle, Hypocycloid)

| # | File | Shape Equation | Colors |
|---|------|---------------|--------|
| 101 | Limacon_Planter.json | Limaçon `R·(1+0.35cosθ)` — D-shaped cross-section, widest on one side, tapers to near-point on opposite side | Dusty rose + terracotta |
| 102 | Rose_Curve_Column.json | 4-petal rose `R·(1+0.26cos2θ+0.08cos4θ)` — four lobes, 2× self-similar harmonic. Basket crosshatch texture. | Ivory + sage |
| 103 | Star_Polygon_Vase.json | 5-point star `R·(1+0.22cos5θ+0.10cos10θ)` — additive harmonic sharpens the star tips. ATan meridian carving. Diagonal drift modifier. | Midnight + gold |
| 104 | Squircle_Tower.json | Squircle n=4 `R·pow(cos⁴θ+sin⁴θ,−0.25)` — halfway between square and circle cross-section. Horizontal bands. | Stone grey |
| 105 | Hypocycloid_Bowl.json | 3-cusp `R·(1+0.28cos3θ−0.08cos6θ)·(1+0.22v^1.8)` — subtracted second harmonic sharpens the 3 concave cusps. Flares to rim. | Slate + cobalt |

### Engineered / Technical Forms

| # | File | Technical Concept | Colors |
|---|------|-----------------|--------|
| 106 | Gear_Tooth_Column.json | `R·(1+0.18cos16θ−0.05cos32θ)` — 16-tooth involute gear profile; second harmonic shapes the tooth profile | Gunmetal grey |
| 107 | Spring_Coil_Tower.json | `R·(1+0.18cos(θ+8πv))` — one-start helix cross-section: the bulge rotates once around the column. Twist drift modifier 0.25. | Copper + bronze |
| 108 | Fractal_Snowflake_Vase.json | Self-similar 3-level `0.14cos6θ + 0.07cos12θ + 0.035cos24θ` — each level halves amplitude and doubles frequency. | Ice blue |
| 109 | Involute_Column.json | `R·(1+0.20·atan(10cos12θ))` — atan compresses the 12-tooth gear involute to sharp ridges and flat faces. | Steel grey + amber |
| 110 | Turbine_Vane_Planter.json | `R·(1+0.22sin(8θ+4πv))` — 8 vanes sweep diagonally as the height rises, mimicking turbine blade sweep. Diagonal drift modifier. | Titanium grey |

### Bio-Inspired Phyllotaxis

| # | File | Bio-Math Concept | Colors |
|---|------|----------------|--------|
| 111 | Sunflower_Spiral_Orb.json | Fibonacci 13/21 on sphere: `sin(13θ+21φ)+sin(21θ−13φ)` — the two golden-ratio spiral families produce sunflower phyllotaxis. Max resolution 240×180. | Sunflower gold |
| 112 | Pinecone_Scale_Orb.json | Fibonacci 8/13: `pow(max(0,sin(8θ+13φ)),1.5)` — max(0,·) makes each spiral family one-directional, creating overlapping raised scales. | Forest green + brown |
| 113 | Seashell_Spiral_Vase.json | `R·(1+0.16sin(θ+8πv)+0.08sin(2θ+12πv)+0.04sin(3θ+14πv))` — 3-harmonic logarithmic-spiral flavor; the cross-section gently rotates and grows as height increases. | Shell pink + pearl |
| 114 | Ammonite_Chamber_Bowl.json | Spiral chamber septa patterns `sin(3πv+0.8θ)` and `sin(6πv+1.6θ)` on a flared bowl — two different angular winding rates simulate ammonite septum geometry. | Stone + amber |
| 115 | Leaf_Vein_Column.json | `abs(sin(theta))·sin(πv)` for the midrib + `cos(14θ)·exp(−abs(sin(theta))·3)` for secondary veins — veins fade at rim and base. | Leaf green |

### Artisan Texture Techniques

| # | File | Texture Concept | Colors |
|---|------|---------------|--------|
| 116 | Guilloche_Tower.json | Engine turning: `sin(20θ+16πv)+0.5sin(24θ−14πv)+0.25sin(28θ+12πv)` — three near-commensurate frequencies produce the guilloché rose-engine pattern. Max resolution 240×200. | Antique gold + black |
| 117 | Celtic_Knot_Vessel.json | `abs(sin(5θ+8πv))·abs(cos(5θ−8πv))` — product of two shifted absolute-sine waves creates knot crossing points where both are near zero. | Forest green + gold |
| 118 | Fingerprint_Bowl.json | `sin(16πv+1.2sin(8θ+2πv))` — nested frequency modulation creates topological fingerprint ridges that bend and fork around the vessel. | Flesh + terracotta |
| 119 | Islamic_Star_Planter.json | `max(cos6θ, cos(6θ+π/3), cos(6θ−π/3))` — max of three 60°-offset cosines creates the 12-pointed Islamic star tiling. Hex base reinforces the geometry. | Turquoise + gold |
| 120 | Hammered_Copper_Vase.json | Three-beat hammered surface: `sin(18θ+14πv)·sin(19θ−13πv)+0.3sin(23θ+9πv)` — three mutual near-frequencies interfere to produce the hammered metal texture. | Copper + verdigris |

### Novel Distortion Types

| # | File | Distortion Concept | Colors |
|---|------|------------------|--------|
| 121 | Triple_Dent_Cylinder.json | 3 Gaussian pressure dents at 120° spacing `exp(−θ²·5)+exp(−(θ−2.094)²·5)+exp(−(θ−4.189)²·5)` — rotationally symmetric 3-point indent. | Concrete grey |
| 122 | Helix_Lean_Tower.json | Helix Lean: `dx=0.18cos(3πv)`, `dz=0.18sin(3πv)` — the lean direction rotates through 1.5 full turns as the tower rises, creating a DNA-like winding tilt. | Ice blue + navy |
| 123 | Inflated_Belly_Pot.json | Outward inflation: `dx=0.28·Gauss(v−0.5)·cosθ`, `dz=0.28·Gauss(v−0.5)·sinθ` — uniform outward pressure inflates the belly like a balloon at mid-height. | Warm clay |
| 124 | Earthquake_Shear_Vase.json | Pure shear: `dx=0.22sin(πv)` — uniform X-displacement that grows sinusoidally from base to rim. The pot appears to slide at the neck without torsion. | Amber + dark brown |
| 125 | Accordion_Squeeze_Tower.json | Axis-aligned squeeze: `dx=−0.25cosθ·Gauss(v−0.5)`, `dz=−0.25sinθ·Gauss(v−0.5)` — inward pressure from all sides compresses the belly uniformly. | Ivory + brown |

### Color / Pattern Explorations

| # | File | Pattern Strategy | Colors |
|---|------|----------------|--------|
| 126 | Mondrian_Grid_Column.json | `floor(5v)/5` horizontal bands × `floor(3(θ+π)/2π)/3` angular sections — quantized grid creates Mondrian-style rectangular color blocks. | Red + blue + yellow + white |
| 127 | Zebra_Spiral_Vase.json | `sin(24πv+6θ)` — diagonal stripe at frequency-24 wraps around the pot in tight spirals; two near-frequency stripes at 24 and 22 create slight beat width variation. | Black + white |
| 128 | Brick_Wall_Planter.json | Staggered brick using `floor()`: `cos(6·(θ + floor(8v+0.5)·π/6))` offsets each course by half a brick. Pattern selects mortar lines and brick faces separately. | Brick red + mortar grey |
| 129 | Acid_Moire_Vessel.json | Dual `smoothstep` moiré windows at opposite winding directions `sin(16θ+12πv)+sin(17θ−11πv)` vs. mirror — neon fluorescent pattern colors. Max resolution 240×200. | Black + neon green + neon pink + yellow |
| 130 | Aurora_Column.json | Two Gaussian pattern belts at v=0.35 and v=0.72 with different angular frequencies — aurora curtains appear at specific heights only, fading away from their centers. | Midnight + green + violet + cyan |

### Spherical & Organic Forms

| # | File | Concept | Colors |
|---|------|---------|--------|
| 131 | Galaxy_Orb.json | `R·(1+0.06sin(13θ+8φ)+0.03sin²φ+0.03cos(21θ−5φ))` — spiral arm interference + equatorial bulge. Spiral drift modifier. | Midnight + nebula purple + stellar white |
| 132 | Toroidal_Ring_Pot.json | `R·(1+0.45sinπv−0.12sin2πv)` — profile is wide at mid-body, narrow at base and rim; 6-lobe texture reinforces the ring geometry. | Metallic silver |
| 133 | Rippled_Membrane_Orb.json | Spherical `sin(12θ+8φ)+cos(12θ−8φ)+0.5sin16φ` — three crossing wave families on the sphere surface. Gentle torsion modifier. | White + ice blue |
| 134 | Moebius_Drift_Vase.json | `R·(1+0.20sin(θ+6πv))` — one-start helix cross-section with twist drift modifier applying a similar rotation: the cross-section bulge and the texture grid rotate together. | Charcoal gradients |
| 135 | Ribbed_Melon_Planter.json | `R·(1+0.16cos8θ+0.04sin²πv)` — 8 melon ribs swell at mid-body; the `sin²πv` term makes them widest at the equator and narrow at top and bottom. | Pale green + forest |

### Nature Object Forms

| # | File | Concept | Colors |
|---|------|---------|--------|
| 136 | Pumpkin_Planter.json | `R·(1+0.22cos8θ·(1−0.30v))` — ribs are deepest at the base and fade upward; `0.12sin²πv` bulges the mid-body. | Orange + dark brown |
| 137 | Tulip_Vase.json | `R·(1−0.18sin²πv+0.30v³)` — waist narrows at mid-body, flares dramatically at rim; 6 petals appear in upper half via `cos6θ·sin^1.5(πv)`. Petal migration modifier. | Red + gold |
| 138 | Mushroom_Cap_Bowl.json | Spherical `R·(1+0.40sin²φ·exp(−(φ−π/2)²·4))` — equatorial Gaussian swell creates the dome-cap shape; 12-spoke radial ribs. | Brown + cream |
| 139 | Cactus_Column_Planter.json | `R·(1+0.22cos11θ)` — 11 deep ridges (odd number creates the non-repeating angular feel of a cactus). | Cactus green |
| 140 | Agate_Slice_Vase.json | Agate veins: `sin(16πv+0.6sin5θ)` — the angular modulation inside the band argument bends the horizontal rings sideways, simulating agate's characteristic curved banding. | Stone + red + white |

### Mineral / Material Palette Pieces

| # | File | Material Inspiration | Colors |
|---|------|-------------------|--------|
| 141 | Lapis_Column_Planter.json | Lapis lazuli veining: `sin(6πv+1.2θ)+sin(9πv−0.8θ)` and `sin(11πv+0.5θ)+sin(7πv−1.4θ)` — two pairs of diagonal vein patterns with different angular winding rates | Deep lapis blue + gold + cobalt |
| 142 | Jade_Melon_Pot.json | Refined 8-lobe jade melon: `R·(1+0.12cos8θ)·(1+0.10sinπv)` — soft ribs, restrained depth, jade green + white fenestration patterns. Minimal and elegant. | Jade green + white |
| 143 | Obsidian_Prism_Pot.json | `R·(1+0.22·atan(14cos6θ))` — very high-gain atan creates extremely sharp prismatic faces on a 6-sided form. Near-black obsidian + edge-silver highlight. | Near-black + silver |
| 144 | Rose_Quartz_Orb.json | Spherical egg `R·(1+0.14cosφ−0.06cos2φ)` + quasi-interference quartz texture `sin(8θ+5φ)+0.4sin(13θ−8φ)` — mineral structure in a soft ovoid form. | Rose + blush + mauve |
| 145 | Chaos_Engine_Vase.json | 6-harmonic Fourier base + 3-term saturated atan texture + dual neon moiré patterns + braided drift modifier + torsion distortion. Every layer at high intensity simultaneously. | Black + neon colors |

### Grand Finale Pieces

| # | File | All-System Concept | Colors |
|---|------|-------------------|--------|
| 146 | Frozen_Wave_Column.json | `R·(1+0.20sinπv)·(1+0.16sin(6θ+8πv)·exp(−(v−0.5)²·4))` — a standing wave body with a wave crest frozen mid-body. Anti-gravity lean distortion as if the wave is airborne. | Ice + deep navy |
| 147 | Echo_Spiral_Tower.json | 4-level self-similar spiral: `0.14cos(4θ+3πv)+0.07cos(8θ+6πv)+0.035cos(16θ+12πv)+0.018cos(32θ+24πv)` — strict doubling in both angular and vertical frequency at each level. Log-ripple texture + braided drift + torsion. Max resolution 240×180. | Brass + bronze |
| 148 | Quantum_Foam_Orb.json | Spherical 5-frequency irrational-winding quasi-random base using √2, √3, √5, √7, √11 — no pattern repeats in any direction. Saturated atan texture. Torsion distortion `0.18·v^1.4`. Max resolution 240×200. | Deep violet + electric blue + pink |
| 149 | Transcendent_Vessel.json | Spherical quasi-lattice 4-frequency irrational base + 4-term audio ripple shell texture + dual moiré window patterns + multi-direction flower modifier + fluid twist XYZ with shoulder Gaussian + base gravity sag (dy). Every system active simultaneously at high strength. Max resolution 240×200. | Black + gold + cyan + white |
| 150 | Omega_Point_Vessel.json | **The Masterpiece.** Spherical body with equatorial bell swell `(1+0.14sin²φ−0.04cosφ)` × 6-frequency irrational quasi-crystal lattice using √2, √3, √5, √7, √11, √13. 6-component audio ripple shell texture. Dual `smoothstep` moiré windows. 5-term multi-direction flower modifier strength 0.42. Fluid twist XYZ with 4 simultaneous Gaussian peaks at different heights + sinusoidal rotation + base gravity sag. Every parameter at or near the design ceiling. Max resolution 240×200. | Pure black + 24k gold + electric cyan + blinding white |

---

## Quick Reference — All 150 Files

| # | File | Coord | Mode | Modifier | Distortion |
|---|------|-------|------|----------|------------|

| # | File | Coord | Mode | Modifier | Distortion |
|---|------|-------|------|----------|------------|
| 1 | Zen_Stone_Vessel.json | cylindrical | pot | none | none |
| 2 | Linen_Ridge_Bowl.json | cylindrical | potplate | none | none |
| 3 | Moss_Weave_Planter.json | cylindrical | pot | none | none |
| 4 | Hex_Column_Planter.json | cylindrical | potplate | none | none |
| 5 | Twisted_Terracotta_Urn.json | cylindrical | pot | twist | none |
| 6 | Petal_Orb_Pod.json | spherical | pot | petal | none |
| 7 | Lattice_Lantern.json | cylindrical | potplate | interference | none |
| 8 | Chromatic_Bloom.json | cylindrical | pot | interference | none |
| 9 | Storm_Vortex_Planter.json | cylindrical | pot | interference | swirl |
| 10 | Hypno_Spiral_Vessel.json | cylindrical | pot | interference | torsion |
| 11 | Carved_Obsidian_Column.json | cylindrical | pot | regional | none |
| 12 | Coral_Scallop_Vase.json | cylindrical | potplate | none | none |
| 13 | Hourglass_Wind_Planter.json | cylindrical | pot | none | wind |
| 14 | Superellipse_Modern_Pot.json | cylindrical | potplate | none | none |
| 15 | Dragon_Egg_Orb.json | spherical | pot | none | none |
| 16 | Folded_Panel_Column.json | cylindrical | pot | diagonal | none |
| 17 | Rim_Vortex_Bowl.json | cylindrical | potplate | none | swirl |
| 18 | Pulsing_Frequency_Vase.json | cylindrical | pot | none | none |
| 19 | Desert_Barrel_Cactus_Pot.json | cylindrical | pot | none | pressure |
| 20 | Interference_Lantern_Orb.json | spherical | potplate | twist | torsion |
| 21 | Soft_Egg_Pod.json | spherical | pot | none | none |
| 22 | Pinched_Neck_Vase.json | cylindrical | pot | none | none |
| 23 | Beveled_Octagon_Tower.json | cylindrical | potplate | none | none |
| 24 | Bamboo_Segment_Column.json | cylindrical | pot | none | none |
| 25 | Gourd_Planter.json | cylindrical | pot | none | none |
| 26 | Dense_Rib_Tower.json | cylindrical | pot | none | none |
| 27 | Woven_Spiral_Basket.json | cylindrical | pot | twist | none |
| 28 | Scalloped_Shell_Vase.json | cylindrical | potplate | none | none |
| 29 | Knurled_Grip_Cylinder.json | cylindrical | pot | none | none |
| 30 | Topographic_Rings_Planter.json | cylindrical | potplate | none | none |
| 31 | Harlequin_Diamond_Vase.json | cylindrical | pot | none | none |
| 32 | Flame_Torch_Vase.json | cylindrical | pot | diagonal | none |
| 33 | Barley_Twist_Column.json | cylindrical | pot | twist | none |
| 34 | Braided_Rope_Vessel.json | cylindrical | pot | interference | none |
| 35 | Leaning_Tower_Planter.json | cylindrical | pot | none | basicEffect |
| 36 | Gravity_Sag_Bowl.json | cylindrical | potplate | none | gravity |
| 37 | Double_Dent_Barrel.json | cylindrical | pot | none | pressure |
| 38 | Torsion_Spire.json | cylindrical | pot | none | torsion |
| 39 | Circuit_Board_Column.json | cylindrical | pot | diagonal | none |
| 40 | Volcanic_Crater_Bowl.json | cylindrical | pot | none | custom |
| 41 | Crystal_Shard_Planter.json | cylindrical | pot | none | none |
| 42 | Ocean_Wave_Planter.json | cylindrical | potplate | none | none |
| 43 | Nautilus_Shell_Vase.json | cylindrical | pot | petal | none |
| 44 | Northern_Lights_Column.json | cylindrical | pot | interference | none |
| 45 | Raku_Fire_Bowl.json | cylindrical | potplate | none | none |
| 46 | Honeycomb_Beeswax_Tower.json | cylindrical | pot | none | none |
| 47 | Plasma_Field_Vase.json | cylindrical | pot | diagonal | none |
| 48 | Marble_Column_Planter.json | cylindrical | potplate | none | none |
| 49 | Hourglass_Pinch_Pod.json | spherical | pot | none | none |
| 50 | Fractal_Bloom_Supreme.json | cylindrical | pot | interference | torsion |
| 51 | Elliptical_Column_Planter.json | cylindrical | potplate | none | none |
| 52 | Tall_Oval_Vase.json | cylindrical | pot | none | none |
| 53 | Shield_Profile_Bowl.json | cylindrical | potplate | none | none |
| 54 | Blunt_Triangle_Column.json | cylindrical | pot | twist | none |
| 55 | Barrel_Oval_Planter.json | cylindrical | pot | none | none |
| 56 | Rounded_Rectangle_Trough.json | cylindrical | potplate | none | none |
| 57 | Soft_Pentagon_Tower.json | cylindrical | pot | none | none |
| 58 | Pillow_Square_Pot.json | cylindrical | potplate | none | none |
| 59 | Bloomfold_Vase.json | cylindrical | pot | twist | none |
| 60 | Petal_Morph_Vase.json | cylindrical | pot | petal | none |
| 61 | Twisted_Trifold_Bloom.json | cylindrical | pot | diagonal | none |
| 62 | Nested_Warp_Blossom.json | cylindrical | pot | petal | none |
| 63 | Antenna_Migration_Tower.json | cylindrical | pot | regional | none |
| 64 | DNA_Double_Helix_Vase.json | cylindrical | pot | interference | none |
| 65 | Harmonic_Oscillator_Vase.json | cylindrical | pot | none | none |
| 66 | Fractal_Growth_Column.json | cylindrical | pot | none | none |
| 67 | Domain_Warp_Rib_Planter.json | cylindrical | pot | petal | none |
| 68 | Terraced_Contour_Bowl.json | cylindrical | potplate | none | none |
| 69 | Log_Ripple_Vase.json | cylindrical | pot | diagonal | none |
| 70 | Saturated_Moire_Tower.json | cylindrical | pot | interference | none |
| 71 | Diamond_Carve_Planter.json | cylindrical | pot | none | none |
| 72 | ATan_Braid_Column.json | cylindrical | pot | interference | none |
| 73 | Quasi_Helix_Window_Vessel.json | cylindrical | pot | interference | none |
| 74 | Crisp_Window_Tower.json | cylindrical | pot | interference | none |
| 75 | Equatorial_Arc_Belt_Bowl.json | cylindrical | potplate | none | none |
| 76 | ATan_Gate_Bands_Vase.json | cylindrical | pot | regional | none |
| 77 | Progressive_Lobe_Tower.json | cylindrical | pot | none | none |
| 78 | Spiral_Triple_Helix_Vessel.json | cylindrical | pot | twist | none |
| 79 | Petal_Belt_Vessel.json | cylindrical | pot | none | none |
| 80 | Lotus_Crown_Planter.json | cylindrical | potplate | regional | none |
| 81 | Gusted_Wind_Tall_Vase.json | cylindrical | pot | none | wind |
| 82 | Diagonal_Sag_Bowl.json | cylindrical | potplate | none | gravity |
| 83 | Crown_Eddy_Orb.json | spherical | pot | none | swirl |
| 84 | Fluid_Twist_Column.json | cylindrical | pot | none | torsion |
| 85 | Counter_Twist_Column.json | cylindrical | pot | none | torsion |
| 86 | Palm_Press_Organic.json | cylindrical | pot | none | pressure |
| 87 | Sway_Wave_Planter.json | cylindrical | pot | none | wind |
| 88 | Fibonacci_Spirals_Orb.json | spherical | pot | diagonal | none |
| 89 | Coral_Brain_Orb.json | spherical | pot | petal | none |
| 90 | Bell_Orb_Pod.json | spherical | pot | none | none |
| 91 | Aerospace_Isogrid_Orb.json | spherical | pot | twist | none |
| 92 | Crown_Splash_Orb.json | spherical | pot | twist | none |
| 93 | Harmonic_Beats_Vase.json | cylindrical | pot | regional | none |
| 94 | Phase_Drift_Shell_Vase.json | cylindrical | pot | interference | none |
| 95 | Braided_Spiral_Orb_Pot.json | spherical | pot | interference | none |
| 96 | Nonlinear_Chevron_Vase.json | cylindrical | pot | diagonal | none |
| 97 | Stepped_Crown_Phase_Column.json | cylindrical | pot | regional | none |
| 98 | Moire_Orb_Pot.json | spherical | pot | none | torsion |
| 99 | Irrational_Weave_Orb.json | spherical | pot | twist | torsion |
| 100 | Absolute_Pinnacle.json | spherical | pot | interference | torsion |
| 101 | Limacon_Planter.json | cylindrical | potplate | none | none |
| 102 | Rose_Curve_Column.json | cylindrical | pot | none | none |
| 103 | Star_Polygon_Vase.json | cylindrical | pot | diagonal | none |
| 104 | Squircle_Tower.json | cylindrical | pot | none | none |
| 105 | Hypocycloid_Bowl.json | cylindrical | potplate | none | none |
| 106 | Gear_Tooth_Column.json | cylindrical | pot | none | none |
| 107 | Spring_Coil_Tower.json | cylindrical | pot | twist | none |
| 108 | Fractal_Snowflake_Vase.json | cylindrical | pot | none | none |
| 109 | Involute_Column.json | cylindrical | pot | none | none |
| 110 | Turbine_Vane_Planter.json | cylindrical | pot | diagonal | none |
| 111 | Sunflower_Spiral_Orb.json | spherical | pot | none | none |
| 112 | Pinecone_Scale_Orb.json | spherical | pot | none | none |
| 113 | Seashell_Spiral_Vase.json | cylindrical | pot | none | none |
| 114 | Ammonite_Chamber_Bowl.json | cylindrical | potplate | none | none |
| 115 | Leaf_Vein_Column.json | cylindrical | pot | none | none |
| 116 | Guilloche_Tower.json | cylindrical | pot | none | none |
| 117 | Celtic_Knot_Vessel.json | cylindrical | pot | none | none |
| 118 | Fingerprint_Bowl.json | cylindrical | potplate | none | none |
| 119 | Islamic_Star_Planter.json | cylindrical | potplate | none | none |
| 120 | Hammered_Copper_Vase.json | cylindrical | pot | none | none |
| 121 | Triple_Dent_Cylinder.json | cylindrical | pot | none | pressure |
| 122 | Helix_Lean_Tower.json | cylindrical | pot | none | wind |
| 123 | Inflated_Belly_Pot.json | cylindrical | pot | none | pressure |
| 124 | Earthquake_Shear_Vase.json | cylindrical | pot | none | basicEffect |
| 125 | Accordion_Squeeze_Tower.json | cylindrical | pot | none | pressure |
| 126 | Mondrian_Grid_Column.json | cylindrical | pot | none | none |
| 127 | Zebra_Spiral_Vase.json | cylindrical | pot | none | none |
| 128 | Brick_Wall_Planter.json | cylindrical | potplate | none | none |
| 129 | Acid_Moire_Vessel.json | cylindrical | pot | interference | none |
| 130 | Aurora_Column.json | cylindrical | pot | none | none |
| 131 | Galaxy_Orb.json | spherical | pot | diagonal | none |
| 132 | Toroidal_Ring_Pot.json | cylindrical | pot | none | none |
| 133 | Rippled_Membrane_Orb.json | spherical | pot | twist | none |
| 134 | Moebius_Drift_Vase.json | cylindrical | pot | twist | none |
| 135 | Ribbed_Melon_Planter.json | cylindrical | pot | none | none |
| 136 | Pumpkin_Planter.json | cylindrical | pot | none | none |
| 137 | Tulip_Vase.json | cylindrical | pot | petal | none |
| 138 | Mushroom_Cap_Bowl.json | spherical | potplate | none | none |
| 139 | Cactus_Column_Planter.json | cylindrical | pot | none | none |
| 140 | Agate_Slice_Vase.json | cylindrical | potplate | none | none |
| 141 | Lapis_Column_Planter.json | cylindrical | pot | none | none |
| 142 | Jade_Melon_Pot.json | cylindrical | pot | none | none |
| 143 | Obsidian_Prism_Pot.json | cylindrical | pot | none | none |
| 144 | Rose_Quartz_Orb.json | spherical | pot | none | none |
| 145 | Chaos_Engine_Vase.json | cylindrical | pot | interference | torsion |
| 146 | Frozen_Wave_Column.json | cylindrical | pot | none | wind |
| 147 | Echo_Spiral_Tower.json | cylindrical | pot | interference | torsion |
| 148 | Quantum_Foam_Orb.json | spherical | pot | twist | torsion |
| 149 | Transcendent_Vessel.json | spherical | pot | interference | torsion |
| 150 | Omega_Point_Vessel.json | spherical | pot | interference | torsion |
