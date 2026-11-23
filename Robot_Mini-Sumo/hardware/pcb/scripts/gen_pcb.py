"""Genera la PCB v2 (robot_sumo.kicad_pcb) a partir de design.py.

Placa de 76 × 80 mm, 2 capas, todo de agujero pasante. Delante (arriba en la imagen) los conectores
de los sensores; en el centro la ESP32; a los lados los dos drivers con sus clemas de motor;
detrás la batería (izquierda) y el regulador y el módulo de arranque (derecha).
Coloca los componentes y la serigrafía; el rutado lo hace autoroute.py (Freerouting).
Coordenadas en mm de la hoja de KiCad: la placa va de (100, 100) a (176, 180). Y crece hacia atrás.
"""
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design                       # noqa: E402
from gen_sch import uid             # noqa: E402

FP_ROOT = '/usr/share/kicad/footprints'
FP_LOCAL = {'Sumo': os.path.join(HERE, '..', 'lib', 'Sumo.pretty')}
OUT = os.path.join(HERE, '..', design.PROJECT + '.kicad_pcb')

X0, Y0, X1, Y1, RADIO = 100.0, 100.0, 176.0, 180.0, 3.0
DEVKIT = (126.57, 113.0)            # pin J1-1 de la DevKit (fila J3 en x + 22,86)
FILA_J3 = DEVKIT[0] + 22.86
CX = (DEVKIT[0] + FILA_J3) / 2      # eje de la placa = 138


def P(x, y):
    return pcbnew.VECTOR2I_MM(x, y)


# ref: (x, y, rotación en grados)
COLOCACION = {
    # --- delante: sensores (tiras de pines horizontales) y condensadores de los drivers
    'J4': (105.5, 103.5, 90), 'J6': (119.5, 103.5, 90),          # distancia y suelo izquierdos
    'J7': (151.5, 103.5, 90), 'J5': (160.5, 103.5, 90),          # suelo y distancia derechos
    'C6': (112.0, 113.0, 0), 'C7': (162.5, 113.0, 0),
    # --- centro: ESP32 y, debajo de ella (componentes bajos), las resistencias de señal
    'U2': (DEVKIT[0], DEVKIT[1], 0),
    'R4': (CX + 5.08, 118.0, 180), 'R5': (CX + 5.08, 122.0, 180),   # pull-ups I2C (SDA/SCL a la izquierda)
    'R3': (CX - 5.08, 126.0, 0),                                  # STBY a GND
    'R6': (CX - 5.08, 130.0, 0), 'R7': (CX - 5.08, 134.0, 0),     # pull-downs del ST4RT
    'R1': (CX - 5.08, 140.0, 0), 'R2': (CX - 5.08, 144.0, 0),     # divisor de batería
    'C3': (CX - 2.5, 149.0, 0),
    # --- lados: drivers (la fila de control mira a la ESP32) y clemas de los motores
    'U3': (110.5, 129.0, 0), 'U4': (165.5, 129.0, 0),
    'J2': (106.0, 145.0, 270), 'J3': (170.0, 150.08, 90),
    # --- detrás a la izquierda: batería, fusible y condensadores de VBAT
    'F1': (104.0, 157.0, 0), 'C1': (111.0, 167.5, 0),
    'J1': (105.5, 175.0, 0),
    # --- detrás a la derecha: regulador de 5 V, LED y módulo de arranque
    'U1': (158.0, 158.0, 0), 'C4': (167.5, 158.0, 0), 'C5': (166.0, 164.5, 0),
    'J8': (157.0, 172.5, 90),
    'D1': (CX - 5.08, 163.0, 0),                                  # bajo la ESP32, cerca de su pin 5V
    # --- taladros M3
    'H1': (104.5, 111.0, 0), 'H2': (171.5, 111.0, 0), 'H3': (121.0, 176.0, 0), 'H4': (171.5, 176.0, 0),
}

# Serigrafía: texto grande de lo que es cada conector y el nombre de cada pin
ROTULOS = [  # (texto, x, y, tamaño, ángulo)
    ('DISTANCIA IZQ', 110.58, 100.9, 0.9, 0), ('SUELO IZQ', 122.04, 100.9, 0.9, 0),
    ('SUELO DER', 154.04, 100.9, 0.9, 0), ('DISTANCIA DER', 165.58, 100.9, 0.9, 0),
    ('MOTOR IZQ', 113.6, 147.5, 0.9, 90), ('MOTOR DER', 162.4, 147.5, 0.9, 90),
    ('BATERIA 2S', 107.0, 178.6, 0.9, 0), ('F1 · FUSIBLE 7,5 A', 109.5, 154.0, 0.9, 0),
    ('U1 · REGULADOR 5 V', 163.0, 154.0, 0.8, 0), ('J8 · ARRANQUE ST4RT', 160.8, 175.4, 0.8, 0),
    ('U3 · DRIVER IZQ', 110.5, 141.0, 1.0, 0), ('U4 · DRIVER DER', 165.5, 141.0, 1.0, 0),
    ('U2 · ESP32-S3-DevKitC-1', CX, 110.0, 1.0, 0), ('USB', CX, 175.6, 0.9, 0),
    ('LHDT · LOS HOMBRES DE LAS TABERNAS', CX, 178.2, 0.8, 0),
]
# nombre de cada pin de las tiras: ref -> lista (pin 1 primero)
PINES = {
    'J4': ['3V3', 'GND', 'SCL', 'SDA', 'XSH'], 'J5': ['3V3', 'GND', 'SCL', 'SDA', 'XSH'],
    'J6': ['3V3', 'GND', 'OUT'], 'J7': ['3V3', 'GND', 'OUT'],
    'J8': ['3V3', 'GND', 'S', 'K'],
}


