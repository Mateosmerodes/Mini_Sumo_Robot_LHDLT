"""Genera la lista de materiales (BOM) de la PCB agrupada por valor + huella.

Salida: hardware/pcb/bom.csv (formato JLCPCB: Comment, Designator, Footprint, LCSC, MPN)
        y una tabla Markdown por la salida estándar.
La columna LCSC se deja vacía a propósito: hay que elegir cada referencia en lcsc.com
comprobando stock y si es "Basic" (más barata de montar en JLC).
"""
import csv
import os
import re
from collections import OrderedDict

import design

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'bom.csv')


def clave_ref(r):
    m = re.match(r'([A-Z]+)(\d+)', r)
    return (m.group(1), int(m.group(2))) if m else (r, 0)


def main():
    grupos = OrderedDict()
    for p in sorted(design.parts, key=lambda p: clave_ref(p['ref'])):
        if p['lib'].startswith('Mechanical'):
            continue
        k = (p['value'], p['fp'].split(':')[1], p['mpn'])
        grupos.setdefault(k, []).append(p['ref'])
    with open(OUT, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC', 'MPN', 'Cantidad'])
        for (val, fp, mpn), refs in grupos.items():
            w.writerow([val, ','.join(refs), fp, '', mpn, len(refs)])
    print('| Cant. | Valor | Encapsulado | Referencias | Nota |')
    print('|---|---|---|---|---|')
    for (val, fp, mpn), refs in grupos.items():
        fp_corto = fp.split('_')[0] if fp.startswith(('R_', 'C_')) else fp.split('_1x')[0]
        fp_corto = re.sub(r'_\d+Metric.*', '', fp)
        print(f"| {len(refs)} | {val} | {fp_corto} | {', '.join(refs)} | {mpn} |")


if __name__ == '__main__':
    main()
