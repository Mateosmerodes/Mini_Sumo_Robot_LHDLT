#!/usr/bin/env python3
"""Cálculos de la ficha técnica del robot v2 (2 motores N20, 2 TB6612FNG, LM2940).

Todo es teórico: nada está montado ni medido. Los datos marcados TIPICO salen de
hojas de datos o de vendedores sin comprobar en el banco; los ESTIMADO son
supuestos del equipo que hay que medir. Cambiad DATOS y volved a ejecutar:

    python3 calculos_v2.py          # imprime y escribe resultados_v2.json
"""
import json, math, pathlib

DATOS = {
    # Batería LiPo 2S (la misma de la v1)
    "celda_nom_V": 3.7, "celda_max_V": 4.2, "celda_min_V": 3.3,   # química LiPo
    "bat_C_mAh": 450, "bat_C_alt_mAh": 650, "bat_tasa_C": 30,     # TIPICO vendedor
    "bat_R_int_ohm": 0.030,                                       # ESTIMADO
    "bat_util": 0.80,                                             # no bajar de 3,3 V/celda
    # Motor N20 6 V ~500 rpm
    "mot_V_nom": 6.0, "mot_I_stall_6V": 1.6,                      # ESTIMADO (ref. Pololu HP 6 V)
    "mot_I_maniobra": 0.40,                                       # ESTIMADO
    "mot_rpm_6V": 500, "rueda_D_mm": 30,                          # TIPICO vendedor / ESTIMADO
    # TB6612FNG (Toshiba), por canal
    "tb_VM_min": 2.5, "tb_VM_max_op": 13.5, "tb_VM_abs": 15.0,
    "tb_I_cont_canal": 1.2, "tb_I_pico_20ms": 2.0, "tb_I_pico_10ms": 3.2,
    "tb_Vsat_UL_1A_typ": 0.5, "tb_Vsat_UL_1A_max": 0.7,           # V con 1 A (alto + bajo)
    "tb_Pd_W": 0.78, "tb_Tj_max": 150, "tb_TSD": 175,             # Pd del CI solo a 25 °C
    "tb_Icc_mA": 1.1, "tb_reparto": 0.55,                         # ESTIMADO: canal que más lleva
    # Firmware
    "pwm_ataque": 0.85, "pwm_giro": 0.45, "pwm_busqueda": 0.40,
    # Electrónica (corriente del raíl de 3,3 V que sale de la DevKit)
    "esp_typ_mA": 100, "esp_pico_mA": 200,                        # ESTIMADO, sin Wi-Fi
    "vl53_typ_mA": 19, "vl53_pico_mA": 40, "n_vl53": 2,           # TIPICO ST / Pololu
    "qre_Vf": 1.2, "qre_R": 100, "n_qre": 2,                      # TIPICO onsemi / módulo
    "st4rt_mA": 5,                                                # ESTIMADO, sin hoja
    "otros_mA": 3,                                                # LED de la DevKit, divisores
    # LM2940CT-5.0
    "reg_Vout": 5.0, "reg_Vout_tol": 0.15, "reg_dropout_typ": 0.2, "reg_dropout_1A": 0.5,
    "reg_Iq_mA": 10, "reg_Rth": (50, 60), "reg_Tj_max": 125, "reg_I_max": 1.0,
    "d1_Vf": (0.30, 0.45),                                        # 1N5819 a 0,2–0,35 A, TIPICO
    "ldo_devkit_drop": 1.1,                                       # peor caso (AMS1117)
    # Protección
    "fusible_A": 7.5, "fusible_uso": 0.75, "xt30_A": 15,
    # PCB: pistas exteriores de 1 oz
    "pista_VBAT_mm": 1.5, "cobre_um": 35,
    # Masas del modelo 3D (hardware/chasis/informe_chasis.json)
    "masa_sin_lastre_g": 187.7, "masa_con_lastre_acero_g": 232.5,
    "lastre_plomo_lleno_g": 123.0, "masa_max_g": 500,
    "planta_mm": (98.0, 97.2), "alto_mm": 42.5,
    "mu": (0.8, 1.0), "g": 9.81, "ambiente_C": 25,
}

