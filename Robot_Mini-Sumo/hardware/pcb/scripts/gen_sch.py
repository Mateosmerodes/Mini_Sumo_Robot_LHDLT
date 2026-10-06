"""Genera el esquemático KiCad (robot_sumo.kicad_sch) a partir de design.py.

Estilo "por etiquetas": cada pin lleva una etiqueta local con el nombre de su red, así el
esquemático es legible por bloques sin cables cruzados. Los UUID son deterministas para que
la PCB siga enlazada al esquemático aunque se regenere.
"""
import copy
import math
import os
import uuid

import design
from libsym import get_symbol, pins
from sexp import Sym as S, dump, find, first

HERE = os.path.dirname(os.path.abspath(__file__))
PCB_DIR = os.path.join(HERE, '..')
LOCAL_LIBS = {'Sumo': os.path.join(PCB_DIR, 'lib', 'Sumo.kicad_sym')}
NS = uuid.UUID('6c1b7d1e-6a2f-4c55-9a43-0d6b5c1e7a01')
ROOT_UUID = str(uuid.uuid5(NS, 'root'))
GRID = 1.27
CHAR_W = 1.05          # ancho aproximado por carácter de etiqueta (tamaño 1.27)
ROTATE_2PIN = {'Device:R', 'Device:C', 'Device:C_Polarized', 'Device:L', 'Device:Fuse'}


def uid(*k):
    return str(uuid.uuid5(NS, '/'.join(map(str, k))))


def snap(v):
    return round(round(v / GRID) * GRID, 4)


def font(size=1.27, hide=False, justify=None, bold=False):
    f = [S('font'), [S('size'), size, size]]
    if bold:
        f.append([S('bold'), S('yes')])
    e = [S('effects'), f]
    if justify:
        e.append([S('justify')] + [S(j) for j in justify.split()])
    if hide:
        e.append([S('hide'), S('yes')])
    return e


def rot(x, y, r):
    a = math.radians(r)
    return (round(x * math.cos(a) - y * math.sin(a), 4), round(x * math.sin(a) + y * math.cos(a), 4))


class Placed:
    def __init__(self, part):
        self.p = part
        self.sym = get_symbol(part['lib'], LOCAL_LIBS)
        self.r = 90 if part['lib'] in ROTATE_2PIN else 0
        self.pins = {}
        for num, (nm, x, y, t, a) in pins(self.sym).items():
            rx, ry = rot(x, y, self.r)
            self.pins[num] = (nm, rx, ry, t, (a + self.r) % 360)
        xs = [v[1] for v in self.pins.values()] or [0]
        ys = [v[2] for v in self.pins.values()] or [0]
        self.x0, self.x1 = min(xs + [-2.54]), max(xs + [2.54])
        self.y0, self.y1 = min(ys + [-2.54]), max(ys + [2.54])
        lab = {0: 0.0, 90: 0.0, 180: 0.0, 270: 0.0}
        for num, (nm, x, y, t, a) in self.pins.items():
            net = part['nets'].get(num)
            ln = (len(net) * CHAR_W + 2.5) if net else 2.0
            lab[a] = max(lab[a], ln)
        # pin con ángulo 0 está a la izquierda -> etiqueta hacia la izquierda, etc.
        self.pad_l, self.pad_r, self.pad_d, self.pad_u = lab[0], lab[180], lab[90], lab[270]
        self.w = (self.x1 - self.x0) + self.pad_l + self.pad_r + 6
        self.h = (self.y1 - self.y0) + self.pad_u + self.pad_d + 13

    def place(self, left, top):
        """Coloca la caja (left, top) en coordenadas de hoja (Y hacia abajo)."""
        self.sx = snap(left + self.pad_l - self.x0 + 3)
        self.sy = snap(top + self.pad_u + self.y1 + 6.5)


def label_for(net, x, y, pin_angle):
    spin = {0: 180, 180: 0, 90: 270, 270: 90}[int(pin_angle)]
    just = 'right bottom' if spin in (180, 270) else 'left bottom'
    return [S('label'), net, [S('at'), x, y, spin], font(justify=just), [S('uuid'), uid('lbl', net, x, y)]]


def symbol_instance(pl, ref, value, extra_props):
    p = pl.p
    sx, sy = pl.sx, pl.sy
    props = []
    lib_props = {pp[1]: pp[2] for pp in find(pl.sym, 'property')}
    top = sy - pl.y1 - pl.pad_u - 1.5
    bot = sy - pl.y0 + pl.pad_d + 2.5
    vals = [('Reference', ref, sx, top, False), ('Value', value, sx, bot, False),
            ('Footprint', p['fp'], sx, sy, True),
            ('Datasheet', lib_props.get('Datasheet', '~'), sx, sy, True),
            ('Description', lib_props.get('Description', ''), sx, sy, True)]
    for k, v in extra_props.items():
        vals.append((k, v, sx, sy, True))
    for name, val, x, y, hide in vals:
        props.append([S('property'), name, val, [S('at'), snap(x), snap(y), pl.r], font(hide=hide)])
    sym_uuid = uid('sym', ref)
    inst = [S('symbol'), [S('lib_id'), p['lib']], [S('at'), sx, sy, pl.r], [S('unit'), 1],
            [S('exclude_from_sim'), S('no')], [S('in_bom'), S('no') if p['lib'].startswith('Mechanical') else S('yes')],
            [S('on_board'), S('yes')], [S('dnp'), S('yes') if p['dnp'] else S('no')],
            [S('uuid'), sym_uuid]] + props
    for num in sorted(pl.pins):
        inst.append([S('pin'), num, [S('uuid'), uid('pin', ref, num)]])
    inst.append([S('instances'), [S('project'), design.PROJECT,
                                  [S('path'), '/' + ROOT_UUID, [S('reference'), ref], [S('unit'), 1]]]])
    return inst