# Posición a mano de referencia y valor donde la de la huella se pisa con otra cosa
TEXTOS_REF = {
    'C1': ((119.3, 166.0), (120.4, 170.8)),
    'C3': ((CX - 4.8, 146.9), (CX + 6.0, 149.0)),
    'C4': ((170.0, 155.6), (170.0, 160.4)),
    'C5': ((171.8, 162.8), (167.25, 168.8)),
    'C6': ((107.6, 112.0), (112.75, 117.4)),
    'C7': ((168.0, 112.0), (163.25, 117.4)),
}

# (red, ancho, capa, puntos)
PRERUTADO = [
    # 3,3 V de la ESP32 (pin J1-1) al lado derecho, por la cara inferior
    ('+3V3', 0.5, pcbnew.B_Cu, [(DEVKIT[0], DEVKIT[1]), (DEVKIT[0] + 2.4, 110.6), (148.0, 110.6),
                                (151.5, 107.1), (151.5, 103.5)]),
    # I2C de las pull-ups (entre las filas) al sensor de distancia izquierdo, por la cara superior
    ('I2C_SDA', 0.4, pcbnew.F_Cu, [(CX - 5.08, 118.0), (CX - 5.08, 111.0), (131.1, 109.2), (114.5, 109.2),
                                   (113.12, 107.8), (113.12, 103.5)]),
    ('I2C_SCL', 0.4, pcbnew.F_Cu, [(CX - 5.08, 122.0), (131.0, 120.1), (131.0, 112.0), (129.6, 110.6),
                                   (112.0, 110.6), (110.58, 109.2), (110.58, 103.5)]),
]


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


def arc(board, center, start, deg):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetCenter(center)
    s.SetStart(start)
    s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(deg, pcbnew.DEGREES_T), True)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(pcbnew.FromMM(0.1))
    board.Add(s)


def contorno(board):
    x0, y0, x1, y1, r = X0, Y0, X1, Y1, RADIO
    segment(board, P(x0 + r, y0), P(x1 - r, y0))
    segment(board, P(x1, y0 + r), P(x1, y1 - r))
    segment(board, P(x1 - r, y1), P(x0 + r, y1))
    segment(board, P(x0, y1 - r), P(x0, y0 + r))
    arc(board, P(x1 - r, y0 + r), P(x1 - r, y0), 90)
    arc(board, P(x1 - r, y1 - r), P(x1, y1 - r), 90)
    arc(board, P(x0 + r, y1 - r), P(x0 + r, y1), 90)
    arc(board, P(x0 + r, y0 + r), P(x0, y0 + r), 90)


def zona(board, net, layer, pts, nombre):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNetCode(net.GetNetCode())
    z.SetZoneName(nombre)
    z.SetLocalClearance(pcbnew.FromMM(0.4))
    z.SetMinThickness(pcbnew.FromMM(0.3))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)
    z.SetThermalReliefGap(pcbnew.FromMM(0.4))
    z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.6))
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        ol.Append(P(x, y))
    board.Add(z)


def sin_cobre(board, pts, nombre):
    """Área de reglas en las dos caras: sin relleno de cobre (pistas sí)."""
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


