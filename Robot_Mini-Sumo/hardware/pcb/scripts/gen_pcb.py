"""Genera la PCB (robot_sumo.kicad_pcb) a partir de design.py y ../../geometria.py.

- Contorno, taladros y posición del ESP32 salen de la geometría mecánica.
- Las huellas se enlazan con los símbolos del esquemático (mismos UUID) para que
  "Actualizar PCB desde esquemático" funcione después en KiCad.
- Coloca los componentes por bloques; el rutado se hace en KiCad.
Las coordenadas de COLOCACION están en el sistema del robot (mm, Y hacia atrás).
"""
import math
import os
import sys

import pcbnew

# Compatibilidad SWIG de KiCad 10 con Python 3.14 (el iterador no expone .next())
if hasattr(pcbnew, 'SwigPyIterator') and not hasattr(pcbnew.SwigPyIterator, 'next'):
    pcbnew.SwigPyIterator.next = pcbnew.SwigPyIterator.__next__

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
import design                       # noqa: E402
import geometria as g               # noqa: E402
from gen_sch import uid             # noqa: E402

FP_ROOT = '/usr/share/kicad/footprints'
OUT = os.path.join(HERE, '..', design.PROJECT + '.kicad_pcb')
OX, OY = 100.0, 50.0                # posición del origen del robot en la hoja de KiCad


def P(x, y):
    return pcbnew.VECTOR2I_MM(OX + x, OY + y)


# ------------------------------------------------------------------ colocación
# ref: (x, y, rotación)   — sistema del robot
COLOCACION = {
    # Fila delantera: sensores frontales + expansión
    'J13': (23.5, 33.4, 0), 'J8': (32.5, 33.4, 0), 'J18': (41.2, 33.4, 0), 'J9': (50.0, 33.4, 0),
    'J19': (58.8, 33.4, 0), 'J10': (67.5, 33.4, 0), 'J14': (76.5, 33.4, 0),
    # Centro: entrada de batería y buck
    'J1': (47.5, 40.6, 0), 'Q1': (46.3, 50.3, 90), 'F1': (54.2, 50.3, 90), 'R1': (51.6, 56.9, 0),
    'U2': (47.0, 60.6, 0), 'L1': (53.6, 60.4, 0), 'C6': (43.6, 60.6, 90), 'C7': (47.0, 58.1, 0),
    'C4': (43.8, 65.4, 90), 'C5': (46.4, 65.4, 90),
    'R5': (49.2, 64.9, 90), 'R6': (51.0, 64.9, 90), 'R7': (49.2, 68.6, 90), 'R8': (51.0, 68.6, 90),
    'C8': (53.6, 65.6, 90), 'C9': (56.2, 65.6, 90),
    # Pads de los motores (el cable sube desde abajo)
    'J3': (40.5, 49.3, 90), 'J4': (40.5, 66.6, 90), 'J5': (59.5, 49.3, 90), 'J6': (59.5, 66.6, 90),
    # Bornes laterales
    'J7': (17.0, 64.0, 90), 'J11': (83.0, 64.0, 90),
    # Reserva VBAT
    'C1': (29.0, 55.6, 0), 'C2': (71.0, 55.6, 0),
    # Comunes de drivers (arriba izquierda) y pull-ups I2C / filtro IR (arriba derecha)
    'R14': (22.5, 40.0, 90), 'R15': (25.0, 40.0, 90), 'C17': (27.5, 40.0, 90),
    'R16': (30.0, 40.0, 90), 'R17': (32.5, 40.0, 90),
    'R60': (67.5, 40.0, 90), 'R61': (70.0, 40.0, 90), 'R62': (72.5, 40.0, 90), 'C62': (75.2, 40.0, 90),
    # Trasera izquierda: LDO, medida de batería, botones, sensores traseros
    'U3': (27.0, 77.6, 0), 'C10': (33.6, 77.6, 90), 'C11': (36.2, 77.6, 90), 'C12': (38.6, 77.6, 90),
    'R3': (15.6, 77.0, 90), 'R4': (17.6, 77.0, 90), 'C3': (19.6, 77.0, 90),
    'SW2': (22.0, 84.0, 0), 'SW3': (28.6, 84.0, 0), 'D3': (33.0, 83.0, 0), 'R9': (33.0, 85.0, 0),
    'R12': (37.4, 83.0, 0), 'C15': (37.4, 85.0, 0), 'R13': (37.4, 81.0, 0),
    'J15': (24.0, 89.0, 0), 'J12': (33.8, 89.0, 0),
    # Trasera derecha: USB, LED, sensores traseros, IR
    'J2': (70.5, 81.0, 0), 'U4': (62.0, 80.4, 90), 'R10': (66.5, 74.6, 0), 'R11': (70.0, 74.6, 0),
    'D1': (78.6, 80.0, 90), 'D2': (82.2, 80.0, 90),
    'D4': (62.0, 76.0, 0), 'C16': (62.0, 74.0, 0),
    'J17': (66.0, 89.0, 0), 'J16': (76.0, 89.0, 0),
    # ESP32 (posición fijada por la geometría: antena fuera del borde trasero) y su desacoplo junto al pin 2 (3V3)
    'C14': (61.0, 89.2, 90), 'C13': (61.0, 85.3, 90),
    'U1': (g.ESP32_X, g.ESP32_Y, 180),
}

