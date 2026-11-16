#!/usr/bin/env python3
"""Calentamiento transitorio de la placa con los 4 motores bloqueados (peor caso de corriente).

Modelo térmico 2D de dos capas (rejilla de 0,2 mm):
  - cobre real de cada cara (todas las redes, de KiCad) que reparte el calor en el plano,
  - FR4 de 1,6 mm entre caras, vías y pads pasantes como puentes térmicos de cobre,
  - convección natural + radiación por las dos caras (h = 10 W/m²K, aire a 25 °C),
  - fuentes de calor: efecto Joule en VBAT y GND (de cobre.py) + componentes de potencia.
Es una estimación simplificada: no modela la caja del robot, el ventilado ni los cables.

Uso: python3 termico.py <robot_sumo.kicad_pcb> <resultados/>   (necesita pcbnew y cobre_*.npz)
"""
import sys, json
import numpy as np
import pcbnew
import scipy.sparse as sp
import scipy.sparse.linalg as spl
from matplotlib.path import Path

pcbfile, res = sys.argv[1], sys.argv[2]
d = np.load(f'{res}/cobre_VBAT.npz')
h0, X0, Y0 = float(d['h']), float(d['X0']), float(d['Y0'])
P0 = d['P'] + np.load(f'{res}/cobre_GND.npz')['P']  # W por celda de 0,1 mm, (2, ny, nx)
ny0, nx0 = P0.shape[1:]
b = pcbnew.LoadBoard(pcbfile)
xs, ys = X0 + np.arange(nx0) * h0, Y0 + np.arange(ny0) * h0


def add_shape(M, sps):
    for i in range(sps.OutlineCount()):
        for hole, o in [(False, sps.Outline(i))] + [(True, sps.Hole(i, k)) for k in range(sps.HoleCount(i))]:
            pts = np.array([(o.CPoint(k).x / 1e6, o.CPoint(k).y / 1e6) for k in range(o.PointCount())])
            if len(pts) < 3:
                continue
            x0, y0 = pts.min(0); x1, y1 = pts.max(0)
            i0, i1 = max(0, int((x0 - X0) / h0) - 1), min(nx0, int((x1 - X0) / h0) + 2)
            j0, j1 = max(0, int((y0 - Y0) / h0) - 1), min(ny0, int((y1 - Y0) / h0) + 2)
            gx, gy = np.meshgrid(xs[i0:i1], ys[j0:j1])
            m = Path(pts).contains_points(np.c_[gx.ravel(), gy.ravel()]).reshape(gy.shape)
            if hole:
                M[j0:j1, i0:i1] &= ~m
            else:
                M[j0:j1, i0:i1] |= m


def shape_of(obj, lid):
    s = pcbnew.SHAPE_POLY_SET()
    obj.TransformShapeToPolygon(s, lid, 0, 10000, pcbnew.ERROR_INSIDE)
    return s


LAY = (pcbnew.F_Cu, pcbnew.B_Cu)
cu = np.zeros((2, ny0, nx0), bool)
for k, lid in enumerate(LAY):
    for z in b.Zones():
        if z.IsOnLayer(lid) and not z.GetIsRuleArea():
            add_shape(cu[k], z.GetFilledPolysList(lid))
    for t in b.GetTracks():
        if t.IsOnLayer(lid):
            add_shape(cu[k], shape_of(t, lid))
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.IsOnLayer(lid):
                add_shape(cu[k], shape_of(p, lid))
# contorno de la placa
edge = np.zeros((ny0, nx0), bool)
outl = pcbnew.SHAPE_POLY_SET()
b.GetBoardPolygonOutlines(outl)
add_shape(edge, outl)

# ---- rejilla gruesa (factor 2 -> 0,2 mm)
F = 2
h = h0 * F
ny, nx = ny0 // F, nx0 // F
def coarse(a, how):
    a = a[..., :ny * F, :nx * F].reshape(a.shape[:-2] + (ny, F, nx, F))
    return a.sum((-3, -1)) if how == 'sum' else a.mean((-3, -1))
fcu = coarse(cu.astype(float), 'mean')        # fracción de cobre por celda
board = coarse(edge.astype(float), 'mean') > 0.5
Pj = coarse(P0, 'sum')                          # W
A = (h * 1e-3) ** 2
k_cu, t_cu = 390.0, 35e-6
k_fr, t_fr = 0.3, 1.6e-3
hconv = 10.0
# conductancia en el plano por capa (cobre + media placa de FR4)
gsh = fcu * k_cu * t_cu + k_fr * t_fr / 2       # W/K por cuadrado
gz = np.full((ny, nx), 0.3 * A / t_fr)          # FR4 vertical por celda
# vías y pads pasantes (todas las redes): barril de cobre de 25 µm
nvias = 0
def addvia(x, y, dr):
    global nvias
    i, j = int((x - X0) / h), int((y - Y0) / h)
    if 0 <= i < nx and 0 <= j < ny:
        gz[j, i] += k_cu * np.pi * dr * 25e-6 / t_fr; nvias += 1
for t in b.GetTracks():
    if t.GetClass() == 'PCB_VIA':
        p = t.GetPosition(); addvia(p.x / 1e6, p.y / 1e6, t.GetDrillValue() / 1e9)
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetDrillSize().x > 0:
            q = p.GetPosition(); addvia(q.x / 1e6, q.y / 1e6, p.GetDrillSize().x / 1e9)
# capacidad calorífica por celda y capa
cap = A * (2.0e6 * t_fr / 2 + 3.45e6 * t_cu * fcu)

