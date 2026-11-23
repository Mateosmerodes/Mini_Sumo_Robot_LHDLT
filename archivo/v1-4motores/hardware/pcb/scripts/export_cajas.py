"""Exporta la caja envolvente de cada componente de la PCB (coordenadas del robot) para el modelo 3D.

Sin las librerías 3D de KiCad, el ensamblaje representa cada componente como un prisma
con su contorno de la capa Fab y una altura típica según el encapsulado.
La ESP32-S3-DevKitC-1 se representa aparte: zócalos sobre la PCB y la DevKit encima de ellos
(campo "z0": altura de la cara inferior de la caja sobre la cara superior de la PCB).
"""
import json
import os
import sys

import pcbnew

if hasattr(pcbnew, 'SwigPyIterator') and not hasattr(pcbnew.SwigPyIterator, 'next'):
    pcbnew.SwigPyIterator.next = pcbnew.SwigPyIterator.__next__

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
import geometria as g               # noqa: E402
from gen_lib import tramos          # noqa: E402

PCB = os.path.join(HERE, '..', 'robot_sumo.kicad_pcb')
OUT = os.path.join(HERE, '..', '..', 'mecanica', 'cad', 'pcb_componentes.json')
OX, OY = 100.0, 50.0

# (fragmento del nombre de huella, altura en mm)
ALTURAS = [
    ('XT30UPB', 11.0), ('JST_SH', 4.25),
    ('HTSSOP', 1.1), ('SOT-223', 1.8), ('SOT-23', 1.1), ('TO-252', 2.4), ('D_SMA', 2.3),
    ('SRN4018', 1.8), ('KMR2', 1.9), ('2512', 0.7), ('1206', 1.2), ('0805', 1.0),
    ('0603', 0.6), ('SolderWire', 0.0), ('MountingHole', 0.0),
]


def bbox_fab(fp):
    xs, ys = [], []
    for it in fp.GraphicalItems():
        if it.GetLayer() == pcbnew.F_Fab and isinstance(it, pcbnew.PCB_SHAPE):
            bb = it.GetBoundingBox()
            xs += [bb.GetX(), bb.GetRight()]
            ys += [bb.GetY(), bb.GetBottom()]
    if not xs:  # sin dibujo en Fab: usar los pads
        bb = fp.GetBoundingBox(False)
        xs, ys = [bb.GetX(), bb.GetRight()], [bb.GetY(), bb.GetBottom()]
    mm = pcbnew.ToMM
    return [mm(min(xs)) - OX, mm(min(ys)) - OY, mm(max(xs)) - OX, mm(max(ys)) - OY]


def cajas_devkit(fp):
    """Zócalos (tira hembra + plástico de la tira macho) y la DevKit con sus componentes encima."""
    mm = pcbnew.ToMM
    x0, y0 = mm(fp.GetPosition().x) - OX, mm(fp.GetPosition().y) - OY
    alto_zocalo = g.ZOCALO_ALTO + g.DEVKIT_SEPARADOR
    out = []
    for fx, nums in ((0.0, [int(p.GetNumber()) for p in fp.Pads() if int(p.GetNumber()) <= 22]),
                     (g.DEVKIT_FILAS, [int(p.GetNumber()) - 22 for p in fp.Pads() if int(p.GetNumber()) > 22])):
        for a, b in tramos(nums):
            out.append({'ref': f'{fp.GetReference()}_zocalo{len(out) + 1}', 'huella': 'tira hembra 2,54 mm',
                        'bbox': [round(v, 3) for v in (x0 + fx - 1.27, y0 + (a - 1) * g.DEVKIT_PASO - 1.27,
                                                       x0 + fx + 1.27, y0 + (b - 1) * g.DEVKIT_PASO + 1.27)],
                        'alto': alto_zocalo})
    px0, py0, px1, _ = g.DEVKIT_PLACA
    ax0, ay0, ax1, ay1 = g.DEVKIT_ANTENA
    out.append({'ref': fp.GetReference(), 'huella': 'ESP32-S3-DevKitC-1',
                'bbox': [round(v, 3) for v in (x0 + px0, y0 + py0, x0 + px1, y0 + g.DEVKIT_USB_Y1)],
                'alto': g.DEVKIT_ALTO, 'z0': alto_zocalo})
    out.append({'ref': f'{fp.GetReference()}_antena', 'huella': 'antena del módulo',
                'bbox': [round(v, 3) for v in (x0 + ax0, y0 + ay0, x0 + ax1, y0 + ay1)],
                'alto': 0.8, 'z0': alto_zocalo + 1.6})
    return out


def main():
    board = pcbnew.LoadBoard(PCB)
    out = []
    for fp in board.GetFootprints():
        name = fp.GetFPID().GetLibItemName().wx_str()
        if 'DevKitC' in name:
            out += cajas_devkit(fp)
            continue
        h = next((a for k, a in ALTURAS if k in name), 1.0)
        if h <= 0:
            continue
        out.append({'ref': fp.GetReference(), 'huella': name, 'bbox': [round(v, 3) for v in bbox_fab(fp)],
                    'alto': h})
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(out, f, indent=1)
    print('escrito', os.path.relpath(OUT), f'({len(out)} componentes)')


if __name__ == '__main__':
    main()
