"""Chasis del robot mini-sumo LHDT v2 — script para Autodesk Fusion 360.

Cómo usarlo:
  1. Fusion 360 > pestaña UTILIDADES > Complementos (Scripts y complementos, o Mayús+S).
  2. Pestaña "Scripts" > botón "+" (o el icono verde) > elegir ESTA carpeta (ChasisLHDT).
  3. Seleccionar "ChasisLHDT" > Ejecutar.
Crea un diseño nuevo con un componente por pieza:
  - chasis, abrazadera_motor_izq, abrazadera_motor_der  -> se imprimen (exportar a STL/3MF)
  - cuchilla_acero                                       -> chapa de 0,4 mm (no se imprime)
  - REFERENCIAS (no imprimir): motores, ruedas, batería, PCB, ESP32, sensores
Las cotas están en geometria_chasis.py (en esta carpeta). Para cambiar una medida, se edita ahí y
se vuelve a ejecutar el script: sale un diseño nuevo con todo recalculado.

Unidades: Fusion trabaja internamente en cm; geometria_chasis.py está en mm y aquí se convierte.
Frente del robot hacia +Y, Z hacia arriba, centrado en el origen.
"""
import importlib
import os
import sys
import traceback

import adsk.core
import adsk.fusion

AQUI = os.path.dirname(os.path.abspath(__file__))


def _g():
    if AQUI not in sys.path:
        sys.path.insert(0, AQUI)
    import geometria_chasis
    importlib.reload(geometria_chasis)   # coge los cambios si se vuelve a ejecutar
    return geometria_chasis


class Constructor:
    """Convierte el árbol de operaciones de geometria_chasis.py en cuerpos temporales de Fusion."""

    def __init__(self, g):
        self.g = g
        self.tbm = adsk.fusion.TemporaryBRepManager.get()

    def P(self, x, y, z):
        return adsk.core.Point3D.create(*self.g.a_fusion(x, y, z))

    def V(self, v):
        return adsk.core.Vector3D.create(*self.g.vec_a_fusion(v))

    def cuerpo(self, op):
        t = op[0]
        if t == 'box':
            _, x0, x1, y0, y1, z0, z1 = op
            obb = adsk.core.OrientedBoundingBox3D.create(
                self.P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0),
                (x1 - x0) / 10.0, (y1 - y0) / 10.0, (z1 - z0) / 10.0)
            return self.tbm.createBox(obb)
        if t == 'obox':
            _, c, l, u, w, dl, du, dw = op
            obb = adsk.core.OrientedBoundingBox3D.create(self.P(*c), self.V(l), self.V(u),
                                                         dl / 10.0, du / 10.0, dw / 10.0)
            return self.tbm.createBox(obb)
        if t == 'cyl':
            _, eje, r, a0, a1, c1, c2 = op
            if eje == 'x':
                p0, p1 = self.P(a0, c1, c2), self.P(a1, c1, c2)
            elif eje == 'y':
                p0, p1 = self.P(c1, a0, c2), self.P(c1, a1, c2)
            else:
                p0, p1 = self.P(c1, c2, a0), self.P(c1, c2, a1)
            return self.tbm.createCylinderOrCone(p0, r / 10.0, p1, r / 10.0)
        if t == 'union':
            b = self.cuerpo(op[1][0])
            for h in op[1][1:]:
                self._bool(b, self.cuerpo(h), adsk.fusion.BooleanTypes.UnionBooleanType)
            return b
        if t == 'cut':
            b = self.cuerpo(op[1])
            for h in op[2]:
                self._bool(b, self.cuerpo(h), adsk.fusion.BooleanTypes.DifferenceBooleanType)
            return b
        raise ValueError('Operación desconocida: %s' % t)

    def _bool(self, a, b, tipo):
        if not self.tbm.booleanOperation(a, b, tipo):
            raise RuntimeError('Falló una operación booleana')


