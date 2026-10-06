"""Genera la librería de símbolos propia del proyecto (hardware/pcb/lib/Sumo.kicad_sym)."""
import os
from sexp import Sym as S, dump

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'lib', 'Sumo.kicad_sym')


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


def main():
    lib = [S('kicad_symbol_lib'), [S('version'), 20251024], [S('generator'), 'gen_lib.py'],
           [S('generator_version'), '10.0'], drv8874()]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        f.write(dump(lib) + '\n')
    print('escrito', os.path.relpath(OUT))


if __name__ == '__main__':
    main()
