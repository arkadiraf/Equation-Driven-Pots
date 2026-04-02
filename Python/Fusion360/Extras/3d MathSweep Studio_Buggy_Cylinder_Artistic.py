import adsk.core, adsk.fusion, traceback
import math

# -----------------------------------------------------------------------------
# Defaults aligned to the uploaded SweepDesigner concept but implemented using
# a segmented-only robust Fusion workflow.
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

    def buildProfileRings(self, frames):
        rings = []
        centers = []
        for frame in frames:
            ring = []
            centers.append(frame['p'])
            for j in range(self.profileSegments):
                theta = 2.0 * math.pi * float(j) / float(self.profileSegments)
                r = self.profileRadiusAt(theta)
                offset_n = scaled_vector(frame['n'], r * math.cos(theta))
                offset_b = scaled_vector(frame['b'], r * math.sin(theta))
                ring.append(adsk.core.Point3D.create(
                    frame['p'].x + offset_n.x + offset_b.x,
                    frame['p'].y + offset_n.y + offset_b.y,
                    frame['p'].z + offset_n.z + offset_b.z
                ))
            rings.append(ring)
        return centers, rings

    def createPathSketch(self, targetComp, path_points):
        sketches = targetComp.sketches
        sketch = sketches.add(targetComp.xYConstructionPlane)
        sketch.name = self.shapeName + ' Path'
        try:
            sketch.is3D = True
        except:
            pass

        lines = sketch.sketchCurves.sketchLines
        first = None
        prev = None
        for pt in path_points:
            sp = sketch.sketchPoints.add(pt)
            if first is None:
                first = sp
            if prev is not None:
                lines.addByTwoPoints(prev, sp)
            prev = sp
        if prev and first:
            lines.addByTwoPoints(prev, first)
        return sketch

    def createProfileSketch(self, targetComp, frame):
        sketches = targetComp.sketches
        sketch = sketches.add(targetComp.xYConstructionPlane)
        sketch.name = self.shapeName + ' Base Profile'
        try:
            sketch.is3D = True
        except:
            pass

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
        first = None
        prev = None
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

    def addSphere(self, tempMgr, bodies, point, radius):
        try:
            body = tempMgr.createSphere(point, radius)
            if body:
                bodies.append(body)
        except:
            pass

    def addCylinder(self, tempMgr, bodies, p0, p1, radius):
        try:
            if vector_length(subtract_points(p1, p0)) < 1e-6:
                return
            body = tempMgr.createCylinderOrCone(p0, radius, p1, radius)
            if body:
                bodies.append(body)
        except:
            pass

    def createSegmentedSweptBody(self, targetComp, centers, rings):
        tempMgr = adsk.fusion.TemporaryBRepManager.get()
        if not tempMgr:
            ui.messageBox('TemporaryBRepManager is unavailable.')
            return None

        if len(rings) < 3 or len(rings[0]) < 3:
            ui.messageBox('Not enough generated geometry to build the segmented sweep.')
            return None

        min_profile_radius = self.estimateMinProfileRadius()
        strut_radius = max(0.02, min_profile_radius * 0.32)
        node_radius = strut_radius * 1.08

        bodies = []
        path_count = len(rings)
        prof_count = len(rings[0])

        # Add centerline reinforcement so the body stays contiguous and robust.
        for i in range(path_count):
            self.addSphere(tempMgr, bodies, centers[i], node_radius)
            self.addCylinder(tempMgr, bodies, centers[i], centers[(i + 1) % path_count], strut_radius)

        for i in range(path_count):
            next_i = (i + 1) % path_count
            for j in range(prof_count):
                next_j = (j + 1) % prof_count
                p = rings[i][j]
                p_next_ring = rings[next_i][j]
                p_next_profile = rings[i][next_j]
                c = centers[i]

                self.addSphere(tempMgr, bodies, p, node_radius)
                self.addCylinder(tempMgr, bodies, p, p_next_ring, strut_radius)
                self.addCylinder(tempMgr, bodies, p, p_next_profile, strut_radius)
                self.addCylinder(tempMgr, bodies, c, p, strut_radius)

        if not bodies:
            ui.messageBox('Failed to create segmented temporary bodies.')
            return None

        merged = bodies[0]
        for i in range(1, len(bodies)):
            try:
                tempMgr.booleanOperation(merged, bodies[i], adsk.fusion.BooleanTypes.UnionBooleanType)
            except:
                pass

        try:
            baseFeat = targetComp.features.baseFeatures.add()
            baseFeat.startEdit()
            body = targetComp.bRepBodies.add(merged, baseFeat)
            baseFeat.finishEdit()
            if body:
                body.name = self.shapeName + ' Body'
                return body
        except:
            ui.messageBox('Failed to convert segmented body into model body.\n\n{}'.format(traceback.format_exc()))
        return None

    def estimateMinProfileRadius(self):
        min_r = None
        sample_count = max(24, self.profileSegments * 2)
        for i in range(sample_count):
            theta = 2.0 * math.pi * float(i) / float(sample_count)
            r = self.profileRadiusAt(theta)
            if min_r is None or r < min_r:
                min_r = r
        return max(0.001, min_r if min_r is not None else self.profileRadius)

    def cleanupExistingGeometry(self, targetComp):
        name_prefixes = [
            self.shapeName + ' Path',
            self.shapeName + ' Base Profile',
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

            self.createPathSketch(targetComp, path_points)
            self.createProfileSketch(targetComp, frames[0])

            if not self.generateSolid:
                return

            centers, rings = self.buildProfileRings(frames)
            body = self.createSegmentedSweptBody(targetComp, centers, rings)
            if not body:
                ui.messageBox('Failed to create the segmented swept body.')
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
                'Generate a selectable r(theta) base shape swept around selectable closed paths using segmented bodies only.'
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