def nuevo_componente(padre, nombre, cuerpo_temporal, design):
    occ = padre.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = nombre
    if design.designType == adsk.fusion.DesignTypes.ParametricDesignType:
        bf = comp.features.baseFeatures.add()
        bf.startEdit()
        comp.bRepBodies.add(cuerpo_temporal, bf)
        bf.finishEdit()
        bf.name = nombre
    else:
        comp.bRepBodies.add(cuerpo_temporal)
    cuerpo = comp.bRepBodies.item(comp.bRepBodies.count - 1)
    cuerpo.name = nombre
    return occ, comp, cuerpo


def grabar_textos(g, comp, cuerpo):
    """Graba los textos en la cara inferior del chasis (se leen mirando el robot por debajo)."""
    planos = comp.constructionPlanes
    pin = planos.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(g.Z_BAJO / 10.0))
    plano = planos.add(pin)
    plano.name = 'cara inferior'
    sk = comp.sketches.add(plano)
    sk.name = 'textos LHDT'
    for texto, x, y, alto in g.textos():
        cx, cy, cz = g.a_fusion(x, y, g.Z_BAJO)
        ancho = len(texto) * alto * 0.8 / 10.0
        h = alto * 1.6 / 10.0
        p0 = sk.modelToSketchSpace(adsk.core.Point3D.create(cx - ancho / 2, cy - h / 2, cz))
        p1 = sk.modelToSketchSpace(adsk.core.Point3D.create(cx + ancho / 2, cy + h / 2, cz))
        ti = sk.sketchTexts.createInput2(texto, alto / 10.0)
        ti.setAsMultiLine(p0, p1, adsk.core.HorizontalAlignments.CenterHorizontalAlignment,
                          adsk.core.VerticalAlignments.MiddleVerticalAlignment, 0)
        st = sk.sketchTexts.add(ti)
        st.isHorizontalFlip = True     # en espejo visto desde arriba = legible desde abajo
        ext = comp.features.extrudeFeatures
        ei = ext.createInput(st, adsk.fusion.FeatureOperations.CutFeatureOperation)
        ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal(g.TEXTO_PROFUNDIDAD / 10.0))
        ei.participantBodies = [cuerpo]
        ext.add(ei)
    sk.isVisible = False
    plano.isLightBulbOn = False


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        g = _g()
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        raiz = design.rootComponent
        raiz.name = 'Robot mini-sumo LHDT v2 - chasis'
        k = Constructor(g)
        avisos = []

        for nombre, (op, imprimir, color) in g.piezas().items():
            occ, comp, cuerpo = nuevo_componente(raiz, nombre, k.cuerpo(op), design)
            if nombre == 'chasis':
                try:
                    grabar_textos(g, comp, cuerpo)
                except Exception:
                    avisos.append('No se pudo grabar el texto LHDT (hacerlo a mano con un boceto de texto '
                                  'en la cara inferior y extruir 0,6 mm cortando):\n' + traceback.format_exc(limit=1))

        occ_ref = raiz.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ_ref.component.name = 'REFERENCIAS (no imprimir)'
        for nombre, op in g.referencias().items():
            _, _, cuerpo = nuevo_componente(occ_ref.component, nombre, k.cuerpo(op), design)
            try:
                cuerpo.opacity = 0.6
            except Exception:
                pass

        app.activeViewport.fit()
        msg = ('Chasis LHDT v2 creado.\n\nImprimir: chasis + 2 abrazaderas (PETG o PLA+).\n'
               'El componente REFERENCIAS solo sirve para ver el montaje.\n'
               'Cotas: geometria_chasis.py (las marcadas con 🔶 hay que medirlas).')
        if avisos:
            msg += '\n\nAVISOS:\n' + '\n'.join(avisos)
        ui.messageBox(msg)
    except Exception:
        if ui:
            ui.messageBox('Error:\n{}'.format(traceback.format_exc()))
