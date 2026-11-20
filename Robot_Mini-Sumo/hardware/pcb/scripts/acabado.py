"""Acabado de la placa después del rutado automático (scripts/autoroute.py).

Uso:   python3 scripts/acabado.py [RED ...] [-RED ...]
       sin argumentos repasa todas las redes; con RED solo esas; -RED borra el rutado no bloqueado
       de esa red y la vuelve a rutar.
1. Rellena las zonas y busca, red a red, los trozos que no están unidos (lo que el DRC llama "unconnected").
2. Los une con un rutador de rejilla propio (A* en dos capas, rejilla de 0,05 mm, holgura 0,2 mm para
   potencia y GND y 0,15 mm para el resto), uniendo los trozos de masa con vías al plano inferior.
3. Quita los tramos bloqueados que hayan quedado colgando y guarda la placa.
Las zonas de VBAT las añade scripts/ensanchar.py; después de ese script hay que volver a pasar este con GND.

Es un rutador sencillo para terminar las pocas conexiones que deja Freerouting: después hay que pasar
el DRC (scripts/check.sh no, porque regenera la placa: kicad-cli pcb drc).
"""
import heapq
import math
import os
import sys

import numpy as np
import pcbnew
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.normpath(os.path.join(HERE, '..', 'robot_sumo.kicad_pcb'))
RES = 0.05            # mm por celda
CLR = 0.2             # holgura usada para todo (la mayor de las clases)
MARGEN = 0.06         # margen por la rejilla
CLR_DEF = 0.15        # holgura entre redes de la clase Default
POTENCIA = ('VBAT', 'VBAT_REV', 'VBAT_RAW', '+3V3', '+5V', 'BUCK_SW', 'V5_ESP')


def es_potencia(n):
    return n in POTENCIA or n.endswith(('_OUTA', '_OUTB'))
VIA_D, VIA_H = 0.6, 0.3
COSTE_VIA = 40
HUECO = 0.5           # distancia mínima entre taladros (borde a borde)
M = pcbnew.ToMM
CAPAS = [pcbnew.F_Cu, pcbnew.B_Cu]


class Rejilla:
    def __init__(self, board):
        bb = board.GetBoardEdgesBoundingBox()
        self.x0, self.y0 = M(bb.GetX()), M(bb.GetY())
        self.w = int(math.ceil(M(bb.GetWidth()) / RES)) + 1
        self.h = int(math.ceil(M(bb.GetHeight()) / RES)) + 1

    def a_celda(self, x, y):
        return int(round((y - self.y0) / RES)), int(round((x - self.x0) / RES))

    def a_mm(self, r, c):
        return self.x0 + c * RES, self.y0 + r * RES

    def poligono(self, sps):
        """SHAPE_POLY_SET -> máscara booleana."""
        img = Image.new('1', (self.w, self.h), 0)
        d = ImageDraw.Draw(img)
        for i in range(sps.OutlineCount()):
            for k, ol in enumerate([sps.Outline(i)] + [sps.Hole(i, j) for j in range(sps.HoleCount(i))]):
                pts = [((M(ol.CPoint(j).x) - self.x0) / RES, (M(ol.CPoint(j).y) - self.y0) / RES)
                       for j in range(ol.PointCount())]
                if len(pts) >= 3:
                    d.polygon(pts, fill=0 if k else 1)
        return np.array(img, dtype=bool)


def disco(r_mm):
    r = int(math.ceil(r_mm / RES))
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def forma(item, capa):
    sps = pcbnew.SHAPE_POLY_SET()
    item.TransformShapeToPolygon(sps, capa, 0, pcbnew.FromMM(0.005), pcbnew.ERROR_INSIDE)
    return sps


