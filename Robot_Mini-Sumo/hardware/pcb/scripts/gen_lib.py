"""Genera la librería propia del proyecto (formato KiCad 7, se abre también con KiCad 8 y 9):
    hardware/pcb/lib/Sumo.kicad_sym   símbolos: ESP32-S3-DevKitC-1 y módulo TB6612FNG
    hardware/pcb/lib/Sumo.pretty/     huellas: zócalos de los dos módulos, con el nombre de cada pin serigrafiado
"""
import os

from sexp import Sym as S, dump

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'lib', 'Sumo.kicad_sym')
OUT_FP = os.path.join(HERE, '..', 'lib', 'Sumo.pretty')

# ESP32-S3-DevKitC-1 (guía de usuario de Espressif v1.1): filas J1 y J3, de la antena (pin 1) al USB (pin 22)
DEVKIT_J1 = ['3V3', '3V3', 'RST', 'IO4', 'IO5', 'IO6', 'IO7', 'IO15', 'IO16', 'IO17', 'IO18', 'IO8',
             'IO3', 'IO46', 'IO9', 'IO10', 'IO11', 'IO12', 'IO13', 'IO14', '5V', 'GND']
DEVKIT_J3 = ['GND', 'IO43', 'IO44', 'IO1', 'IO2', 'IO42', 'IO41', 'IO40', 'IO39', 'IO38', 'IO37',
             'IO36', 'IO35', 'IO0', 'IO45', 'IO48', 'IO47', 'IO21', 'IO20', 'IO19', 'GND', 'GND']
DEVKIT_FILAS = 22.86          # distancia entre filas (0,9")
DEVKIT_PLACA = (-1.27, -1.2, 24.13, 61.5)   # contorno de la DevKit respecto al pin J1-1
DEVKIT_ANTENA = (2.5, -7.0, 20.4, -1.2)

# Módulo TB6612FNG, patillaje de SparkFun ROB-14450 (sacado de sus ficheros Eagle, CC BY-SA):
# fila de potencia JP1 (pines 1–8) y fila de control JP2 (pines 9–16), separadas 15,24 mm.
TB_POT = ['GND', 'BO1', 'BO2', 'AO2', 'AO1', 'GND', 'VCC', 'VM']             # pines 1..8
TB_CTRL = ['PWMA', 'AIN2', 'AIN1', 'STBY', 'BIN1', 'BIN2', 'PWMB', 'GND']    # pines 9..16


def font(size=1.27, justify=None, hide=False):
    e = [S('effects'), [S('font'), [S('size'), size, size]]]
    if justify:
        e.append([S('justify')] + [S(j) for j in justify.split()])
    if hide:
        e.append(S('hide'))
    return e


def prop(name, value, x=0.0, y=0.0, hide=False, idn=0):
    return [S('property'), name, value, [S('id'), idn], [S('at'), x, y, 0], font(hide=hide)]


def pin(kind, x, y, ang, name, num, length=2.54):
    return [S('pin'), S(kind), S('line'), [S('at'), x, y, ang], [S('length'), length],
            [S('name'), name, font()], [S('number'), num, font()]]


def rect(x0, y0, x1, y1):
    return [S('rectangle'), [S('start'), x0, y0], [S('end'), x1, y1],
            [S('stroke'), [S('width'), 0.254], [S('type'), S('default')]], [S('fill'), [S('type'), S('background')]]]


def simbolo(nombre, ref, fp, desc, cuerpo, pines, alto):
    return [S('symbol'), nombre, [S('in_bom'), S('yes')], [S('on_board'), S('yes')],
            prop('Reference', ref, 0, alto + 2.54, idn=0), prop('Value', nombre, 0, -alto - 2.54, idn=1),
            prop('Footprint', fp, hide=True, idn=2), prop('Datasheet', '~', hide=True, idn=3),
            prop('ki_description', desc, hide=True, idn=4),
            [S('symbol'), nombre + '_0_1'] + cuerpo, [S('symbol'), nombre + '_1_1'] + pines]


def tipo_devkit(nombre, num):
    if nombre == '3V3':
        return 'power_out' if num == 1 else 'passive'   # dos salidas unidas darían error en el ERC
    if nombre in ('5V', 'GND'):
        return 'power_in'
    return 'input' if nombre == 'RST' else 'bidirectional'


