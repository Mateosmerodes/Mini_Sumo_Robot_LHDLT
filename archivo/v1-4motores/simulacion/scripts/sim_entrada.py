#!/usr/bin/env python3
"""Entrada de batería, Q1, F1, VBAT y los 4 drivers: enchufe, arranque, inversión, bloqueo y crucero."""
import json, sys
import numpy as np
import matplotlib.pyplot as plt
from comun import run, guardar, COL

R = {}
CTRL_IGUAL = '\n'.join([f'Bf{k} f{k} 0 V=V(f1)' for k in (2, 3, 4)] + [f'Br{k} r{k} 0 V=V(r1)' for k in (2, 3, 4)])


def base(vcell=8.4, rint='30m', lw='100n', tplug='0.1m', lock=0):
    return f'.param VCELL={vcell} RINT={rint} LW={lw} TPLUG={tplug} LOCK={lock}\n.include entrada_base.inc\n'


# ---------------------------------------------------------------- 1. maniobra completa a 8,4 V
c = base() + ('Vf f1 0 PWL(0 0 10m 0 10.001m 1 60m 1 60.001m 0)\n'
              'Vr r1 0 PWL(0 0 60m 0 60.001m 1 100m 1 100.001m 0)\n' + CTRL_IGUAL)
v = ['v(vbat)', 'v(vm8)', 'i(vbat)', 'v(x5.wr)', 'v(x5.wv)', 'i(v.x5.vsen)']
d = run('e1', c, v, '.tran 0.2u 130m 0 0.2u uic')
t = d['t'] * 1e3
ib = -d['i(vbat)']
w = lambda a, b: (t >= a) & (t < b)
R['maniobra'] = {
    'I_bat_max_A': float(ib[t > 5].max()), 'I_bat_min_A': float(ib[t > 5].min()),
    'VM8_min_V': float(d['v(vm8)'][t > 5].min()), 'VM8_max_V': float(d['v(vm8)'][t > 5].max()),
    'I_motor_max_arranque_A': float(np.abs(d['i(v.x5.vsen)'][w(10, 60)]).max()),
    'I_motor_max_inversion_A': float(np.abs(d['i(v.x5.vsen)'][w(60, 100)]).max()),
    'v_robot_60ms_m_s': float(d['v(x5.wv)'][w(59, 60)][-1] * 0.015),
}
fig, ax = plt.subplots(3, 1, figsize=(7.5, 7), sharex=True)
for a, b, txt in [(10, 60, 'adelante 100 %'), (60, 100, 'atrás 100 %'), (100, 130, 'freno')]:
    for x in ax:
        x.axvspan(a, b, color='#000', alpha=0.04 if txt != 'atrás 100 %' else 0.08, lw=0)
    ax[0].text((a + b) / 2, 8.5, txt, ha='center', fontsize=8)
ax[0].plot(t, d['v(vbat)'], label='VBAT (junto a F1)')
ax[0].plot(t, d['v(vm8)'], label='VM del driver U8 (el más lejano)', lw=0.8)
ax[0].set_ylim(7.5, 8.7); ax[0].set_ylabel('V'); ax[0].legend(loc='lower left', fontsize=8)
ax[1].plot(t, ib, color=COL[1], lw=0.6)
ax[1].axhline(15 * 0.75, color='k', ls='--', lw=0.8); ax[1].text(1, 11.5, 'fusible 15 A × 0,75', fontsize=8)
ax[1].set_ylabel('Corriente de batería (A)'); ax[1].set_ylim(-2, 13)
ax[2].plot(t, d['i(v.x5.vsen)'], color=COL[2], lw=0.6, label='corriente del motor 1 (A)')
ax[2].plot(t, d['v(x5.wv)'] * 0.015 * 4, color=COL[3], label='velocidad del robot × 4 (m/s)')
ax[2].axhline(2.44, color='k', ls=':', lw=0.8); ax[2].axhline(-2.44, color='k', ls=':', lw=0.8)
ax[2].text(1, -2.3, 'I_TRIP ±2,44 A', fontsize=8)
ax[2].legend(loc='upper right', fontsize=8); ax[2].set_xlabel('tiempo (ms)')
fig.suptitle('Arranque a fondo, inversión y freno con la batería llena (8,4 V)', fontsize=10)
guardar(fig, '01_maniobra_vbat.png')

# ---------------------------------------------------------------- 2. enchufe del XT30 (barrido)
c0 = 'Vf f1 0 0\nVr r1 0 0\n' + CTRL_IGUAL
filas = []
fig, ax = plt.subplots(1, 2, figsize=(8, 3.3))
for rint in ['10m', '30m', '50m']:
    for lw in ['50n', '100n', '300n', '1u']:
        d = run(f'e2_{rint}_{lw}', base(rint=rint, lw=lw, tplug='10u') + c0, ['v(vbat)', 'i(vbat)', 'v(q1g)', 'v(vrev)'],
                '.tran 5n 300u 0 5n uic')
        vmax, imax = float(d['v(vbat)'].max()), float(-d['i(vbat)'].min())
        filas.append({'R_int': rint, 'L_cables': lw, 'VBAT_max_V': round(vmax, 2), 'I_pico_A': round(imax, 1)})
        if rint == '10m' or (rint == '30m' and lw == '100n'):
            lab = 'R_int ' + rint.replace('m', ' mΩ') + ', L cables ' + lw.replace('n', ' nH').replace('u', ' µH')
            ax[0].plot((d['t'] - 10e-6) * 1e6, d['v(vbat)'], label=lab, lw=0.9)
            ax[1].plot((d['t'] - 10e-6) * 1e6, -d['i(vbat)'], lw=0.9)
