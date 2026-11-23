#!/usr/bin/env python3
"""Buck TPS563201 a 5,3 V: escalones de carga, batería baja, rizado de VBAT y arranque de la placa."""
import json
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import matplotlib.pyplot as plt
from comun import run, guardar, COL

R = {}
V = ['v(v5)', 'v(v5e)', 'v(v33)', 'i(v.xu2.vil)', 'v(xu2.hs)']


def medias(d, a, b):
    m = (d['t'] > a) & (d['t'] < b)
    hs = d['v(xu2.hs)'][m] > 0.5
    return {'V5': float(d['v(v5)'][m].mean()), 'rizado_V5_mVpp': float(np.ptp(d['v(v5)'][m]) * 1e3),
            'V5_ESP': float(d['v(v5e)'][m].mean()), 'V5_ESP_min': float(d['v(v5e)'][m].min()),
            'V33': float(d['v(v33)'][m].mean()), 'V33_min': float(d['v(v33)'][m].min()),
            'f_kHz': float(np.sum(np.diff(hs.astype(int)) == 1) / (b - a) / 1e3), 'IL_pico_A': float(d['i(v.xu2.vil)'][m].max())}


# ---------------------------------------------------------------- 1. escalón de carga a 8,4 V y 6,6 V
def escalon(vin):
    c = (f'.param TOFF=310n\n.include buck_base.inc\nVb vbat 0 {vin}\n'
         'Iload v33 0 PWL(0 0.15 2.5m 0.15 2.501m 0.56 3.3m 0.56 3.301m 0.15)\n')
    return vin, run(f'b1_{vin}', c, V, '.tran 10n 4m 0 10n uic')


with ThreadPoolExecutor(4) as ex:
    esc = dict(ex.map(escalon, [8.4, 6.6]))
fig, ax = plt.subplots(3, 1, figsize=(7.5, 6.5), sharex=True)
R['escalon'] = {}
for i, (vin, d) in enumerate(esc.items()):
    t = (d['t'] - 2.5e-3) * 1e6
    lab = f'VBAT {vin} V'.replace('.', ',')
    R['escalon'][str(vin)] = {'0,15 A': medias(d, 2.2e-3, 2.5e-3), '0,56 A': medias(d, 3.0e-3, 3.3e-3),
                              'V5_min_en_escalon': float(d['v(v5)'][(d['t'] > 2.5e-3) & (d['t'] < 2.7e-3)].min()),
                              'V33_min_en_escalon': float(d['v(v33)'][(d['t'] > 2.5e-3) & (d['t'] < 2.7e-3)].min())}
    ax[0].plot(t, d['v(v5)'], lw=0.7, label=lab, color=COL[i])
    ax[1].plot(t, d['v(v5e)'], lw=0.7, color=COL[i])
    ax[1].plot(t, d['v(v33)'], lw=0.9, color=COL[i], ls='--')
    ax[2].plot(t, d['i(v.xu2.vil)'], lw=0.5, color=COL[i])
ax[0].set_ylabel('+5V, salida del buck (V)'); ax[0].legend(fontsize=8); ax[0].set_ylim(5.1, 5.45)
ax[1].set_ylabel('pin 5V DevKit (—) y 3V3 (- -)'); ax[1].set_ylim(3.1, 5.2)
ax[2].set_ylabel('corriente en L1 (A)'); ax[2].set_xlabel('µs desde el escalón 0,15 → 0,56 A en 3V3')
ax[2].set_xlim(-200, 1000)
fig.suptitle('Buck a 5,3 V: escalón de carga del raíl de 3,3 V (0,15 → 0,56 → 0,15 A)', fontsize=10)
guardar(fig, '05_buck_escalon_carga.png')


# ---------------------------------------------------------------- 2. barrido de VBAT con carga máxima
def punto(args):
    vin, toff = args
    c = f'.param TOFF={toff}\n.include buck_base.inc\nVb vbat 0 {vin}\nIload v33 0 0.56\n'
    d = run(f'b2_{vin}_{toff}', c, V, '.tran 10n 2.2m 0 10n uic')
    return (vin, toff), medias(d, 1.8e-3, 2.2e-3)


vins = [8.4, 7.4, 6.6, 6.1, 5.8, 5.5, 5.2]
with ThreadPoolExecutor(4) as ex:
    pts = dict(ex.map(punto, [(v, t) for v in vins for t in ('310n', '220n')]))
R['barrido_vbat_0,56A'] = {f'{v} V, toff {t}': m for (v, t), m in pts.items()}
fig, ax = plt.subplots(figsize=(6.5, 3.6))
for toff, ls in (('310n', '-'), ('220n', '--')):
    nm = 'peor caso t_OFF 310 ns' if toff == '310n' else 't_OFF típico 220 ns'
    ax.plot(vins, [pts[(v, toff)]['V5'] for v in vins], ls, marker='o', ms=3, color=COL[0], label=f'+5V ({nm})')
    ax.plot(vins, [pts[(v, toff)]['V5_ESP'] for v in vins], ls, marker='o', ms=3, color=COL[1], label=f'pin 5V DevKit ({nm})')
    ax.plot(vins, [pts[(v, toff)]['V33'] for v in vins], ls, marker='o', ms=3, color=COL[2], label=f'3V3 ({nm})')
