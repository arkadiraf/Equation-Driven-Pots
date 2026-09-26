// Regression check for EquationDrivenWovenPots.html.
//
// Open  EquationDrivenWovenPots.html#regression  in a browser. The page loads this file, builds
// every case below with the page's own buildMesh (never from the form, so whatever the sidebar
// happens to show does not matter), fingerprints each result and compares it with EXPECTED.
// The panel lists every case as PASS / FAIL / NEW, with what differs.
//
// A fingerprint is exact, not approximate: triangle count, a position-weighted checksum of every
// vertex (to 1e-6), the bounding box (to 1e-9), the debris count and - for colour builds - the
// same for every colour part and plate part. Any change to the geometry shows up; a change that
// only moves code around does not.
//
// When a change is MEANT to alter geometry: run it, check that only the cases you expected
// failed and why, then press "Copy new fingerprints" and paste the result over EXPECTED below.
// Record the reason in the commit message.
//
// Scripted runs: WovenRegression.run() resolves to { passed, failed, fresh, results, fingerprints }
// and the result is also left on window.wovenRegressionResult.
(function () {
    // The default Torus Knot pot, single strand, every option off - written out in full so a
    // case never depends on the sidebar, the browser's form restore or DEFAULT_DESIGN_CONFIG.
    const BASE = {
        type: 'Torus Knot', params: { p: 2, q: 3, amp: 3.5, phase: 0, wave: 0, taper: 0 }, plateMode: 'silhouette', pathExpr: null,
        eq: '1.0', diameter: 20, zStretch: 8, sections: 400, radialRes: 48, shellThick: 0.35, doHollow: false, mode: 'pot',
        avoidSelfIntersect: false, extraClean: false, bottomCutPct: 10, topCutPct: 90, drainHoleDiam: 1, debrisPct: 0.1, bottomThick: 0.35,
        rotX: 0, rotY: 0, rotZ: 0, texEq: '0', texIntensity: 0.15, patternEq1: '-1', patternEq2: '-1',
        baseColor: '#c12e1f', patternColor1: '#0056b8', patternColor2: '#5f4a8b', overlapColor: '#8ab04d',
        patternDepthCm: 0.12, includePlate: true, applyPlateColoring: true, plateOffsetCm: 1.5, plateHeightCm: 1.5,
        plateWallThickness: 0.35, plateBaseThickness: 0.35, plateOpeningAngleDeg: 25, plateSmoothDeg: 10,
        smoothPatternEdges: true, boundaryRefine: 2, patternResU: 400, patternResT: 48,
        vaseInsertEnabled: false, vaseBaseDiameter: 3, vaseTopDiameter: 4, vaseHeight: 8, vaseInsertOffsetCm: 0.1, vaseWallCm: 0.1,
        strands: { mode: 'off', count: 1, stepDeg: null, zOffCm: 0, rOffCm: 0, counterWind: false, cableD: 1, cableT: 6, altScale: 1,
                   crossMode: 'merge', crossClrMm: 1, crossLenCm: 3, crossParity: 0, colourByStrand: false }
    };
    // Built-in path defaults, straight from pathLib (so a changed default is a deliberate, visible diff).
    const pathCase = (type, over) => () => {
        const entry = pathLib[type];
        const params = {}; for (const p of entry.params) params[p.id] = p.val;
        return Object.assign({}, BASE, { type, params, plateMode: entry.plateMode || 'silhouette', rotY: entry.defaultRotY || 0,
            pathExpr: entry.custom ? { x: entry.x, y: entry.y, z: entry.z } : null }, over || {});
    };
    const strands = over => Object.assign({}, BASE.strands, over);
    const lowColour = { sections: 160, radialRes: 24, patternResU: 160, patternResT: 24,
        patternEq1: 'sin(8*theta + 12*pi*u)', patternEq2: 'cos(10*pi*v)' };

    // [name, cfg factory, build colours?]
    const CASES = [
        ['torus pot',              pathCase('Torus Knot')],
        ['spherical pot',          pathCase('Spherical Knot')],
        ['coiled basket pot',      pathCase('Coiled Basket')],
        ['flower ring pot',        pathCase('Flower Ring', { params: { n: 5, amp: 3, weave: 0.3 } })],
        ['braided loop pot',       pathCase('Braided Loop')],
        ['mobius pot',             pathCase('Mobius Curve')],
        ['lissajous pot',          pathCase('Lissajous Tangle')],
        ['custom rosette pot',     pathCase('Custom Path')],
        ['torus object solid',     pathCase('Torus Knot', { mode: 'object' })],
        ['torus object hollow',    pathCase('Torus Knot', { mode: 'object', doHollow: true })],
        ['torus pot hollow',       pathCase('Torus Knot', { doHollow: true })],
        ['torus pinch',            pathCase('Torus Knot', { eq: '2.2', avoidSelfIntersect: true })],
        ['mobius hollow clean',    pathCase('Mobius Curve', { doHollow: true, extraClean: true })],
        ['torus texture',          pathCase('Torus Knot', { texEq: '0.6*cos(8*theta + 8*pi*u)', texIntensity: 0.15 })],
        // Wide enough to reach the strands - the knot's own centre is empty, so the stock 3-4 cm vase cuts nothing.
        ['torus vase insert',      pathCase('Torus Knot', { doHollow: true, vaseInsertEnabled: true, vaseBaseDiameter: 14, vaseTopDiameter: 16 })],
        ['colour smooth',          pathCase('Torus Knot', Object.assign({ smoothPatternEdges: true, boundaryRefine: 1 }, lowColour)), true],
        ['colour stepped',         pathCase('Torus Knot', Object.assign({ smoothPatternEdges: false }, lowColour)), true],
        ['colour stepped custom',  pathCase('Custom Path', Object.assign({ smoothPatternEdges: false }, lowColour)), true],
        ['strands wound 3',        pathCase('Torus Knot', { eq: '1.2', strands: strands({ mode: 'wound', count: 3 }) })],
        ['strands cable lissajous', pathCase('Lissajous Tangle', { eq: '0.5', strands: strands({ mode: 'cable', count: 3, cableD: 0.6, cableT: 6 }) })],
        ['strands expression',     pathCase('Custom Path', { eq: '0.8', pathExpr: { x: '(rx + c*cos(a*t)) * cos(t + b*sin(a*t) + sp/a)', y: '(rx + c*cos(a*t)) * sin(t + b*sin(a*t) + sp/a)', z: 'zA * sin(a*t)' },
                                       strands: strands({ mode: 'expression', count: 3 }) })],
        ['strands over-under',     pathCase('Torus Knot', { mode: 'object', strands: strands({ mode: 'wound', count: 2, counterWind: true, crossMode: 'alternate' }) })],
        ['strands pinch + clean',  pathCase('Torus Knot', { eq: '2.2', doHollow: true, extraClean: true, strands: strands({ mode: 'wound', count: 3 }) })],
        ['strands colour-by',      pathCase('Torus Knot', { eq: '1.2', sections: 200, strands: strands({ mode: 'wound', count: 3, colourByStrand: true }) }), true],
        ['strands pattern',        pathCase('Torus Knot', Object.assign({ eq: '1.2', smoothPatternEdges: false, strands: strands({ mode: 'wound', count: 3 }) }, lowColour)), true],
    ];

    // Paste "Copy new fingerprints" output here.
    const EXPECTED = {
        "torus pot": {"tris": 31832, "sum": "465.962776", "bbox": "-12.039290428,-13.835605621,-7.199481487,14.499827385,13.835605621,7.199481487", "debris": 0, "plate": "4:1800:-27974.544683"},
        "spherical pot": {"tris": 29514, "sum": "-76.848148", "bbox": "-9.589837074,-13.129414558,-6.872916698,14.499032974,13.129356384,6.872982502", "debris": 0, "plate": "4:1800:-26735.087301"},
        "coiled basket pot": {"tris": 30802, "sum": "273481.061017", "bbox": "-13.401871681,-13.442605972,-0.000080307,12.999370575,12.786536217,7.999276638", "debris": 0, "plate": "4:1800:2099.964475"},
        "flower ring pot": {"tris": 33170, "sum": "-70.622621", "bbox": "-12.771068573,-13.689977646,-7.199999809,13.999716759,13.690008163,7.199999332", "debris": 0, "plate": "4:1800:-27936.198889"},
        "braided loop pot": {"tris": 32342, "sum": "145.050722", "bbox": "-9.500000000,-13.043921471,-7.384907722,14.499852180,13.043933868,7.384921074", "debris": 0, "plate": "4:1800:-28554.731324"},
        "mobius pot": {"tris": 30150, "sum": "39045.711429", "bbox": "-8.932181358,-16.884317398,-8.632019997,8.932168007,16.884305954,15.929646492", "debris": 0, "plate": "4:1800:-32899.289343"},
        "lissajous pot": {"tris": 34806, "sum": "-2860.344892", "bbox": "-10.999569893,-10.999853134,-7.199997425,10.999454498,10.998447418,7.199997425", "debris": 0, "plate": "4:1800:-27760.476043"},
        "custom rosette pot": {"tris": 33816, "sum": "-35.107067", "bbox": "-13.500000000,-12.640898705,-7.199998379,13.499709129,12.640897751,7.199996948", "debris": 0, "plate": "4:1798:-27660.399941"},
        "torus object solid": {"tris": 38400, "sum": "-100.161022", "bbox": "-12.039290428,-13.835605621,-8.999351501,14.499827385,13.835605621,8.999351501", "debris": 0},
        "torus object hollow": {"tris": 76800, "sum": "241.291307", "bbox": "-12.039290428,-13.835605621,-8.999351501,14.499827385,13.835605621,8.999351501", "debris": 0},
        "torus pot hollow": {"tris": 61494, "sum": "14026.328374", "bbox": "-12.039290428,-13.835605621,-7.199481487,14.499827385,13.835605621,7.199481487", "debris": 0, "plate": "4:1800:-27974.544683"},
        "torus pinch": {"tris": 34560, "sum": "148.396656", "bbox": "-13.236684799,-15.035589218,-8.158859253,15.699620247,15.035589218,8.158859253", "debris": 0, "plate": "4:1800:-31356.750227"},
        "mobius hollow clean": {"tris": 59914, "sum": "83013.705696", "bbox": "-8.932181358,-16.884317398,-8.632019997,8.932168007,16.884305954,15.929646492", "debris": 0, "plate": "4:1800:-32899.289343"},
        "torus texture": {"tris": 32236, "sum": "339.446460", "bbox": "-12.065394402,-13.914165497,-7.268837452,14.589811325,13.914164543,7.268837929", "debris": 0, "plate": "4:1800:-27982.378483"},
        "torus vase insert": {"tris": 44222, "sum": "-27369.075464", "bbox": "-12.039290428,-13.835605621,-7.199481487,14.499827385,13.835605621,7.199481487", "debris": 0, "plate": "4:1800:-27974.544683"},
        "colour smooth": {"tris": 7052, "sum": "215.997169", "bbox": "-12.032850266,-13.823513031,-7.199500084,14.498920441,13.823511124,7.199504375", "debris": 0, "parts": "0:7076:41.385911 1:64574:819.209810 2:72700:-6619.929942 3:72698:665.968793", "plate": "4:2880:-45107.967178 5:28636:-452144.246182 6:34626:-563465.938711 7:34724:-565211.374200"},
        "colour stepped": {"tris": 7052, "sum": "215.997169", "bbox": "-12.032850266,-13.823513031,-7.199500084,14.498920441,13.823511124,7.199504375", "debris": 0, "parts": "0:7076:41.385911 1:27286:-6877.866228 2:27378:-17901.644510 3:27226:-222.665896", "plate": "4:2880:-45107.967178 5:28636:-452144.246182 6:34626:-563465.938711 7:34724:-565211.374200"},
        "colour stepped custom": {"tris": 8028, "sum": "239.024746", "bbox": "-13.499999046,-12.632012367,-7.193651676,13.498188972,12.631807327,7.194017410", "debris": 0, "parts": "0:8028:103.021881 1:41790:413.562446 2:35274:-19237.048242 3:35290:18721.374503", "plate": "4:2880:-45183.413245 5:28640:-451937.526069 6:34584:-561310.266114 7:34726:-563142.716278"},
        "strands wound 3": {"tris": 98184, "sum": "-1889.228238", "bbox": "-14.398468971,-14.623079300,-7.359377384,14.699792862,14.620594978,7.359377861", "debris": 0, "plate": "4:1800:-28427.295580"},
        "strands cable lissajous": {"tris": 111708, "sum": "-31647.851109", "bbox": "-11.086391449,-11.062388420,-7.279013634,11.085872650,11.048897743,7.279230595", "debris": 0, "plate": "4:1800:-27360.885125"},
        "strands expression": {"tris": 95100, "sum": "94.826783", "bbox": "-13.300000191,-13.202732086,-7.039998531,13.299767494,13.202737808,7.039997578", "debris": 0, "plate": "4:1800:-27295.490961"},
        "strands over-under": {"tris": 76800, "sum": "-74.224532", "bbox": "-14.497120857,-14.724132538,-8.999578476,14.499827385,14.733332634,8.999534607", "debris": 0},
        "strands pinch + clean": {"tris": 277422, "sum": "67498.232477", "bbox": "-15.397548676,-15.622204781,-8.158859253,15.699620247,15.619665146,8.158859253", "debris": 0, "plate": "4:1798:-31427.644551"},
        "strands colour-by": {"tris": 51312, "sum": "-2030.178973", "bbox": "-14.398456573,-14.623083115,-7.359390736,14.699171066,14.620474815,7.359393120", "debris": 0, "parts": "0:17268:-2022.782971 1:17280:-1486.286792 2:17302:1173.414895", "plate": "4:1800:-28442.928987"},
        "strands pattern": {"tris": 21588, "sum": "125.087389", "bbox": "-14.394639969,-14.619270325,-7.359399796,14.698704720,14.607286453,7.359405518", "debris": 0, "parts": "0:21552:984.365768 1:85350:4296.284175 2:85290:-22028.968316 3:85462:24775.689951", "plate": "4:2880:-46252.867665 5:28640:-461100.163861 6:34622:-576400.224600 7:34620:-574379.618242"}
    };

    function checksum(a) { let s = 0; for (let i = 0; i < a.length; i++) s += a[i] * ((i % 7) + 1); return s.toFixed(6); }
    function bboxOf(a) {
        const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
        for (let i = 0; i < a.length; i += 3) for (let k = 0; k < 3; k++) { const v = a[i + k]; if (v < lo[k]) lo[k] = v; if (v > hi[k]) hi[k] = v; }
        return lo.concat(hi).map(v => v.toFixed(9)).join(',');
    }
    const partPrint = p => `${p.state}:${p.indices.length / 3}:${checksum(p.positions)}`;
    function fingerprint(geo) {
        const u = geo.userData, pos = geo.attributes.position.array;
        const fp = { tris: geo.index.count / 3, sum: checksum(pos), bbox: bboxOf(pos), debris: u.debrisRemoved || 0 };
        if (u.patternParts) fp.parts = u.patternParts.map(partPrint).join(' ');
        if (u.plateParts) fp.plate = u.plateParts.map(partPrint).join(' ');
        return fp;
    }
    function diff(want, got) {
        const out = [];
        for (const k of new Set([...Object.keys(want), ...Object.keys(got)])) if (String(want[k]) !== String(got[k])) out.push(`${k}: ${want[k]} → ${got[k]}`);
        return out;
    }

    let panel;
    function ensurePanel() {
        if (panel) return panel;
        panel = document.createElement('div');
        panel.style.cssText = 'position:fixed;left:16px;right:16px;bottom:16px;max-height:55vh;overflow:auto;z-index:9999;background:#fff;color:#222;border:1px solid #bbb;border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,.25);padding:12px 14px;font:12px/1.45 Consolas,monospace';
        document.body.appendChild(panel);
        return panel;
    }
    function render(state) {
        const p = ensurePanel();
        const rows = state.results.map(r => {
            const colour = r.status === 'PASS' ? '#1e8449' : r.status === 'NEW' ? '#b9770e' : '#c0392b';
            const detail = r.error ? ` - ${r.error}` : r.diffs && r.diffs.length ? '<br>&nbsp;&nbsp;' + r.diffs.map(d => d.replace(/</g, '&lt;')).join('<br>&nbsp;&nbsp;') : '';
            return `<div><b style="color:${colour}">${r.status.padEnd(4)}</b> ${r.name} <span style="color:#888">${r.ms} ms</span>${detail}</div>`;
        }).join('');
        const head = state.done
            ? `<b>Regression: ${state.passed} passed, ${state.failed} failed, ${state.fresh} new</b> of ${CASES.length} cases`
            : `<b>Regression: running ${state.results.length + 1} / ${CASES.length}…</b>`;
        p.innerHTML = `<div style="display:flex;gap:8px;align-items:center;margin-bottom:6px">${head}
            <span style="flex:1"></span>
            ${state.done ? '<button id="regCopy">Copy new fingerprints</button>' : ''}
            <button id="regClose">Close</button></div>${rows}
            ${state.done ? '<textarea id="regOut" style="width:100%;height:80px;margin-top:8px;font:11px Consolas,monospace"></textarea>' : ''}`;
        p.querySelector('#regClose').onclick = () => p.remove();
        if (state.done) {
            const ta = p.querySelector('#regOut');
            ta.value = JSON.stringify(state.fingerprints, null, 2);
            p.querySelector('#regCopy').onclick = () => { ta.select(); try { navigator.clipboard.writeText(ta.value); } catch (e) { document.execCommand('copy'); } };
        }
    }

    const tick = () => new Promise(r => setTimeout(r, 0));
    async function run() {
        while (!window.CSG) await new Promise(r => setTimeout(r, 200));
        const state = { results: [], fingerprints: {}, passed: 0, failed: 0, fresh: 0, done: false };
        render(state);
        for (const [name, make, colours] of CASES) {
            await tick();
            const t0 = performance.now();
            let entry;
            try {
                const geo = buildMesh(make(), 1, { colors: !!colours });
                const fp = fingerprint(geo);
                state.fingerprints[name] = fp;
                const want = EXPECTED[name];
                const diffs = want ? diff(want, fp) : [];
                entry = { name, status: !want ? 'NEW' : diffs.length ? 'FAIL' : 'PASS', diffs };
            } catch (e) {
                entry = { name, status: 'FAIL', error: e.message };
            }
            entry.ms = Math.round(performance.now() - t0);
            state[entry.status === 'PASS' ? 'passed' : entry.status === 'NEW' ? 'fresh' : 'failed']++;
            state.results.push(entry);
            render(state);
        }
        state.done = true;
        render(state);
        console.log(`Woven regression: ${state.passed} passed, ${state.failed} failed, ${state.fresh} new`);
        window.wovenRegressionResult = state;
        return state;
    }

    window.WovenRegression = { run, CASES, BASE, fingerprint };
    if (/regression/.test(location.hash + location.search)) run();
})();
