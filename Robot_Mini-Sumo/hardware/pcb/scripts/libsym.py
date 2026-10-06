"""Carga símbolos de las librerías de KiCad y calcula la posición de sus pines."""
import os
from sexp import parse, find, first

SYS_LIB = '/usr/share/kicad/symbols'
_cache = {}


def load_lib(path):
    if path not in _cache:
        with open(path) as f:
            root = parse(f.read())
        _cache[path] = {s[1]: s for s in find(root, 'symbol')}
    return _cache[path]


def get_symbol(lib_id, local_libs=None):
    lib, name = lib_id.split(':')
    path = (local_libs or {}).get(lib) or os.path.join(SYS_LIB, lib + '.kicad_sym')
    syms = load_lib(path)
    s = syms[name]
    ext = first(s, 'extends')
    if ext:  # resolver herencia: copiar cuerpo del padre con el nombre/props del hijo
        parent = syms[ext[1]]
        merged = [s[0], name]
        merged += [x for x in s[2:] if isinstance(x, list) and x[0] not in ('extends',)]
        props = {p[1] for p in find(s, 'property')}
        for x in parent[2:]:
            if not isinstance(x, list):
                continue
            if x[0] == 'property' and x[1] in props:
                continue
            if x[0] == 'symbol':
                x = [x[0], x[1].replace(ext[1], name, 1)] + x[2:]
            if x[0] in ('pin_numbers', 'pin_names', 'exclude_from_sim', 'in_bom', 'on_board') and first(merged, x[0]):
                continue
            merged.append(x)
        s = merged
    return s


def pins(sym, unit=1):
    """Devuelve {numero: (nombre, x, y, tipo, angulo)} en coordenadas de librería (Y hacia arriba)."""
    out = {}
    for sub in find(sym, 'symbol'):
        parts = sub[1].rsplit('_', 2)
        u = int(parts[-2])
        if u not in (0, unit):
            continue
        for p in find(sub, 'pin'):
            at = first(p, 'at')
            nm = first(p, 'name')[1]
            num = first(p, 'number')[1]
            ang = float(at[3]) if len(at) > 3 else 0.0
            out[num] = (nm, float(at[1]), float(at[2]), str(p[1]), ang)
    return out
