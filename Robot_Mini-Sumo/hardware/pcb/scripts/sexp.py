"""Parser/serializador mínimo de S-expresiones de KiCad."""
import re

_TOKEN = re.compile(r'\s*(?:(\()|(\))|("(?:\\.|[^"\\])*")|([^\s()"]+))')


class Sym(str):
    """Átomo sin comillas (keyword o número)."""


def parse(text):
    stack, cur, pos = [], [], 0
    while True:
        m = _TOKEN.match(text, pos)
        if not m or m.end() == pos:
            break
        pos = m.end()
        op, cl, st, at = m.groups()
        if op:
            stack.append(cur)
            cur = []
        elif cl:
            done = cur
            cur = stack.pop()
            cur.append(done)
        elif st is not None:
            cur.append(st[1:-1].replace('\\"', '"').replace('\\\\', '\\'))
        else:
            cur.append(Sym(at))
    return cur[0]


def q(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'


def dump(e, ind=0):
    if not isinstance(e, list):
        if isinstance(e, Sym):
            return str(e)
        if isinstance(e, bool):
            return 'yes' if e else 'no'
        if isinstance(e, (int, float)):
            return fmt(e)
        return q(e)
    tab = '\t' * ind
    simple = all(not isinstance(x, list) for x in e)
    if simple:
        return '(' + ' '.join(dump(x) for x in e) + ')'
    out = '(' + ' '.join(dump(x) for x in e if not isinstance(x, list))
    for x in e:
        if isinstance(x, list):
            out += '\n' + tab + '\t' + dump(x, ind + 1)
    return out + '\n' + tab + ')'


def fmt(v):
    if isinstance(v, int):
        return str(v)
    s = f'{v:.4f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def find(e, key):
    return [x for x in e if isinstance(x, list) and x and x[0] == key]


def first(e, key):
    r = find(e, key)
    return r[0] if r else None
