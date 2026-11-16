#!/usr/bin/env python3
"""Mapas de densidad de corriente (VBAT y GND) y calentamiento de la placa."""
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from comun import guardar

RES = '../resultados'
fig, ax = plt.subplots(2, 2, figsize=(9, 7.4))
for i, net in enumerate(('VBAT', 'GND')):
    d = np.load(f'{RES}/cobre_{net}.npz')
    J, X0, Y0, h, mask = d['J'], float(d['X0']), float(d['Y0']), float(d['h']), d['mask']
    ny, nx = J.shape[1:]
    ext = [X0, X0 + nx * h, Y0 + ny * h, Y0]
    for k, L in enumerate(('F.Cu (cara superior)', 'B.Cu (cara inferior)')):
        a = ax[i, k]
        a.imshow(np.where(mask[k], 0.5, np.nan), extent=ext, cmap='Greys', vmin=0, vmax=1, alpha=0.25)
        im = a.imshow(np.where(mask[k], J[k] + 0.01, np.nan), extent=ext, norm=LogNorm(1, 300), cmap='inferno')
        a.set_title(f'{net} · {L}', fontsize=9); a.set_xticks([]); a.set_yticks([])
fig.colorbar(im, ax=ax, shrink=0.6, label='densidad de corriente (A/mm²)')
fig.suptitle('Corriente en el cobre con los 4 motores a 2,44 A (9,8 A en total)', fontsize=10)
fig.savefig('../graficas/12_cobre_densidad_corriente.png', dpi=150, bbox_inches='tight'); plt.close(fig)

t = np.load(f'{RES}/termico.npz')
hist, names = t['hist'], [str(n) for n in t['names']]
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw={'width_ratios': [1.1, 1]})
for j, n in enumerate(names):
    ax[0].plot(hist[:, 0], 25 + hist[:, j + 1], label=n, ls='-' if j < 4 else '--')
ax[0].axvline(3, color='#999', lw=0.7, ls=':'); ax[0].text(3.1, 30, '3 s de empuje', fontsize=7)
ax[0].set_xlabel('s con los 4 motores bloqueados'); ax[0].set_ylabel('temperatura de la placa (°C), aire a 25 °C')
ax[0].legend(fontsize=6.5); ax[0].set_title('Calentamiento en el peor caso (sin caja ni viento)', fontsize=9)
T3, X0, Y0, h, board = t['T3'], float(t['X0']), float(t['Y0']), float(t['h']), t['board']
ny, nx = T3.shape[1:]
im = ax[1].imshow(np.where(board, 25 + T3.max(0), np.nan), extent=[X0, X0 + nx * h, Y0 + ny * h, Y0], cmap='magma')
fig.colorbar(im, ax=ax[1], label='°C'); ax[1].set_xticks([]); ax[1].set_yticks([])
ax[1].set_title('Mapa de temperatura a los 3 s', fontsize=9)
guardar(fig, '13_termico_placa.png')
