#!/usr/bin/env python3
"""Rellena la plantilla de la ficha técnica (la del profesor, en la versión que ya
entregamos para la v1) con los datos del robot v2.

Los números salen de hardware/calculos/resultados_v2.json (calculos_v2.py).
Uso: python3 rellenar_ficha.py salida.docx
"""
import json, pathlib, sys
import docx

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
PLANTILLA = RAIZ / "archivo/v1-4motores/entregas-iniciales/ficha_técnica_robot.docx"
RES = json.loads((AQUI.parents[1] / "hardware/calculos/resultados_v2.json").read_text())["resultados"]

def coma(x, n=1):
    return f"{x:.{n}f}".replace(".", ",")

def poner(p, valor, n=1):
    """Deja los n primeros runs (la etiqueta de la plantilla) y pone el valor detrás."""
    runs = p.runs
    for r in runs[n:]:
        r.text = ""
    if len(runs) > n:
        runs[n].text = " " + valor
        runs[n].bold = False
    else:
        p.add_run(" " + valor)

def celda(c, texto):
    ps = c.paragraphs
    for p in ps[1:]:
        p._element.getparent().remove(p._element)
    p = ps[0]
    for r in p.runs[1:]:
        r.text = ""
    if p.runs:
        p.runs[0].text = texto
    else:
        p.add_run(texto)

def main(salida):
    d = docx.Document(PLANTILLA)
    P = d.paragraphs
    b, m, drv, pot, aut, el, mec = (RES[k] for k in ("bateria", "motor", "driver", "potencia", "autonomia", "electronica", "mecanica"))
    poner(P[1], "Hombres De Las Tabernas (LHDT) · robot mini sumo v2", n=3)
    poner(P[2], "CERN-OHL-P")
    # 3.1 Batería
    poner(P[7], "LiPo 2S con conector XT30")
    poner(P[8], f"{coma(b['V_nom'])} V (2 × 3,7 V)")
    poner(P[9], f"{coma(b['V_max'])} V (2 × 4,2 V)")
    poner(P[10], "450 mAh (estimado, según el vendedor)")
    poner(P[11], "30 C (según el vendedor): hasta 13,5 A; el robot pide como máximo "
                 f"{coma(pot['I_bat_pico_A'])} A ({coma(pot['C_necesario'])} C)")
    poner(P[12], "fusible de cuchilla mini de 7,5 A a la entrada · conector XT30 con polaridad "
                 "(no se puede enchufar al revés) · protección térmica y de baja tensión internas "
                 "de los TB6612FNG · regulador LM2940 con límite de corriente y protección térmica · "
                 "medida de la tensión de batería (divisor 100 kΩ / 33 kΩ al ADC) para el aviso de batería baja")
    # 3.2 Actuadores
    poner(P[14], "2 × micromotorreductor N20 de 6 V, ~500 rpm (tracción trasera)")
    poner(P[15], f"6,6–8,4 V de batería; con el PWM de ataque al 85 % le llegan como máximo {coma(m['V_ataque_bat_llena'])} V")
    poner(P[16], f"{coma(m['bloqueo']['8.4']['I_A'],2)} A a 8,4 V por motor (estimado: 1,6 A a 6 V; hay que medirlo)")
    poner(P[17], "Toshiba TB6612FNG, en módulo formato SparkFun ROB-14450; uno por motor, con sus dos canales en paralelo")
    poner(P[18], n=3, valor="motor (VM) 2,5–13,5 V; lógica (VCC) 2,7–5,5 V, se alimenta a 3,3 V")
    poner(P[19], n=2, valor="1,2 A continuos / 3,2 A de pico (10 ms) por canal → "
                 f"{coma(drv['I_cont_motor'])} A continuos / {coma(drv['I_pico_motor_10ms'])} A de pico por motor")
    # 3.3 Consumo
    poner(P[21], f"{coma(pot['P_max_W'])} W (2 motores bloqueados con la batería llena + electrónica)", n=2)
    e = aut["escenarios"]
    poner(P[22], f"≈ {round(e['40']['min_450'])} minutos con la batería de 450 mAh "
                 f"({coma(e['100']['min_450'])} min si empuja todo el tiempo)")
    P[24].text = ""
    P[24].add_run(
        f"Se usa el 80 % de la capacidad (360 mAh) para no bajar de 3,3 V por celda. En un combate típico "
        f"el robot empuja el 40 % del tiempo (2 motores casi bloqueados con PWM al 85 %: "
        f"{coma(aut['I_empuje_A'],2)} A), maniobra el resto (2 × 0,4 A) y la electrónica gasta "
        f"{coma(el['I_bat_typ_A'],2)} A. Corriente media = 0,4 × {coma(aut['I_empuje_A'],2)} + 0,6 × 0,80 + "
        f"{coma(el['I_bat_typ_A'],2)} = {coma(e['40']['I_A'],2)} A → t = 0,36 Ah / {coma(e['40']['I_A'],2)} A × 60 = "
        f"{coma(e['40']['min_450'])} min. Cálculo completo en el anexo, apartado 7.")
    # 2. Mecánica
    t = d.tables[0]
    celda(t.rows[1].cells[1], "9,8 × 9,7 × 4,3 cm")
    celda(t.rows[2].cells[1], f"≈ {int(mec['masa_g'] + 0.5)} g (estimada con el modelo 3D; sin pesar)")
    celda(t.rows[3].cells[1], "Base impresa en 3D (PETG) + PCB de FR4 + chapa de acero de 0,4 mm en la cuña (opcional)")
    celda(t.rows[4].cells[1], "2WD: dos ruedas motrices traseras; la cuña delantera apoya en el suelo")
    celda(t.rows[5].cells[1], "Silicona (ruedas de 30 mm de los N20)")
    # 4. Control y sensado
    t = d.tables[1]
    filas = [
        ("Placa de Control Abierta", "Espressif ESP32-S3-DevKitC-1", "5 V en su pin 5V (≈ 4,65 V tras el diodo); da 3,3 V a los sensores", "100 mA"),
        ("Módulo del Receptor IR", "Sobotz ST4RT (lo da el profesor)", "3,3 V (patillaje por confirmar)", "≈ 5 mA (estimado, sin hoja)"),
        ("Sensores de Borde (Línea)", "QRE1113 analógico (módulo), × 2 delante", "3,3 V", "21 mA cada uno"),
        ("Sensores de Oponente", "VL53L0X ToF (módulo), × 2 delante", "2,6–3,5 V; a 3,3 V", "19 mA cada uno (40 mA de pico)"),
        ("Regulador de 5 V", "TI LM2940CT-5.0 (TO-220)", f"entrada 5,5–26 V; salida 5 V", f"{round(el['I_3V3_typ_mA'])} mA típ. / {round(el['I_3V3_pico_mA'])} mA pico (máx. 1 A)"),
    ]
    for fila, valores in zip(t.rows[1:], filas):
        for c, v in zip(fila.cells, valores):
            celda(c, v)
    # 5. Criterio 9: quitar el LaTeX de la plantilla
    c = d.tables[2].rows[9].cells[0]
    for p in c.paragraphs:
        if "$" in p.text:
            for r in p.runs[1:]:
                r.text = ""
            p.runs[0].text = "Masa ≤ 500 g y dimensiones iniciales ≤ 10 cm × 10 cm (sin límite de altura)."
    d.save(salida)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ficha_tecnica_robot_v2.docx")
