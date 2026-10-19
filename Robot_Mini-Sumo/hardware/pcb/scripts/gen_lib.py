"""Genera la librería propia del proyecto:
    hardware/pcb/lib/Sumo.kicad_sym   símbolos (DRV8874, ESP32-S3-DevKitC-1)
    hardware/pcb/lib/Sumo.pretty/     huellas (zócalo de la DevKitC-1)
"""
import os
import sys

from sexp import Sym as S, dump

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
import design                       # noqa: E402
import geometria as g               # noqa: E402

OUT = os.path.join(HERE, '..', 'lib', 'Sumo.kicad_sym')
OUT_FP = os.path.join(HERE, '..', 'lib', 'Sumo.pretty')

# Pines de la ESP32-S3-DevKitC-1 (documentación de Espressif, v1.0/v1.1): J1 y J3 de arriba (antena) abajo (USB)
DEVKIT_J1 = ['3V3', '3V3', 'RST', 'IO4', 'IO5', 'IO6', 'IO7', 'IO15', 'IO16', 'IO17', 'IO18', 'IO8',
             'IO3', 'IO46', 'IO9', 'IO10', 'IO11', 'IO12', 'IO13', 'IO14', '5V', 'GND']
DEVKIT_J3 = ['GND', 'TX/IO43', 'RX/IO44', 'IO1', 'IO2', 'IO42', 'IO41', 'IO40', 'IO39', 'IO38', 'IO37',
             'IO36', 'IO35', 'IO0', 'IO45', 'IO48', 'IO47', 'IO21', 'IO20/D+', 'IO19/D-', 'GND', 'GND']


def font(size=1.27):
    return [S('effects'), [S('font'), [S('size'), size, size]]]


def prop(name, value, x=0.0, y=0.0, hide=False):
    eff = font()
    if hide:
        eff.append([S('hide'), S('yes')])
    return [S('property'), name, value, [S('at'), x, y, 0], eff]


def pin(kind, x, y, ang, name, num, length=2.54):
    return [S('pin'), S(kind), S('line'), [S('at'), x, y, ang], [S('length'), length],
            [S('name'), name, font()], [S('number'), num, font()]]


def drv8874():
    # (nombre, número, tipo, x, y, ángulo)
    L, R, T, B = -12.7, 12.7, 17.78, -17.78
    pins = [
        ('EN/IN1', '1', 'input', L, 10.16, 0), ('PH/IN2', '2', 'input', L, 7.62, 0),
        ('nSLEEP', '3', 'input', L, 2.54, 0), ('PMODE', '16', 'input', L, -2.54, 0),
        ('IMODE', '7', 'input', L, -5.08, 0), ('VREF', '5', 'input', L, -10.16, 0),
        ('VCP', '12', 'passive', R, 12.7, 180), ('CPH', '13', 'passive', R, 10.16, 180),
        ('CPL', '14', 'passive', R, 7.62, 180), ('OUT1', '8', 'output', R, 2.54, 180),
        ('OUT2', '10', 'output', R, 0.0, 180), ('IPROPI', '6', 'output', R, -5.08, 180),
        ('nFAULT', '4', 'open_collector', R, -10.16, 180),
        ('VM', '11', 'power_in', 0.0, T, 270),
        ('GND', '15', 'power_in', -2.54, B, 90), ('PGND', '9', 'power_in', 0.0, B, 90),
        ('PAD', '17', 'passive', 2.54, B, 90),
    ]
    body = [S('symbol'), 'DRV8874_0_1',
            [S('rectangle'), [S('start'), -10.16, 15.24], [S('end'), 10.16, -15.24],
             [S('stroke'), [S('width'), 0.254], [S('type'), S('default')]],
             [S('fill'), [S('type'), S('background')]]]]
    pinsym = [S('symbol'), 'DRV8874_1_1'] + [pin(t, x, y, a, n, num) for n, num, t, x, y, a in pins]
    return [S('symbol'), 'DRV8874',
            [S('exclude_from_sim'), S('no')], [S('in_bom'), S('yes')], [S('on_board'), S('yes')],
            prop('Reference', 'U', 0, 20.32), prop('Value', 'DRV8874', 0, -20.32),
            prop('Footprint', 'Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.46x2.31mm', hide=True),
            prop('Datasheet', 'https://www.ti.com/lit/ds/symlink/drv8874.pdf', hide=True),
            prop('Description', 'Driver puente H 37 V / 6 A pico con sensado de corriente (IPROPI) y regulación ITRIP', hide=True),
            body, pinsym]


