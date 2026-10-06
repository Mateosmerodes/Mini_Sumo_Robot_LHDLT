"""Renderiza vistas del modelo 3D (montado y despiece) a PNG con matplotlib.

Uso:  python3 hardware/mecanica/cad/render.py   (después de freecadcmd robot.py)
Lee las mallas de _render/ e informe_3d.json; escribe en docs/img/.
"""
import json
import os
import struct

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt                                # noqa: E402
import numpy as np                                             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RENDER = os.path.join(HERE, '_render')
IMG = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'docs', 'img'))

# Desplazamiento de cada grupo en el despiece (X, Y, Z) en mm; Y del modelo = hacia delante
DESPIECE = {
    'carcasa': (0, 0, 38), 'techo': (0, 0, 62), 'bateria': (0, 0, 92), 'pcb': (0, 0, 18), 'frontal': (0, 28, -6),
    'trasera': (0, -28, -6), 'lastre': (0, 0, -32), 'motores': (0, 0, 0), 'ruedas': (0, 0, 0),
}
DESPIECE_RUEDA_X = 16


def leer_stl(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:5] == b'solid' and b'facet' in data[:300]:
        tri = []
        for line in data.decode(errors='ignore').splitlines():
            line = line.strip()
            if line.startswith('vertex'):
                tri.append([float(v) for v in line.split()[1:4]])
        return np.array(tri).reshape(-1, 3, 3)
    n = struct.unpack('<I', data[80:84])[0]
    arr = np.frombuffer(data[84:84 + n * 50], dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')]))
    return arr['v'].reshape(-1, 3, 3).astype(float)


def sombrear(tris, color, luz=np.array([0.4, 0.6, 0.9])):
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    norm = np.linalg.norm(n, axis=1, keepdims=True)
    norm[norm == 0] = 1
    n = n / norm
    luz = luz / np.linalg.norm(luz)
    k = 0.45 + 0.55 * np.abs(n @ luz)
    return np.clip(np.outer(k, color), 0, 1)


def escena(info, despiece=False):
    tris, cols = [], []
    for nombre, meta in info['piezas'].items():
        path = os.path.join(RENDER, nombre + '.stl')
        if not os.path.exists(path):
            continue
        t = leer_stl(path)
        if despiece:
            dx, dy, dz = DESPIECE.get(meta['grupo'], (0, 0, 0))
            if meta['grupo'] == 'ruedas':
                dx = -DESPIECE_RUEDA_X if '_izq_' in nombre else DESPIECE_RUEDA_X
            t = t + np.array([dx, dy, dz])
        tris.append(t)
        cols.append(sombrear(t, np.array(meta['color'])))
    return np.concatenate(tris), np.concatenate(cols)


def rasterizar(tris, cols, elev, azim, w=1400, h=1100, zoom=1.0):
    """Proyección ortográfica + z-buffer (numpy). Devuelve una imagen RGB."""
    e, a = np.radians(elev), np.radians(azim)
    # cámara: mira hacia el centro desde (azim, elev), Z arriba
    d = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])   # hacia la cámara
    right = np.cross([0, 0, 1], d)
    if np.linalg.norm(right) < 1e-6:
        right = np.array([np.cos(a + np.pi / 2), np.sin(a + np.pi / 2), 0.0])
    right /= np.linalg.norm(right)
    up = np.cross(d, right)
    pts = tris.reshape(-1, 3)
    c = (pts.min(0) + pts.max(0)) / 2
    P = (pts - c) @ np.stack([right, up, d]).T
    span = max(np.ptp(P[:, 0]) / w, np.ptp(P[:, 1]) / h) * 1.08 / zoom
    sx = P[:, 0] / span + w / 2
    sy = h / 2 - P[:, 1] / span
    sz = P[:, 2]
    S = np.stack([sx, sy, sz], 1).reshape(-1, 3, 3)
    img = np.ones((h, w, 3))
    zb = np.full((h, w), -np.inf)
    for t, col in zip(S, cols):
        x0, x1 = int(max(0, np.floor(t[:, 0].min()))), int(min(w - 1, np.ceil(t[:, 0].max())))
        y0, y1 = int(max(0, np.floor(t[:, 1].min()))), int(min(h - 1, np.ceil(t[:, 1].max())))
        if x1 < x0 or y1 < y0:
            continue
        (ax_, ay, az), (bx, by, bz), (cx_, cy, cz) = t
        den = (by - cy) * (ax_ - cx_) + (cx_ - bx) * (ay - cy)
        if abs(den) < 1e-9:
            continue
        X, Y = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        l1 = ((by - cy) * (X - cx_) + (cx_ - bx) * (Y - cy)) / den
        l2 = ((cy - ay) * (X - cx_) + (ax_ - cx_) * (Y - cy)) / den
        l3 = 1 - l1 - l2
        m = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        if not m.any():
            continue
        z = l1 * az + l2 * bz + l3 * cz
        sub = zb[y0:y1 + 1, x0:x1 + 1]
        m &= z > sub + 1e-4
        sub[m] = z[m]
        img[y0:y1 + 1, x0:x1 + 1][m] = col
    # contornos suaves donde salta la profundidad (mejor lectura de las piezas)
    zf = np.where(np.isfinite(zb), zb, zb[np.isfinite(zb)].min() - 50 if np.isfinite(zb).any() else 0)
    gy, gx = np.gradient(zf)
    edge = np.hypot(gx, gy) > 0.8 + 3.0 * span      # salto de profundidad, no pendiente de una cara
    img[edge] *= 0.25
    return img


def dibujar(tris, cols, elev, azim, nombre, titulo, zoom=1.0):
    img = rasterizar(tris, cols, elev, azim, zoom=zoom)
    fig = plt.figure(figsize=(9.6, 7.9), dpi=150)
    ax = fig.add_axes([0, 0, 1, 0.93])
    ax.imshow(img, interpolation='lanczos')
    ax.set_axis_off()
    fig.suptitle(titulo, fontsize=13, y=0.97)
    out = os.path.join(IMG, nombre)
    fig.savefig(out, facecolor='white')
    plt.close(fig)
    print('escrito', os.path.relpath(out))


def main():
    os.makedirs(IMG, exist_ok=True)
    with open(os.path.join(HERE, 'informe_3d.json')) as f:
        info = json.load(f)
    t, c = escena(info)
    m = info['masa_total_g']
    dibujar(t, c, 24, 128, '3d_montado.png', f'Robot mini-sumo · montado ({m:.0f} g estimados)', 1.0)
    dibujar(t, c, 0, 90, '3d_frontal.png', 'Vista frontal', 1.0)
    dibujar(t, c, 0, 180, '3d_lateral.png', 'Vista lateral izquierda (delante a la izquierda)', 1.0)
    dibujar(t, c, 90, -90, '3d_planta.png', 'Planta', 1.0)
    t, c = escena(info, despiece=True)
    dibujar(t, c, 20, 128, '3d_despiece.png', 'Despiece', 1.05)
    dibujar(t, c, 20, -52, '3d_despiece_trasera.png', 'Despiece (desde atrás)', 1.05)


if __name__ == '__main__':
    main()