ax.axhline(3.3 * 0.95, color='k', lw=0.7, ls=':'); ax.text(5.25, 3.17, '3,3 V − 5 %', fontsize=7)
ax.axvspan(5.2, 6.4, color='#e4572e', alpha=0.06, lw=0); ax.text(5.25, 3.6, 'por debajo del corte\ndel firmware (6,4 V)', fontsize=7)
ax.set_xlabel('VBAT en la placa (V)'); ax.set_ylabel('V'); ax.legend(fontsize=6.5, loc='center right')
ax.set_title('Raíles con 0,56 A en 3V3 según la tensión de la batería (LDO tipo AMS1117)', fontsize=9)
guardar(fig, '06_buck_bateria_baja.png')

# ---------------------------------------------------------------- 3. VBAT baja con rizado de los motores
c = ('.param TOFF=310n\n.include buck_base.inc\nVb vbat 0 SIN(6.11 0.15 20k)\nIload v33 0 0.56\n')
d = run('b3', c, V, '.tran 10n 2.2m 0 10n uic')
R['vbat_6,11_con_rizado_300mVpp'] = medias(d, 1.8e-3, 2.2e-3)

# ---------------------------------------------------------------- 4. arranque de la placa al enchufar
c = ('.param TOFF=310n\n.include buck_base.inc\n'
     'Vbat bat 0 PWL(0 0 0.2m 0 0.20002m 8.4)\nRint bat vb1 40m\nLw vb1 vbat 100n\nCv vbat 0 68u\n'
     'Iload v33 0 PWL(0 0 0.1m 0)\nRld v33 0 22\n'   # ESP32 en reset + sensores ≈ 0,15 A a 3,3 V
     '* módulo ST4RT: R62 10 Ω + C62 10 µF (-> 6 µF); consumo supuesto 10 mA\n'
     'R62 v33 stvcc 10\nC62 stvcc 0 6u\nRst stvcc 0 330\n'
     '* DRV_EN: GPIO21 en alta impedancia mientras arranca el ESP32 -> R17 (100 k) a GND\n'
     'R17 drven 0 100k\n'
     '* KILL: el módulo no lo fuerza hasta que arranca (supuesto) -> R66 (100 k) a GND\n'
     'R66 kill 0 100k\n'
     '* U3 74LVC1G08: funciona desde 1,65 V\n'
     'Bu3 nsleep 0 V = V(v33)>1.65 ? (V(drven)>V(v33)/2 && V(kill)>V(v33)/2 ? V(v33) : 0) : 0\n')
d = run('b4', c, V + ['v(vbat)', 'v(en)', 'v(stvcc)', 'v(nsleep)', 'v(xu2.ss)'], '.tran 10n 3.5m 0 10n uic')
t = (d['t'] - 0.2e-3) * 1e3
fig, ax = plt.subplots(2, 1, figsize=(7.5, 5.5), sharex=True)
ax[0].plot(t, d['v(vbat)'], label='VBAT'); ax[0].plot(t, d['v(en)'], label='EN del buck')
ax[0].plot(t, d['v(v5)'], label='+5V'); ax[0].plot(t, d['v(v5e)'], label='pin 5V DevKit')
ax[0].plot(t, d['v(v33)'], label='3V3'); ax[0].plot(t, d['v(stvcc)'], label='alimentación ST4RT', ls='--')
ax[0].set_ylabel('V'); ax[0].legend(fontsize=7, ncol=3)
ax[1].plot(t, d['v(nsleep)'], color=COL[1], label='nSLEEP de los drivers (U3)')
ax[1].plot(t, d['i(v.xu2.vil)'], color=COL[2], lw=0.4, label='corriente en L1 (A)')
ax[1].set_ylim(-0.2, 3.5); ax[1].legend(fontsize=7); ax[1].set_xlabel('ms desde que se enchufa la batería')
fig.suptitle('Arranque de la placa: el buck sube en ~1 ms y los drivers siguen dormidos', fontsize=10)
guardar(fig, '07_arranque_placa.png')
m = d['t'] > 3.2e-3
cross = lambda v, lvl: float(t[np.argmax(d[v] > lvl)])
R['arranque'] = {'t_EN_ms': cross('v(en)', 1.2), 't_5V_al_90%_ms': cross('v(v5)', 0.9 * 5.3),
                 't_3V3_al_90%_ms': cross('v(v33)', 0.9 * 3.3), 'V5_max_V': float(d['v(v5)'].max()),
                 'nSLEEP_max_V': float(d['v(nsleep)'].max()), 'IL_pico_A': float(d['i(v.xu2.vil)'].max())}
json.dump(R, open('../resultados/buck.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(R, indent=1, ensure_ascii=False))