def devkit_tipo(nombre, num):
    if nombre == '3V3':
        return 'power_out' if num == 1 else 'passive'   # dos salidas unidas darían error en el ERC
    if nombre in ('5V', 'GND'):
        return 'power_in'
    return 'input' if nombre == 'RST' else 'bidirectional'


def devkit():
    paso, n = 2.54, len(DEVKIT_J1)
    top = (n - 1) * paso / 2
    L, R = -15.24, 15.24
    pins = []
    for i, nm in enumerate(DEVKIT_J1):
        pins.append(pin(devkit_tipo(nm, i + 1), L, top - i * paso, 0, nm, str(i + 1)))
    for i, nm in enumerate(DEVKIT_J3):
        pins.append(pin(devkit_tipo(nm, 23 + i), R, top - i * paso, 180, nm, str(23 + i)))
    body = [S('symbol'), 'ESP32-S3-DevKitC-1_0_1',
            [S('rectangle'), [S('start'), L + 2.54, top + 2.54], [S('end'), R - 2.54, -top - 2.54],
             [S('stroke'), [S('width'), 0.254], [S('type'), S('default')]],
             [S('fill'), [S('type'), S('background')]]],
            [S('text'), 'J1', [S('at'), -7.62, top + 1.27, 0], font()],
            [S('text'), 'J3', [S('at'), 7.62, top + 1.27, 0], font()],
            [S('text'), 'ANTENA ↑   USB ↓', [S('at'), 0, 0, 900], font()]]
    return [S('symbol'), 'ESP32-S3-DevKitC-1',
            [S('exclude_from_sim'), S('no')], [S('in_bom'), S('yes')], [S('on_board'), S('yes')],
            prop('Reference', 'U', 0, top + 5.08), prop('Value', 'ESP32-S3-DevKitC-1', 0, -top - 5.08),
            prop('Footprint', 'Sumo:ESP32-S3-DevKitC-1_Zocalo', hide=True),
            prop('Datasheet', 'https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/'
                              'esp32-s3-devkitc-1/user_guide_v1.1.html', hide=True),
            prop('Description', 'Placa ESP32-S3-DevKitC-1 completa, enchufada en tiras hembra de 2,54 mm', hide=True),
            body, [S('symbol'), 'ESP32-S3-DevKitC-1_1_1'] + pins]


# ------------------------------------------------------------------ huella del zócalo de la DevKit
def fp_line(x0, y0, x1, y1, layer, w):
    return [S('fp_line'), [S('start'), x0, y0], [S('end'), x1, y1],
            [S('stroke'), [S('width'), w], [S('type'), S('solid')]], [S('layer'), layer]]


def fp_rect(x0, y0, x1, y1, layer, w):
    return [fp_line(x0, y0, x1, y0, layer, w), fp_line(x1, y0, x1, y1, layer, w),
            fp_line(x1, y1, x0, y1, layer, w), fp_line(x0, y1, x0, y0, layer, w)]


def fp_text(kind, text, x, y, layer, size=1.0, angle=0, hide=False):
    t = [S('fp_text'), S(kind), text, [S('at'), x, y, angle], [S('layer'), layer]]
    if hide:
        t.append(S('hide'))
    t.append([S('effects'), [S('font'), [S('size'), size, size], [S('thickness'), round(size * 0.15, 3)]]])
    return t


def tramos(pines):
    """Agrupa números de pin consecutivos: [1, 2, 4, 5, 6] -> [(1, 2), (4, 6)]."""
    out = []
    for p in sorted(pines):
        if out and p == out[-1][1] + 1:
            out[-1][1] = p
        else:
            out.append([p, p])
    return out


