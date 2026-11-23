import cadquery as cq

LLAMADAS = []   # registro de llamadas que no generan geometría (textos, planos...)


class Point3D:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    @staticmethod
    def create(x=0.0, y=0.0, z=0.0):
        return Point3D(x, y, z)

    def v(self):
        return cq.Vector(self.x, self.y, self.z)


class Vector3D(Point3D):
    @staticmethod
    def create(x=0.0, y=0.0, z=0.0):
        return Vector3D(x, y, z)


class Matrix3D:
    @staticmethod
    def create():
        return Matrix3D()


class OrientedBoundingBox3D:
    @staticmethod
    def create(centerPoint, lengthDirection, widthDirection, length, width, height):
        o = OrientedBoundingBox3D()
        o.c, o.l, o.w = centerPoint.v(), lengthDirection.v().normalized(), widthDirection.v().normalized()
        o.dl, o.dw, o.dh = length, width, height
        return o


class ValueInput:
    @staticmethod
    def createByReal(v):
        return v


class DocumentTypes:
    FusionDesignDocumentType = 0


class HorizontalAlignments:
    CenterHorizontalAlignment = 1


class VerticalAlignments:
    MiddleVerticalAlignment = 1


class _UI:
    def messageBox(self, m):
        print('[messageBox]', m)
        LLAMADAS.append(('messageBox', m))


class _Viewport:
    def fit(self):
        pass


class _Docs:
    def __init__(self, app):
        self.app = app

    def add(self, tipo):
        from . import fusion
        self.app.activeProduct = fusion.Design()
        return object()


class Application:
    _app = None

    def __init__(self):
        self.userInterface = _UI()
        self.documents = _Docs(self)
        self.activeProduct = None
        self.activeViewport = _Viewport()

    @staticmethod
    def get():
        if Application._app is None:
            Application._app = Application()
        return Application._app
