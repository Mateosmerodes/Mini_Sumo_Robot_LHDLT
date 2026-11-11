"""Genera la PCB (robot_sumo.kicad_pcb) a partir de design.py y ../../geometria.py.

- Contorno, taladros y posición de la ESP32-S3-DevKitC-1 salen de la geometría mecánica.
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
FP_LOCAL = {'Sumo': os.path.join(HERE, '..', 'lib', 'Sumo.pretty')}     # generada por gen_lib.py
OUT = os.path.join(HERE, '..', design.PROJECT + '.kicad_pcb')
OX, OY = 100.0, 50.0                # posición del origen del robot en la hoja de KiCad


def P(x, y):
    return pcbnew.VECTOR2I_MM(OX + x, OY + y)


# ------------------------------------------------------------------ colocación
# ref: (x, y, rotación)   — sistema del robot
COLOCACION = {
    # Fila delantera: sensores frontales (J9 queda bajo el borde de la DevKit: se enchufa antes que ella)
    'J13': (23.5, 33.4, 0), 'J8': (32.0, 33.4, 0), 'J9': (50.0, 33.4, 0),
    'J10': (68.0, 33.4, 0), 'J14': (76.5, 33.4, 0),
    # Delante a la izquierda: entrada de batería (fuera de la DevKit: el XT30 mide 11 mm y asoma por el techo)
    'J1': (22.5, 40.0, 0),
    # Centro (bajo la DevKit, a 11 mm por encima): protección y buck.
    # VBAT_RAW entra desde el XT30 por el hueco del pin J1-3 (sin zócalo) y VBAT sale hacia los drivers
    # de la derecha por el hueco de J3-11..14.
    'C14': (42.0, 35.2, 90), 'C13': (44.2, 36.0, 90),
    'Q1': (46.0, 43.6, 90), 'F1': (55.0, 43.6, 90), 'R1': (51.0, 47.6, 0),
    'U2': (47.0, 60.6, 0), 'L1': (53.6, 60.4, 0), 'C6': (43.6, 60.6, 90), 'C7': (47.0, 58.1, 0),
    'C4': (43.8, 65.4, 90), 'C5': (46.4, 65.4, 90),
    'R5': (49.2, 64.9, 90), 'R6': (51.0, 64.9, 90), 'R7': (49.2, 68.6, 90), 'R8': (51.0, 68.6, 90),
    'C8': (53.6, 65.6, 90), 'C9': (56.2, 65.6, 90),
    # Centro trasero: comunes de los drivers y diodos de 5 V
    'R14': (43.0, 73.6, 90), 'R15': (45.0, 73.6, 90), 'C17': (47.0, 73.6, 90),
    'R16': (49.0, 73.6, 90), 'R17': (51.0, 73.6, 90),
    'U3': (46.0, 78.6, 0), 'C15': (46.0, 81.6, 0), 'D1': (54.0, 78.6, 0), 'C10': (55.6, 73.6, 90), 'C11': (42.6, 81.6, 0),
    # Pads de los motores: a cada lado, junto a su driver (la corriente no cruza las filas de la DevKit).
    # El cable sube desde el motor por un canal de la cuna, fuera de la zona de apoyo del motor.
    'J3': (g.PAD_MOTOR_X_IZQ[0], g.PAD_MOTOR_Y_DEL, 0), 'J4': (g.PAD_MOTOR_X_IZQ[0], g.PAD_MOTOR_Y_TRAS, 0),
    'J5': (g.PAD_MOTOR_X_DER[0], g.PAD_MOTOR_Y_DEL, 0), 'J6': (g.PAD_MOTOR_X_DER[0], g.PAD_MOTOR_Y_TRAS, 0),
    # Bornes laterales
    'J7': (17.0, 64.0, 90), 'J11': (83.0, 64.0, 90),
    # Reserva VBAT
    'C1': (33.5, 57.4, 90), 'C2': (66.5, 57.4, 90),
    # Delante a la derecha: pull-ups I2C
    'R60': (67.5, 40.0, 90), 'R61': (70.0, 40.0, 90),
    # Detrás a la izquierda (v1.2): módulo de arranque ST4RT, cerca de IR_START (J1-11) y de U3
    'R63': (21.6, 83.0, 90), 'R64': (23.6, 83.0, 90), 'R65': (25.6, 83.0, 90), 'R66': (27.6, 83.0, 90),
    'R67': (29.6, 83.0, 90), 'JP1': (33.0, 83.0, 90), 'R62': (35.6, 80.0, 90), 'C62': (35.6, 84.0, 90),
    'TP1': (18.6, 79.5, 0), 'R68': (19.6, 83.0, 90), 'R69': (17.6, 83.0, 90),
    # Trasera izquierda: medida de batería, LED de alimentación, sensores traseros
    'R3': (21.6, 77.0, 90), 'R4': (23.6, 77.0, 90), 'C3': (25.6, 77.0, 90),
    'D3': (31.0, 77.0, 0), 'R9': (31.0, 79.0, 0),
    'J15': (24.0, 89.0, 0), 'J17': (32.0, 89.0, 0),
    # Trasera derecha: expansión I2C, auxiliar, IR y sensor trasero
    'J19': (68.0, 78.0, 0), 'J18': (76.5, 78.0, 0),
    'J12': (67.5, 89.0, 0), 'J16': (76.0, 89.0, 0),
    # ESP32-S3-DevKitC-1: posición fijada por la geometría (USB a ras de la pared trasera)
    'U1': (g.DEVKIT_X, g.DEVKIT_Y, 0),
}

# Grupo de cada driver respecto al centro del DRV8874 (rotación 0)
DRIVER = {
    'U': (0.0, 0.0, 0),
    # v1.2: girados 180° (pad de señal hacia el driver, GND hacia fuera) y alineados con los pines 6 y 7
    'R_IPROPI': (-6.5, 0.975, 180), 'C_IPROPI': (-6.5, -0.525, 180), 'R_IMODE': (-6.5, 2.9, 180),
    # v1.2: C_VCP y C_CP (0402) junto a los pines 12-14; ver salida_driver()
    'C_VCP': (5.08, 0.25, 0), 'C_CP': (5.08, -1.0, 0), 'C_VM': (7.5, 1.0, 0), 'C_BULK': (6.6, 4.2, 0),
}
CENTROS_DRIVER = {1: (28.0, 46.0), 2: (28.0, 64.0), 3: (71.0, 46.0), 4: (71.0, 64.0)}
for k, (cx, cy) in CENTROS_DRIVER.items():
    b = 20 + (k - 1) * 10
    refs = {'U': f'U{4 + k}', 'R_IPROPI': f'R{b}', 'C_IPROPI': f'C{b}', 'R_IMODE': f'R{b + 1}',
            'C_VCP': f'C{b + 1}', 'C_CP': f'C{b + 2}', 'C_VM': f'C{b + 3}', 'C_BULK': f'C{b + 4}'}
    for key, (dx, dy, r) in DRIVER.items():
        COLOCACION[refs[key]] = (cx + dx, cy + dy, r)

# Etiquetas de serigrafía: ref -> (texto, lado del courtyard donde se escribe: N/S/E/O)
ETIQUETAS = {
    'J13': ('LÍN FI', 'O'), 'J8': ('ToF FI', 'S'), 'J18': ('I2C', 'N'), 'J9': ('ToF F', 'S'),
    'J19': ('AUX', 'N'), 'J10': ('ToF FD', 'S'), 'J14': ('LÍN FD', 'S'),
    'J7': ('ToF I', 'S'), 'J11': ('ToF D', 'S'),
    'J15': ('LÍN TI', 'N'), 'J12': ('ToF T', 'N'), 'J17': ('ST4RT', 'N'), 'JP1': ('BANCO', 'O'), 'J16': ('LÍN TD', 'N'),
    'J3': ('M1', 'O'), 'J4': ('M2', 'O'), 'J5': ('M3', 'E'), 'J6': ('M4', 'E'),
}

for i, (x, y, _) in enumerate(g.TALADROS):
    COLOCACION[f'H{i + 1}'] = (x, y, 0)


# ------------------------------------------------------------------ utilidades
def load_fp(fpid):
    lib, name = fpid.split(':')
    fp = pcbnew.FootprintLoad(FP_LOCAL.get(lib) or os.path.join(FP_ROOT, lib + '.pretty'), name)
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


def ajustes_zona(z):
    """v1.2: holgura 0,2 mm, SMD unidos en macizo y PTH con alivio térmico (radios de 0,4 mm)."""
    z.SetLocalClearance(pcbnew.FromMM(0.2))
    z.SetMinThickness(pcbnew.FromMM(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)
    z.SetThermalReliefGap(pcbnew.FromMM(0.25))
    z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.4))


def zone(board, net, layer, pts, name='', priority=0):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNetCode(net.GetNetCode())
    z.SetZoneName(name)
    z.SetAssignedPriority(priority)
    ajustes_zona(z)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        ol.Append(P(x, y))
    board.Add(z)
    return z


def sin_cobre(board, pts, nombre='antena_DevKit'):
    """Área de reglas en las dos caras: prohíbe rellenos de cobre (pistas y pads siguen permitidos)."""
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board)
        z.SetIsRuleArea(True)
        z.SetLayer(layer)
        z.SetDoNotAllowCopperPour(True)
        z.SetDoNotAllowTracks(False)
        z.SetDoNotAllowVias(False)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        z.SetZoneName(nombre)
        ol = z.Outline()
        ol.NewOutline()
        for x, y in pts:
            ol.Append(P(x, y))
        board.Add(z)


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


def pista(board, net, pts, w, layer=pcbnew.F_Cu):
    for a, b in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(P(*a)); t.SetEnd(P(*b)); t.SetWidth(pcbnew.FromMM(w)); t.SetLayer(layer)
        t.SetNet(net); t.SetLocked(True)
        board.Add(t)


def via(board, net, x, y, d, drill):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(P(x, y)); v.SetWidth(pcbnew.FromMM(d)); v.SetDrill(pcbnew.FromMM(drill))
    v.SetNet(net); v.SetLocked(True)
    board.Add(v)


def salida_driver(board, nets, k, cx, cy):
    """Salida pre-rutada (fija) de los pines 9-15 del DRV8874 k hacia sus condensadores.

    Paso de 0,65 mm: el autorrutador no conseguía sacar CPL, CPH, VCP y VM a la vez. Coordenadas
    relativas al centro del driver; pads del lado derecho en x = 2,8625.
    """
    m = f'M{k}'
    def r(pts):
        return [(cx + x, cy + y) for x, y in pts]
    X = 2.8625
    pista(board, nets[f'{m}_CPL'], r([(X, -0.975), (3.6, -0.975), (4.225, -1.6), (5.56, -1.6), (5.56, -1.0)]), 0.2)
    pista(board, nets[f'{m}_CPH'], r([(X, -0.325), (4.0, -0.325), (4.45, -0.775)]), 0.2)
    pista(board, nets[f'{m}_VCP'], r([(X, 0.325), (4.45, 0.325)]), 0.2)
    pista(board, nets['VBAT'], r([(X, 0.975), (6.8, 0.975)]), 0.4)
    pista(board, nets['VBAT'], r([(5.56, 0.975), (5.56, 0.4)]), 0.4)
    pista(board, nets['VBAT'], r([(6.45, 1.2), (6.45, 2.4), (5.3, 3.55), (5.3, 3.7)]), 0.4)
    pista(board, nets[f'{m}_OUTB'], r([(X, 1.625), (3.9, 1.625), (4.5, 2.225), (4.5, 2.45)]), 0.4)
    via(board, nets[f'{m}_OUTB'], cx + 4.5, cy + 2.45, 0.8, 0.4)
    # lado izquierdo: pines 1-5 salen en diagonal hacia arriba; 6 y 7 a sus resistencias; 8 (OUTA) baja
    izq = {1: f'{m}_IN1', 2: f'{m}_IN2', 3: 'DRV_nSLEEP', 4: 'DRV_nFAULT', 5: 'DRV_VREF'}
    for pin, red in izq.items():
        y = -2.275 + 0.65 * (pin - 1)
        pista(board, nets[red], r([(-X, y), (-3.75, y), (-4.55, y - 0.8)]), 0.2)
    pista(board, nets[f'ISENSE_{m}'], r([(-X, 0.975), (-5.725, 0.975), (-5.725, -0.525)]), 0.2)
    pista(board, nets[f'{m}_IMODE'], r([(-X, 1.625), (-3.75, 1.625), (-5.0, 2.875), (-5.725, 2.875)]), 0.2)
    pista(board, nets[f'{m}_OUTA'], r([(-X, 2.275), (-3.2, 2.275), (-3.2, 3.6)]), 0.4)
    pista(board, nets['GND'], r([(-7.275, -0.525), (-7.275, 2.9)]), 0.3)
    via(board, nets['GND'], cx - 7.275, cy + 1.95, 0.6, 0.3)
    for y in (-1.625, 2.275):  # GND de los pines 15 y 9 al pad térmico
        pista(board, nets['GND'], r([(2.3, y), (1.4, y)]), 0.25)


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
    # Reglas mínimas también aquí (el relleno de zonas se hace antes de cargar el .kicad_pro)
    ds.m_HoleClearance = pcbnew.FromMM(0.25)
    ds.m_CopperEdgeClearance = pcbnew.FromMM(0.3)
    ds.m_MinClearance = pcbnew.FromMM(0.15)

    tb = board.GetTitleBlock()
    tb.SetTitle(design.TITLE)
    tb.SetCompany(design.COMPANY)
    tb.SetRevision(design.REV)
    tb.SetDate('2026-11-10')

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
        if p['ref'] == 'U1':  # zócalo de la DevKit: GND en macizo (no hay sitio para los 4 radios del alivio)
            fp.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
        board.Add(fp)
        if p['ref'].startswith('U') and p['lib'] == 'Sumo:DRV8874':
            vias_termicas(board, x, y, nets['GND'])
            salida_driver(board, nets, int(p['ref'][1:]) - 4, x, y)
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

    # Serigrafía: obligatoria con el nombre del equipo. En la cara inferior, en las franjas delantera y
    # trasera, las únicas que no cruzan las filas de pines de la DevKit.
    text(board, 'HOMBRES DE LAS TABERNAS', 50, 31.8, 1.8, pcbnew.B_SilkS)
    text(board, f'Robot Mini-Sumo {design.REV} · Tecnología Eléctrica · USC · 2026 · CERN-OHL-S v2',
         50, 90.6, 1.0, pcbnew.B_SilkS, False)
    text(board, 'HOMBRES DE LAS TABERNAS', 50, 90.8, 1.0, pcbnew.F_SilkS)
    # Bajo la antena de la DevKit (que vuela por delante de su placa) no se rellena cobre
    ax0, ay0, ax1, ay1 = g.DEVKIT_ANTENA
    sin_cobre(board, [(g.DEVKIT_X + ax0, y0 + i), (g.DEVKIT_X + ax1, y0 + i),
                      (g.DEVKIT_X + ax1, g.DEVKIT_Y + ay1), (g.DEVKIT_X + ax0, g.DEVKIT_Y + ay1)])
    # Alrededor de los taladros M2 (NPTH) no se rellena cobre: 2,0 mm de radio (taladro 1,1 + 0,9)
    for x, y, _ in g.TALADROS:
        sin_cobre(board, [(x + 2.0 * math.cos(a * math.pi / 8), y + 2.0 * math.sin(a * math.pi / 8))
                          for a in range(16)], 'taladro_M2')
    zona_motor_fab(board)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(OUT, board)
    print('escrito', os.path.relpath(OUT), f'({len(design.parts)} huellas, {len(nets)} redes)')


if __name__ == '__main__':
    main()
