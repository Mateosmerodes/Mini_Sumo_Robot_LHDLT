"""Ensancha las pistas de potencia todo lo que deja el DRC (después de autoroute.py y acabado.py).

Uso:   python3 scripts/ensanchar.py
Las pistas de VBAT (hasta 10 A) y de las salidas de motor (hasta 2,44 A) se rutan a 0,4 mm para que
entren en los pines de 0,65 mm de paso de los DRV8874. Aquí se prueba cada tramo con el mayor ancho
de la lista y se va bajando un escalón en los tramos que el DRC de KiCad marca, hasta que no queda
ninguna infracción. Los tramos fijos (salida de los drivers) no se tocan.
Al final añade cuatro zonas de VBAT en la cara superior (prioridad sobre el plano de GND) que
engordan el reparto de batería hacia los cuatro drivers. Las zonas parten islas del plano de GND
superior: después hay que volver a coser GND con  python3 scripts/acabado.py GND  y pasar el DRC.
"""
import json
import os
import subprocess
import tempfile

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.normpath(os.path.join(HERE, '..', 'robot_sumo.kicad_pcb'))
TRONCO = ('VBAT', 'VBAT_REV', 'VBAT_RAW')
ANCHOS_TRONCO = [2.0, 1.5, 1.2, 1.0, 0.8, 0.6, 0.5]
ANCHOS_MOTOR = [1.0, 0.8, 0.6, 0.5]
TIPOS = {'clearance', 'hole_clearance', 'copper_edge_clearance', 'shorting_items', 'tracks_crossing',
         'solder_mask_bridge'}


def anchos(red):
    if red in TRONCO:
        return ANCHOS_TRONCO
    if red.endswith(('_OUTA', '_OUTB')):
        return ANCHOS_MOTOR
    return None


def drc_uuids():
    out = os.path.join(tempfile.mkdtemp(), 'drc.json')
    subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '--severity-error', '-o', out, PCB],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    rep = json.load(open(out))
    malos = set()
    for v in rep.get('violations', []):
        if v.get('type') in TIPOS:
            for it in v.get('items', []):
                malos.add(it.get('uuid'))
    return malos, rep


# Zonas de VBAT en F.Cu (x0, y0, x1, y1) en mm: drivers izquierdos, centro (Q1/F1), drivers derechos y
# el puente entre centro y derecha (prioridad 2 porque solapa a las otras dos).
ZONAS_VBAT = [((129.5, 93, 137.5, 119), 1), ((139.5, 93, 160.5, 109), 1), ((172.5, 93, 182, 119), 1),
              ((160, 106, 175, 112), 2)]


def zonas_vbat(board):
    from gen_pcb import ajustes_zona
    for z in list(board.Zones()):
        if z.GetZoneName().startswith('VBAT_sup'):
            board.Delete(z)
    net = board.FindNet('VBAT')
    for i, ((x0, y0, x1, y1), prio) in enumerate(ZONAS_VBAT):
        z = pcbnew.ZONE(board)
        z.SetLayer(pcbnew.F_Cu)
        z.SetNetCode(net.GetNetCode())
        z.SetZoneName(f'VBAT_sup{i}')
        z.SetAssignedPriority(prio)
        ajustes_zona(z)
        o = z.Outline()
        o.NewOutline()
        for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
            o.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
        board.Add(z)


def main():
    board = pcbnew.LoadBoard(PCB)
    nivel = {}
    original = {}
    for t in board.GetTracks():
        if t.GetClass() == 'PCB_TRACK' and not t.IsLocked() and anchos(t.GetNetname()):
            u = t.m_Uuid.AsString()
            nivel[u] = 0
            original[u] = t.GetWidth()
    print(f'tramos de potencia: {len(nivel)}')
    for it in range(12):
        for t in board.GetTracks():
            u = t.m_Uuid.AsString()
            if u in nivel:
                lista = anchos(t.GetNetname())
                w = pcbnew.FromMM(lista[nivel[u]]) if nivel[u] < len(lista) else original[u]
                t.SetWidth(max(w, original[u]))
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        pcbnew.SaveBoard(PCB, board)
        malos, _ = drc_uuids()
        bajar = [u for u in malos if u in nivel and nivel[u] < len(anchos_de(board, u))]
        print(f'  iteración {it}: {len(bajar)} tramos a estrechar')
        if not bajar:
            break
        for u in bajar:
            nivel[u] += 1
    zonas_vbat(board)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    resumen = {}
    for t in board.GetTracks():
        if t.m_Uuid.AsString() in nivel:
            k = (t.GetNetname() if t.GetNetname() in TRONCO else 'motores', round(pcbnew.ToMM(t.GetWidth()), 2))
            resumen[k] = resumen.get(k, 0) + pcbnew.ToMM(t.GetLength())
    for (red, w), l in sorted(resumen.items()):
        print(f'  {red:9s} {w:4.2f} mm: {l:6.1f} mm de pista')


_cache = {}


def anchos_de(board, u):
    if not _cache:
        for t in board.GetTracks():
            _cache[t.m_Uuid.AsString()] = anchos(t.GetNetname()) or []
    return _cache.get(u, [])


if __name__ == '__main__':
    main()