def lib_symbol_copy(lib_id, sym):
    s = copy.deepcopy(sym)
    s[1] = lib_id
    return s


def main():
    items, lib_symbols = [], {}
    groups = []
    for p in design.parts:
        if not groups or groups[-1][0] != p['group']:
            groups.append((p['group'], []))
        groups[-1][1].append(p)
    # PWR_FLAG como grupo final
    flag_parts = [dict(ref=f'#FLG0{i + 1}', lib='power:PWR_FLAG', value='PWR_FLAG', fp='',
                       nets={'1': n}, group='Banderas de alimentación', mpn='', dnp=False)
                  for i, n in enumerate(design.POWER_FLAGS)]
    groups.append(('Banderas de alimentación', flag_parts))

    # Empaquetado: cada grupo es un bloque de ancho máx. BW; los bloques en estanterías.
    SHEET_W, SHEET_H, M = 841.0, 594.0, 15.0     # A1 apaisado
    BW = 200.0
    blocks = []
    for name, ps in groups:
        placed = [Placed(p) for p in ps]
        x = y = 0.0
        row_h = 0.0
        pos = []
        for pl in placed:
            if x > 0 and x + pl.w > BW:
                x, y = 0.0, y + row_h
                row_h = 0.0
            pos.append((pl, x, y))
            x += pl.w
            row_h = max(row_h, pl.h)
        bw = max(px + pl.w for pl, px, _ in pos)
        bh = y + row_h + 8
        blocks.append((name, pos, bw, bh))
    cx, cy, shelf_h = M, M, 0.0
    for name, pos, bw, bh in blocks:
        if cx > M and cx + bw > SHEET_W - M:
            cx, cy, shelf_h = M, cy + shelf_h + 6, 0.0
        ox, oy = cx, cy
        items.append([S('rectangle'), [S('start'), snap(ox), snap(oy)], [S('end'), snap(ox + bw + 4), snap(oy + bh + 4)],
                      [S('stroke'), [S('width'), 0.2], [S('type'), S('dash')]], [S('fill'), [S('type'), S('none')]],
                      [S('uuid'), uid('box', name)]])
        items.append([S('text'), name.upper(), [S('exclude_from_sim'), S('no')], [S('at'), snap(ox + 2), snap(oy + 5), 0],
                      font(2.0, justify='left bottom', bold=True), [S('uuid'), uid('txt', name)]])
        for pl, px, py in pos:
            pl.place(ox + 2 + px, oy + 6 + py)
            p = pl.p
            if p['lib'] not in lib_symbols:
                lib_symbols[p['lib']] = lib_symbol_copy(p['lib'], pl.sym)
            extra = {'MPN': p['mpn']} if p['mpn'] else {}
            items.append(symbol_instance(pl, p['ref'], p['value'], extra))
            done = set()
            for num, (nm, x, y, t, a) in pl.pins.items():
                X, Y = snap(pl.sx + x), snap(pl.sy - y)
                net = p['nets'].get(num)
                if (X, Y) in done:
                    continue
                done.add((X, Y))
                if net:
                    items.append(label_for(net, X, Y, a))
                else:
                    items.append([S('no_connect'), [S('at'), X, Y], [S('uuid'), uid('nc', p['ref'], num)]])
        cx += bw + 10
        shelf_h = max(shelf_h, bh + 4)
    if cy + shelf_h > SHEET_H - 40:
        raise SystemExit(f'No cabe en la hoja: alto {cy + shelf_h:.0f} mm')

    sch = [S('kicad_sch'), [S('version'), 20250114], [S('generator'), 'eeschema'], [S('generator_version'), '9.0'],
           [S('uuid'), ROOT_UUID], [S('paper'), 'A1'],
           [S('title_block'), [S('title'), design.TITLE], [S('date'), '2026-10-06'], [S('rev'), design.REV],
            [S('company'), design.COMPANY],
            [S('comment'), 1, 'Generado con hardware/pcb/scripts/gen_sch.py a partir de design.py'],
            [S('comment'), 2, 'Licencia CERN-OHL-S v2']],
           [S('lib_symbols')] + list(lib_symbols.values())] + items + [
        [S('sheet_instances'), [S('path'), '/', [S('page'), '1']]],
        [S('embedded_fonts'), S('no')]]
    out = os.path.join(PCB_DIR, design.PROJECT + '.kicad_sch')
    with open(out, 'w') as f:
        f.write(dump(sch) + '\n')
    print('escrito', os.path.relpath(out), f'({len(design.parts)} componentes, alto usado {cy + shelf_h:.0f} mm)')


if __name__ == '__main__':
    main()