# Grupo de cada driver respecto al centro del DRV8874 (rotación 0)
DRIVER = {
    'U': (0.0, 0.0, 0), 'R_IPROPI': (-6.5, 0.6, 0), 'C_IPROPI': (-6.5, 2.4, 0), 'R_IMODE': (-6.5, 4.2, 0),
    'C_VCP': (6.5, -2.7, 0), 'C_CP': (6.5, -0.9, 0), 'C_VM': (6.5, 0.9, 0), 'C_BULK': (6.5, 3.4, 0),
}
CENTROS_DRIVER = {1: (29.0, 46.0), 2: (29.0, 64.0), 3: (71.0, 46.0), 4: (71.0, 64.0)}
for k, (cx, cy) in CENTROS_DRIVER.items():
    b = 20 + (k - 1) * 10
    refs = {'U': f'U{4 + k}', 'R_IPROPI': f'R{b}', 'C_IPROPI': f'C{b}', 'R_IMODE': f'R{b + 1}',
            'C_VCP': f'C{b + 1}', 'C_CP': f'C{b + 2}', 'C_VM': f'C{b + 3}', 'C_BULK': f'C{b + 4}'}
    for key, (dx, dy, r) in DRIVER.items():
        COLOCACION[refs[key]] = (cx + dx, cy + dy, r)

# Etiquetas de serigrafía: ref -> (texto, lado del courtyard donde se escribe: N/S/E/O)
ETIQUETAS = {
    'J13': ('LÍN FI', 'S'), 'J8': ('ToF FI', 'S'), 'J18': ('I2C', 'S'), 'J9': ('ToF F', 'S'),
    'J19': ('AUX', 'S'), 'J10': ('ToF FD', 'S'), 'J14': ('LÍN FD', 'S'),
    'J7': ('ToF I', 'E'), 'J11': ('ToF D', 'O'),
    'J15': ('LÍN TI', 'N'), 'J12': ('ToF T', 'N'), 'J17': ('IR', 'N'), 'J16': ('LÍN TD', 'N'),
    'J3': ('M1', 'N'), 'J4': ('M2', 'N'), 'J5': ('M3', 'N'), 'J6': ('M4', 'N'),
    'SW2': ('RST', 'N'), 'SW3': ('BOOT', 'N'), 'J2': ('USB', 'N'),
}

for i, (x, y, _) in enumerate(g.TALADROS):
    COLOCACION[f'H{i + 1}'] = (x, y, 0)


# ------------------------------------------------------------------ utilidades
def load_fp(fpid):
    lib, name = fpid.split(':')
    fp = pcbnew.FootprintLoad(os.path.join(FP_ROOT, lib + '.pretty'), name)
    if fp is None:
        raise SystemExit(f'No encuentro la huella {fpid}')
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