# ---- fuentes de calor de componentes (peor caso: 4 motores bloqueados en I_TRIP = 2,44 A)
ITRIP = 2.44
I_bat = 4 * ITRIP + 0.42
comp = {  # referencia: (W, cara)  — valores supuestos, ver docs/14
    'U5': (ITRIP ** 2 * 0.30, 0), 'U6': (ITRIP ** 2 * 0.30, 0), 'U7': (ITRIP ** 2 * 0.30, 0), 'U8': (ITRIP ** 2 * 0.30, 0),
    'Q1': (I_bat ** 2 * 0.015, 0), 'F1': (I_bat ** 2 * 0.005, 0), 'U2': (0.25, 0), 'L1': (0.12, 0), 'D1': (0.45 * 0.45, 0),
}
Pc = np.zeros((2, ny, nx))
for ref, (w, L) in comp.items():
    f = b.FindFootprintByReference(ref)
    bbx = f.GetBoundingBox(False)
    i0, i1 = int((bbx.GetX() / 1e6 - X0) / h), int((bbx.GetRight() / 1e6 - X0) / h)
    j0, j1 = int((bbx.GetY() / 1e6 - Y0) / h), int((bbx.GetBottom() / 1e6 - Y0) / h)
    # el calor entra por el pad central / pads: se reparte en el 50 % central de la huella
    ci, cj = (i0 + i1) // 2, (j0 + j1) // 2
    wi, wj = max(1, (i1 - i0) // 4), max(1, (j1 - j0) // 4)
    Pc[L, cj - wj:cj + wj + 1, ci - wi:ci + wi + 1] += w / ((2 * wi + 1) * (2 * wj + 1))

# ---- matriz
N = 2 * ny * nx
id_ = np.arange(N).reshape(2, ny, nx)
r, c, v = [], [], []
def lk(a, bb_, gv):
    r.extend(np.r_[a, bb_, a, bb_]); c.extend(np.r_[a, bb_, bb_, a]); v.extend(np.r_[gv, gv, -gv, -gv])
for k in range(2):
    g_ = gsh[k] * board
    gx = 2 * g_[:, :-1] * g_[:, 1:] / (g_[:, :-1] + g_[:, 1:] + 1e-30)
    gy = 2 * g_[:-1, :] * g_[1:, :] / (g_[:-1, :] + g_[1:, :] + 1e-30)
    lk(id_[k][:, :-1].ravel(), id_[k][:, 1:].ravel(), gx.ravel())
    lk(id_[k][:-1, :].ravel(), id_[k][1:, :].ravel(), gy.ravel())
lk(id_[0].ravel(), id_[1].ravel(), (gz * board).ravel())
Gconv = np.r_[(hconv * A * board).ravel(), (hconv * A * board).ravel()] + 1e-9
Gm = sp.coo_matrix((v, (r, c)), shape=(N, N)).tocsc() + sp.diags(Gconv)
Cm = np.r_[(cap[0] * board).ravel(), (cap[1] * board).ravel()] + 1e-9
Ptot = (Pj + Pc).ravel()
print(f'potencia total {Ptot.sum():.2f} W (Joule cobre {Pj.sum():.2f} W, componentes {Pc.sum():.2f} W), {nvias} vías/pads')
dt = 0.05
lu = spl.splu((sp.diags(Cm / dt) + Gm).tocsc())
T = np.zeros(N)
hist, snaps = [], {}
watch = {'U5': (128.0, 96.0), 'U7': (171.0, 96.0), 'Q1': (146.0, 93.6), 'F1': (155.0, 93.6),
         'cuello VBAT (138,6; 98,5)': (138.6, 98.5), 'cuello GND F (120,2; 122,6)': (120.2, 122.6),
         'cuello GND B (172,6; 106,2)': (172.6, 106.2)}
def at(Tk, x, y, L):
    return Tk[L, int((y - Y0) / h), int((x - X0) / h)]
for step in range(1, int(10 / dt) + 1):
    T = lu.solve(Cm / dt * T + Ptot)
    t = step * dt
    T3 = T.reshape(2, ny, nx)
    hist.append([t] + [float(max(at(T3, x, y, 0), at(T3, x, y, 1))) for x, y in watch.values()])
    if abs(t - 3) < 1e-6 or abs(t - 10) < 1e-6:
        snaps[f'{t:.0f}'] = T3.copy()
# solo cobre: cuánto calientan los cuellos por su propio efecto Joule (sin los drivers)
lu_ss = spl.splu(Gm.tocsc())
T_joule = lu_ss.solve(Pj.ravel()).reshape(2, ny, nx)
print('ΔT a 3 s / 10 s (K):')
for i, k in enumerate(watch):
    a3 = [hh for hh in hist if abs(hh[0] - 3) < 1e-6][0][i + 1]
    print(f'  {k}: {a3:.1f} / {hist[-1][i + 1]:.1f}')
x, y = watch['cuello VBAT (138,6; 98,5)']
print('solo Joule del cobre, régimen permanente: cuello VBAT', round(float(max(at(T_joule, x, y, 0), at(T_joule, x, y, 1))), 1),
      'K; máx placa', round(float(T_joule.max()), 1), 'K')
np.savez_compressed(f'{res}/termico.npz', hist=np.array(hist), names=np.array(list(watch)), T3=snaps['3'], T10=snaps['10'],
                    Tj=T_joule, X0=X0, Y0=Y0, h=h, board=board, Pj=Pj, Pc=Pc, comp=json.dumps({k: v[0] for k, v in comp.items()}))