def agujeros(board, rej, excluir=None):
    """Máscara de los taladros (PTH, NPTH y vías), menos los de la red `excluir`."""
    img = Image.new('1', (rej.w, rej.h), 0)
    d = ImageDraw.Draw(img)
    items = [(p.GetPosition(), max(p.GetDrillSize().x, p.GetDrillSize().y)) for f in board.GetFootprints()
             for p in f.Pads() if p.GetDrillSize().x > 0 and (excluir is None or p.GetNetname() != excluir)]
    items += [(t.GetPosition(), t.GetDrill()) for t in board.GetTracks()
              if t.GetClass() == 'PCB_VIA' and (excluir is None or t.GetNetname() != excluir)]
    for pos, dr in items:
        x, y = (M(pos.x) - rej.x0) / RES, (M(pos.y) - rej.y0) / RES
        r = M(dr) / 2 / RES
        d.ellipse([x - r, y - r, x + r, y + r], fill=1)
    return np.array(img, dtype=bool)


def cobre(board, rej, capa, red=None, excluir=None, zonas=False, filtro=None):
    """Cobre de la capa: solo de la red `red`, o de todas menos `excluir` (y que cumplan `filtro`)."""
    m = np.zeros((rej.h, rej.w), bool)
    def vale(n):
        return ((red is None or n == red) and (excluir is None or n != excluir)
                and (filtro is None or filtro(n)))
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.IsOnLayer(capa) and vale(p.GetNetname()):
                m |= rej.poligono(forma(p, capa))
    for t in board.GetTracks():
        if t.IsOnLayer(capa) and vale(t.GetNetname()):
            m |= rej.poligono(forma(t, capa))
    if zonas:
        for z in board.Zones():
            if not z.GetIsRuleArea() and z.IsOnLayer(capa) and vale(z.GetNetname()) and z.HasFilledPolysForLayer(capa):
                m |= rej.poligono(z.GetFilledPolysList(capa))
    return m


def contorno(board, rej):
    sps = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(sps)
    return rej.poligono(sps)


def astar(libre, via_ok, src, dst, coste_via=COSTE_VIA):
    """libre[l]: celdas por las que puede pasar el eje de la pista en la capa l. src/dst: máscaras [l]."""
    h, w = libre[0].shape
    objetivo = [np.argwhere(dst[l]) for l in (0, 1)]
    tgt = np.vstack([np.c_[o, np.full(len(o), l)] for l, o in enumerate(objetivo) if len(o)])
    if not len(tgt):
        return None
    cy, cx = tgt[:, 0].mean(), tgt[:, 1].mean()
    def heur(r, c):
        return 1.0 * math.hypot(r - cy, c - cx)
    dist = {}
    prev = {}
    pq = []
    for l in (0, 1):
        for r, c in np.argwhere(src[l] & libre[l]):
            k = (int(r), int(c), l)
            dist[k] = 0.0
            heapq.heappush(pq, (heur(r, c), 0.0, k))
    pasos = [(-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1), (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)]
    n = 0
    while pq:
        f, g, k = heapq.heappop(pq)
        if g > dist.get(k, 1e18):
            continue
        r, c, l = k
        if dst[l][r, c]:
            camino = [k]
            while camino[-1] in prev:
                camino.append(prev[camino[-1]])
            return camino[::-1]
        n += 1
        if n > 12_000_000:
            print('  (búsqueda cortada)')
            return None
        vec = [(r + dr, c + dc, l, cost) for dr, dc, cost in pasos]
        if via_ok[r, c]:
            vec.append((r, c, 1 - l, coste_via))
        for rr, cc, ll, cost in vec:
            if 0 <= rr < h and 0 <= cc < w and libre[ll][rr, cc]:
                ng = g + cost
                kk = (rr, cc, ll)
                if ng < dist.get(kk, 1e18):
                    dist[kk] = ng
                    prev[kk] = k
                    heapq.heappush(pq, (ng + heur(rr, cc), ng, kk))
    return None