def segment(board, a, b, layer=pcbnew.Edge_Cuts, w=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(a)
    s.SetEnd(b)
    s.SetLayer(layer)
    s.SetWidth(pcbnew.FromMM(w))
    board.Add(s)


def arc(board, center, start, deg, layer=pcbnew.Edge_Cuts, w=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetCenter(center)
    s.SetStart(start)
    s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(deg, pcbnew.DEGREES_T), True)
    s.SetLayer(layer)
    s.SetWidth(pcbnew.FromMM(w))
    board.Add(s)


def outline(board):
    x0, y0, x1, y1, r = g.PCB_X0, g.PCB_Y0, g.PCB_X1, g.PCB_Y1, g.PCB_RADIO_ESQUINA
    segment(board, P(x0 + r, y0), P(x1 - r, y0))
    segment(board, P(x1, y0 + r), P(x1, y1 - r))
    segment(board, P(x1 - r, y1), P(x0 + r, y1))
    segment(board, P(x0, y1 - r), P(x0, y0 + r))
    arc(board, P(x1 - r, y0 + r), P(x1 - r, y0), 90)
    arc(board, P(x1 - r, y1 - r), P(x1, y1 - r), 90)
    arc(board, P(x0 + r, y1 - r), P(x0 + r, y1), 90)
    arc(board, P(x0 + r, y0 + r), P(x0, y0 + r), 90)


def zone(board, net, layer, pts, name='', priority=0):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNetCode(net.GetNetCode())
    z.SetZoneName(name)
    z.SetAssignedPriority(priority)
    z.SetLocalClearance(pcbnew.FromMM(0.3))
    z.SetMinThickness(pcbnew.FromMM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(pcbnew.FromMM(0.3))
    z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.5))
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        ol.Append(P(x, y))
    board.Add(z)
    return z