def texto(board, s, x, y, size=1.0, layer=pcbnew.F_SilkS, angle=0, bold=True):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(P(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I_MM(size, size))
    t.SetTextThickness(pcbnew.FromMM(max(0.15, size * (0.18 if bold else 0.15))))
    if angle:
        t.SetTextAngleDegrees(angle)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    board.Add(t)


def main():
    board = pcbnew.NewBoard(OUT)
    board.SetCopperLayerCount(2)
    ds = board.GetDesignSettings()
    ds.m_MinClearance = pcbnew.FromMM(0.2)
    ds.m_CopperEdgeClearance = pcbnew.FromMM(0.5)
    ds.m_HoleClearance = pcbnew.FromMM(0.25)
    tb = board.GetTitleBlock()
    tb.SetTitle(design.TITLE)
    tb.SetCompany(design.COMPANY)
    tb.SetRevision(design.REV)
    tb.SetDate('2026-11-23')

    nets = {}
    for p in design.parts:
        for n in p['nets'].values():
            if n not in nets:
                nets[n] = pcbnew.NETINFO_ITEM(board, n)
                board.Add(nets[n])

    for p in design.parts:
        fp = load_fp(p['fp'])
        fp.SetReference(p['ref'])
        fp.SetValue(p['value'])
        fp.SetPath(pcbnew.KIID_PATH('/' + uid('sym', p['ref'])))
        x, y, r = COLOCACION[p['ref']]
        fp.SetPosition(P(x, y))
        fp.SetOrientationDegrees(r)
        ref = fp.Reference()
        ref.SetTextSize(pcbnew.VECTOR2I_MM(1.0, 1.0))
        ref.SetTextThickness(pcbnew.FromMM(0.18))
        if p['ref'].startswith(('H', 'J', 'U', 'F')):   # los conectores llevan su rótulo; los taladros, nada
            ref.SetVisible(False)
        val = fp.Value()
        val.SetLayer(pcbnew.F_SilkS)
        val.SetTextSize(pcbnew.VECTOR2I_MM(0.8, 0.8))
        val.SetTextThickness(pcbnew.FromMM(0.15))
        if p['lib'] == 'Device:R':      # valor dentro del cuerpo y referencia a la derecha
            xs = [pcbnew.ToMM(q.GetPosition().x) for q in fp.Pads()]
            val.SetPosition(P(sum(xs) / 2, y))
            val.SetTextAngleDegrees(0)
            ref.SetPosition(P(max(xs) + 2.3, y))
            ref.SetTextAngleDegrees(0)
            ref.SetTextSize(pcbnew.VECTOR2I_MM(0.9, 0.9))
        elif p['lib'] in ('Device:C', 'Device:C_Polarized', 'Diode:1N5819',
                          'Regulator_Linear:L7805'):
            pass                         # valor donde lo pone la huella, ya en serigrafía
        else:
            val.SetVisible(False)
        for pad in fp.Pads():
            n = p['nets'].get(pad.GetNumber())
            if n:
                pad.SetNet(nets[n])
        if p['ref'] in TEXTOS_REF:
            (rx, ry), (vx, vy) = TEXTOS_REF[p['ref']]
            ref.SetPosition(P(rx, ry))
            val.SetPosition(P(vx, vy))
        if p['ref'] in ('J1', 'U3', 'U4'):   # corriente de motores: GND unido en macizo al plano
            fp.SetZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
        board.Add(fp)
        if p['ref'] in PINES:   # nombre de cada pin, encima de la tira (las tiras van en horizontal)
            for i, nm in enumerate(PINES[p['ref']]):
                pad = [q for q in fp.Pads() if q.GetNumber() == str(i + 1)][0]
                c = pad.GetPosition()
                dy = -2.4 if p['ref'] == 'J8' else 2.4
                texto(board, nm, pcbnew.ToMM(c.x), pcbnew.ToMM(c.y) + dy, 0.8)

    # Pistas fijas (cruces que Freerouting no resolvía): pasan por delante de la fila J1 de la ESP32
    for red, ancho, capa, pts in PRERUTADO:
        for a, b in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(P(*a)); t.SetEnd(P(*b)); t.SetWidth(pcbnew.FromMM(ancho)); t.SetLayer(capa)
            t.SetNet(nets[red]); t.SetLocked(True)
            board.Add(t)

    contorno(board)
    # Planos de GND en las dos caras
    i, c = 0.5, 2.5
    rect = [(X0 + i + c, Y0 + i), (X1 - i - c, Y0 + i), (X1 - i, Y0 + i + c), (X1 - i, Y1 - i - c),
            (X1 - i - c, Y1 - i), (X0 + i + c, Y1 - i), (X0 + i, Y1 - i - c), (X0 + i, Y0 + i + c)]
    zona(board, nets['GND'], pcbnew.B_Cu, rect, 'GND_inferior')
    zona(board, nets['GND'], pcbnew.F_Cu, rect, 'GND_superior')
    # Sin cobre bajo la antena de la ESP32 (sobresale por delante de su placa)
    ax, ay = DEVKIT
    sin_cobre(board, [(ax + 2.0, Y0 + 0.5), (ax + 20.9, Y0 + 0.5), (ax + 20.9, ay - 1.0), (ax + 2.0, ay - 1.0)],
              'antena_ESP32')

    for s, x, y, size, ang in ROTULOS:
        texto(board, s, x, y, size, angle=ang)
    # Polaridad de batería y motores
    # Nombre del equipo (requisito académico): por delante bajo la ESP32 y por detrás grande
    texto(board, 'LHDT', CX, 153.4, 2.0)
    texto(board, 'LOS HOMBRES', CX, 156.4, 1.0)
    texto(board, 'DE LAS TABERNAS', CX, 158.2, 1.0)
    # Por detrás: en la franja delantera (bajo la antena no hay pads) y entre las filas de la ESP32
    texto(board, 'LHDT', CX, 104.0, 3.0, pcbnew.B_SilkS)
    texto(board, 'LOS HOMBRES DE LAS TABERNAS', CX, 108.3, 1.0, pcbnew.B_SilkS)
    texto(board, f'Mini-Sumo {design.REV} · 2026', CX, 158.0, 0.9, pcbnew.B_SilkS, bold=False)

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(OUT, board)
    print('escrito', os.path.relpath(OUT), f'({len(design.parts)} huellas, {len(nets)} redes)')


if __name__ == '__main__':
    main()
