/* Bambu Studio project export (.3mf), shared by EquationDrivenPotDesigner.html,
   EquationDrivenBowls.html and EquationDrivenWovenPots.html. Needs JSZip, and exposes a single
   global, BambuExport, so none of its names collide with the pages' own.

   One .3mf that Bambu Studio opens as a finished project. Each printed object (pot, plate,
   bowl, ring stand...) gets its own build plate. Every color is assigned to a filament slot
   holding Bambu PLA Basic in that color. A page hands in its objects already in printer
   coordinates (millimetres, Z up). A part is either a closed body in one color, or a closed body
   painted per triangle, which Bambu stores as multi-material painting.

   project_settings.config carries preset NAMES plus the filament slots, the purge matrix and the
   sparse infill density. Bambu Studio looks each name up in its own system profiles and rebuilds
   that system preset, keeping only the keys listed in different_settings_to_system
   (PresetCollection::load_external_preset -> update_non_diff_values_to_base_config). Only the
   infill densities are listed. So the file never ships stale temperatures or G-code and does not
   raise the "modified G-code" warning. Names are from Bambu Studio 02.05
   resources/profiles/BBL; every printer uses its 0.4 mm nozzle and 0.20mm Standard process. */
const BambuExport = (() => {
    'use strict';

    // Bambu Lab PLA Basic palette (see PLA_Colors.txt).
    const PLA_BASIC_COLORS = [
        ['Jade White', '#FFFFFF'], ['Beige', '#F7E6DE'], ['Gold', '#E4BD68'], ['Silver', '#A6A9AA'],
        ['Gray', '#8E9089'], ['Bronze', '#847D48'], ['Brown', '#9D432C'], ['Cocoa Brown', '#6F5034'],
        ['Maroon Red', '#9D2235'], ['Red', '#C12E1F'], ['Magenta', '#EC008C'], ['Pink', '#F55A74'],
        ['Hot Pink', '#F5547C'], ['Orange', '#FF6A13'], ['Pumpkin Orange', '#FF9016'],
        ['Sunflower Yellow', '#FEC600'], ['Yellow', '#F4EE2A'], ['Bright Green', '#BECF00'],
        ['Bambu Green', '#00AE42'], ['Mistletoe Green', '#3F8E43'], ['Turquoise', '#00B1B7'],
        ['Cyan', '#0086D6'], ['Blue', '#0A2989'], ['Cobalt Blue', '#0056B8'], ['Purple', '#5E43B7'],
        ['Indigo Purple', '#482960'], ['Blue Gray', '#5B6579'], ['Light Gray', '#D1D3D5'],
        ['Dark Gray', '#545454'], ['Black', '#000000']
    ];

    // flush holds one [purge data set, minimum purge mm3] pair per nozzle, for the Standard
    // nozzle: nozzle_flush_dataset, and nozzle_volume minus the default filament retraction when
    // cutting (Plater.cpp get_min_flush_volumes).
    const PRINTERS = [
        { id: 'H2C', model: 'Bambu Lab H2C', process: '0.20mm Standard @BBL H2C', filament: 'Bambu PLA Basic @BBL H2C', flush: [[1, 96], [1, 111]], bed: [330, 320], height: 325 },
        { id: 'H2D', model: 'Bambu Lab H2D', process: '0.20mm Standard @BBL H2D', filament: 'Bambu PLA Basic @BBL H2D', flush: [[1, 130], [1, 145]], bed: [350, 320], height: 325 },
        { id: 'H2DP', model: 'Bambu Lab H2D Pro', process: '0.20mm Standard @BBL H2DP', filament: 'Bambu PLA Basic @BBL H2DP', flush: [[1, 130], [1, 145]], bed: [350, 320], height: 325 },
        { id: 'H2S', model: 'Bambu Lab H2S', process: '0.20mm Standard @BBL H2S', filament: 'Bambu PLA Basic @BBL H2S', flush: [[1, 145]], bed: [340, 320], height: 340 },
        { id: 'X1C', model: 'Bambu Lab X1 Carbon', process: '0.20mm Standard @BBL X1C', filament: 'Bambu PLA Basic @BBL X1C', flush: [[0, 63]], bed: [256, 256], height: 250 },
        { id: 'X1E', model: 'Bambu Lab X1E', process: '0.20mm Standard @BBL X1C', filament: 'Bambu PLA Basic @BBL X1C', flush: [[0, 107]], bed: [256, 256], height: 250 },
        { id: 'P2S', model: 'Bambu Lab P2S', process: '0.20mm Standard @BBL P2S', filament: 'Bambu PLA Basic @BBL P2S', flush: [[0, 110]], bed: [256, 256], height: 256 },
        { id: 'P1S', model: 'Bambu Lab P1S', process: '0.20mm Standard @BBL X1C', filament: 'Bambu PLA Basic @BBL P1S 0.4 nozzle', flush: [[0, 63]], bed: [256, 256], height: 250 },
        { id: 'A1', model: 'Bambu Lab A1', process: '0.20mm Standard @BBL A1', filament: 'Bambu PLA Basic @BBL A1', flush: [[0, 48]], bed: [256, 256], height: 256 },
        { id: 'A1M', model: 'Bambu Lab A1 mini', process: '0.20mm Standard @BBL A1M', filament: 'Bambu PLA Basic @BBL A1M', flush: [[0, 48]], bed: [180, 180], height: 180 }
    ];
    const DEFAULT_PRINTER_ID = 'H2C';
    const DEFAULT_SPARSE_INFILL = 35;
    // Written as the file's generator. From 2.0.0 on, Bambu Studio skips its pre-2.0 project
    // migration, and keeping it at 2.0 means no 2.x install warns about a newer file.
    const APP_VERSION = '02.00.00.00';
    // Bambu Studio lays build plates out in a grid with a fifth of a plate between them.
    const PLATE_GAP = 1 / 5;
    // Bambu Studio keeps these three densities in step when sparse infill is edited.
    const INFILL_DENSITY_KEYS = ['skeleton_infill_density', 'skin_infill_density', 'sparse_infill_density'];
    // Shared by all three tools, so a printer picked in one is the default in the others.
    const STORAGE_KEYS = {
        bambuPrinter: 'edp.bambuPrinter',
        bambuFilamentColors: 'edp.bambuFilamentColors',
        bambuSparseInfill: 'edp.bambuSparseInfill'
    };
    const NS_3MF_CORE = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02';
    const NS_3MF_PRODUCTION = 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06';
    const NS_BAMBU = 'http://schemas.bambulab.com/package/2021';
    const NS_RELATIONSHIPS = 'http://schemas.openxmlformats.org/package/2006/relationships';
    const REL_TYPE_3DMODEL = 'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel';

    /* ---------- export options (printer, filament colors, sparse infill) ---------- */

    // Fills the printer list and restores the last choices. The page supplies the three controls
    // (#bambuPrinter, #bambuFilamentColors, #bambuSparseInfill).
    function initOptions() {
        const printerSelect = document.getElementById('bambuPrinter');
        if (printerSelect && !printerSelect.options.length) {
            PRINTERS.forEach(p => printerSelect.add(new Option(shortModel(p), p.id)));
            printerSelect.value = DEFAULT_PRINTER_ID;
        }
        Object.entries(STORAGE_KEYS).forEach(([id, key]) => {
            const el = document.getElementById(id);
            if (!el) return;
            let saved = null;
            try { saved = localStorage.getItem(key); } catch (err) { /* storage blocked: keep the default */ }
            if (saved && (el.tagName !== 'SELECT' || Array.from(el.options).some(o => o.value === saved))) el.value = saved;
            el.addEventListener('change', () => {
                try { localStorage.setItem(key, el.value); } catch (err) { /* not persisted */ }
            });
        });
    }

    function readOptions() {
        const printerId = document.getElementById('bambuPrinter')?.value || DEFAULT_PRINTER_ID;
        const infill = parseFloat(document.getElementById('bambuSparseInfill')?.value);
        return {
            printer: PRINTERS.find(p => p.id === printerId) || PRINTERS[0],
            colorMode: document.getElementById('bambuFilamentColors')?.value === 'exact' ? 'exact' : 'pla',
            sparseInfill: Number.isFinite(infill) ? Math.min(100, Math.max(0, Math.round(infill))) : DEFAULT_SPARSE_INFILL
        };
    }

    function shortModel(printer) {
        return printer.model.replace(/^Bambu Lab /, '');
    }

    /* ---------- color matching ---------- */

    function normalizeHexColor(hex) {
        const raw = String(hex || '#FFFFFF').trim();
        const body = raw.startsWith('#') ? raw.slice(1) : raw;
        return /^[0-9a-fA-F]{6}$/.test(body) ? `#${body.toUpperCase()}` : '#FFFFFF';
    }

    function hexToRgb01(hex) {
        const n = parseInt(normalizeHexColor(hex).slice(1), 16);
        return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255];
    }

    function srgbHexToLab(hex) {
        const lin = hexToRgb01(hex).map(c => c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
        const x = (0.4124 * lin[0] + 0.3576 * lin[1] + 0.1805 * lin[2]) / 0.95047;
        const y = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
        const z = (0.0193 * lin[0] + 0.1192 * lin[1] + 0.9505 * lin[2]) / 1.08883;
        const f = t => t > 216 / 24389 ? Math.cbrt(t) : (24389 / 27 * t + 16) / 116;
        return [116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))];
    }

    // CIEDE2000 color difference. Plain Lab distance (CIE76) is badly skewed in the blues - it maps
    // #0F4D80 to Blue Gray - while this picks Cobalt Blue, as a person would.
    function deltaE2000(lab1, lab2) {
        const rad = Math.PI / 180;
        const [L1, a1, b1] = lab1;
        const [L2, a2, b2] = lab2;
        const cBar = (Math.hypot(a1, b1) + Math.hypot(a2, b2)) / 2;
        const g = 0.5 * (1 - Math.sqrt(cBar ** 7 / (cBar ** 7 + 25 ** 7)));
        const a1p = (1 + g) * a1;
        const a2p = (1 + g) * a2;
        const c1p = Math.hypot(a1p, b1);
        const c2p = Math.hypot(a2p, b2);
        const h1p = (Math.atan2(b1, a1p) / rad + 360) % 360;
        const h2p = (Math.atan2(b2, a2p) / rad + 360) % 360;
        const chromaless = c1p * c2p === 0;
        let dhp = chromaless ? 0 : h2p - h1p;
        if (dhp > 180) dhp -= 360;
        else if (dhp < -180) dhp += 360;
        const dLp = L2 - L1;
        const dCp = c2p - c1p;
        const dHp = 2 * Math.sqrt(c1p * c2p) * Math.sin(dhp * rad / 2);
        const lBarP = (L1 + L2) / 2;
        const cBarP = (c1p + c2p) / 2;
        let hBarP = h1p + h2p;
        if (!chromaless) {
            if (Math.abs(h1p - h2p) <= 180) hBarP /= 2;
            else hBarP = hBarP < 360 ? (hBarP + 360) / 2 : (hBarP - 360) / 2;
        }
        const t = 1 - 0.17 * Math.cos((hBarP - 30) * rad) + 0.24 * Math.cos(2 * hBarP * rad)
            + 0.32 * Math.cos((3 * hBarP + 6) * rad) - 0.20 * Math.cos((4 * hBarP - 63) * rad);
        const dTheta = 30 * Math.exp(-(((hBarP - 275) / 25) ** 2));
        const rc = 2 * Math.sqrt(cBarP ** 7 / (cBarP ** 7 + 25 ** 7));
        const sl = 1 + 0.015 * (lBarP - 50) ** 2 / Math.sqrt(20 + (lBarP - 50) ** 2);
        const sc = 1 + 0.045 * cBarP;
        const sh = 1 + 0.015 * cBarP * t;
        const rt = -Math.sin(2 * dTheta * rad) * rc;
        return Math.sqrt((dLp / sl) ** 2 + (dCp / sc) ** 2 + (dHp / sh) ** 2 + rt * (dCp / sc) * (dHp / sh));
    }

    // Closest Bambu PLA Basic color to an arbitrary design color, so a hand-picked hex still
    // lands on a filament that exists.
    function nearestPlaBasicColor(hex) {
        const target = srgbHexToLab(normalizeHexColor(hex));
        let best = null;
        PLA_BASIC_COLORS.forEach(([name, swatchHex]) => {
            const d = deltaE2000(target, srgbHexToLab(swatchHex));
            if (!best || d < best.d) best = { name, hex: swatchHex, d };
        });
        return { name: best.name, hex: best.hex };
    }

    /* ---------- purge volumes ----------
       Computed exactly as Bambu Studio's "Re-calculate" does (ports of libslic3r FlushVolCalc.cpp
       and FlushVolPredictor.cpp, 02.05). Checked against a real H2C project: all 1,984
       off-diagonal entries of its 32-filament matrix match. Without the matrix Bambu Studio pads
       its 2-filament default with zeros, so filaments 3+ would change with no purge at all.

       A color pair is first looked up in Bambu's measured tables (resources/flush/
       flush_data_standard.txt for data set 0, flush_data_dual_standard.txt for data set 1). Each
       color is snapped to the first table color within CIEDE2000 5. On a miss, an HSV formula is
       used instead. Entries are FROM (6 hex) + TO (6 hex) + purge mm3. */
    const FLUSH_TABLES = {
        0: {
            colors: '000000 C12E1F 00AE42 545454 D1D3D5 5B6579 F4EE2A 9D432C 5E43B7 0A2989 FF6A13 8E9089',
            pairs: '000000F4EE2A450 0000005E43B7330 C12E1FF4EE2A420 C12E1FFF6A13210 00AE42D1D3D5330 00AE42F4EE2A240 ' +
                '00AE42FF6A13270 54545400AE42180 545454D1D3D5240 545454F4EE2A270 5454545E43B7120 545454FF6A13300 ' +
                '5454548E9089120 D1D3D5F4EE2A120 D1D3D5FF6A13150 5B6579C12E1F120 5B657900AE4290 5B6579D1D3D5120 ' +
                '5B6579F4EE2A180 5B65799D432C120 5B65790A298990 5B6579FF6A13180 5B65798E908990 F4EE2A000000120 ' +
                'F4EE2AC12E1F90 F4EE2A00AE42150 F4EE2A9D432C150 F4EE2AFF6A1390 9D432C00AE42240 9D432CD1D3D5300 ' +
                '9D432CF4EE2A270 9D432CFF6A13180 9D432C8E9089210 5E43B700AE42180 5E43B7D1D3D5270 5E43B7F4EE2A270 ' +
                '5E43B79D432C150 5E43B7FF6A13270 5E43B78E9089210 0A2989C12E1F330 0A298900AE42210 0A2989545454150 ' +
                '0A2989D1D3D5450 0A29895B6579240 0A29899D432C270 0A29895E43B7180 0A2989FF6A13390 0A29898E9089270 ' +
                'FF6A13C12E1F90 FF6A13D1D3D5210 FF6A13F4EE2A210 FF6A139D432C120 FF6A138E9089180 8E9089C12E1F150 ' +
                '8E908900AE42120 8E9089D1D3D5150 8E9089F4EE2A270 8E9089FF6A13150'
        },
        1: {
            colors: '000000 FFFFFF 545454 8E9089 C12E1F F4EE2A 0086D6 F7E6DE 00AE42 5E43B7 482960 0056B8 FEC600 EC008C F5547C 6F5034 FF9016 00B1B7 BECF00',
            pairs: '000000FFFFFF900 000000545454450 0000008E9089540 000000C12E1F600 000000F4EE2A900 0000000086D6570 ' +
                '000000F7E6DE900 00000000AE42810 0000005E43B7480 000000482960270 0000000056B8540 000000FEC600900 ' +
                '000000EC008C900 000000F5547C900 000000FF9016900 00000000B1B7630 000000BECF00900 FFFFFF00000090 ' +
                'FFFFFF545454240 FFFFFF8E9089120 FFFFFFC12E1F90 FFFFFFF4EE2A90 FFFFFF0086D690 FFFFFFF7E6DE90 ' +
                'FFFFFF00AE42120 FFFFFF5E43B790 FFFFFF0056B890 FFFFFFFEC600150 FFFFFFEC008C150 FFFFFFF5547C120 ' +
                'FFFFFF6F5034120 FFFFFFFF9016120 FFFFFF00B1B7120 FFFFFFBECF0090 54545400000090 545454FFFFFF360 ' +
                '5454548E9089120 545454C12E1F270 545454F4EE2A330 5454540086D6270 545454F7E6DE390 54545400AE42270 ' +
                '5454545E43B7120 545454482960150 5454540056B8180 545454FEC600300 545454EC008C240 545454F5547C300 ' +
                '5454546F5034120 545454FF9016240 54545400B1B7270 545454BECF00300 8E9089000000270 8E9089FFFFFF330 ' +
                '8E9089545454300 8E9089C12E1F240 8E9089F4EE2A240 8E90890086D6240 8E9089F7E6DE390 8E908900AE42210 ' +
                '8E90895E43B7270 8E9089482960300 8E90890056B8180 8E9089FEC600240 8E9089EC008C240 8E9089F5547C240 ' +
                '8E90896F5034210 8E9089FF9016240 8E908900B1B7210 8E9089BECF00270 C12E1F000000150 C12E1FFFFFFF900 ' +
                'C12E1F545454300 C12E1F8E9089570 C12E1FF4EE2A450 C12E1F0086D6390 C12E1FF7E6DE630 C12E1F00AE42420 ' +
                'C12E1F5E43B7330 C12E1F482960210 C12E1F0056B8300 C12E1FFEC600660 C12E1FEC008C240 C12E1FF5547C180 ' +
                'C12E1F6F5034210 C12E1FFF9016270 C12E1F00B1B7540 C12E1FBECF00360 F4EE2A000000150 F4EE2AFFFFFF900 ' +
                'F4EE2A545454390 F4EE2A8E9089450 F4EE2AC12E1F180 F4EE2A0086D6270 F4EE2AF7E6DE570 F4EE2A00AE42120 ' +
                'F4EE2A5E43B7330 F4EE2A482960330 F4EE2A0056B8240 F4EE2AFEC60090 F4EE2AEC008C330 F4EE2AF5547C420 ' +
                'F4EE2A6F5034240 F4EE2AFF9016150 F4EE2A00B1B7360 F4EE2ABECF00240 0086D6000000150 0086D6FFFFFF420 ' +
                '0086D6545454120 0086D68E9089480 0086D6C12E1F240 0086D6F4EE2A360 0086D6F7E6DE390 0086D600AE42120 ' +
                '0086D65E43B7150 0086D6482960150 0086D60056B8120 0086D6EC008C330 0086D6F5547C330 0086D66F5034150 ' +
                '0086D6FF9016300 0086D600B1B7150 0086D6BECF00270 F7E6DE00000090 F7E6DEFFFFFF90 F7E6DE545454120 ' +
                'F7E6DE8E9089120 F7E6DEC12E1F90 F7E6DEF4EE2A60 F7E6DE0086D690 F7E6DE00AE4290 F7E6DE5E43B790 ' +
                'F7E6DE482960120 F7E6DE0056B8120 F7E6DEFEC600120 F7E6DEEC008C150 F7E6DEF5547C120 F7E6DE6F5034150 ' +
                'F7E6DEFF9016120 F7E6DE00B1B790 F7E6DEBECF00120 00AE42000000150 00AE42FFFFFF900 00AE42545454240 ' +
                '00AE428E9089330 00AE42C12E1F210 00AE42F4EE2A270 00AE42F7E6DE360 00AE425E43B7180 00AE42482960180 ' +
                '00AE420056B8240 00AE42FEC600300 00AE42EC008C300 00AE42F5547C390 00AE426F5034180 00AE42FF9016300 ' +
                '00AE4200B1B7360 00AE42BECF00270 5E43B700000090 5E43B7FFFFFF630 5E43B7545454150 5E43B78E9089210 ' +
                '5E43B7C12E1F210 5E43B7F4EE2A330 5E43B70086D6180 5E43B7F7E6DE510 5E43B700AE42240 5E43B7482960150 ' +
                '5E43B70056B8120 5E43B7FEC600540 5E43B7EC008C270 5E43B7F5547C420 5E43B76F5034150 5E43B7FF9016330 ' +
                '5E43B700B1B7270 5E43B7BECF00330 48296000000090 482960FFFFFF900 482960545454240 4829608E9089510 ' +
                '482960C12E1F360 482960F4EE2A420 4829600086D6330 482960F7E6DE510 48296000AE42390 4829605E43B7270 ' +
                '4829600056B8300 482960FEC600660 482960EC008C360 482960F5547C510 4829606F5034180 482960FF9016540 ' +
                '48296000B1B7450 482960BECF00600 0056B800000090 0056B8FFFFFF780 0056B8545454270 0056B88E9089270 ' +
                '0056B8C12E1F330 0056B8F4EE2A630 0056B80086D6180 0056B8F7E6DE840 0056B800AE42270 0056B85E43B7270 ' +
                '0056B8482960150 0056B8FEC600630 0056B8EC008C450 0056B86F5034240 0056B8FF9016510 0056B800B1B7240 ' +
                '0056B8BECF00510 FEC60000000090 FEC600FFFFFF900 FEC600545454390 FEC6008E9089600 FEC600C12E1F180 ' +
                'FEC600F4EE2A150 FEC6000086D6330 FEC600F7E6DE600 FEC60000AE42180 FEC6005E43B7270 FEC600482960330 ' +
                'FEC6000056B8300 FEC600EC008C390 FEC600F5547C570 FEC6006F5034240 FEC600FF9016150 FEC60000B1B7510 ' +
                'FEC600BECF00300 EC008C00000090 EC008CFFFFFF900 EC008C545454240 EC008C8E9089270 EC008CC12E1F120 ' +
                'EC008CF4EE2A360 EC008C0086D6270 EC008CF7E6DE660 EC008C00AE42330 EC008C5E43B7270 EC008C482960270 ' +
                'EC008C0056B8210 EC008CFEC600510 EC008CF5547C120 EC008C6F5034180 EC008C00B1B7360 EC008CBECF00570 ' +
                'F5547C00000090 F5547CFFFFFF900 F5547C545454180 F5547C8E9089180 F5547CC12E1F150 F5547CF4EE2A270 ' +
                'F5547C0086D6270 F5547CF7E6DE540 F5547C00AE42300 F5547C5E43B7210 F5547C482960240 F5547C0056B8210 ' +
                'F5547CFEC600330 F5547CEC008C120 F5547C6F5034180 F5547CFF9016150 F5547C00B1B7300 F5547CBECF00330 ' +
                '6F5034000000180 6F5034FFFFFF660 6F5034545454180 6F50348E9089240 6F5034C12E1F240 6F5034F4EE2A390 ' +
                '6F50340086D6330 6F5034F7E6DE420 6F503400AE42300 6F50345E43B7300 6F5034482960180 6F50340056B8300 ' +
                '6F5034FEC600270 6F5034EC008C210 6F5034F5547C240 6F5034FF9016240 6F503400B1B7270 6F5034BECF00360 ' +
                'FF9016FFFFFF900 FF9016545454240 FF90168E9089270 FF9016C12E1F150 FF9016F4EE2A330 FF90160086D6240 ' +
                'FF9016F7E6DE390 FF901600AE42240 FF90165E43B7270 FF9016482960180 FF90160056B8240 FF9016FEC600210 ' +
                'FF9016EC008C210 FF9016F5547C210 FF90166F5034180 FF901600B1B7300 FF9016BECF00270 00B1B7000000210 ' +
                '00B1B7FFFFFF480 00B1B7545454300 00B1B78E9089180 00B1B7C12E1F300 00B1B7F4EE2A300 00B1B70086D6150 ' +
                '00B1B7F7E6DE390 00B1B700AE42120 00B1B75E43B7270 00B1B7482960270 00B1B70056B8150 00B1B7FEC600330 ' +
                '00B1B7EC008C270 00B1B7F5547C270 00B1B76F5034210 00B1B7FF9016270 00B1B7BECF00240 BECF00000000270 ' +
                'BECF00FFFFFF450 BECF00545454270 BECF008E9089270 BECF00C12E1F150 BECF00F4EE2A90 BECF000086D6300 ' +
                'BECF00F7E6DE300 BECF0000AE42180 BECF005E43B7270 BECF00482960210 BECF000056B8240 BECF00FEC600210 ' +
                'BECF00EC008C240 BECF00F5547C150 BECF006F5034150 BECF00FF9016150 BECF0000B1B7270'
        }
    };
    const MAX_FLUSH_VOLUME = 900;
    const MIN_FORMULA_FLUSH = 60;
    const flushTableCache = {};

    function getFlushTable(dataset) {
        if (!flushTableCache[dataset]) {
            const src = FLUSH_TABLES[dataset];
            const colors = src.colors.split(' ').map(hex => `#${hex}`);
            const volumes = new Map(src.pairs.split(' ').map(entry =>
                [`#${entry.slice(0, 6)}>#${entry.slice(6, 12)}`, Number(entry.slice(12))]));
            flushTableCache[dataset] = { colors, labs: colors.map(srgbHexToLab), volumes };
        }
        return flushTableCache[dataset];
    }

    function lookupFlushTable(dataset, fromHex, toHex) {
        const table = getFlushTable(dataset);
        const snap = hex => {
            const lab = srgbHexToLab(hex);
            return table.colors.find((color, i) => deltaE2000(table.labs[i], lab) <= 5);
        };
        const from = snap(fromHex);
        const to = snap(toHex);
        const volume = from && to ? table.volumes.get(`${from}>${to}`) : undefined;
        return volume === undefined ? null : volume;
    }

    // RGB2HSV from ColorSpaceConvert.cpp: hue in degrees, and can be negative (fmod keeps sign).
    function rgbToHsv(r, g, b) {
        const cmax = Math.max(r, g, b);
        const delta = cmax - Math.min(r, g, b);
        let h;
        if (Math.abs(delta) < 0.001) h = 0;
        else if (cmax === r) h = 60 * (((g - b) / delta) % 6);
        else if (cmax === g) h = 60 * ((b - r) / delta + 2);
        else h = 60 * ((r - g) / delta + 4);
        return [h, Math.abs(cmax) < 0.001 ? 0 : delta / cmax, cmax];
    }

    // FlushVolCalculator::calc_flush_vol_rgb without its table lookup.
    function formulaFlush(fromHex, toHex) {
        const rad = Math.PI / 180;
        const from = hexToRgb01(fromHex);
        const to = hexToRgb01(toHex);
        const [h1, s1, v1] = rgbToHsv(...from);
        const [h2, s2, v2] = rgbToHsv(...to);
        let hsDist = Math.min(1.2, Math.hypot(
            Math.cos(h1 * rad) * s1 * v1 - Math.cos(h2 * rad) * s2 * v2,
            Math.sin(h1 * rad) * s1 * v1 - Math.sin(h2 * rad) * s2 * v2));
        const luminance = ([r, g, b]) => r * 0.3 + g * 0.59 + b * 0.11;
        const fromLumi = luminance(from);
        const toLumi = luminance(to);
        let lumiFlush;
        if (toLumi >= fromLumi) {
            lumiFlush = Math.pow(toLumi - fromLumi, 0.7) * 560;
        } else {
            lumiFlush = (fromLumi - toLumi) * 80;
            hsDist = Math.min(0.67 * v2 + 0.33 * v1, hsDist);
        }
        const hsFlush = 230 * hsDist;
        const flush = Math.sqrt(hsFlush ** 2 + lumiFlush ** 2 - 2 * hsFlush * lumiFlush * Math.cos(120 * rad));
        return Math.max(flush, MIN_FORMULA_FLUSH);
    }

    // FlushVolCalculator::calc_flush_vol for opaque colors.
    function flushVolume(fromHex, toHex, dataset, minFlush) {
        let flush = dataset !== 0 ? lookupFlushTable(dataset, fromHex, toHex) : null;
        if (flush === null) {
            const measured = dataset === 0 ? lookupFlushTable(0, fromHex, toHex) : null;
            flush = Math.trunc(measured !== null ? measured : formulaFlush(fromHex, toHex));
            // Bambu tests 0-255 channel luminance against 0-1 thresholds here, so in practice this
            // fires for any non-black color followed by black.
            const luminance255 = hex => hexToRgb01(hex).reduce((sum, c, k) => sum + c * 255 * [0.3, 0.59, 0.11][k], 0);
            if (dataset !== 0 && luminance255(fromHex) > 180 / 255 && luminance255(toHex) < 75 / 255) flush *= 1.3;
            flush += minFlush;
        }
        return Math.min(Math.trunc(flush), MAX_FLUSH_VOLUME);
    }

    // Row = from, column = to, one n x n block per nozzle, as flush_volumes_matrix stores it.
    function buildFlushMatrix(printer, filaments) {
        const values = [];
        printer.flush.forEach(([dataset, minFlush]) => {
            filaments.forEach((from, i) => filaments.forEach((to, j) => {
                values.push(String(i === j ? 0 : flushVolume(from.hex, to.hex, dataset, minFlush)));
            }));
        });
        return values;
    }

    /* ---------- project settings ---------- */

    function buildProjectSettings(printer, filaments, sparseInfill) {
        const n = filaments.length;
        const fill = value => Array(n).fill(value);
        const perNozzle = value => Array(printer.flush.length).fill(value);
        const [bedW, bedD] = printer.bed;
        const infillDensities = Object.fromEntries(INFILL_DENSITY_KEYS.map(key => [key, `${sparseInfill}%`]));
        return {
            name: 'project_settings',
            from: 'project',
            version: APP_VERSION,
            printer_model: printer.model,
            printer_settings_id: `${printer.model} 0.4 nozzle`,
            print_settings_id: printer.process,
            // Per-nozzle keys, sized to the printer. On a dual-nozzle printer Bambu Studio drops the
            // whole config unless extruder_type matches nozzle_diameter, and it reads
            // nozzle_volume_type once per nozzle after loading.
            nozzle_diameter: perNozzle('0.4'),
            extruder_type: perNozzle('Direct Drive'),
            nozzle_volume_type: perNozzle('Standard'),
            printable_area: ['0x0', `${bedW}x0`, `${bedW}x${bedD}`, `0x${bedD}`],
            printable_height: String(printer.height),
            filament_settings_id: fill(printer.filament),
            filament_colour: filaments.map(f => f.hex),
            filament_multi_colour: filaments.map(f => f.hex),
            filament_type: fill('PLA'),
            filament_vendor: fill('Bambu Lab'),
            filament_ids: fill('GFA00'),
            filament_diameter: fill('1.75'),
            // One extruder variant per slot. Bambu Studio rejects the config as invalid unless
            // filament_self_index lines up with this list entry for entry.
            filament_extruder_variant: fill('Direct Drive Standard'),
            filament_self_index: filaments.map((f, i) => String(i + 1)),
            // One multiplier per nozzle, so Bambu Studio reads the matrix as n x n per nozzle and
            // keeps it instead of resizing it.
            flush_volumes_matrix: buildFlushMatrix(printer, filaments),
            flush_multiplier: perNozzle('1'),
            ...infillDensities,
            // Entries are print, filaments..., printer. Empty means "the system preset,
            // unchanged". A key missing from the print entry would be reset to the system value
            // on load, so the infill densities are listed there. The process then opens as a
            // modified copy of its system preset, as if edited by hand.
            inherits_group: Array(n + 2).fill(''),
            different_settings_to_system: [INFILL_DENSITY_KEYS.join(';'), ...Array(n + 1).fill('')],
            curr_bed_type: 'Textured PEI Plate'
        };
    }

    /* ---------- filament slots ---------- */

    // Triangle counts per palette index for a painted part.
    function paintedColorCounts(part) {
        const counts = new Map();
        const tris = part.indices.length / 3;
        for (let t = 0; t < tris; t++) {
            const c = part.triangleColors[t] || 0;
            counts.set(c, (counts.get(c) || 0) + 1);
        }
        return counts;
    }

    // One filament slot per distinct color actually printed, in the order the parts list them.
    // Two colors that land on the same filament share a slot, so the printer never swaps to an
    // identical spool. Returns the slots and a slot lookup by design color.
    function assignFilaments(objects, colorMode) {
        const filaments = [];
        const slotByColor = new Map();
        const use = hex => {
            const key = normalizeHexColor(hex);
            if (slotByColor.has(key)) return;
            const pick = colorMode === 'exact' ? { name: null, hex: key } : nearestPlaBasicColor(key);
            let slot = filaments.findIndex(f => f.hex === pick.hex);
            if (slot < 0) slot = filaments.push(pick) - 1;
            slotByColor.set(key, slot + 1);
        };
        objects.forEach(object => object.parts.forEach(part => {
            if (part.triangleColors) {
                [...paintedColorCounts(part).keys()].sort((a, b) => a - b).forEach(c => use(part.colors[c]));
            } else {
                use(part.color);
            }
        }));
        return { filaments, slotOf: hex => slotByColor.get(normalizeHexColor(hex)) };
    }

    // Bambu's per-triangle paint code for a whole, unsplit triangle in filament `slot`
    // (TriangleSelector::serialize + FacetsAnnotation::get_triangle_as_string): 1 -> "4",
    // 2 -> "8", 3 -> "0C", 4 -> "1C", ...
    function paintCode(slot) {
        if (slot < 3) return ['', '4', '8'][slot];
        let n = slot - 3;
        let code = 'C';
        while (n >= 15) { code = `F${code}`; n -= 15; }
        return n.toString(16).toUpperCase() + code;
    }

    // The part's own filament, plus a paint code for every triangle printed in another one.
    function resolvePartFilaments(part, slotOf) {
        if (!part.triangleColors) return { extruder: slotOf(part.color), paint: null };
        const counts = paintedColorCounts(part);
        const main = [...counts.entries()].sort((a, b) => b[1] - a[1])[0][0];
        const extruder = slotOf(part.colors[main]);
        const codeByColor = part.colors.map(hex => {
            const slot = slotOf(hex);
            return slot === undefined || slot === extruder ? '' : paintCode(slot);
        });
        const tris = part.indices.length / 3;
        const paint = new Array(tris);
        for (let t = 0; t < tris; t++) paint[t] = codeByColor[part.triangleColors[t] || 0];
        return { extruder, paint };
    }

    /* ---------- 3MF package ---------- */

    function xmlEscape(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&apos;');
    }

    function meshObjectXml(id, name, positions, indices, paint) {
        const lines = [`  <object id="${id}" type="model" name="${xmlEscape(name)}">`, '   <mesh>', '    <vertices>'];
        for (let i = 0; i < positions.length; i += 3) {
            lines.push(`     <vertex x="${positions[i].toFixed(6)}" y="${positions[i + 1].toFixed(6)}" z="${positions[i + 2].toFixed(6)}"/>`);
        }
        lines.push('    </vertices>', '    <triangles>');
        for (let i = 0; i < indices.length; i += 3) {
            const code = paint && paint[i / 3];
            lines.push(`     <triangle v1="${indices[i]}" v2="${indices[i + 1]}" v3="${indices[i + 2]}"${code ? ` paint_color="${code}"` : ''}/>`);
        }
        lines.push('    </triangles>', '   </mesh>', '  </object>');
        return lines.join('\n');
    }

    function boundsOf(parts) {
        const min = [Infinity, Infinity, Infinity];
        const max = [-Infinity, -Infinity, -Infinity];
        parts.forEach(part => {
            const p = part.positions;
            for (let i = 0; i < p.length; i += 3) {
                for (let k = 0; k < 3; k++) {
                    if (p[i + k] < min[k]) min[k] = p[i + k];
                    if (p[i + k] > max[k]) max[k] = p[i + k];
                }
            }
        });
        return { min, max };
    }

    const nextFrame = () => new Promise(resolve => requestAnimationFrame(() => setTimeout(resolve, 0)));

    /* Builds the project.
       objects: [{ kind, name, parts }], one build plate each, in order. kind is a short label for
       the status line ("Pot", "Plate"...); name is shown in Bambu Studio.
       part: { name, positions, indices } in mm, printer frame (Z up), plus either
         color: '#RRGGBB'                        - a body in one color, or
         colors: [...hex], triangleColors: [...]  - painted per triangle (index into colors).
       Parts without triangles are dropped; so are objects left with no parts.
       Returns { blob, filaments, plates: [{ kind, name, size, fits }] }, or null when nothing is
       printable. */
    async function buildProject({ title = '', objects, options = readOptions(), onProgress = () => {} }) {
        const { printer, colorMode, sparseInfill } = options;
        const printable = objects
            .map(o => Object.assign({}, o, { parts: o.parts.filter(p => p.indices && p.indices.length) }))
            .filter(o => o.parts.length);
        if (!printable.length) return null;

        const { filaments, slotOf } = assignFilaments(printable, colorMode);
        const cols = Math.ceil(Math.sqrt(printable.length));
        const [bedW, bedD] = printer.bed;
        let nextId = 1;
        const layout = printable.map((object, i) => {
            const partIds = object.parts.map(() => nextId++);
            const assemblyId = nextId++;
            const bounds = boundsOf(object.parts);
            // Centre the object on its own build plate and stand it on the bed.
            const plateX = (i % cols) * bedW * (1 + PLATE_GAP) + bedW / 2;
            const plateY = -Math.floor(i / cols) * bedD * (1 + PLATE_GAP) + bedD / 2;
            const tx = plateX - (bounds.min[0] + bounds.max[0]) / 2;
            const ty = plateY - (bounds.min[1] + bounds.max[1]) / 2;
            const tz = -bounds.min[2];
            const size = bounds.max.map((v, k) => v - bounds.min[k]);
            return {
                kind: object.kind,
                name: object.name,
                parts: object.parts.map(part => Object.assign({}, part, resolvePartFilaments(part, slotOf))),
                partIds,
                assemblyId,
                path: `/3D/Objects/object_${i + 1}.model`,
                transform: `1 0 0 0 1 0 0 0 1 ${tx.toFixed(4)} ${ty.toFixed(4)} ${tz.toFixed(4)}`,
                size,
                fits: size[0] <= bedW && size[1] <= bedD && size[2] <= printer.height
            };
        });

        const modelHeader = `<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="${NS_3MF_CORE}" xmlns:BambuStudio="${NS_BAMBU}" xmlns:p="${NS_3MF_PRODUCTION}" requiredextensions="p">`;

        const rootModelXml = `${modelHeader}
 <metadata name="Application">BambuStudio-${APP_VERSION}</metadata>
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <metadata name="CreationDate">${new Date().toISOString().slice(0, 10)}</metadata>
 <metadata name="Title">${xmlEscape(title)}</metadata>
 <resources>
${layout.map(o => `  <object id="${o.assemblyId}" type="model">
   <components>
${o.partIds.map(id => `    <component p:path="${o.path}" objectid="${id}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>`).join('\n')}
   </components>
  </object>`).join('\n')}
 </resources>
 <build>
${layout.map(o => `  <item objectid="${o.assemblyId}" transform="${o.transform}" printable="1"/>`).join('\n')}
 </build>
</model>`;

        const modelRelsXml = `<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="${NS_RELATIONSHIPS}">
${layout.map((o, i) => ` <Relationship Target="${o.path}" Id="rel-${i + 1}" Type="${REL_TYPE_3DMODEL}"/>`).join('\n')}
</Relationships>`;

        const modelSettingsXml = `<?xml version="1.0" encoding="UTF-8"?>
<config>
${layout.map(o => `  <object id="${o.assemblyId}">
    <metadata key="name" value="${xmlEscape(o.name)}"/>
    <metadata key="extruder" value="${o.parts[0].extruder}"/>
${o.parts.map((part, k) => `    <part id="${o.partIds[k]}" subtype="normal_part">
      <metadata key="name" value="${xmlEscape(part.name)}"/>
      <metadata key="extruder" value="${part.extruder}"/>
    </part>`).join('\n')}
  </object>`).join('\n')}
${layout.map((o, i) => `  <plate>
    <metadata key="plater_id" value="${i + 1}"/>
    <metadata key="plater_name" value="${xmlEscape(o.name)}"/>
    <metadata key="locked" value="false"/>
    <model_instance>
      <metadata key="object_id" value="${o.assemblyId}"/>
      <metadata key="instance_id" value="0"/>
      <metadata key="identify_id" value="${o.assemblyId}"/>
    </model_instance>
  </plate>`).join('\n')}
</config>`;

        const zip = new JSZip();
        zip.file('[Content_Types].xml', `<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>`);
        zip.file('_rels/.rels', `<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="${NS_RELATIONSHIPS}">
 <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="${REL_TYPE_3DMODEL}"/>
</Relationships>`);
        zip.file('3D/3dmodel.model', rootModelXml);
        zip.file('3D/_rels/3dmodel.model.rels', modelRelsXml);
        layout.forEach(o => {
            zip.file(o.path.slice(1), `${modelHeader}
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <resources>
${o.parts.map((part, k) => meshObjectXml(o.partIds[k], part.name, part.positions, part.indices, part.paint)).join('\n')}
 </resources>
 <build/>
</model>`);
        });
        zip.file('Metadata/model_settings.config', modelSettingsXml);
        zip.file('Metadata/project_settings.config', JSON.stringify(buildProjectSettings(printer, filaments, sparseInfill), null, 4));

        onProgress('Compressing Bambu Studio project...');
        await nextFrame();
        const blob = await zip.generateAsync({ type: 'blob', mimeType: 'model/3mf', compression: 'DEFLATE', compressionOptions: { level: 6 } });
        return {
            blob,
            filaments,
            plates: layout.map(o => ({ kind: o.kind, name: o.name, size: o.size, fits: o.fits }))
        };
    }

    // Status-line pieces shared by all three tools: printer, plates, filaments, infill, and any
    // object too big for the chosen printer.
    function summarize(result, options = readOptions()) {
        const { printer, sparseInfill } = options;
        return [
            `Bambu Studio project exported for ${printer.model}`,
            result.plates.map((p, i) => `Plate ${i + 1}: ${p.kind}`).join(', '),
            `Filaments ${result.filaments.map((f, i) => `${i + 1} ${f.name || f.hex}`).join(', ')}`,
            `Sparse infill ${sparseInfill}%`,
            ...result.plates.filter(p => !p.fits)
                .map(p => `${p.kind} ${p.size.map(v => (v / 10).toFixed(1)).join(' x ')} cm exceeds the ${shortModel(printer)} build volume`)
        ];
    }

    return {
        PLA_BASIC_COLORS,
        PRINTERS,
        initOptions,
        readOptions,
        nearestPlaBasicColor,
        buildFlushMatrix,
        paintCode,
        buildProject,
        summarize,
        nextFrame
    };
})();
