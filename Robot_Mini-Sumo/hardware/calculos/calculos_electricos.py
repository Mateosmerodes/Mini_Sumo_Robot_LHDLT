"""Cálculos eléctricos y mecánicos del robot (los de la ficha técnica y algunos más).

Uso:   python3 hardware/calculos/calculos_electricos.py
Genera:
    hardware/calculos/resultados.json        todos los resultados numéricos
    docs/img/calc_autonomia.png               autonomía frente a % de tiempo empujando
    docs/img/calc_consumo_3v3.png             reparto del consumo del raíl de 3,3 V
Explicación de cada cálculo: docs/Informe-consumos-y-calculos.md

Todos los datos de entrada están en DATOS, con su fuente. Los marcados "estimado" o "a medir"
se cambian aquí cuando lleguen las piezas y se vuelve a ejecutar.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
HW = os.path.normpath(os.path.join(HERE, '..'))
IMG = os.path.normpath(os.path.join(HW, '..', 'docs', 'img'))

# ------------------------------------------------------------------ datos de entrada
DATOS = {
    # Batería LiPo 2S (genérica, sin hoja oficial)
    'bat_celdas': 2, 'bat_v_celda_nom': 3.7, 'bat_v_celda_max': 4.2, 'bat_v_celda_min': 3.3,
    'bat_capacidades_mAh': [450, 650], 'bat_C': 30,
    'bat_r_interna_ohm': 0.030,          # estimado para un 2S 450 mAh 30 C (≈ 15 mΩ por celda)
    'bat_fraccion_util': 0.8,            # no bajar de 3,3 V por celda
    # Motores N20 6 V ~500 rpm (genéricos). Referencia: Pololu HP 6 V, 1,6 A de bloqueo a 6 V
    'mot_n': 4, 'mot_v_nom': 6.0, 'mot_i_stall_6v': 1.6,   # a medir
    'mot_i_stall_variantes_6v': [0.7, 1.0, 1.6, 2.0],       # para el análisis de sensibilidad
    'mot_rpm_6v': 500, 'mot_i_maniobra': 0.4,               # estimado: marcha con aceleraciones
    'mot_pwm_crucero': 0.75,
    # DRV8874 (TI)
    'drv_a_ipropi': 450e-6,              # A/A, tabla de características eléctricas
    'drv_r_ipropi': 1500.0, 'drv_vref_r_alta': 10e3, 'drv_vref_r_baja': 10e3,
    'drv_rdson_total': 0.200,            # Ω, lado alto + lado bajo
    'drv_i_vm_activo': 3e-3,             # A, VM activo con salidas paradas (típ. a 24 V)
    'drv_i_cont': 2.1, 'drv_i_pico': 6.0,
    'drv_rth_ja': (30.0, 40.0),          # °C/W, rango según el cobre de la placa (orientativo)
    # Electrónica de 3,3 V (típica, pico) en A
    'c_esp32': (0.100, 0.350),           # ESP32-S3: pico 350 mA en TX 802.11b
    'c_vl53l0x': (0.019, 0.019), 'n_vl53l0x': 6,
    'c_qre_v_led': 1.2, 'c_qre_r_led': 100.0, 'n_qre': 4,   # LED IR con 100 Ω en el módulo
    'c_ir': (0.00045, 0.00045),          # TSOP38238: 0,45 mA
    'c_led_pwr_v': 2.0, 'c_led_pwr_r': 1000.0,
    'c_varios': (0.003, 0.005),          # pull-ups, divisores, reguladores de los módulos ToF
    'v33': 3.3,
    # Cadena de alimentación
    'buck_vfb': 0.768, 'buck_vfb_min': 0.749, 'buck_vfb_max': 0.787,
    'buck_r_alta': 62e3, 'buck_r_baja': 10e3, 'buck_eta': 0.90, 'buck_f': 580e3, 'buck_l': 3.3e-6,
    'diodo_vf': (0.40, 0.55),            # SS34 a 0,3 A … 3 A
    'ldo_dropout_ams1117': 1.1,          # caso desfavorable (clones con AMS1117)
    'q1_rdson': 0.015, 'fusible_r': 0.005, 'xt30_r': 0.0012,
    'fusible_a': 10.0, 'xt30_a': 15.0,
    'div_r_alta': 100e3, 'div_r_baja': 33e3, 'div_c': 100e-9,
    'adc_fondo': 3.1, 'adc_bits': 12,    # ESP32-S3 con atenuación de 11/12 dB
    'ipropi_c': 10e-9, 'pwm_f': 20e3,
    'i2c_r_pullup': 2200.0, 'i2c_c_bus': 150e-12,          # 6 módulos + cables (estimado)
    # Mecánica
    'masa_objetivo_g': 495, 'mu': (0.8, 1.0), 'g': 9.81, 'rueda_d': 0.030, 'dohyo_d': 0.77,
    'borde_blanco': 0.025,
    'perfil_empuje': 0.40,               # fracción del combate empujando
}


def calcular(d):
    r = {}
    # ---------------------------------------------------------- batería
    vnom = d['bat_celdas'] * d['bat_v_celda_nom']
    vmax = d['bat_celdas'] * d['bat_v_celda_max']
    vmin = d['bat_celdas'] * d['bat_v_celda_min']
    r['bat'] = {'v_nom': vnom, 'v_max': vmax, 'v_min': vmin,
                'energia_Wh': {c: vnom * c / 1000 for c in d['bat_capacidades_mAh']},
                'i_max_A': {c: c / 1000 * d['bat_C'] for c in d['bat_capacidades_mAh']}}

    # ---------------------------------------------------------- motores y drivers
    r_mot = d['mot_v_nom'] / d['mot_i_stall_6v']
    vref = 3.3 * d['drv_vref_r_baja'] / (d['drv_vref_r_alta'] + d['drv_vref_r_baja'])
    itrip = vref / (d['drv_a_ipropi'] * d['drv_r_ipropi'])
    i_st = {v: v / r_mot for v in (d['mot_v_nom'], vnom, vmax)}
    p_cobre = {v: v * i for v, i in i_st.items()}
    i_lim = min(i_st[vmax], itrip)
    p_drv = i_lim ** 2 * d['drv_rdson_total']
    v_crucero = d['mot_pwm_crucero'] * vmax
    r['motor'] = {
        'r_bobinado': r_mot, 'i_stall': i_st, 'p_bloqueo_W': p_cobre,
        'i_stall_crucero_A': v_crucero / r_mot, 'p_bloqueo_crucero_W': v_crucero ** 2 / r_mot,
        'sobretension': vmax / d['mot_v_nom'],
        'rpm': {v: d['mot_rpm_6v'] * v / d['mot_v_nom'] for v in (d['mot_v_nom'], vnom, vmax)},
    }
    r['driver'] = {
        'vref': vref, 'itrip': itrip, 'margen_itrip_sobre_stall': itrip / i_st[vmax] - 1,
        'p_conduccion_W': p_drv,
        'dT_C': [p_drv * rt for rt in d['drv_rth_ja']],
        'v_ipropi_por_A': d['drv_a_ipropi'] * d['drv_r_ipropi'],
        'v_ipropi_stall': i_lim * d['drv_a_ipropi'] * d['drv_r_ipropi'],
        'ipropi_fc_Hz': 1 / (2 * math.pi * d['drv_r_ipropi'] * d['ipropi_c']),
        'ipropi_atenuacion_pwm_dB': -10 * math.log10(
            1 + (d['pwm_f'] * 2 * math.pi * d['drv_r_ipropi'] * d['ipropi_c']) ** 2),
    }
    lsb = d['adc_fondo'] / 2 ** d['adc_bits']
    r['driver']['resolucion_corriente_mA'] = lsb / r['driver']['v_ipropi_por_A'] * 1000

    # ---------------------------------------------------------- electrónica de 3,3 V
    i_qre = (d['v33'] - d['c_qre_v_led']) / d['c_qre_r_led']
    i_led = (d['v33'] - d['c_led_pwr_v']) / d['c_led_pwr_r']
    cargas = {
        'ESP32-S3 (DevKitC-1)': d['c_esp32'],
        f"{d['n_vl53l0x']} × VL53L0X": tuple(d['n_vl53l0x'] * x for x in d['c_vl53l0x']),
        f"{d['n_qre']} × QRE1113": (d['n_qre'] * i_qre,) * 2,
        'Receptor IR': d['c_ir'],
        'LED de alimentación': (i_led, i_led),
        'Pull-ups, divisores, otros': d['c_varios'],
    }
    i33 = [sum(v[k] for v in cargas.values()) for k in (0, 1)]
    vbuck = d['buck_vfb'] * (1 + d['buck_r_alta'] / d['buck_r_baja'])
    vbuck_rango = [d['buck_vfb_min'] * (1 + d['buck_r_alta'] / d['buck_r_baja']),
                   d['buck_vfb_max'] * (1 + d['buck_r_alta'] / d['buck_r_baja'])]
    v5 = [vbuck - d['diodo_vf'][1], vbuck - d['diodo_vf'][0]]
    v5esp = [vbuck - 2 * d['diodo_vf'][1], vbuck - 2 * d['diodo_vf'][0]]
    p_bat_elec = [vbuck * i / d['buck_eta'] for i in i33]
    r['3v3'] = {
        'cargas_A': cargas, 'i_qre_A': i_qre, 'i_led_A': i_led, 'total_A': i33,
        'p_W': [d['v33'] * i for i in i33],
        'ldo_p_W': [(v5esp[1] - d['v33']) * i33[0], (v5esp[1] - d['v33']) * i33[1]],
        'ldo_margen_V_ams1117': v5esp[0] - d['v33'] - d['ldo_dropout_ams1117'],
    }
    r['alim'] = {
        'v_buck': vbuck, 'v_buck_rango': vbuck_rango, 'v_5V': v5, 'v_pin5V_devkit': v5esp,
        'ciclo_trabajo': {v: vbuck / v for v in (vmin, vnom, vmax)},
        'rizado_L_App': {v: (v - vbuck) * (vbuck / v) / (d['buck_l'] * d['buck_f'])
                         for v in (vnom, vmax)},
        'p_bat_electronica_W': p_bat_elec, 'i_bat_electronica_A': [p / vnom for p in p_bat_elec],
        'div_v_adc': {v: v * d['div_r_baja'] / (d['div_r_alta'] + d['div_r_baja']) for v in (vmin, vnom, vmax)},
        'div_i_uA': vmax / (d['div_r_alta'] + d['div_r_baja']) * 1e6,
        'div_tau_ms': (d['div_r_alta'] * d['div_r_baja'] / (d['div_r_alta'] + d['div_r_baja'])) * d['div_c'] * 1e3,
        'div_resolucion_mV': lsb * (d['div_r_alta'] + d['div_r_baja']) / d['div_r_baja'] * 1000,
    }

    # ---------------------------------------------------------- potencia máxima y protecciones
    p_mot_max = d['mot_n'] * vmax * i_lim
    p_mot_nom = d['mot_n'] * vnom * min(i_st[vnom], itrip)
    i_bat_pico = p_mot_max / vmax + p_bat_elec[1] / vmax
    r_serie = d['q1_rdson'] + d['fusible_r'] + 2 * d['xt30_r']
    r['potencia'] = {
        'p_motores_max_W': p_mot_max, 'p_total_max_W': p_mot_max + p_bat_elec[1],
        'p_total_nom_W': p_mot_nom + p_bat_elec[1], 'i_bat_pico_A': i_bat_pico,
        'C_minimo': {c: i_bat_pico / (c / 1000) for c in d['bat_capacidades_mAh']},
        'margen_fusible': d['fusible_a'] / i_bat_pico - 1, 'margen_xt30': d['xt30_a'] / i_bat_pico - 1,
        'caida_bateria_V': i_bat_pico * d['bat_r_interna_ohm'],
        'caida_serie_V': i_bat_pico * r_serie, 'p_q1_pico_W': i_bat_pico ** 2 * d['q1_rdson'],
        'v_motor_real_V': vmax - i_bat_pico * (d['bat_r_interna_ohm'] + r_serie),
    }

    # ---------------------------------------------------------- autonomía
    i_e = r['alim']['i_bat_electronica_A'][0]

    def i_media(f_emp, i_st6=d['mot_i_stall_6v']):
        ist = min(vnom / (d['mot_v_nom'] / i_st6), itrip)
        return f_emp * d['mot_n'] * ist + (1 - f_emp) * d['mot_n'] * d['mot_i_maniobra'] + i_e

    def minutos(cap, i):
        return d['bat_fraccion_util'] * cap / (i * 1000) * 60

    escenarios = {'Empujando todo el tiempo': 1.0, 'Combate típico (40 % empujando)': d['perfil_empuje'],
                  'Solo buscando': 0.0}
    r['autonomia'] = {
        'escenarios': {n: {'i_A': i_media(f), **{f'{c} mAh': minutos(c, i_media(f))
                                                    for c in d['bat_capacidades_mAh']}}
                       for n, f in escenarios.items()},
        'sensibilidad_stall': {s: minutos(450, i_media(d['perfil_empuje'], s))
                               for s in d['mot_i_stall_variantes_6v']},
        'carga_1C_min': 60,              # a 1 C, ≈ 1 h desde vacía (CC-CV)
    }

    # ---------------------------------------------------------- mecánica
    m = d['masa_objetivo_g'] / 1000
    f_trac = [mu * m * d['g'] for mu in d['mu']]
    v_lin = {v: rpm * math.pi * d['rueda_d'] / 60 for v, rpm in r['motor']['rpm'].items()}
    r['mecanica'] = {
        'f_traccion_N': f_trac, 'f_por_rueda_N': [f / 4 for f in f_trac],
        'par_por_rueda_Nm': [f / 4 * d['rueda_d'] / 2 for f in f_trac],
        'par_por_rueda_kgcm': [f / 4 * d['rueda_d'] / 2 / d['g'] * 100 for f in f_trac],
        'v_m_s': v_lin, 't_cruzar_dohyo_s': {v: d['dohyo_d'] / s for v, s in v_lin.items()},
        't_borde_ms': {v: d['borde_blanco'] / s * 1000 for v, s in v_lin.items()},
        'i2c_t_subida_ns': 0.8473 * d['i2c_r_pullup'] * d['i2c_c_bus'] * 1e9,
        'i2c_i_sumidero_mA': d['v33'] / d['i2c_r_pullup'] * 1000,
    }
    return r, i_media, minutos


# ------------------------------------------------------------------ gráficas
AZUL, NARANJA, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
TXT, TXT2, REJ, FONDO = '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'


def estilo(ax):
    ax.set_facecolor(FONDO)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(REJ)
    ax.tick_params(colors=TXT2, labelsize=9)
    ax.grid(True, color=REJ, linewidth=0.6)
    ax.set_axisbelow(True)


def graficas(d, r, i_media, minutos):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    os.makedirs(IMG, exist_ok=True)

    # 1) Autonomía frente al % de tiempo empujando
    fig, ax = plt.subplots(figsize=(8, 4.6), dpi=150, facecolor=FONDO)
    estilo(ax)
    fs = [i / 100 for i in range(0, 101, 2)]
    series = [(450, d['mot_i_stall_6v'], AZUL, '450 mAh'), (650, d['mot_i_stall_6v'], NARANJA, '650 mAh')]
    for cap, st, col, lab in series:
        ys = [minutos(cap, i_media(f, st)) for f in fs]
        ax.plot([f * 100 for f in fs], ys, color=col, linewidth=2, label=lab)
        ax.annotate(lab, (100, ys[-1]), xytext=(6, 0), textcoords='offset points', color=TXT,
                    fontsize=9, va='center')
    ax.axvline(d['perfil_empuje'] * 100, color=TXT2, linewidth=1, linestyle='--')
    ax.annotate('combate típico', (d['perfil_empuje'] * 100, ax.get_ylim()[1] * 0.92), xytext=(5, 0),
                textcoords='offset points', color=TXT2, fontsize=9)
    ax.axhline(3, color=AQUA, linewidth=2)
    ax.annotate('3 min de combate', (2, 3), xytext=(0, 5), textcoords='offset points', color=TXT, fontsize=9)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, None)
    ax.set_xlabel('Tiempo empujando (motores casi bloqueados), %', color=TXT2)
    ax.set_ylabel('Autonomía, min', color=TXT2)
    ax.set_title('Autonomía según el tiempo que se pasa empujando', color=TXT, loc='left', fontsize=12)
    ax.legend(frameon=False, labelcolor=TXT, fontsize=9, loc='upper right')
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, 'calc_autonomia.png'), facecolor=FONDO)
    plt.close(fig)

    # 2) Reparto del consumo de 3,3 V (barras horizontales, típico)
    cargas = r['3v3']['cargas_A']
    nombres = list(cargas)[::-1]
    tip = [cargas[n][0] * 1000 for n in nombres]
    pk = [cargas[n][1] * 1000 for n in nombres]
    fig, ax = plt.subplots(figsize=(8, 3.8), dpi=150, facecolor=FONDO)
    estilo(ax)
    ax.grid(True, axis='x', color=REJ, linewidth=0.6)
    ax.grid(False, axis='y')
    y = range(len(nombres))
    ax.barh([i + 0.2 for i in y], tip, height=0.36, color=AZUL, label='Típico')
    ax.barh([i - 0.2 for i in y], pk, height=0.36, color=NARANJA, label='Pico')
    for i, (t, p) in enumerate(zip(tip, pk)):
        ax.annotate(f'{t:.0f}' if t >= 10 else f'{t:.1f}', (t, i + 0.2), xytext=(4, 0), textcoords='offset points', va='center',
                    fontsize=8, color=TXT)
        if p != t:
            ax.annotate(f'{p:.0f}' if p >= 10 else f'{p:.1f}', (p, i - 0.2), xytext=(4, 0), textcoords='offset points', va='center',
                        fontsize=8, color=TXT)
    ax.set_yticks(list(y))
    ax.set_yticklabels(nombres, color=TXT, fontsize=9)
    ax.set_xlabel('Corriente, mA', color=TXT2)
    tt, tp = (x * 1000 for x in r['3v3']['total_A'])
    ax.set_title(f'Consumo del raíl de 3,3 V: {tt:.0f} mA típicos, {tp:.0f} mA de pico',
                 color=TXT, loc='left', fontsize=12)
    ax.legend(frameon=False, labelcolor=TXT, fontsize=9, loc='lower right')
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, 'calc_consumo_3v3.png'), facecolor=FONDO)
    plt.close(fig)


def a_json(x):
    if isinstance(x, dict):
        return {str(k): a_json(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [a_json(v) for v in x]
    if isinstance(x, float):
        return round(x, 4)
    return x


def main():
    r, i_media, minutos = calcular(DATOS)
    with open(os.path.join(HERE, 'resultados.json'), 'w') as f:
        json.dump(a_json(r), f, indent=1, ensure_ascii=False)
    graficas(DATOS, r, i_media, minutos)
    print(json.dumps(a_json(r), indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
