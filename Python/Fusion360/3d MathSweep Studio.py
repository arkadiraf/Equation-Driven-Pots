import adsk.core, adsk.fusion, traceback
import math

# -----------------------------------------------------------------------------
# Clean sweep-based MathSweep Studio.
# - Uses a true continuous sweep body instead of node/ring thickening.
# - Uses a native circle profile when profileType == 'Circle'.
# - Keeps sampled r(theta) profiles for petal variants.
# -----------------------------------------------------------------------------
defaultName = 'Segmented Sweep Shape'
defaultPathType = 'Mobius Curve'
defaultProfileType = 'Circle'
defaultDiameter = 20.0          # cm
defaultZStretch = 10.0          # cm
defaultPathSegments = 120
defaultProfileSegments = 24
defaultProfileRadius = 3.0      # cm
defaultProfileEquation = 'R'
defaultGenerateSolid = False

defaultInternalLoops = 0

defaultMainLoops = 2
defaultSecondaryLoops = 3
defaultAmplitude = 3.5          # cm

defaultPetals = 5
defaultFlowerAmplitude = 3.0    # cm

defaultBaseFreq = 3
defaultAmp1 = 2.5               # cm
defaultAmp2 = 1.0               # cm

handlers = []
app = adsk.core.Application.get()
ui = app.userInterface if app else None

PROFILE_PRESET_EQUATIONS = {
    'Circle': 'R',
    '2 Petals': 'R*(1+0.4*cos(2*theta))',
    '3 Petals': 'R*(1+0.3*cos(3*theta))',
    '4 Petals': 'R*(1+0.2*cos(4*theta))',
    '5 Petals': 'R*(1+0.3*cos(5*theta))',
}

CLOSED_PATHS = ['Mobius Curve', 'Torus Knot', 'Flower Ring', 'Braided Loop']


def getTargetComponent():
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    return design.rootComponent if design else None


def vector_length(v):
    return math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z)


def normalize(v):
    length = vector_length(v)
    if length < 1e-9:
        return adsk.core.Vector3D.create(0, 0, 0)
    return adsk.core.Vector3D.create(v.x / length, v.y / length, v.z / length)


def cross(a, b):
    return adsk.core.Vector3D.create(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    )


def dot(a, b):
    return a.x * b.x + a.y * b.y + a.z * b.z


def scaled_vector(v, s):
    return adsk.core.Vector3D.create(v.x * s, v.y * s, v.z * s)


def add_point_vec(p, v):
    return adsk.core.Point3D.create(p.x + v.x, p.y + v.y, p.z + v.z)


def subtract_points(p2, p1):
    return adsk.core.Vector3D.create(p2.x - p1.x, p2.y - p1.y, p2.z - p1.z)


class ShapeCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            unitsMgr = app.activeProduct.unitsManager
            command = args.firingEvent.sender
            inputs = command.commandInputs

            shape = ShapeGenerator()

            for input in inputs:
                if input.id == 'shapeName':
                    shape.shapeName = input.value
                elif input.id == 'pathType' and getattr(input, 'selectedItem', None):
                    shape.pathType = input.selectedItem.name
                elif input.id == 'profileType' and getattr(input, 'selectedItem', None):
                    shape.profileType = input.selectedItem.name
                elif input.id == 'diameter':
                    shape.diameter = unitsMgr.evaluateExpression(input.expression, 'cm')
                elif input.id == 'zStretch':
                    shape.zStretch = unitsMgr.evaluateExpression(input.expression, 'cm')
                elif input.id == 'pathSegments':
                    shape.pathSegments = int(input.value)
                elif input.id == 'profileSegments':
                    shape.profileSegments = int(input.value)
                elif input.id == 'profileRadius':
                    shape.profileRadius = unitsMgr.evaluateExpression(input.expression, 'cm')
                elif input.id == 'profileEquation':
                    shape.profileEquation = input.value
                elif input.id == 'internalLoops':
                    shape.internalLoops = int(input.value)
                elif input.id == 'mainLoops':
                    shape.mainLoops = int(input.value)
                elif input.id == 'secondaryLoops':
                    shape.secondaryLoops = int(input.value)
                elif input.id == 'amplitude':
                    shape.amplitude = unitsMgr.evaluateExpression(input.expression, 'cm')
                elif input.id == 'petals':
                    shape.petals = int(input.value)
                elif input.id == 'flowerAmplitude':
                    shape.flowerAmplitude = unitsMgr.evaluateExpression(input.expression, 'cm')
                elif input.id == 'baseFreq':
                    shape.baseFreq = int(input.value)
                elif input.id == 'amp1':
                    shape.amp1 = unitsMgr.evaluateExpression(input.expression, 'cm')
                elif input.id == 'amp2':
                    shape.amp2 = unitsMgr.evaluateExpression(input.expression, 'cm')
                elif input.id == 'generateSolid':
                    shape.generateSolid = input.value

            shape.build()
            args.isValidResult = True
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class ShapeCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class ShapeCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            changedInput = args.input
            inputs = args.inputs

            if changedInput.id not in ['pathType', 'profileType', 'diameter', 'zStretch', 'profileRadius', 'profileEquation', 'generateSolid', 'pathSegments', 'profileSegments', 'internalLoops', 'mainLoops', 'secondaryLoops', 'amplitude', 'petals', 'flowerAmplitude', 'baseFreq', 'amp1', 'amp2']:
                return

            pathInput = inputs.itemById('pathType')
            profileInput = inputs.itemById('profileType')
            pathType = pathInput.selectedItem.name if pathInput.selectedItem else defaultPathType
            profileType = profileInput.selectedItem.name if profileInput.selectedItem else defaultProfileType

            internalLoopsInput = inputs.itemById('internalLoops')
            mainLoopsInput = inputs.itemById('mainLoops')
            secondaryLoopsInput = inputs.itemById('secondaryLoops')
            amplitudeInput = inputs.itemById('amplitude')
            petalsInput = inputs.itemById('petals')
            flowerAmplitudeInput = inputs.itemById('flowerAmplitude')
            baseFreqInput = inputs.itemById('baseFreq')
            amp1Input = inputs.itemById('amp1')
            amp2Input = inputs.itemById('amp2')
            profileSegmentsInput = inputs.itemById('profileSegments')

            for inp in [
                internalLoopsInput, mainLoopsInput, secondaryLoopsInput,
                amplitudeInput, petalsInput, flowerAmplitudeInput,
                baseFreqInput, amp1Input, amp2Input
            ]:
                inp.isVisible = False

            if pathType == 'Mobius Curve':
                internalLoopsInput.isVisible = True
            elif pathType == 'Torus Knot':
                mainLoopsInput.isVisible = True
                secondaryLoopsInput.isVisible = True
                amplitudeInput.isVisible = True
            elif pathType == 'Flower Ring':
                petalsInput.isVisible = True
                flowerAmplitudeInput.isVisible = True
            elif pathType == 'Braided Loop':
                baseFreqInput.isVisible = True
                amp1Input.isVisible = True
                amp2Input.isVisible = True

            eqInput = inputs.itemById('profileEquation')
            if changedInput.id == 'profileType' and eqInput:
                eqInput.value = PROFILE_PRESET_EQUATIONS.get(profileType, defaultProfileEquation)

            if profileSegmentsInput:
                profileSegmentsInput.isEnabled = (profileType != 'Circle')
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class ShapeCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = False

            onExecute = ShapeCommandExecuteHandler()
            cmd.execute.add(onExecute)

            onExecutePreview = ShapeCommandExecuteHandler()
            cmd.executePreview.add(onExecutePreview)

            onDestroy = ShapeCommandDestroyHandler()
            cmd.destroy.add(onDestroy)

            onInputChanged = ShapeCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)

            handlers.append(onExecute)
            handlers.append(onExecutePreview)
            handlers.append(onDestroy)
            handlers.append(onInputChanged)

            inputs = cmd.commandInputs
            inputs.addStringValueInput('shapeName', 'Shape Name', defaultName)

            pathTypeInput = inputs.addDropDownCommandInput(
                'pathType', 'Path Type', adsk.core.DropDownStyles.TextListDropDownStyle
            )
            pathItems = pathTypeInput.listItems
            pathItems.add('Mobius Curve', True, '')
            pathItems.add('Torus Knot', False, '')
            pathItems.add('Flower Ring', False, '')
            pathItems.add('Braided Loop', False, '')

            profileTypeInput = inputs.addDropDownCommandInput(
                'profileType', 'Base Shape r(theta)', adsk.core.DropDownStyles.TextListDropDownStyle
            )
            profileItems = profileTypeInput.listItems
            profileItems.add('Circle', True, '')
            profileItems.add('2 Petals', False, '')
            profileItems.add('3 Petals', False, '')
            profileItems.add('4 Petals', False, '')
            profileItems.add('5 Petals', False, '')

            eqInput = inputs.addStringValueInput('profileEquation', 'r(theta) Equation', defaultProfileEquation)
            eqInput.tooltip = 'Use R, theta, pi, sin, cos, tan, abs, min, max. Example: R*(1+0.3*cos(5*theta))'

            inputs.addValueInput('diameter', 'Path Diameter', 'cm', adsk.core.ValueInput.createByReal(defaultDiameter))
            inputs.addValueInput('zStretch', 'Z Stretch', 'cm', adsk.core.ValueInput.createByReal(defaultZStretch))
            inputs.addValueInput('profileRadius', 'Base Profile Radius', 'cm', adsk.core.ValueInput.createByReal(defaultProfileRadius))
            inputs.addBoolValueInput('generateSolid', 'Generate 3D Sweep Body', True, '', defaultGenerateSolid)

            inputs.addIntegerSpinnerCommandInput('pathSegments', 'Path Segments', 12, 2000, 1, defaultPathSegments)
            inputs.addIntegerSpinnerCommandInput('profileSegments', 'Base Shape Resolution', 6, 360, 1, defaultProfileSegments)

            inputs.addIntegerSpinnerCommandInput('internalLoops', 'Internal Loops', 0, 100, 1, defaultInternalLoops)
            inputs.addIntegerSpinnerCommandInput('mainLoops', 'p (Main)', 1, 100, 1, defaultMainLoops)
            inputs.addIntegerSpinnerCommandInput('secondaryLoops', 'q (Secondary)', 1, 100, 1, defaultSecondaryLoops)
            inputs.addValueInput('amplitude', 'Amplitude', 'cm', adsk.core.ValueInput.createByReal(defaultAmplitude))
            inputs.addIntegerSpinnerCommandInput('petals', 'Petals (n)', 1, 100, 1, defaultPetals)
            inputs.addValueInput('flowerAmplitude', 'Flower Amplitude', 'cm', adsk.core.ValueInput.createByReal(defaultFlowerAmplitude))
            inputs.addIntegerSpinnerCommandInput('baseFreq', 'Base Freq (n1)', 1, 100, 1, defaultBaseFreq)
            inputs.addValueInput('amp1', 'Amp 1', 'cm', adsk.core.ValueInput.createByReal(defaultAmp1))
            inputs.addValueInput('amp2', 'Amp 2', 'cm', adsk.core.ValueInput.createByReal(defaultAmp2))

            inputs.itemById('mainLoops').isVisible = False
            inputs.itemById('secondaryLoops').isVisible = False
            inputs.itemById('amplitude').isVisible = False
            inputs.itemById('petals').isVisible = False
            inputs.itemById('flowerAmplitude').isVisible = False
            inputs.itemById('baseFreq').isVisible = False
            inputs.itemById('amp1').isVisible = False
            inputs.itemById('amp2').isVisible = False

            shape = ShapeGenerator()
            shape.buildFromInputs(inputs)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class ShapeGenerator:
    def __init__(self):
        self._shapeName = defaultName
        self._pathType = defaultPathType
        self._profileType = defaultProfileType
        self._diameter = defaultDiameter
        self._zStretch = defaultZStretch
        self._pathSegments = defaultPathSegments
        self._profileSegments = defaultProfileSegments
        self._profileRadius = defaultProfileRadius
        self._profileEquation = defaultProfileEquation
        self._generateSolid = defaultGenerateSolid
        self._internalLoops = defaultInternalLoops
        self._mainLoops = defaultMainLoops
        self._secondaryLoops = defaultSecondaryLoops
        self._amplitude = defaultAmplitude
        self._petals = defaultPetals
        self._flowerAmplitude = defaultFlowerAmplitude
        self._baseFreq = defaultBaseFreq
        self._amp1 = defaultAmp1
        self._amp2 = defaultAmp2

    @property
    def shapeName(self):
        return self._shapeName

    @shapeName.setter
    def shapeName(self, value):
        self._shapeName = value

    @property
    def pathType(self):
        return self._pathType

    @pathType.setter
    def pathType(self, value):
        self._pathType = str(value)

    @property
    def profileType(self):
        return self._profileType

    @profileType.setter
    def profileType(self, value):
        self._profileType = str(value)

    @property
    def diameter(self):
        return self._diameter

    @diameter.setter
    def diameter(self, value):
        self._diameter = max(0.001, float(value))

    @property
    def zStretch(self):
        return self._zStretch

    @zStretch.setter
    def zStretch(self, value):
        self._zStretch = float(value)

    @property
    def pathSegments(self):
        return self._pathSegments

    @pathSegments.setter
    def pathSegments(self, value):
        self._pathSegments = max(12, int(value))

    @property
    def profileSegments(self):
        return self._profileSegments

    @profileSegments.setter
    def profileSegments(self, value):
        self._profileSegments = max(6, int(value))

    @property
    def profileRadius(self):
        return self._profileRadius

    @profileRadius.setter
    def profileRadius(self, value):
        self._profileRadius = max(0.001, float(value))

    @property
    def profileEquation(self):
        return self._profileEquation

    @profileEquation.setter
    def profileEquation(self, value):
        val = str(value).strip()
        self._profileEquation = val if val else defaultProfileEquation

    @property
    def generateSolid(self):
        return self._generateSolid

    @generateSolid.setter
    def generateSolid(self, value):
        self._generateSolid = bool(value)

    @property
    def internalLoops(self):
        return self._internalLoops

    @internalLoops.setter
    def internalLoops(self, value):
        self._internalLoops = max(0, int(value))

    @property
    def mainLoops(self):
        return self._mainLoops

    @mainLoops.setter
    def mainLoops(self, value):
        self._mainLoops = max(1, int(value))

    @property
    def secondaryLoops(self):
        return self._secondaryLoops

    @secondaryLoops.setter
    def secondaryLoops(self, value):
        self._secondaryLoops = max(1, int(value))

    @property
    def amplitude(self):
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value):
        self._amplitude = float(value)

    @property
    def petals(self):
        return self._petals

    @petals.setter
    def petals(self, value):
        self._petals = max(1, int(value))

    @property
    def flowerAmplitude(self):
        return self._flowerAmplitude

    @flowerAmplitude.setter
    def flowerAmplitude(self, value):
        self._flowerAmplitude = float(value)

    @property
    def baseFreq(self):
        return self._baseFreq

    @baseFreq.setter
    def baseFreq(self, value):
        self._baseFreq = max(1, int(value))

    @property
    def amp1(self):
        return self._amp1

    @amp1.setter
    def amp1(self, value):
        self._amp1 = float(value)

    @property
    def amp2(self):
        return self._amp2

    @amp2.setter
    def amp2(self, value):
        self._amp2 = float(value)

    def pointAt(self, t):
        rx = self.diameter * 0.5
        zA = self.zStretch

        if self.pathType == 'Mobius Curve':
            phi = 0.5 * t + self.internalLoops * t
            return adsk.core.Point3D.create(
                (rx + zA * math.cos(phi)) * math.cos(t),
                (rx + zA * math.cos(phi)) * math.sin(t),
                zA * math.sin(phi)
            )

        if self.pathType == 'Torus Knot':
            p = self.mainLoops
            q = self.secondaryLoops
            r = self.amplitude
            return adsk.core.Point3D.create(
                (rx + r * math.cos(q * t)) * math.cos(p * t),
                (rx + r * math.cos(q * t)) * math.sin(p * t),
                zA * math.sin(q * t)
            )

        if self.pathType == 'Flower Ring':
            n = self.petals
            r = self.flowerAmplitude
            return adsk.core.Point3D.create(
                (rx + r * math.cos(n * t)) * math.cos(t),
                (rx + r * math.cos(n * t)) * math.sin(t),
                zA * math.sin(n * t)
            )

        if self.pathType == 'Braided Loop':
            n1 = self.baseFreq
            n2 = n1 + 3
            radial = rx + self.amp1 * math.cos(n1 * t) + self.amp2 * math.cos(n2 * t)
            return adsk.core.Point3D.create(
                radial * math.cos(t),
                radial * math.sin(t),
                zA * math.sin(n1 * t) + self.amp2 * math.sin(n2 * t)
            )

        return adsk.core.Point3D.create(rx * math.cos(t), rx * math.sin(t), 0.0)

    def totalAngle(self):
        if self.pathType == 'Mobius Curve':
            return 4.0 * math.pi
        return 2.0 * math.pi

    def isClosedPath(self):
        return self.pathType in CLOSED_PATHS

    def pointsAreClose(self, p1, p2, tol=1e-4):
        return (
            abs(p1.x - p2.x) < tol and
            abs(p1.y - p2.y) < tol and
            abs(p1.z - p2.z) < tol
        )

    def profileRadiusAt(self, theta):
        safe_names = {
            'R': self.profileRadius,
            'theta': theta,
            'pi': math.pi,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'abs': abs,
            'min': min,
            'max': max
        }
        try:
            r = eval(self.profileEquation, {'__builtins__': {}}, safe_names)
        except:
            r = self.profileRadius
        try:
            r = float(r)
        except:
            r = self.profileRadius
        return max(0.001, r)

    def buildPathPoints(self):
        pts = []
        total = self.totalAngle()
        for i in range(self.pathSegments):
            t = total * float(i) / float(self.pathSegments)
            pts.append(self.pointAt(t))
        return pts

    def buildTransportFrames(self, points):
        count = len(points)
        if count < 3:
            return []

        tangents = []
        for i in range(count):
            prev_pt = points[(i - 1 + count) % count]
            next_pt = points[(i + 1) % count]
            tangents.append(normalize(subtract_points(next_pt, prev_pt)))

        tangent0 = tangents[0]
        normal0 = adsk.core.Vector3D.create(1, 0, 0)
        if abs(dot(tangent0, normal0)) > 0.9:
            normal0 = adsk.core.Vector3D.create(0, 1, 0)
        binormal0 = normalize(cross(tangent0, normal0))
        normal0 = normalize(cross(binormal0, tangent0))

        normals = [normal0]
        binormals = [binormal0]

        for i in range(1, count):
            prev_t = tangents[i - 1]
            cur_t = tangents[i]
            axis = cross(prev_t, cur_t)
            axis_len = vector_length(axis)

            prev_n = normals[-1]
            prev_b = binormals[-1]

            if axis_len < 1e-8:
                normals.append(prev_n)
                binormals.append(prev_b)
                continue

            axis = normalize(axis)
            c = max(-1.0, min(1.0, dot(prev_t, cur_t)))
            angle = math.acos(c)
            normals.append(self.rotateAroundAxis(prev_n, axis, angle))
            binormals.append(self.rotateAroundAxis(prev_b, axis, angle))

        twist = math.atan2(dot(normals[-1], binormals[0]), dot(normals[-1], normals[0]))
        corrected_normals = []
        corrected_binormals = []
        denom = float(max(1, count))
        for i in range(count):
            corr = -(float(i) / denom) * twist
            n = self.rotateAroundAxis(normals[i], tangents[i], corr)
            b = self.rotateAroundAxis(binormals[i], tangents[i], corr)
            corrected_normals.append(normalize(n))
            corrected_binormals.append(normalize(b))

        frames = []
        for i in range(count):
            frames.append({'p': points[i], 't': tangents[i], 'n': corrected_normals[i], 'b': corrected_binormals[i]})
        return frames

    def rotateAroundAxis(self, vec, axis, angle):
        axis = normalize(axis)
        c = math.cos(angle)
        s = math.sin(angle)
        term1 = scaled_vector(vec, c)
        term2 = scaled_vector(cross(axis, vec), s)
        term3 = scaled_vector(axis, dot(axis, vec) * (1.0 - c))
        return adsk.core.Vector3D.create(
            term1.x + term2.x + term3.x,
            term1.y + term2.y + term3.y,
            term1.z + term2.z + term3.z
        )

    def createPreviewPathSketch(self, targetComp, path_points):
        sketches = targetComp.sketches
        sketch = sketches.add(targetComp.xYConstructionPlane)
        sketch.name = self.shapeName + ' Path Preview'
        try:
            sketch.is3D = True
        except:
            pass

        lines = sketch.sketchCurves.sketchLines
        prev = None
        first = None
        for pt in path_points:
            sp = sketch.sketchPoints.add(pt)
            if first is None:
                first = sp
            if prev is not None:
                lines.addByTwoPoints(prev, sp)
            prev = sp

        if self.isClosedPath() and prev and first and prev != first:
            lines.addByTwoPoints(prev, first)
        return sketch

    def createPreviewProfileSketch(self, targetComp, frame):
        sketches = targetComp.sketches
        sketch = sketches.add(targetComp.xYConstructionPlane)
        sketch.name = self.shapeName + ' Base Profile Preview'
        try:
            sketch.is3D = True
        except:
            pass

        if self.profileType == 'Circle':
            points = []
            sample_count = max(24, self.profileSegments)
            for j in range(sample_count):
                theta = 2.0 * math.pi * float(j) / float(sample_count)
                offset_n = scaled_vector(frame['n'], self.profileRadius * math.cos(theta))
                offset_b = scaled_vector(frame['b'], self.profileRadius * math.sin(theta))
                points.append(adsk.core.Point3D.create(
                    frame['p'].x + offset_n.x + offset_b.x,
                    frame['p'].y + offset_n.y + offset_b.y,
                    frame['p'].z + offset_n.z + offset_b.z
                ))
            lines = sketch.sketchCurves.sketchLines
            prev = None
            first = None
            for pt in points:
                sp = sketch.sketchPoints.add(pt)
                if first is None:
                    first = sp
                if prev is not None:
                    lines.addByTwoPoints(prev, sp)
                prev = sp
            if prev and first:
                lines.addByTwoPoints(prev, first)
            return sketch

        points = []
        for j in range(self.profileSegments):
            theta = 2.0 * math.pi * float(j) / float(self.profileSegments)
            r = self.profileRadiusAt(theta)
            offset_n = scaled_vector(frame['n'], r * math.cos(theta))
            offset_b = scaled_vector(frame['b'], r * math.sin(theta))
            points.append(adsk.core.Point3D.create(
                frame['p'].x + offset_n.x + offset_b.x,
                frame['p'].y + offset_n.y + offset_b.y,
                frame['p'].z + offset_n.z + offset_b.z
            ))

        lines = sketch.sketchCurves.sketchLines
        prev = None
        first = None
        for pt in points:
            sp = sketch.sketchPoints.add(pt)
            if first is None:
                first = sp
            if prev is not None:
                lines.addByTwoPoints(prev, sp)
            prev = sp
        if prev and first:
            lines.addByTwoPoints(prev, first)
        return sketch

    def createPerpendicularStartPlane(self, targetComp, startPoint, tangentVec):
        planes = targetComp.constructionPlanes
        sketches = targetComp.sketches

        tangent = normalize(tangentVec)
        if vector_length(tangent) < 1e-9:
            return None

        helperUp = adsk.core.Vector3D.create(0, 0, 1)
        if abs(dot(tangent, helperUp)) > 0.95:
            helperUp = adsk.core.Vector3D.create(0, 1, 0)

        side = normalize(cross(helperUp, tangent))
        if vector_length(side) < 1e-9:
            return None

        normal_in_plane = normalize(cross(tangent, side))
        if vector_length(normal_in_plane) < 1e-9:
            return None

        refSize = max(self.diameter * 0.2, self.profileRadius * 2.0, 0.5)

        p1 = startPoint
        p2 = add_point_vec(startPoint, scaled_vector(side, refSize))
        p3 = add_point_vec(startPoint, scaled_vector(normal_in_plane, refSize))

        helperSketch = sketches.add(targetComp.xYConstructionPlane)
        helperSketch.name = self.shapeName + ' Start Plane Helper'
        try:
            helperSketch.is3D = True
        except:
            pass

        sp1 = helperSketch.sketchPoints.add(p1)
        sp2 = helperSketch.sketchPoints.add(p2)
        sp3 = helperSketch.sketchPoints.add(p3)

        line1 = helperSketch.sketchCurves.sketchLines.addByTwoPoints(sp1, sp2)
        line1.isConstruction = True
        line2 = helperSketch.sketchCurves.sketchLines.addByTwoPoints(sp1, sp3)
        line2.isConstruction = True

        planeInput = planes.createInput()
        planeInput.setByThreePoints(sp1, sp2, sp3)
        plane = planes.add(planeInput)
        plane.name = self.shapeName + ' Start Plane'
        return plane

    def createSweepPath(self, targetComp, path_points):
        if len(path_points) < 2:
            return None, None

        sketches = targetComp.sketches
        sketch = sketches.add(targetComp.xYConstructionPlane)
        sketch.name = self.shapeName + ' Sweep Path'
        try:
            sketch.is3D = True
        except:
            pass

        lines = sketch.sketchCurves.sketchLines
        sketch_points = sketch.sketchPoints

        first_sketch_point = sketch_points.add(path_points[0])
        prev_sketch_point = first_sketch_point
        first_line = None

        for i in range(1, len(path_points)):
            next_sketch_point = sketch_points.add(path_points[i])
            line = lines.addByTwoPoints(prev_sketch_point, next_sketch_point)
            if first_line is None:
                first_line = line
            prev_sketch_point = next_sketch_point

        if self.isClosedPath() and len(path_points) > 2:
            if not self.pointsAreClose(path_points[0], path_points[-1]):
                close_line = lines.addByTwoPoints(prev_sketch_point, first_sketch_point)
                if first_line is None:
                    first_line = close_line

        if not first_line:
            return sketch, None

        feats = targetComp.features
        try:
            path = feats.createPath(first_line, True)
        except:
            path = None

        return sketch, path

    def createSweepProfileSketch(self, targetComp, startPlane, frame):
        if not startPlane:
            return None, None

        sketches = targetComp.sketches
        sketch = sketches.add(startPlane)
        sketch.name = self.shapeName + ' Sweep Profile'

        if self.profileType == 'Circle':
            center2d = sketch.modelToSketchSpace(frame['p'])
            circles = sketch.sketchCurves.sketchCircles
            circles.addByCenterRadius(center2d, self.profileRadius)
            if sketch.profiles.count < 1:
                return sketch, None
            return sketch, sketch.profiles.item(0)

        skPoints = []
        for j in range(self.profileSegments):
            theta = 2.0 * math.pi * float(j) / float(self.profileSegments)
            r = self.profileRadiusAt(theta)
            offset_n = scaled_vector(frame['n'], r * math.cos(theta))
            offset_b = scaled_vector(frame['b'], r * math.sin(theta))
            worldPt = adsk.core.Point3D.create(
                frame['p'].x + offset_n.x + offset_b.x,
                frame['p'].y + offset_n.y + offset_b.y,
                frame['p'].z + offset_n.z + offset_b.z
            )
            skPoints.append(sketch.modelToSketchSpace(worldPt))

        lines = sketch.sketchCurves.sketchLines
        prev = None
        first = None
        for pt in skPoints:
            if prev is None:
                prev = pt
                first = pt
                continue
            lines.addByTwoPoints(prev, pt)
            prev = pt
        if prev and first:
            lines.addByTwoPoints(prev, first)

        if sketch.profiles.count < 1:
            return sketch, None
        return sketch, sketch.profiles.item(0)

    def createSweptBody(self, targetComp, profile, path):
        if not profile or not path:
            return None

        sweeps = targetComp.features.sweepFeatures
        sweepInput = sweeps.createInput(
            profile,
            path,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        sweep = sweeps.add(sweepInput)
        if sweep and sweep.bodies.count > 0:
            body = sweep.bodies.item(0)
            body.name = self.shapeName + ' Body'
            return body
        return None

    def cleanupExistingGeometry(self, targetComp):
        name_prefixes = [
            self.shapeName + ' Path',
            self.shapeName + ' Sweep Path',
            self.shapeName + ' Path Preview',
            self.shapeName + ' Base Profile Preview',
            self.shapeName + ' Sweep Profile',
            self.shapeName + ' Start Plane Helper',
            self.shapeName + ' Start Plane',
            self.shapeName + ' Body'
        ]

        try:
            for i in range(targetComp.bRepBodies.count - 1, -1, -1):
                body = targetComp.bRepBodies.item(i)
                if any(body.name.startswith(prefix) for prefix in name_prefixes):
                    body.deleteMe()
        except:
            pass

        try:
            for i in range(targetComp.sketches.count - 1, -1, -1):
                sketch = targetComp.sketches.item(i)
                if any(sketch.name.startswith(prefix) for prefix in name_prefixes):
                    sketch.deleteMe()
        except:
            pass

        try:
            for i in range(targetComp.constructionPlanes.count - 1, -1, -1):
                plane = targetComp.constructionPlanes.item(i)
                if any(plane.name.startswith(prefix) for prefix in name_prefixes):
                    plane.deleteMe()
        except:
            pass

    def buildFromInputs(self, inputs):
        unitsMgr = app.activeProduct.unitsManager
        self.shapeName = inputs.itemById('shapeName').value
        pathInput = inputs.itemById('pathType')
        profileInput = inputs.itemById('profileType')
        self.pathType = pathInput.selectedItem.name if pathInput and pathInput.selectedItem else defaultPathType
        self.profileType = profileInput.selectedItem.name if profileInput and profileInput.selectedItem else defaultProfileType
        self.diameter = unitsMgr.evaluateExpression(inputs.itemById('diameter').expression, 'cm')
        self.zStretch = unitsMgr.evaluateExpression(inputs.itemById('zStretch').expression, 'cm')
        self.profileRadius = unitsMgr.evaluateExpression(inputs.itemById('profileRadius').expression, 'cm')
        self.profileEquation = inputs.itemById('profileEquation').value
        self.generateSolid = inputs.itemById('generateSolid').value
        self.pathSegments = int(inputs.itemById('pathSegments').value)
        self.profileSegments = int(inputs.itemById('profileSegments').value)
        self.internalLoops = int(inputs.itemById('internalLoops').value)
        self.mainLoops = int(inputs.itemById('mainLoops').value)
        self.secondaryLoops = int(inputs.itemById('secondaryLoops').value)
        self.amplitude = unitsMgr.evaluateExpression(inputs.itemById('amplitude').expression, 'cm')
        self.petals = int(inputs.itemById('petals').value)
        self.flowerAmplitude = unitsMgr.evaluateExpression(inputs.itemById('flowerAmplitude').expression, 'cm')
        self.baseFreq = int(inputs.itemById('baseFreq').value)
        self.amp1 = unitsMgr.evaluateExpression(inputs.itemById('amp1').expression, 'cm')
        self.amp2 = unitsMgr.evaluateExpression(inputs.itemById('amp2').expression, 'cm')
        self.build()

    def build(self):
        try:
            targetComp = getTargetComponent()
            if not targetComp:
                ui.messageBox('Failed to get target component.')
                return

            self.cleanupExistingGeometry(targetComp)

            path_points = self.buildPathPoints()
            if len(path_points) < 3:
                ui.messageBox('Not enough path points generated.')
                return

            frames = self.buildTransportFrames(path_points)
            if len(frames) < 3:
                ui.messageBox('Failed to build stable transported frames along the path.')
                return

            self.createPreviewPathSketch(targetComp, path_points)
            self.createPreviewProfileSketch(targetComp, frames[0])

            if not self.generateSolid:
                return

            _, sweepPath = self.createSweepPath(targetComp, path_points)
            if not sweepPath:
                ui.messageBox('Failed to create a continuous closed sweep path.')
                return

            tangentVec = subtract_points(path_points[1], path_points[0])
            if vector_length(tangentVec) < 1e-9 and len(path_points) > 2:
                tangentVec = subtract_points(path_points[2], path_points[0])

            startPlane = self.createPerpendicularStartPlane(targetComp, path_points[0], tangentVec)
            if not startPlane:
                ui.messageBox('Failed to create start plane for sweep profile.')
                return

            _, profile = self.createSweepProfileSketch(targetComp, startPlane, frames[0])
            if not profile:
                ui.messageBox('Failed to create a closed sweep profile.')
                return

            body = self.createSweptBody(targetComp, profile, sweepPath)
            if not body:
                ui.messageBox('Failed to create swept body.')
        except:
            if ui:
                ui.messageBox('Failed to create shape.\n\n{}'.format(traceback.format_exc()))


def run(context):
    try:
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox('The DESIGN workspace must be active when running this script.')
            return

        commandDefinitions = ui.commandDefinitions
        cmdDef = commandDefinitions.itemById('SegmentedSweepShapeGenerator')

        if not cmdDef:
            cmdDef = commandDefinitions.addButtonDefinition(
                'SegmentedSweepShapeGenerator',
                'Segmented Sweep Shape Generator',
                'Generate a selectable r(theta) base shape swept around selectable closed paths using a clean continuous sweep workflow.'
            )

        onCommandCreated = ShapeCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)

        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
