import cadquery as cq

from .core import LLAMADAS


class BooleanTypes:
    DifferenceBooleanType, IntersectionBooleanType, UnionBooleanType = 0, 1, 2


class DesignTypes:
    DirectDesignType, ParametricDesignType = 0, 1


class FeatureOperations:
    JoinFeatureOperation, CutFeatureOperation = 0, 1


class TBody:
    """Cuerpo temporal: un sólido de CadQuery (en cm, como Fusion)."""
    def __init__(self, s):
        self.s = s


class TemporaryBRepManager:
    @staticmethod
    def get():
        return TemporaryBRepManager()

    def createBox(self, obb):
        h = obb.l.cross(obb.w)
        base = obb.c - h * (obb.dh / 2)
        pts = [base + obb.l * (a * obb.dl / 2) + obb.w * (b * obb.dw / 2)
               for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        cara = cq.Face.makeFromWires(cq.Wire.makePolygon(pts, close=True))
        return TBody(cq.Solid.extrudeLinear(cara, h * obb.dh))

    def createCylinderOrCone(self, pointOne, pointOneRadius, pointTwo, pointTwoRadius):
        assert abs(pointOneRadius - pointTwoRadius) < 1e-12
        d = pointTwo.v() - pointOne.v()
        return TBody(cq.Solid.makeCylinder(pointOneRadius, d.Length, pointOne.v(), d.normalized()))

    def booleanOperation(self, targetBody, toolBody, booleanType):
        if booleanType == BooleanTypes.UnionBooleanType:
            targetBody.s = targetBody.s.fuse(toolBody.s).clean()
        elif booleanType == BooleanTypes.DifferenceBooleanType:
            targetBody.s = targetBody.s.cut(toolBody.s).clean()
        else:
            targetBody.s = targetBody.s.intersect(toolBody.s).clean()
        return True


class BRepBody:
    def __init__(self, s):
        self.s, self.name, self.opacity = s, '', 1.0


class _Bodies:
    def __init__(self):
        self.l = []

    def add(self, body, baseFeature=None):
        if baseFeature is not None:
            assert baseFeature.editando, 'bRepBodies.add con baseFeature fuera de startEdit/finishEdit'
        b = BRepBody(body.s)
        self.l.append(b)
        return b

    @property
    def count(self):
        return len(self.l)

    def item(self, i):
        return self.l[i]


class _BaseFeature:
    def __init__(self):
        self.editando, self.name = False, ''

    def startEdit(self):
        self.editando = True

    def finishEdit(self):
        self.editando = False


class _BaseFeatures:
    def add(self):
        return _BaseFeature()


class _Registro:
    """Objeto que acepta cualquier llamada/atributo y lo apunta (planos, bocetos, textos, extrusiones)."""
    def __init__(self, nombre):
        object.__setattr__(self, '_n', nombre)

    def __getattr__(self, a):
        return _Registro(self._n + '.' + a)

    def __setattr__(self, a, v):
        LLAMADAS.append((self._n + '.' + a + ' =', v))

    def __call__(self, *args, **kw):
        LLAMADAS.append((self._n, args))
        return _Registro(self._n + '()')


class _Features:
    def __init__(self):
        self.baseFeatures = _BaseFeatures()
        self.extrudeFeatures = _Registro('extrudeFeatures')


class Component:
    def __init__(self):
        self.name = ''
        self.bRepBodies = _Bodies()
        self.features = _Features()
        self.occurrences = _Occurrences()
        self.constructionPlanes = _Registro('constructionPlanes')
        self.xYConstructionPlane = 'xY'
        self.sketches = _Registro('sketches')


class Occurrence:
    def __init__(self):
        self.component = Component()


class _Occurrences:
    def __init__(self):
        self.l = []

    def addNewComponent(self, m):
        o = Occurrence()
        self.l.append(o)
        return o


class _RootComponent(Component):
    """Como en Fusion: el nombre del componente raíz no se puede cambiar."""
    def __setattr__(self, a, v):
        if a == 'name' and 'name' in self.__dict__:
            raise RuntimeError('3 : root component name cannot be changed')
        object.__setattr__(self, a, v)


class Design:
    def __init__(self):
        self.designType = DesignTypes.DirectDesignType
        self.rootComponent = _RootComponent()

    @staticmethod
    def cast(x):
        return x