def sym_devkit():
    paso, n = 2.54, len(DEVKIT_J1)
    top = (n - 1) * paso / 2
    L, R = -15.24, 15.24
    pines = [pin(tipo_devkit(nm, i + 1), L, top - i * paso, 0, nm, str(i + 1)) for i, nm in enumerate(DEVKIT_J1)]
    pines += [pin(tipo_devkit(nm, 23 + i), R, top - i * paso, 180, nm, str(23 + i)) for i, nm in enumerate(DEVKIT_J3)]
    cuerpo = [rect(L + 2.54, top + 2.54, R - 2.54, -top - 2.54),
              [S('text'), 'J1', [S('at'), -7.62, top + 1.27, 0], font()],
              [S('text'), 'J3', [S('at'), 7.62, top + 1.27, 0], font()],
              [S('text'), 'ANTENA arriba - USB abajo', [S('at'), 0, 0, 900], font()]]
    return simbolo('ESP32-S3-DevKitC-1', 'U', 'Sumo:ESP32-S3-DevKitC-1_Zocalo',
                   'Placa ESP32-S3-DevKitC-1 completa, enchufada en dos tiras hembra 1x22', cuerpo, pines, top + 2.54)


def sym_tb6612():
    # izquierda: control (entradas); derecha: potencia
    izq = [(9, 'PWMA'), (11, 'AIN1'), (10, 'AIN2'), (15, 'PWMB'), (13, 'BIN1'), (14, 'BIN2'), (12, 'STBY')]
    der = [(8, 'VM'), (7, 'VCC'), (5, 'AO1'), (4, 'AO2'), (2, 'BO1'), (3, 'BO2'), (1, 'GND'), (6, 'GND'), (16, 'GND')]
    top = 10.16
    pines = [pin('input', -12.7, top - i * 2.54, 0, nm, str(n)) for i, (n, nm) in enumerate(izq)]
    tipos = {'VM': 'power_in', 'VCC': 'power_in', 'GND': 'power_in'}
    pines += [pin(tipos.get(nm, 'passive'), 12.7, top - i * 2.54, 180, nm, str(n)) for i, (n, nm) in enumerate(der)]
    cuerpo = [rect(-10.16, top + 2.54, 10.16, top - 9 * 2.54)]
    return simbolo('TB6612FNG_Modulo', 'U', 'Sumo:TB6612FNG_Modulo',
                   'Modulo driver doble TB6612FNG (patillaje SparkFun ROB-14450)', cuerpo, pines, top + 2.54)


# ------------------------------------------------------------------ huellas
def fp_line(x0, y0, x1, y1, layer, w):
    return [S('fp_line'), [S('start'), x0, y0], [S('end'), x1, y1],
            [S('stroke'), [S('width'), w], [S('type'), S('solid')]], [S('layer'), layer]]


def fp_rect(x0, y0, x1, y1, layer, w):
    return [fp_line(x0, y0, x1, y0, layer, w), fp_line(x1, y0, x1, y1, layer, w),
            fp_line(x1, y1, x0, y1, layer, w), fp_line(x0, y1, x0, y0, layer, w)]


def fp_text(kind, text, x, y, layer, size=1.0, angle=0, hide=False, justify=None):
    t = [S('fp_text'), S(kind), text, [S('at'), x, y, angle], [S('layer'), layer]]
    if hide:
        t.append(S('hide'))
    e = [S('effects'), [S('font'), [S('size'), size, size], [S('thickness'), max(0.15, round(size * 0.17, 3))]]]
    if justify:
        e.append([S('justify'), S(justify)])
    t.append(e)
    return t


def pad(num, x, y, cuadrado=False):
    return [S('pad'), str(num), S('thru_hole'), S('rect' if cuadrado else 'circle'), [S('at'), x, y],
            [S('size'), 1.8, 1.8], [S('drill'), 1.0], [S('layers'), '*.Cu', '*.Mask']]


def huella(nombre, descr, ref_xy, items):
    return [S('footprint'), nombre, [S('version'), 20221018], [S('generator'), 'gen_lib.py'], [S('layer'), 'F.Cu'],
            [S('descr'), descr], [S('attr'), S('through_hole')],
            fp_text('reference', 'REF**', ref_xy[0], ref_xy[1], 'F.Fab', 1.0),
            fp_text('value', nombre, ref_xy[0], ref_xy[1] + 2, 'F.Fab', 1.0)] + items