def r(x, n=2):
    return round(x, n)

def calcular(d=DATOS):
    o = {}
    Vn, Vmax, Vmin = 2 * d["celda_nom_V"], 2 * d["celda_max_V"], 2 * d["celda_min_V"]
    o["bateria"] = {"V_nom": r(Vn), "V_max": r(Vmax), "V_min": r(Vmin),
                    "energia_Wh": r(Vn * d["bat_C_mAh"] / 1000),
                    "I_max_A": r(d["bat_C_mAh"] / 1000 * d["bat_tasa_C"], 1)}
    # Motor
    R = d["mot_V_nom"] / d["mot_I_stall_6V"]
    stall = {f"{V:.1f}": {"I_A": r(V / R), "P_W": r(V * V / R, 1)} for V in (6.0, Vn, Vmax)}
    o["motor"] = {"R_ohm": r(R), "bloqueo": stall,
                  "bloqueo_8V4_ataque_A": r(d["pwm_ataque"] * Vmax / R),
                  "V_ataque_bat_llena": r(d["pwm_ataque"] * Vmax),
                  "sobretension_bat_llena": r(Vmax / d["mot_V_nom"])}
    Is = Vmax / R
    # Inversión de marcha a tope: fem ≈ V·(1 - I_maniobra/I_stall) aprox -> pico (V + E)/R
    E = d["pwm_ataque"] * Vmax  # fem en vacío ≈ tensión aplicada
    o["motor"]["pico_inversion_A"] = r((d["pwm_ataque"] * Vmax + E) / R)
    # Velocidad
    vel = {}
    for V in (6.0, Vn, Vmax):
        rpm = d["mot_rpm_6V"] * V / 6.0
        v = rpm * math.pi * d["rueda_D_mm"] / 1000 / 60
        vel[f"{V:.1f}"] = {"rpm": round(rpm), "v_m_s": r(v), "t_dohyo_s": r(0.77 / v), "t_borde_ms": round(25e-3 / v * 1000)}
    o["velocidad"] = vel
    # Driver: dos canales en paralelo por motor
    Rch_t, Rch_m = d["tb_Vsat_UL_1A_typ"] / 1.0, d["tb_Vsat_UL_1A_max"] / 1.0
    Rth = (125 if False else (d["tb_Tj_max"] - 25) / d["tb_Pd_W"])  # °C/W deducido de Pd
    drv = {"I_cont_motor": r(2 * d["tb_I_cont_canal"], 1), "I_pico_motor_20ms": r(2 * d["tb_I_pico_20ms"], 1),
           "I_pico_motor_10ms": r(2 * d["tb_I_pico_10ms"], 1), "Rth_C_W": round(Rth), "casos": {}}
    for nombre, pwm in (("bloqueo_100", 1.0), ("bloqueo_ataque", d["pwm_ataque"]), ("maniobra", None)):
        Im = Is * pwm if pwm else d["mot_I_maniobra"]
        Ich = Im / 2
        Ich_peor = Im * d["tb_reparto"]
        P_t = 2 * Ich ** 2 * Rch_t
        P_m = 2 * Ich ** 2 * Rch_m
        drv["casos"][nombre] = {"I_motor": r(Im), "I_canal": r(Ich), "I_canal_desigual": r(Ich_peor),
                               "P_typ_W": r(P_t), "P_max_W": r(P_m),
                               "Tj_typ_C": round(d["ambiente_C"] + P_t * Rth), "Tj_max_C": round(d["ambiente_C"] + P_m * Rth)}
    # PWM de ataque que deja Tj <= 125 °C con R típica
    Pok = (125 - d["ambiente_C"]) / Rth
    Im_ok = 2 * math.sqrt(Pok / (2 * Rch_t))
    drv["I_motor_Tj125_A"] = r(Im_ok)
    drv["pwm_Tj125"] = r(Im_ok / Is)
    drv["margen_inversion_canal_A"] = r(o["motor"]["pico_inversion_A"] / 2)
    o["driver"] = drv
    # Electrónica
    qre = (3.3 - d["qre_Vf"]) / d["qre_R"] * 1000
    cargas = {
        "ESP32-S3 DevKitC-1": (d["esp_typ_mA"], d["esp_pico_mA"]),
        "2 x VL53L0X": (d["n_vl53"] * d["vl53_typ_mA"], d["n_vl53"] * d["vl53_pico_mA"]),
        "2 x QRE1113": (d["n_qre"] * qre, d["n_qre"] * qre),
        "Lógica de los 2 TB6612FNG": (2 * d["tb_Icc_mA"], 2 * d["tb_Icc_mA"]),
        "ST4RT": (d["st4rt_mA"], d["st4rt_mA"]),
        "Otros": (d["otros_mA"], d["otros_mA"]),
    }
    I3t = sum(v[0] for v in cargas.values()); I3p = sum(v[1] for v in cargas.values())
    Ibt = (I3t + d["reg_Iq_mA"]) / 1000; Ibp = (I3p + d["reg_Iq_mA"]) / 1000
    el = {"cargas_mA": {k: [r(a, 1), r(b, 1)] for k, (a, b) in cargas.items()},
          "qre_mA": r(qre, 1), "I_3V3_typ_mA": r(I3t, 1), "I_3V3_pico_mA": r(I3p, 1),
          "I_bat_typ_A": r(Ibt, 3), "I_bat_pico_A": r(Ibp, 3),
          "P_bat_typ_W": r(Vn * Ibt), "P_bat_pico_W": r(Vmax * Ibp)}
    # Regulador
    Rth_min, Rth_max = d["reg_Rth"]
    reg = {}
    for nombre, V, I in (("typ_7V4", Vn, I3t / 1000), ("typ_8V4", Vmax, I3t / 1000), ("pico_8V4", Vmax, I3p / 1000)):
        P = (V - d["reg_Vout"]) * I + V * d["reg_Iq_mA"] / 1000
        reg[nombre] = {"P_W": r(P), "Tj_C": [round(d["ambiente_C"] + P * Rth_min), round(d["ambiente_C"] + P * Rth_max)]}
    reg["V_bat_min_regula"] = r(d["reg_Vout"] + d["reg_dropout_typ"])
    V5min = d["reg_Vout"] - d["reg_Vout_tol"]
    reg["V_devkit"] = [r(V5min - d["d1_Vf"][1]), r(d["reg_Vout"] + d["reg_Vout_tol"] - d["d1_Vf"][0])]
    reg["margen_ldo_devkit_peor_V"] = r(V5min - d["d1_Vf"][1] - 3.3 - d["ldo_devkit_drop"])
    el["regulador"] = reg
    o["electronica"] = el
    # Potencia y corrientes de batería
    Ib_pico = 2 * Is + Ibp
    Ib_pico_ataque = 2 * d["pwm_ataque"] * Is + Ibp
    Pmax = 2 * Vmax * Is + Vmax * Ibp
    Pnom = 2 * Vn * (Vn / R) + Vn * Ibp
    caida = Ib_pico * (d["bat_R_int_ohm"] + 0.005 + 0.003)  # pack + fusible + XT30 y pistas
    o["potencia"] = {"I_bat_pico_A": r(Ib_pico), "I_bat_pico_ataque_A": r(Ib_pico_ataque),
                     "P_max_W": r(Pmax, 1), "P_nom_W": r(Pnom, 1),
                     "P_motores_W": r(2 * Vmax * Is, 1),
                     "C_necesario": r(Ib_pico / (d["bat_C_mAh"] / 1000), 1),
                     "caida_V": r(caida), "V_bat_baja_en_pico": r(Vmin - caida)}
    # Fusible
    util = d["fusible_A"] * d["fusible_uso"]
    o["fusible"] = {"util_A": r(util, 2), "uso_pico_pct": round(100 * Ib_pico / d["fusible_A"]),
                    "margen_util_pct": round(100 * (util / Ib_pico - 1)),
                    "I_stall_motor_limite_A": r((util - Ibp) / 2),
                    "pico_inversion_total_A": r(2 * o["motor"]["pico_inversion_A"] + Ibp),
                    "bateria_A": o["bateria"]["I_max_A"], "xt30_A": d["xt30_A"]}
    # Pista VBAT (IPC-2221, capa exterior)
    A_mil2 = d["pista_VBAT_mm"] / 0.0254 * d["cobre_um"] / 25.4
    I10 = 0.048 * 10 ** 0.44 * A_mil2 ** 0.725
    dT = (Ib_pico / (0.048 * A_mil2 ** 0.725)) ** (1 / 0.44)
    dT_m = (Is / (0.048 * A_mil2 ** 0.725)) ** (1 / 0.44)
    o["pista"] = {"A_mil2": r(A_mil2, 1), "I_dT10_A": r(I10), "dT_tronco_pico_C": r(dT, 1), "dT_motor_C": r(dT_m, 1)}
    # Autonomía
    C_util = d["bat_util"] * d["bat_C_mAh"] / 1000
    I_emp = 2 * d["pwm_ataque"] * (Vn / R)  # conservador: la corriente del motor sale entera de la batería
    I_man = 2 * d["mot_I_maniobra"]
    aut = {"C_util_Ah": r(C_util, 2), "I_empuje_A": r(I_emp), "I_maniobra_A": r(I_man), "escenarios": {}}
    for f in (1.0, 0.4, 0.0):
        I = f * I_emp + (1 - f) * I_man + Ibt
        aut["escenarios"][f"{int(f*100)}"] = {"I_A": r(I), "min_450": r(C_util / I * 60, 1),
                                              "min_650": r(d["bat_util"] * d["bat_C_alt_mAh"] / 1000 / I * 60, 1)}
    sens = {}
    for Is6 in (0.7, 1.0, 1.6, 2.0):
        Ie = 2 * d["pwm_ataque"] * Vn / (6.0 / Is6)
        I = 0.4 * Ie + 0.6 * I_man + Ibt
        sens[f"{Is6}"] = r(C_util / I * 60, 1)
    aut["sensibilidad_stall_6V"] = sens
    o["autonomia"] = aut
    # Masa y mecánica
    m = d["masa_con_lastre_acero_g"] / 1000
    F = [mu * m * d["g"] for mu in d["mu"]]
    o["mecanica"] = {"masa_g": d["masa_con_lastre_acero_g"], "masa_sin_lastre_g": d["masa_sin_lastre_g"],
                     "masa_plomo_g": r(d["masa_sin_lastre_g"] + d["lastre_plomo_lleno_g"], 1),
                     "margen_g": r(d["masa_max_g"] - d["masa_con_lastre_acero_g"], 1),
                     "F_N": [r(x) for x in F], "par_rueda_Nm": r(F[1] / 2 * d["rueda_D_mm"] / 2000, 4),
                     "par_rueda_kgcm": r(F[1] / 2 * d["rueda_D_mm"] / 2000 / 9.81 * 100, 2)}
    return o

if __name__ == "__main__":
    o = calcular()
    out = pathlib.Path(__file__).with_name("resultados_v2.json")
    out.write_text(json.dumps({"aviso": "Cálculo teórico; nada medido.", "datos": DATOS, "resultados": o},
                              ensure_ascii=False, indent=2))
    print(json.dumps(o, ensure_ascii=False, indent=1))