def simplificar(camino):
    """Lista de celdas -> tramos rectos por capa y posiciones de vía."""
    tramos, vias = [], []
    ini = camino[0]
    d_ant = None
    for a, b in zip(camino, camino[1:]):
        if a[2] != b[2]:
            if (a[0], a[1]) != (ini[0], ini[1]):
                tramos.append((ini, a))
            vias.append(a)
            ini, d_ant = b, None
            continue
        d = (b[0] - a[0], b[1] - a[1])
        if d_ant is not None and d != d_ant:
            tramos.append((ini, a))
            ini = a
        d_ant = d
    if (camino[-1][0], camino[-1][1]) != (ini[0], ini[1]):
        tramos.append((ini, camino[-1]))
    return tramos, vias


def componentes(board, rej, red):
    """Trozos conexos de una red (pads, pistas, vías y zonas) en las dos capas."""
    cu = [cobre(board, rej, l, red=red, zonas=True) for l in CAPAS]
    enlace = np.zeros_like(cu[0])
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() == red and p.GetDrillSize().x > 0:
                enlace |= rej.poligono(forma(p, pcbnew.F_Cu))
    for t in board.GetTracks():
        if t.GetClass() == 'PCB_VIA' and t.GetNetname() == red:
            enlace |= rej.poligono(forma(t, pcbnew.F_Cu))
    vol = np.stack(cu)
    est = np.zeros((3, 3, 3), bool)
    est[1] = ndimage.generate_binary_structure(2, 1)
    lab, n = ndimage.label(vol, structure=est)
    # unir capas por vías y pads con taladro
    for r, c in np.argwhere(enlace & cu[0] & cu[1]):
        a, b = lab[0, r, c], lab[1, r, c]
        if a != b and a and b:
            lab[lab == b] = a
    return lab


def rutar_red(board, rej, red, ancho, base_libre, borde, taladros, nets):
    lab = componentes(board, rej, red)
    ids = [i for i in np.unique(lab) if i]
    if len(ids) < 2:
        return 0
    # obstáculos: cobre de las demás redes (sin zonas de GND si no es GND)
    zon = False  # las zonas de GND se vuelven a rellenar alrededor de lo nuevo
    pot = [cobre(board, rej, l, excluir=red, zonas=zon, filtro=lambda n: es_potencia(n) or n == 'GND') for l in CAPAS]
    sen = [cobre(board, rej, l, excluir=red, zonas=zon, filtro=lambda n: not (es_potencia(n) or n == 'GND')) for l in CAPAS]
    c_sen = CLR if es_potencia(red) or red == 'GND' else CLR_DEF
    def bloqueo(l, r_extra):
        return (ndimage.binary_dilation(pot[l], disco(CLR + r_extra + MARGEN))
                | ndimage.binary_dilation(sen[l], disco(c_sen + r_extra + MARGEN)))
    anchos = ancho if isinstance(ancho, (list, tuple)) else [ancho]
    libres = {a: [~bloqueo(l, a / 2) & borde & ~ndimage.binary_dilation(taladros, disco(0.25 + a / 2 + MARGEN))
                  for l in (0, 1)] for a in anchos}
    via_ok = (~bloqueo(0, VIA_D / 2) & ~bloqueo(1, VIA_D / 2)
              & ~ndimage.binary_dilation(taladros, disco(HUECO + VIA_H / 2 + MARGEN)) & borde)
    # el trozo más grande es el destino; se van uniendo los demás
    tam = {i: int((lab == i).sum()) for i in ids}
    hechos = 0
    principal = max(tam, key=tam.get)
    for i in sorted(ids, key=lambda i: tam[i]):
        if i == principal:
            continue
        src = [lab[l] == i for l in (0, 1)]
        dst = [lab[l] == principal for l in (0, 1)]
        camino = None
        for k, a in enumerate(anchos):
            # los anchos grandes (todos menos el último) van solo por arriba: sin vías en el tronco
            vo = via_ok if k == len(anchos) - 1 else np.zeros_like(via_ok)
            camino = astar(libres[a], vo, src, dst)
            if camino is not None:
                ancho_t = a
                break
        if camino is None:
            rr, cc, _ = np.argwhere(np.stack(src))[:, [1, 2, 0]].mean(0)
            x, y = rej.a_mm(rr, cc)
            print(f'  {red}: no se pudo unir un trozo de {tam[i]} celdas (en x={x:.1f}, y={y:.1f} mm)')
            continue
        tramos, vias = simplificar(camino)
        pos = []
        for v in vias:   # dos cambios de capa en la misma celda se anulan
            if pos and pos[-1] == (v[0], v[1]):
                pos.pop()
            else:
                pos.append((v[0], v[1]))
        vias = pos
        for a, b in tramos:
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I_MM(*rej.a_mm(a[0], a[1])))
            t.SetEnd(pcbnew.VECTOR2I_MM(*rej.a_mm(b[0], b[1])))
            t.SetWidth(pcbnew.FromMM(ancho_t)); t.SetLayer(CAPAS[a[2]]); t.SetNet(nets[red])
            board.Add(t)
        for v in vias:
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pcbnew.VECTOR2I_MM(*rej.a_mm(v[0], v[1])))
            via.SetWidth(pcbnew.FromMM(VIA_D)); via.SetDrill(pcbnew.FromMM(VIA_H)); via.SetNet(nets[red])
            board.Add(via)
        for v in vias:   # la vía nueva es obstáculo para las uniones siguientes
            m = np.zeros_like(via_ok); m[v[0], v[1]] = True
            via_ok &= ~ndimage.binary_dilation(m, disco(VIA_H + HUECO + MARGEN))
        hechos += 1
        print(f'  {red}: unido un trozo a {ancho_t} mm ({len(tramos)} tramos, {len(vias)} vías)')
        # actualizar: el trozo i pasa a ser parte del principal y el cobre nuevo es obstáculo para la red siguiente
        lab[lab == i] = principal
    return hechos


