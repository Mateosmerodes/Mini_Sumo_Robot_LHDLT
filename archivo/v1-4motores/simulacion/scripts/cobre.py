#!/usr/bin/env python3
"""Caída de tensión, densidad de corriente y pérdidas en el cobre de una red de la PCB.

Método: diferencias finitas 2D sobre el cobre real que guarda KiCad (zonas rellenas, pistas y pads
de F.Cu y B.Cu), con rejilla de 0,1 mm. Las vías y los pads pasantes unen las dos caras.
Basado en hardware/pcb/scripts/correccion_vbat/solve.py, con dos cambios: une también las caras en
los pads pasantes (sin eso parte del GND sale aislado) y guarda los mapas para dibujarlos.

Uso: python3 cobre.py <robot_sumo.kicad_pcb> <RED> <pad_fuente> <pad1,pad2,...> <oz> <A_por_pad> <salida.npz>
Necesita el módulo pcbnew de KiCad 9.
"""
import sys
import numpy as np
import pcbnew
import scipy.sparse as sp
import scipy.sparse.linalg as spl
import scipy.sparse.csgraph as cg
from matplotlib.path import Path

pcbfile, NET, src = sys.argv[1], sys.argv[2], sys.argv[3]
sinks = sys.argv[4].split(',')
oz, Iper, out = float(sys.argv[5]), float(sys.argv[6]), sys.argv[7]
h = 0.1  # mm
RHO = 1.72e-8
b = pcbnew.LoadBoard(pcbfile)
bb = b.GetBoardEdgesBoundingBox()
X0, Y0 = bb.GetX() / 1e6, bb.GetY() / 1e6
nx, ny = int(bb.GetWidth() / 1e6 / h) + 1, int(bb.GetHeight() / 1e6 / h) + 1
xs, ys = X0 + np.arange(nx) * h, Y0 + np.arange(ny) * h


def poly_mask(pts):
    p = Path(pts)
    x0, y0 = pts.min(0)
    x1, y1 = pts.max(0)
    i0, i1 = max(0, int((x0 - X0) / h) - 1), min(nx, int((x1 - X0) / h) + 2)
    j0, j1 = max(0, int((y0 - Y0) / h) - 1), min(ny, int((y1 - Y0) / h) + 2)
    gx, gy = np.meshgrid(xs[i0:i1], ys[j0:j1])
    return j0, j1, i0, i1, p.contains_points(np.c_[gx.ravel(), gy.ravel()]).reshape(gy.shape)


def add_shape(M, sps):
    for i in range(sps.OutlineCount()):
        o = sps.Outline(i)
        pts = np.array([(o.CPoint(k).x / 1e6, o.CPoint(k).y / 1e6) for k in range(o.PointCount())])
        if len(pts) < 3:
            continue
        j0, j1, i0, i1, m = poly_mask(pts)
        M[j0:j1, i0:i1] |= m
        for hI in range(sps.HoleCount(i)):
            ho = sps.Hole(i, hI)
            hp = np.array([(ho.CPoint(k).x / 1e6, ho.CPoint(k).y / 1e6) for k in range(ho.PointCount())])
            j0, j1, i0, i1, m = poly_mask(hp)
            M[j0:j1, i0:i1] &= ~m


def cells(obj, lid):
    s = pcbnew.SHAPE_POLY_SET()
    obj.TransformShapeToPolygon(s, lid, 0, 10000, pcbnew.ERROR_INSIDE)
    M = np.zeros((ny, nx), bool)
    add_shape(M, s)
    return M


LAY = (pcbnew.F_Cu, pcbnew.B_Cu)
masks = []
for lid in LAY:
    M = np.zeros((ny, nx), bool)
    for z in b.Zones():
        if z.GetNetname() == NET and z.IsOnLayer(lid):
            add_shape(M, z.GetFilledPolysList(lid))
    for t in b.GetTracks():
        if t.GetNetname() == NET and t.IsOnLayer(lid):
            M |= cells(t, lid)
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() == NET and p.IsOnLayer(lid):
                M |= cells(p, lid)
    masks.append(M)
idx = -np.ones((2, ny, nx), int)
n = 0
for k in range(2):
    c = masks[k].sum()
    idx[k][masks[k]] = np.arange(n, n + c)
    n += c