ax[0].axhline(17, color='k', ls='--', lw=0.8); ax[0].text(150, 16.3, 'máx. recomendado TPS563201 (17 V)', fontsize=7)
ax[0].set_xlim(-5, 200); ax[0].set_ylabel('VBAT (V)'); ax[0].set_xlabel('µs desde el contacto'); ax[0].legend(fontsize=7)
ax[1].set_xlim(-2, 60); ax[1].set_ylabel('Corriente de batería (A)'); ax[1].set_xlabel('µs desde el contacto')
fig.suptitle('Enchufar la batería: sobretensión y pico de carga de los condensadores', fontsize=10)
guardar(fig, '02_enchufe_xt30.png')
R['enchufe'] = filas
# batería al revés
d = run('e2_inv', base(vcell=-8.4, tplug='10u') + c0, ['v(vbat)', 'i(vbat)', 'v(q1g)', 'v(vrev)'], '.tran 50n 2m 0 50n uic')
R['bateria_al_reves'] = {'VBAT_min_V': float(d['v(vbat)'].min()), 'I_max_mA': float(np.abs(d['i(vbat)'][d['t'] > 1e-3]).max() * 1e3)}

# ---------------------------------------------------------------- 3. 4 motores bloqueados (peor caso)
fig, ax = plt.subplots(1, 2, figsize=(8, 3.3))
R['bloqueo'] = {}
for vc in (8.4, 6.6):
    c = base(vcell=vc, lock=1) + 'Vf f1 0 PWL(0 0 2m 0 2.001m 1)\nVr r1 0 0\n' + CTRL_IGUAL
    d = run(f'e3_{vc}', c, ['v(vbat)', 'v(vm8)', 'i(vbat)', 'v(j1p)', 'v(vrev)', 'i(v.x5.vsen)'], '.tran 0.1u 8m 0 0.1u uic')
    t = d['t'] * 1e3; m = t > 5
    ib = -d['i(vbat)']
    pq1 = (d['v(j1p)'] - d['v(vrev)']) * ib
    R['bloqueo'][str(vc)] = {'I_bat_media_A': float(ib[m].mean()), 'I_bat_max_A': float(ib[m].max()),
                             'VM8_media_V': float(d['v(vm8)'][m].mean()), 'VM8_min_V': float(d['v(vm8)'][m].min()),
                             'P_Q1_media_W': float(pq1[m].mean()), 'I_motor_media_A': float(d['i(v.x5.vsen)'][m].mean())}
    ax[0].plot(t, d['v(vm8)'], label=f'batería {vc} V'.replace('.', ','), lw=0.7)
    ax[1].plot(t, ib, lw=0.5)
ax[0].set_ylabel('VM del driver U8 (V)'); ax[0].set_xlabel('ms'); ax[0].legend(fontsize=8); ax[0].set_xlim(1, 8)
ax[1].set_ylabel('Corriente de batería (A)'); ax[1].set_xlabel('ms'); ax[1].set_xlim(1, 8)
fig.suptitle('Los 4 motores bloqueados a fondo (el driver limita a 2,44 A cada uno)', fontsize=10)
guardar(fig, '03_bloqueo_4_motores.png')

# ---------------------------------------------------------------- 4. crucero con PWM (rizado en VBAT)
R['crucero'] = {}
fig, ax = plt.subplots(1, 2, figsize=(8, 3.3))
for duty in (0.5, 0.65):
    c = base(vcell=7.4, lock=1) + f'Vf f1 0 PULSE(0 1 1m 10n 10n {duty * 50e-6} 50u)\nVr r1 0 0\n' + CTRL_IGUAL
    d = run(f'e4_{duty}', c, ['v(vbat)', 'v(vm8)', 'v(c1e)', 'i(vbat)'], '.tran 20n 6m 0 20n uic')
    t = d['t'] * 1e3; m = t > 5
    ic1 = d['v(c1e)'] / 5e-3
    R['crucero'][str(duty)] = {'rizado_VM8_mVpp': float(np.ptp(d['v(vm8)'][m]) * 1e3), 'I_rms_C1_A': float(np.sqrt(np.mean(ic1[m] ** 2))),
                               'I_bat_media_A': float(-d['i(vbat)'][m].mean())}
    if duty == 0.65:
        ax[0].plot((t - 5) * 1e3, d['v(vm8)'], lw=0.8, label='VM de U8'); ax[0].plot((t - 5) * 1e3, d['v(vbat)'], lw=0.8, label='VBAT')
        ax[1].plot((t - 5) * 1e3, ic1, lw=0.8, color=COL[2])
ax[0].set_xlim(0, 150); ax[0].set_xlabel('µs'); ax[0].set_ylabel('V'); ax[0].legend(fontsize=8)
ax[1].set_xlim(0, 150); ax[1].set_xlabel('µs'); ax[1].set_ylabel('Corriente en C1 (A)')
fig.suptitle('PWM al 65 % a 20 kHz, los 4 drivers en fase, motores frenados (peor caso de rizado)', fontsize=10)
guardar(fig, '04_rizado_pwm.png')

json.dump(R, open('../resultados/entrada.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(R, indent=1, ensure_ascii=False))