def text(board, s, x, y, size=1.2, layer=pcbnew.F_SilkS, bold=True, angle=0):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(P(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I_MM(size, size))
    t.SetTextThickness(pcbnew.FromMM(size * (0.2 if bold else 0.15)))
    t.SetBold(bold)
    if angle:
        t.SetTextAngleDegrees(angle)
    if layer in (pcbnew.B_SilkS, pcbnew.B_Fab, pcbnew.B_Cu):
        t.SetMirrored(True)
    board.Add(t)


def vias_termicas(board, x, y, gnd):
    """12 vías de 0,3 mm en el pad térmico del DRV8874 (JLC no hace 0,2 mm en 2 capas)."""
    for dx in (-1.0, 0.0, 1.0):
        for dy in (-1.65, -0.55, 0.55, 1.65):
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(P(x + dx, y + dy))
            v.SetWidth(pcbnew.FromMM(0.6))
            v.SetDrill(pcbnew.FromMM(0.3))
            v.SetNet(gnd)
            board.Add(v)


def etiqueta(board, fp, s, lado, size=0.8):
    bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    x0, y0 = pcbnew.ToMM(bb.GetX()) - OX, pcbnew.ToMM(bb.GetY()) - OY
    x1, y1 = pcbnew.ToMM(bb.GetRight()) - OX, pcbnew.ToMM(bb.GetBottom()) - OY
    cx, cy, m = (x0 + x1) / 2, (y0 + y1) / 2, 0.75
    pos = {'N': (cx, y0 - m, 0), 'S': (cx, y1 + m, 0), 'E': (x1 + m, cy, 90), 'O': (x0 - m, cy, 90)}[lado]
    text(board, s, pos[0], pos[1], size, pcbnew.F_SilkS, True, pos[2])


def zona_motor_fab(board):
    """Dibuja en B.Fab dónde van los motores y el lastre (referencia para el montaje)."""
    for (x0, y0, x1, y1) in g.ZONAS_MOTOR:
        for a, b in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
            segment(board, P(*a), P(*b), pcbnew.B_Fab, 0.1)
        text(board, 'N20', (x0 + x1) / 2, (y0 + y1) / 2, 1.5, pcbnew.B_Fab, False)


# ------------------------------------------------------------------ principal
def main():
    board = pcbnew.NewBoard(OUT)
    ds = board.GetDesignSettings()
    ds.SetAuxOrigin(P(0, 0))
    ds.SetGridOrigin(P(0, 0))
    board.SetCopperLayerCount(2)

    tb = board.GetTitleBlock()
    tb.SetTitle(design.TITLE)
    tb.SetCompany(design.COMPANY)
    tb.SetRevision(design.REV)
    tb.SetDate('2026-10-06')

    nets = {}

    def net(name):
        if name not in nets:
            n = pcbnew.NETINFO_ITEM(board, name)
            board.Add(n)
            nets[name] = n
        return nets[name]

    for p in design.parts:
        for n in p['nets'].values():
            net(n)

    faltan = []
    for p in design.parts:
        fp = load_fp(p['fp'])
        fp.SetReference(p['ref'])
        fp.SetValue(p['value'])
        fp.SetPath(pcbnew.KIID_PATH('/' + uid('sym', p['ref'])))
        fp.SetSheetname('/')
        fp.SetSheetfile(design.PROJECT + '.kicad_sch')
        if p['ref'] not in COLOCACION:
            faltan.append(p['ref'])
            x, y, r = 5.0, 5.0, 0
        else:
            x, y, r = COLOCACION[p['ref']]
        fp.SetPosition(P(x, y))
        fp.SetOrientationDegrees(r)
        ref_txt = fp.Reference()          # referencia a la capa de montaje (no cabe en serigrafía)
        ref_txt.SetLayer(pcbnew.F_Fab)
        ref_txt.SetTextSize(pcbnew.VECTOR2I_MM(0.8, 0.8))
        ref_txt.SetTextThickness(pcbnew.FromMM(0.15))
        for item in fp.GraphicalItems():  # el texto ${REFERENCE} de la capa Fab ya lo cubre la referencia
            if isinstance(item, pcbnew.PCB_TEXT) and item.GetText() == '${REFERENCE}':
                item.SetVisible(False)
        for pad in fp.Pads():
            n = p['nets'].get(pad.GetNumber())
            if n:
                pad.SetNet(nets[n])
        board.Add(fp)
        if p['ref'].startswith('U') and p['lib'] == 'Sumo:DRV8874':
            vias_termicas(board, x, y, nets['GND'])
        if p['ref'] in ETIQUETAS:
            etiqueta(board, fp, *ETIQUETAS[p['ref']])
    if faltan:
        print('SIN COLOCAR:', ' '.join(faltan))

    outline(board)

    # Planos de GND en las dos caras (la inferior queda casi entera: no hay componentes)
    x0, y0, x1, y1 = g.PCB_X0, g.PCB_Y0, g.PCB_X1, g.PCB_Y1
    i, c = 0.3, 2.0      # retranqueo y chaflán para no tocar el borde redondeado
    rect = [(x0 + i + c, y0 + i), (x1 - i - c, y0 + i), (x1 - i, y0 + i + c), (x1 - i, y1 - i - c),
            (x1 - i - c, y1 - i), (x0 + i + c, y1 - i), (x0 + i, y1 - i - c), (x0 + i, y0 + i + c)]
    zone(board, nets['GND'], pcbnew.B_Cu, rect, 'GND_inf')
    zone(board, nets['GND'], pcbnew.F_Cu, rect, 'GND_sup')

    # Serigrafía: obligatoria con el nombre del equipo
    text(board, 'HOMBRES DE LAS TABERNAS', 50, 47.0, 2.4, pcbnew.B_SilkS)
    text(board, 'Robot Mini-Sumo ' + design.REV, 50, 51.5, 1.6, pcbnew.B_SilkS)
    text(board, 'Tecnología Eléctrica · USC · 2026', 50, 55.0, 1.2, pcbnew.B_SilkS, False)
    text(board, 'CERN-OHL-S v2', 50, 58.0, 1.0, pcbnew.B_SilkS, False)
    text(board, 'HOMBRES DE LAS TABERNAS', 50, 71.0, 1.0, pcbnew.F_SilkS)
    zona_motor_fab(board)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(OUT, board)
    print('escrito', os.path.relpath(OUT), f'({len(design.parts)} huellas, {len(nets)} redes)')


if __name__ == '__main__':
    main()
