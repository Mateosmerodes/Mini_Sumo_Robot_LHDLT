"""Ejecuta ChasisLHDT.py fuera de Fusion con la API simulada (adsk_simulado) y compara cada pieza
con la que construye construir_cadquery.py. Uso: python pruebas/probar_script_fusion.py

Comprueba la lógica del script (conversión mm -> cm, orientación, operaciones). No sustituye a
ejecutarlo de verdad en Fusion 360.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CHASIS = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(AQUI, 'adsk_simulado'))
sys.path.insert(0, os.path.join(CHASIS, 'fusion360', 'ChasisLHDT'))
sys.path.insert(0, CHASIS)

import ChasisLHDT  # noqa: E402
import construir_cadquery as cqb  # noqa: E402
import geometria_chasis as g  # noqa: E402
from adsk import core  # noqa: E402

ChasisLHDT.run({})
design = core.Application.get().activeProduct
raiz = design.rootComponent
cuerpos = {}
for occ in raiz.occurrences.l:
    c = occ.component
    for b in c.bRepBodies.l:
        cuerpos[b.name] = b.s
    for o2 in c.occurrences.l:
        for b in o2.component.bRepBodies.l:
            cuerpos[b.name] = b.s

esperado = {n: op for n, (op, _, _) in g.piezas().items()}
esperado.update(g.referencias())
fallos = 0
for nombre, op in esperado.items():
    ref = cqb.solido(op)                       # mm, coordenadas de Fusion
    fus = cuerpos[nombre].scale(10.0)          # cm -> mm
    dif = ref.cut(fus).Volume() + fus.cut(ref).Volume()
    ok = dif < 1e-3 * max(ref.Volume(), 1)
    fallos += not ok
    print(f'{"OK " if ok else "MAL"} {nombre:24s} V_fusion={fus.Volume():10.1f} mm3  V_cadquery={ref.Volume():10.1f} mm3  diferencia={dif:.4f}')
textos = [l for l in core.LLAMADAS if 'sketchTexts' in l[0]]
print('Llamadas de texto registradas:', len(textos))
print('Tipo de diseño paramétrico:', design.designType == 1)
errores = [l for l in core.LLAMADAS if l[0] == 'messageBox' and 'Error' in l[1]]
sys.exit(1 if fallos or errores else 0)
