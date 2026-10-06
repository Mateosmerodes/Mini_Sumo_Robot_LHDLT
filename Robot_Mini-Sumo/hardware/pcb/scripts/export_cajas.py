"""Exporta la caja envolvente de cada componente de la PCB (coordenadas del robot) para el modelo 3D.

Sin las librerías 3D de KiCad, el ensamblaje representa cada componente como un prisma
con su contorno de la capa Fab y una altura típica según el encapsulado.
"""
import json
import os

import pcbnew

if hasattr(pcbnew, 'SwigPyIterator') and not hasattr(pcbnew.SwigPyIterator, 'next'):
    pcbnew.SwigPyIterator.next = pcbnew.SwigPyIterator.__next__

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.join(HERE, '..', 'robot_sumo.kicad_pcb')
OUT = os.path.join(HERE, '..', '..', 'mecanica', 'cad', 'pcb_componentes.json')
OX, OY = 100.0, 50.0

# (fragmento del nombre de huella, altura en mm)
ALTURAS = [
    ('ESP32-S3-WROOM', 3.1), ('XT30UPB', 11.0), ('XKB_U262', 7.4), ('JST_SH', 4.25),
    ('HTSSOP', 1.1), ('SOT-223', 1.8), ('SOT-23', 1.1), ('TO-252', 2.4), ('D_SMA', 2.3),
    ('SRN4018', 1.8), ('KMR2', 1.9), ('2512', 0.7), ('1206', 1.2), ('0805', 1.0),
    ('0603', 0.6), ('WS2812B-2020', 0.85), ('SolderWire', 0.0), ('MountingHole', 0.0),
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


def main():
    board = pcbnew.LoadBoard(PCB)
    out = []
    for fp in board.GetFootprints():
        name = fp.GetFPID().GetLibItemName().wx_str()
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
