#!/usr/bin/env python3
"""Gráficas de la simulación del firmware (sim_combate)."""
import json, os, sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
from comun import guardar, COL, TMP

D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(TMP, 'fw')
cols = ['t', 'x', 'y', 'th', 'start', 'kill', 'estado', 'modo', 'izq', 'der', 'nsleep', 'ox', 'oy']
lee = lambda n: dict(zip(cols, np.loadtxt(os.path.join(D, n), delimiter=',').T))

# ---------------------------------------------------------------- 1. arranque y parada
d = lee('fw_arranque_parada.csv')
fig, ax = plt.subplots(5, 1, figsize=(7, 5.8), sharex=True)
ax[0].step(d['t'], d['start'], where='post', color=COL[0]); ax[0].set_ylabel('START')
ax[1].step(d['t'], d['kill'], where='post', color=COL[1]); ax[1].set_ylabel('KILL')
ax[2].step(d['t'], d['nsleep'], where='post', color=COL[3]); ax[2].set_ylabel('nSLEEP')
ax[3].step(d['t'], d['estado'], where='post', color=COL[2]); ax[3].set_yticks([0, 1, 2], ['ESPERA', 'COMBATE', 'PARADO'])
v = np.r_[0, np.hypot(np.diff(d['x']), np.diff(d['y'])) / np.diff(d['t'])]
ax[4].plot(d['t'], v, color=COL[4]); ax[4].set_ylabel('m/s'); ax[4].set_xlabel('s')
ax[0].text(0.02, 0.5, 'setup() del ESP32: drivers dormidos', transform=ax[2].transAxes, fontsize=7)
for a in ax:
    a.axvline(1.0, color='#999', lw=0.6, ls='--'); a.axvline(1.6, color='#999', lw=0.6, ls='--')
fig.suptitle('Firmware: orden de inicio (1,0 s) y de parada (1,6 s) del módulo ST4RT', fontsize=10)
guardar(fig, '10_firmware_arranque_parada.png')


# ---------------------------------------------------------------- 2. trayectorias en el dohyo
def dohyo(a, titulo):
    a.add_patch(Circle((0, 0), 0.385, fc='white', ec='#999', zorder=0))   # franja blanca de 25 mm
    a.add_patch(Circle((0, 0), 0.36, color='#222', zorder=0))
    a.set_xlim(-0.42, 0.42); a.set_ylim(-0.42, 0.42); a.set_aspect('equal'); a.grid(False)
    a.set_xticks([]); a.set_yticks([]); a.set_title(titulo, fontsize=8)
    for sp in a.spines.values(): sp.set_visible(False)


fig, ax = plt.subplots(1, 3, figsize=(10, 3.6))
for a, (n, tit) in zip(ax, [('fw_bordes.csv', 'Dohyo vacío, 60 s (μ = 0,6; 8,4 V)'),
                             ('fw_rival_1.csv', 'Rival dando vueltas a 0,3 m/s'),
                             ('fw_esquiva.csv', 'Rival que esquiva junto al borde (μ = 0,6)')]):
    dohyo(a, tit)
    if not os.path.exists(os.path.join(D, n)):
        continue
    d = lee(n)
    a.plot(d['x'], d['y'], color=COL[4], lw=0.6, zorder=2)
    a.plot(d['x'][0], d['y'][0], 'o', color=COL[2], ms=4, zorder=3)
    a.plot(d['x'][-1], d['y'][-1], 's', color=COL[1], ms=4, zorder=3)
    if n != 'fw_bordes.csv':
        a.plot(d['ox'], d['oy'], color='#2a6fdb', lw=0.6, ls='--', zorder=2)
guardar(fig, '11_firmware_trayectorias.png')
r = json.load(open(os.path.join(D, 'firmware.json')))
json.dump(r, open(os.path.join(os.path.dirname(__file__), '..', 'resultados', 'firmware.json'), 'w'), indent=1, ensure_ascii=False)