t_cu = oz * 35e-6
g = t_cu / RHO  # conductancia de un cuadrado
rows, cols, vals = [], [], []


def link_many(a, c, gv):
    rows.extend(np.r_[a, c, a, c]); cols.extend(np.r_[a, c, c, a])
    vals.extend(np.r_[np.full(len(a), gv), np.full(len(a), gv), np.full(len(a), -gv), np.full(len(a), -gv)])


for k in range(2):
    I = idx[k]
    a, c = I[:, :-1], I[:, 1:]
    m = (a >= 0) & (c >= 0)
    link_many(a[m], c[m], g)
    a, c = I[:-1, :], I[1:, :]
    m = (a >= 0) & (c >= 0)
    link_many(a[m], c[m], g)
GV = 1e3  # unión ideal entre caras en cada celda de vía / pad pasante
for t in b.GetTracks():
    if t.GetClass() == 'PCB_VIA' and t.GetNetname() == NET:
        M = cells(t, LAY[0])
        f_, b_ = idx[0][M], idx[1][M]
        ok = (f_ >= 0) & (b_ >= 0)
        link_many(f_[ok], b_[ok], GV)
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetNetname() == NET and p.GetDrillSize().x > 0:
            M = cells(p, LAY[0]) & cells(p, LAY[1])
            f_, b_ = idx[0][M], idx[1][M]
            ok = (f_ >= 0) & (b_ >= 0)
            link_many(f_[ok], b_[ok], GV)


def padcells(ref):
    r, num = ref.split('.')
    fp = b.FindFootprintByReference(r)
    outc = []
    for p in fp.Pads():
        if p.GetNumber() == num:
            for k, lid in enumerate(LAY):
                if p.IsOnLayer(lid):
                    M = cells(p, lid)
                    outc += list(idx[k][M][idx[k][M] >= 0])
    return np.array(outc, int)


G = sp.coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsr()
nc, lab = cg.connected_components(G != 0, directed=False)
srcc = padcells(src)
for s in sinks:
    if set(lab[padcells(s)]) != set(lab[srcc]):
        sys.exit(f'{s} no está unido a {src} en el cobre')
G = G + sp.diags(np.isin(np.arange(n), srcc) * 1e3)
Ib = np.zeros(n)
for s in sinks:
    cc = padcells(s)
    Ib[cc] -= Iper / len(cc)
V = spl.spsolve(G.tocsc(), Ib)
drops = {s: float(-V[padcells(s)].mean()) for s in sinks}
# densidad de corriente (A/mm²) en el centro de cada celda y potencia por celda (W)
J = np.zeros((2, ny, nx))
Vm = np.full((2, ny, nx), np.nan)
for k in range(2):
    Vk = np.full((ny, nx), np.nan)
    m = idx[k] >= 0
    Vk[m] = V[idx[k][m]]
    Vm[k] = Vk
    ex = np.zeros((ny, nx)); ey = np.zeros((ny, nx))
    dx = np.diff(Vk, axis=1) / (h * 1e-3); dy = np.diff(Vk, axis=0) / (h * 1e-3)
    dx = np.nan_to_num(dx); dy = np.nan_to_num(dy)
    ex[:, :-1] += dx / 2; ex[:, 1:] += dx / 2
    ey[:-1, :] += dy / 2; ey[1:, :] += dy / 2
    J[k] = np.hypot(ex, ey) / RHO / 1e6 * m
P = (J * 1e6) ** 2 * RHO * (h * 1e-3) ** 2 * t_cu  # W por celda
for s, d in drops.items():
    print(f'{s}: caída {d * 1000:.1f} mV')
print(f'pérdidas totales {P.sum():.3f} W')
for k, L in enumerate('FB'):
    j = np.unravel_index(np.argmax(J[k]), J[k].shape)
    print(f'{L}.Cu: J máx {J[k].max():.0f} A/mm² en ({X0 + j[1] * h:.1f}, {Y0 + j[0] * h:.1f})')
np.savez_compressed(out, J=J, P=P, V=Vm, mask=np.array(masks), X0=X0, Y0=Y0, h=h, drops=str(drops),
                    net=NET, I=Iper * len(sinks))