def fp_devkit():
    """Origen en el pin J1-1. Dos tiras hembra 1×22 enteras. El nombre de cada pin usado va
    serigrafiado por fuera de las filas (se lee al soldar, antes de pinchar la DevKit)."""
    import design
    paso, fx = 2.54, DEVKIT_FILAS
    usados = {int(k) for k in design.esp}
    items = []
    for x, nombres, off in ((0.0, DEVKIT_J1, 0), (fx, DEVKIT_J3, 22)):
        items += fp_rect(x - 1.27, -1.27, x + 1.27, 21 * paso + 1.27, 'F.SilkS', 0.15)
        items += fp_rect(x - 1.5, -1.5, x + 1.5, 21 * paso + 1.5, 'F.CrtYd', 0.05)
        for i, nm in enumerate(nombres):
            items.append(pad(i + 1 + off, x, i * paso, cuadrado=(i + off == 0)))
            if i + 1 + off in usados:
                lado = -1 if off == 0 else 1
                items.append(fp_text('user', nm, x + lado * 1.8, i * paso, 'F.SilkS', 0.9,
                                     justify='right' if off == 0 else 'left'))
    x0, y0, x1, y1 = DEVKIT_PLACA
    items += fp_rect(x0, y0, x1, y1, 'F.Fab', 0.1)
    items += fp_rect(*DEVKIT_ANTENA, 'F.Fab', 0.1)
    items.append(fp_text('user', 'ANTENA', fx / 2, -4.0, 'F.Fab', 1.0))
    items.append(fp_text('user', 'ESP32-S3-DevKitC-1 (USB hacia atras)', fx / 2, y1 / 2, 'F.Fab', 1.2, 90))
    return huella('ESP32-S3-DevKitC-1_Zocalo',
                  'Zócalo ESP32-S3-DevKitC-1: dos tiras hembra 1x22 de 2,54 mm, filas a 22,86 mm',
                  (fx / 2, y1 / 2 - 14), items)


def fp_tb6612(girado=False):
    """Origen en el centro del módulo (20,32 × 20,32 mm). Normal: fila de potencia a la izquierda
    (pin 8 = VM arriba) y fila de control a la derecha (pin 9 = PWMA arriba). «Girado» es el mismo módulo
    dado la vuelta 180° (para el lado derecho del robot), con los textos al derecho."""
    k = -1 if girado else 1
    items = fp_rect(-10.16, -10.16, 10.16, 10.16, 'F.SilkS', 0.15)
    items += fp_rect(-10.4, -10.4, 10.4, 10.4, 'F.CrtYd', 0.05)
    filas = [(TB_POT, 1, -7.62, lambda i: 8.89 - i * 2.54), (TB_CTRL, 9, 7.62, lambda i: -8.89 + i * 2.54)]
    for nombres, n0, x, fy in filas:
        for i, nm in enumerate(nombres):
            px, py = k * x, k * fy(i)
            items.append(pad(n0 + i, px, py, cuadrado=(n0 + i == 1)))
            dentro = 1 if px < 0 else -1
            items.append(fp_text('user', nm, px + dentro * 1.7, py, 'F.SilkS', 0.9,
                                 justify='left' if px < 0 else 'right'))
    nombre = 'TB6612FNG_Modulo' + ('_Girado' if girado else '')
    return huella(nombre, 'Zócalo de módulo TB6612FNG formato SparkFun ROB-14450: 2 tiras hembra 1x8, '
                  'filas a 15,24 mm' + (' (girado 180°)' if girado else ''), (0, -11.5), items)


def main():
    lib = [S('kicad_symbol_lib'), [S('version'), 20220914], [S('generator'), S('gen_lib')],
           sym_devkit(), sym_tb6612()]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        f.write(dump(lib) + '\n')
    os.makedirs(OUT_FP, exist_ok=True)
    for fp in (fp_devkit(), fp_tb6612(), fp_tb6612(True)):
        with open(os.path.join(OUT_FP, fp[1] + '.kicad_mod'), 'w') as f:
            f.write(dump(fp) + '\n')
    print('librería escrita en', os.path.relpath(os.path.dirname(OUT)))


if __name__ == '__main__':
    main()