def quitar_colgantes(board):
    """Quita los tramos con un extremo al aire (restos de la salida fija de los drivers que el
    autorrutador no aprovechó). Repite hasta que no queda ninguno."""
    total = 0
    while True:
        conn = board.GetConnectivity()
        conn.RecalculateRatsnest()
        malos = [t for t in board.GetTracks() if t.GetClass() == 'PCB_TRACK' and t.IsLocked()
                 and conn.TestTrackEndpointDangling(t, False)]
        if not malos:
            return total
        for t in malos:
            board.Delete(t)
        total += len(malos)
        board.BuildConnectivity()


def main():
    board = pcbnew.LoadBoard(PCB)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    rej = Rejilla(board)
    nets = {str(k): v for k, v in board.GetNetsByName().items() if str(k)}
    borde = ndimage.binary_erosion(contorno(board, rej), disco(0.3 + 0.1 + MARGEN))
    args = sys.argv[1:]
    quitar = [a[1:] for a in args if a.startswith('-')]   # -RED: levanta su rutado y la vuelve a rutar
    for t in list(board.GetTracks()):
        if t.GetNetname() in quitar and not t.IsLocked():
            board.Delete(t)
    redes = [a for a in args if not a.startswith('-')] + quitar or [str(k) for k in nets]
    total = 0
    for red in redes:
        taladros = agujeros(board, rej, red)
        if red in ('VBAT', 'VBAT_REV', 'VBAT_RAW'):
            ancho = [1.5, 1.0, 0.4]
        elif red.endswith(('_OUTA', '_OUTB')):
            ancho = [0.8, 0.4]
        else:
            ancho = 0.2
        n = rutar_red(board, rej, red, ancho, None, borde, taladros, nets)
        total += n
        if n:
            filler.Fill(board.Zones())
    print(f'tramos colgantes quitados: {quitar_colgantes(board)}')
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    print(f'conexiones añadidas: {total}')


if __name__ == '__main__':
    main()