def devkit_zocalo():
    """Huella con origen en el pin J1-1. Solo lleva taladro donde hay señal (tiras hembra cortadas a medida);
    el contorno de la DevKit va en F.Fab y el courtyard solo cubre los zócalos, porque debajo de la DevKit
    (a 11 mm de altura) caben componentes bajos."""
    paso, fx = g.DEVKIT_PASO, g.DEVKIT_FILAS
    usados = {int(k) for k in design.esp}
    filas = [(0.0, sorted(p for p in usados if p <= 22), DEVKIT_J1, 0),
             (fx, sorted(p - 22 for p in usados if p > 22), DEVKIT_J3, 22)]
    items = []
    for x, pines, nombres, off in filas:
        for a, b in tramos(pines):
            y0, y1 = (a - 1) * paso - 1.27, (b - 1) * paso + 1.27
            items += fp_rect(x - 1.27, y0, x + 1.27, y1, 'F.SilkS', 0.12)
            items += fp_rect(x - 1.52, y0 - 0.25, x + 1.52, y1 + 0.25, 'F.CrtYd', 0.05)
        for p in pines:
            forma = 'rect' if p + off == 1 else 'circle'
            items.append([S('pad'), str(p + off), S('thru_hole'), S(forma), [S('at'), x, (p - 1) * paso],
                          [S('size'), 1.7, 1.7], [S('drill'), 1.0], [S('layers'), '*.Cu', '*.Mask']])
        for i, nm in enumerate(nombres):   # nombre de cada pin junto a la fila, en la capa de montaje
            dx = -2.2 if off == 0 else 2.2
            items.append(fp_text('user', nm, x + dx, i * paso, 'F.Fab', 0.6, 0))
    x0, y0, x1, y1 = g.DEVKIT_PLACA
    items += fp_rect(x0, y0, x1, y1, 'F.Fab', 0.1)
    items += fp_rect(*g.DEVKIT_ANTENA, 'F.Fab', 0.1)
    for xc in (fx / 2 - 6.6, fx / 2 + 6.0):   # USB-UART (J1) y USB nativo (J3)
        items += fp_rect(xc - 4.0, y1 - 5.5, xc + 4.0, g.DEVKIT_USB_Y1, 'F.Fab', 0.1)
    items.append(fp_text('user', 'ANTENA', fx / 2, (g.DEVKIT_ANTENA[1] + g.DEVKIT_ANTENA[3]) / 2, 'F.Fab', 1.0))
    items.append(fp_text('user', 'ESP32-S3-DevKitC-1 (USB hacia atrás)', fx / 2, y1 / 2, 'F.Fab', 1.0, 90))
    items.append(fp_line(-2.0, -1.6, -2.0, 1.0, 'F.SilkS', 0.2))     # marca del pin 1
    return [S('footprint'), 'ESP32-S3-DevKitC-1_Zocalo', [S('version'), 20221018],
            [S('generator'), 'gen_lib.py'], [S('layer'), 'F.Cu'],
            [S('descr'), 'Zócalo para ESP32-S3-DevKitC-1: tiras hembra 2,54 mm, filas a 22,86 mm; '
                         'solo los pines con señal. Contorno de la placa en F.Fab.'],
            [S('tags'), 'ESP32-S3 DevKitC-1 zocalo'], [S('attr'), S('through_hole')],
            fp_text('reference', 'REF**', fx / 2, y1 / 2 - 12, 'F.Fab', 1.0),
            fp_text('value', 'ESP32-S3-DevKitC-1_Zocalo', fx / 2, y1 / 2 + 12, 'F.Fab', 1.0)] + items


def main():
    lib = [S('kicad_symbol_lib'), [S('version'), 20251024], [S('generator'), 'gen_lib.py'],
           [S('generator_version'), '10.0'], drv8874(), devkit()]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        f.write(dump(lib) + '\n')
    print('escrito', os.path.relpath(OUT))
    os.makedirs(OUT_FP, exist_ok=True)
    path = os.path.join(OUT_FP, 'ESP32-S3-DevKitC-1_Zocalo.kicad_mod')
    with open(path, 'w') as f:
        f.write(dump(devkit_zocalo()) + '\n')
    print('escrito', os.path.relpath(path))


if __name__ == '__main__':
    main()
