#!/usr/bin/env python3
"""Medidas analógicas: divisor VBAT_SENSE (R3/R4/C3) y lectura de corriente IPROPI (R20/C20)."""
import json
import numpy as np
import matplotlib.pyplot as plt
from comun import run, guardar, COL

R = {}
rng = np.random.default_rng(1)
# ---------------------------------------------------------------- 1. VBAT_SENSE en el tiempo
# VBAT de prueba: 8,0 V; a los 20 ms arrancan los motores (caída de 0,6 V que se recupera en 30 ms)
# y queda un rizado de 300 mVpp a 20 kHz por el PWM.
c = ('Vb vb 0 PWL(0 8.0 20m 8.0 20.05m 7.4 50m 7.85 80m 7.85)\n'
     'Br vbat 0 V = V(vb) + (time>20m ? 0.15*sin(2*3.14159*20k*time) : 0)\n'
     'R3 vbat s 100k\nR4 s 0 33k\nC3 s 0 100n\n'
     '* entrada del ADC del ESP32-S3: condensador de muestreo (~2 pF supuesto) que se carga cada 10 µs\n'
     'Ssm s cs smp 0 SWS\nCsm cs 0 2p\nRdis cs 0 1e9\nVsmp smp 0 PULSE(0 1 0 1n 1n 0.5u 10u)\n'
     '.model SWS sw(vt=0.5 vh=0.1 ron=1k roff=1e12)\n')
d = run('s1', c, ['v(vbat)', 'v(s)'], '.tran 1u 80m 0 1u')
t = d['t'] * 1e3
lect = d['v(s)'] * 133 / 33
fig, ax = plt.subplots(figsize=(7, 3.4))
ax.plot(t, d['v(vbat)'], lw=0.3, color='#bbbbbb', label='VBAT real (con rizado del PWM)')
ax.plot(t, lect, color=COL[0], label='lo que lee el firmware: V(VBAT_SENSE) × 133/33')
ax.set_xlabel('ms'); ax.set_ylabel('V'); ax.legend(fontsize=8)
ax.set_title('Divisor VBAT_SENSE: el filtro (τ = 2,5 ms) quita el rizado de 20 kHz', fontsize=9)
guardar(fig, '08_vbat_sense.png')
m = t > 70
R['vbat_sense'] = {'tau_ms': 100e3 * 33e3 / 133e3 * 100e-9 * 1e3, 'fc_Hz': 1 / (2 * np.pi * 24.8e3 * 100e-9),
                   'rizado_restante_mVpp_en_VBAT': float(np.ptp(lect[m]) * 1e3),
                   'retardo_al_63pc_ms': float(t[(t > 20) & (lect < 8.0 - 0.63 * (8.0 - 7.45))][0] - 20) if np.any((t > 20) & (lect < 7.65)) else None,
                   'V_SENSE_a_8,4V': 8.4 * 33 / 133, 'V_SENSE_a_6,4V': 6.4 * 33 / 133}
# tolerancias: resistencias al 1 % y error del ADC calibrado (±10 mV supuesto, analogReadMilliVolts)
N = 20000
r3 = 100e3 * (1 + rng.uniform(-0.01, 0.01, N)); r4 = 33e3 * (1 + rng.uniform(-0.01, 0.01, N))
for vb in (6.4, 7.4, 8.4):
    vs = vb * r4 / (r3 + r4) + rng.uniform(-0.010, 0.010, N)
    err = vs * 133 / 33 - vb
    R['vbat_sense'][f'error_lectura_{vb}V_mV_p99'] = float(np.percentile(np.abs(err), 99) * 1e3)

# ---------------------------------------------------------------- 2. IPROPI con PWM
# El DRV8874 da en IPROPI 455 µA por amperio que pasa por sus transistores ALTOS. En el modo del
# firmware (IN1 = 1, IN2 = PWM) el tiempo "apagado" es freno por los transistores bajos: ahí IPROPI = 0.
fig, ax = plt.subplots(1, 2, figsize=(8.5, 3.4))
R['ipropi'] = {}
for i, duty in enumerate((0.45, 0.65, 1.0)):
    c = (f'Vp hs 0 PULSE(0 1 0 20n 20n {duty * 50e-6 if duty < 1 else 1} 50u)\n'
         'Bi 0 ip I = 455e-6*1.5*V(hs)\nR20 ip 0 1.5k\nC20 ip 0 10n\n')
    d = run(f's2_{duty}', c, ['v(ip)'], '.tran 50n 1m 0 50n')
    t = d['t']; m = t > 0.5e-3
    v = d['v(ip)'][m]
    lect = v / (455e-6 * 1500)
    R['ipropi'][str(duty)] = {'I_real_A': 1.5, 'lectura_media_A': float(lect.mean()), 'lectura_min_A': float(lect.min()),
                              'lectura_max_A': float(lect.max())}
    if duty < 1:
        ax[0].plot((t[m] - 0.5e-3) * 1e6, lect, lw=1, color=COL[i], label=f'PWM {duty * 100:.0f} %')
ax[0].axhline(1.5, color='k', ls='--', lw=0.8); ax[0].text(3, 1.53, 'corriente real del motor: 1,5 A', fontsize=7)
ax[0].axhline(1.4, color=COL[1], ls=':', lw=0.8); ax[0].text(3, 1.32, 'umbral de "contacto" del firmware 1,4 A', fontsize=7)
ax[0].set_xlim(0, 150); ax[0].set_ylim(0, 1.7); ax[0].set_xlabel('µs'); ax[0].set_ylabel('corriente leída (A)')
ax[0].legend(fontsize=7, loc='lower right'); ax[0].set_title('Lectura de IPROPI con PWM', fontsize=9)
# retraso del límite de corriente por C20 (rampa de corriente del motor bloqueado: 8,4 V / 0,5 mH)
c = ('Bi 0 ip I = 455e-6*min(16.8e3*time, 3)\nR20 ip 0 1.5k\nC20 ip 0 10n\n')
d = run('s3', c, ['v(ip)'], '.tran 10n 200u')
t = d['t'] * 1e6
ireal = np.minimum(16.8e3 * d['t'], 3)
vref = 1.65
k = np.argmax(d['v(ip)'] > vref)
R['ipropi']['I_real_al_disparar_A'] = float(ireal[k]); R['ipropi']['retraso_us'] = float(t[k] - 2.44 / 16.8e3 * 1e6)
ax[1].plot(t, ireal, color='#999', label='corriente real')
ax[1].plot(t, d['v(ip)'] / (455e-6 * 1500), color=COL[0], label='IPROPI (en amperios)')
ax[1].axhline(2.44, color='k', ls=':', lw=0.8)
ax[1].axvline(t[k], color=COL[1], lw=0.8); ax[1].text(t[k] + 3, 1.7, f'dispara con\n{ireal[k]:.2f} A'.replace('.', ','), fontsize=7)
ax[1].set_xlim(100, 200); ax[1].set_ylim(1.5, 3.1); ax[1].set_xlabel('µs'); ax[1].legend(fontsize=7, loc='upper left')
ax[1].set_title('Retraso del límite I_TRIP por el filtro de 15 µs', fontsize=9)
guardar(fig, '09_ipropi.png')
json.dump(R, open('../resultados/sensado.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(R, indent=1, ensure_ascii=False))
