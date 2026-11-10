"""Definición eléctrica de la placa base del robot (fuente única de verdad).

Cada componente: referencia, símbolo, valor, huella, {pin: red}, grupo del esquemático y MPN.
Los pines que no aparecen en el diccionario se marcan como "sin conexión".
gen_sch.py y gen_pcb.py leen este fichero.
"""

PROJECT = 'robot_sumo'
TITLE = 'Robot Mini-Sumo · Placa base'
COMPANY = 'HOMBRES DE LAS TABERNAS'
REV = 'v1.2'

R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'
C1206 = 'Capacitor_SMD:C_1206_3216Metric'
CPEL = 'Capacitor_SMD:CP_Elec_6.3x7.7'
JST_SH = 'Connector_JST:JST_SH_BM0{n}B-SRSS-TB_1x0{n}-1MP_P1.00mm_Vertical'  # SMD: cara inferior plana
DRV_FP = 'Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.46x2.31mm'  # vías térmicas de 0,3 mm las añade gen_pcb.py

parts = []


def add(ref, lib, value, fp, nets, group, mpn='', dnp=False):
    parts.append(dict(ref=ref, lib=lib, value=value, fp=fp, nets=nets, group=group, mpn=mpn, dnp=dnp))


def R(ref, value, a, b, group, mpn=''):
    add(ref, 'Device:R', value, R0603, {'1': a, '2': b}, group, mpn)


def C(ref, value, a, b, group, fp=C0603, mpn=''):
    add(ref, 'Device:C', value, fp, {'1': a, '2': b}, group, mpn)


# ---------------------------------------------------------------- Alimentación
G = 'Alimentación'
add('J1', 'Connector_Generic:Conn_01x02', 'XT30 BATERÍA 2S',
    'Connector_AMASS:AMASS_XT30UPB-M_1x02_P5.0mm_Vertical',
    {'1': 'GND', '2': 'VBAT_RAW'}, G, 'AMASS XT30UPB-M (macho, vertical PCB)')
# Q1: protección contra inversión de polaridad (D a batería, S a carga, G a GND)
add('Q1', 'Transistor_FET:Q_PMOS_GDS', 'AOD4185', 'Package_TO_SOT_SMD:TO-252-2',
    {'1': 'Q1_G', '2': 'VBAT_RAW', '3': 'VBAT_REV'}, G, 'AOD4185 (-40 V, -40 A, 15 mΩ)')
R('R1', '10k', 'Q1_G', 'GND', G)
# Sin interruptor de potencia: el robot se enciende al enchufar el XT30 (práctica habitual en minisumo).
# v1.2: 15 A. El techo de corriente lo pone ITRIP (4 × 2,44 A + electrónica ≈ 10,2 A), por encima de un
# fusible de 10 A trabajando al 75 % (revisión PR #3, punto 3). Ver hardware/calculos.
add('F1', 'Device:Fuse', '15A', 'Fuse:Fuse_Littelfuse-NANO2-451_453', {'1': 'VBAT_REV', '2': 'VBAT'}, G,
    'Littelfuse NANO2 451/453, 15 A rápido (p. ej. 0451015.MRL; verificar stock)')
# Reserva en VBAT (además de 10 µF por driver): cerámicos, más bajos que un electrolítico
C('C1', '22u 25V', 'VBAT', 'GND', G, C1206)
C('C2', '22u 25V', 'VBAT', 'GND', G, C1206)
# Medida de batería: 8,4 V -> 2,08 V
R('R3', '100k', 'VBAT', 'VBAT_SENSE', G)
R('R4', '33k', 'VBAT_SENSE', 'GND', G)
C('C3', '100n', 'VBAT_SENSE', 'GND', G)

# Buck 5,3 V (v1.2: sin D2). +5V = salida del buck; D1 -> pin 5V de la DevKit ≈ 4,85 V.
# Con la batería baja el buck satura por su t_OFF mínimo (D_max ≈ 82 %): +5V ≈ 5,0 V y pin 5V ≈ 4,45 V,
# que aún deja margen a un LDO AMS1117 (caída 1,1 V). Cálculo en hardware/calculos.
G = 'Buck 5 V'
add('U2', 'Regulator_Switching:TPS563201', 'TPS563201', 'Package_TO_SOT_SMD:SOT-23-6',
    {'1': 'GND', '2': 'BUCK_SW', '3': 'VBAT', '4': 'BUCK_FB', '5': 'BUCK_EN', '6': 'BUCK_BST'}, G,
    'TPS563201DDCR')
C('C4', '10u 25V', 'VBAT', 'GND', G, C1206)
C('C5', '10u 25V', 'VBAT', 'GND', G, C1206)
C('C6', '100n', 'VBAT', 'GND', G)
R('R5', '100k', 'VBAT', 'BUCK_EN', G)
R('R6', '51k', 'BUCK_EN', 'GND', G)
C('C7', '100n', 'BUCK_SW', 'BUCK_BST', G)
add('L1', 'Device:L', '3.3u', 'Inductor_SMD:L_Bourns-SRN4018', {'1': 'BUCK_SW', '2': '+5V'}, G,
    'SRN4018-3R3M (3,3 µH, Isat ≥ 2,5 A)')
R('R7', '59k', '+5V', 'BUCK_FB', G)      # Vout = 0,768·(1+59k/10k) = 5,30 V (E96)
R('R8', '10k', 'BUCK_FB', 'GND', G)
C('C8', '22u 10V', '+5V', 'GND', G, C1206)
C('C9', '22u 10V', '+5V', 'GND', G, C1206)
# D2 (SS34 en serie con la salida del buck) eliminado en v1.2: restaba 0,4–0,55 V sin proteger nada que
# no proteja ya D1.

# ---------------------------------------------------------------- Alimentación de la DevKit
# La DevKit genera los 3,3 V con su propio LDO (800 mA – 1 A según la placa) y los devuelve por sus
# pines 3V3 para los sensores. Se alimenta por su pin 5V a través de D1: así, con el USB de la DevKit
# enchufado, su VBUS no empuja hacia nuestra placa y nuestro buck no empuja hacia el PC.
G = 'Alimentación DevKit'
C('C10', '22u 10V', '+5V', 'GND', G, C1206)
add('D1', 'Diode:SS34', 'SS34', 'Diode_SMD:D_SMA', {'1': 'V5_ESP', '2': '+5V'}, G)
C('C11', '10u 10V', 'V5_ESP', 'GND', G, C0805)
add('D3', 'Device:LED', 'verde', 'LED_SMD:LED_0603_1608Metric', {'1': 'LED_PWR_K', '2': '+3V3'}, G)
R('R9', '1k', 'LED_PWR_K', 'GND', G)

# ---------------------------------------------------------------- ESP32-S3-DevKitC-1 (enchufable)
# Placa de desarrollo completa pinchada en tiras hembra de 2,54 mm (filas separadas 22,86 mm).
# Trae USB (nativo + UART), botones BOOT/RESET, LED RGB y LDO: nada de eso va ya en nuestra placa.
# Pines del símbolo: 1–22 = J1 de la DevKit, 23–44 = J3 (pin 23 = J3-1).
# Solo se montan zócalos donde hay señal: los huecos dejan pasar pistas gruesas entre las filas.
G = 'ESP32-S3-DevKitC-1'
DEVKIT_J1 = {   # pin de J1 -> red   (GPIO en el comentario)
    1: '+3V3', 2: '+3V3',                           # salida del LDO de la DevKit
    4: 'LINE_RL', 5: 'LINE_RR',                     # IO4, IO5
    6: 'ISENSE_M1', 7: 'ISENSE_M2',                 # IO6, IO7
    8: 'M3_IN1', 9: 'M3_IN2',                       # IO15, IO16
    10: 'XSHUT_B', 11: 'IR_START',                  # IO17, IO18
    12: 'ISENSE_M3',                                # IO8
    13: 'XSHUT_R',                                  # IO3
    14: 'M4_IN2',                                   # IO46 (arranque: el pull-down del DRV8874 lo deja a 0)
    15: 'ISENSE_M4', 16: 'VBAT_SENSE',              # IO9, IO10
    17: 'M1_IN1', 18: 'M1_IN2',                     # IO11, IO12
    19: 'M2_IN1', 20: 'M2_IN2',                     # IO13, IO14
    21: 'V5_ESP', 22: 'GND',
    # 3 = RST (EN): sin zócalo, la DevKit ya tiene su botón
}
DEVKIT_J3 = {
    1: 'GND',
    2: 'AUX_TX', 3: 'AUX_RX',                       # IO43, IO44 (compartidos con el puente USB-UART)
    4: 'LINE_FL', 5: 'LINE_FR',                     # IO1, IO2
    6: 'XSHUT_FL', 7: 'XSHUT_L',                    # IO42, IO41
    8: 'I2C_SCL', 9: 'I2C_SDA',                     # IO40, IO39
    10: 'DRV_nFAULT',                               # IO38 (LED RGB en la DevKit v1.1: aquí solo es entrada)
    15: 'M4_IN1',                                   # IO45 (arranque: el pull-down del DRV8874 lo deja a 0)
    16: 'XSHUT_FR', 17: 'XSHUT_F',                  # IO48, IO47
    18: 'DRV_EN',                                   # IO21 (va a U3: nSLEEP = DRV_EN AND KILL)
    21: 'GND', 22: 'GND',
    # 11–13 = IO37/36/35: los usa la PSRAM octal de las variantes R8 (N8R8, N16R8) -> sin zócalo
    # 14 = IO0: botón BOOT de la DevKit, reutilizable como botón de usuario -> sin zócalo
    # 19, 20 = IO20/IO19: USB nativo de la DevKit -> sin zócalo
}
esp = {str(k): v for k, v in DEVKIT_J1.items()}
esp.update({str(22 + k): v for k, v in DEVKIT_J3.items()})
add('U1', 'Sumo:ESP32-S3-DevKitC-1', 'ESP32-S3-DevKitC-1', 'Sumo:ESP32-S3-DevKitC-1_Zocalo', esp, G,
    'ESP32-S3-DevKitC-1 (cualquier variante: N8, N8R2, N8R8, N16R8) + tiras hembra 2,54 mm cortadas')
C('C13', '22u 10V', '+3V3', 'GND', G, C1206)
C('C14', '100n', '+3V3', 'GND', G)

# ---------------------------------------------------------------- Drivers de motor
# ITRIP = VREF / (A_IPROPI · R_IPROPI) = 1,65 V / (450 µA/A · 1,5 kΩ) ≈ 2,44 A
G = 'Drivers comunes'
R('R14', '10k', '+3V3', 'DRV_VREF', G)
R('R15', '10k', 'DRV_VREF', 'GND', G)
C('C17', '100n', 'DRV_VREF', 'GND', G)
R('R16', '10k', '+3V3', 'DRV_nFAULT', G)
R('R17', '100k', 'DRV_EN', 'GND', G)       # motores parados mientras el ESP32 arranca

# ---------------------------------------------------------------- Módulo de arranque ST4RT (profesor)
# v1.2. Módulo Sobotz ST4RT, compatible (según el fabricante) con el start module de p1r.se/startmodule.com:
#   pines + (2,8–5,2 V), − (GND), S (START: alto = combate) y K (KILL: bajo = parar motores), y una
#   salida IR "en bruto" del receptor. Se alimenta a 3,3 V para que S y K no pasen nunca de 3,3 V en un GPIO.
#   ⚠️ Orden físico de pines, niveles y consumo SIN CONFIRMAR hasta tener el módulo (diciembre):
#   el cable a J17 se hace a medida, así el orden de la PCB no depende del orden del módulo.
# Parada por hardware: nSLEEP de los 4 DRV8874 = DRV_EN (firmware) AND KILL (módulo). Si el módulo
#   ordena parar, los drivers se duermen aunque el firmware esté colgado. Sin módulo, KILL queda a 0
#   (R66) y los motores no se mueven: para probar en el banco sin módulo, cerrar JP1.
G = 'Arranque ST4RT'
R('R62', '10', '+3V3', 'ST_VCC', G)                    # filtro RC de la alimentación del módulo
C('C62', '10u 10V', 'ST_VCC', 'GND', G, C0805)
add('J17', 'Connector_Generic:Conn_01x05', 'ST4RT (módulo IR)', JST_SH.format(n=5),
    {'1': 'ST_VCC', '2': 'GND', '3': 'ST_START_IN', '4': 'ST_KILL_IN', '5': 'ST_IR_RAW'}, G,
    'JST SH 5P SMD vertical (BM05B-SRSS-TB) + cable a medida hasta el módulo')
R('R63', '1k', 'ST_START_IN', 'IR_START', G)          # serie: limita corriente si el módulo diera 5 V
R('R64', '1k', 'ST_KILL_IN', 'ST_KILL', G)
R('R65', '100k', 'IR_START', 'GND', G)               # sin módulo = no arranca
R('R66', '100k', 'ST_KILL', 'GND', G)                # sin módulo = motores dormidos
# Por si S/K del módulo resultaran ser de drenador abierto (sin confirmar): huecos para pull-ups a 3,3 V.
# Si se montan, quitar R65/R66. Por defecto NO se montan (DNP).
add('R68', 'Device:R', '10k', R0603, {'1': '+3V3', '2': 'IR_START'}, G, 'DNP: solo si S es de drenador abierto', dnp=True)
add('R69', 'Device:R', '10k', R0603, {'1': '+3V3', '2': 'ST_KILL'}, G, 'DNP: solo si K es de drenador abierto', dnp=True)
R('R67', '10k', '+3V3', 'JP1_A', G)
add('JP1', 'Jumper:SolderJumper_2_Open', 'BANCO SIN MÓDULO', 'Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm',
    {'1': 'JP1_A', '2': 'ST_KILL'}, G, 'Puente de soldadura: cerrado = KILL a 1 sin módulo (solo banco)')
add('U3', '74xGxx:74LVC1G08', '74LVC1G08', 'Package_TO_SOT_SMD:SOT-23-5',
    {'1': 'DRV_EN', '2': 'ST_KILL', '3': 'GND', '4': 'DRV_nSLEEP', '5': '+3V3'}, G, 'SN74LVC1G08DBVR')
C('C15', '100n', '+3V3', 'GND', G)
add('TP1', 'Connector:TestPoint', 'IR_RAW', 'TestPoint:TestPoint_Pad_D1.0mm', {'1': 'ST_IR_RAW'}, G,
    'Punto de prueba (salida IR en bruto del módulo, sin uso en combate)')

MOTORES = {1: 'izq. delantero', 2: 'izq. trasero', 3: 'der. delantero', 4: 'der. trasero'}
for k in MOTORES:
    G = f'Motor {k}'
    u, n = f'U{4 + k}', f'M{k}'
    add(u, 'Sumo:DRV8874', 'DRV8874', DRV_FP, {
        '1': f'{n}_IN1', '2': f'{n}_IN2', '3': 'DRV_nSLEEP', '4': 'DRV_nFAULT', '5': 'DRV_VREF',
        '6': f'ISENSE_{n}', '7': f'{n}_IMODE', '8': f'{n}_OUTA', '9': 'GND', '10': f'{n}_OUTB',
        '11': 'VBAT', '12': f'{n}_VCP', '13': f'{n}_CPH', '14': f'{n}_CPL', '15': 'GND',
        '16': '+3V3', '17': 'GND'}, G, 'DRV8874PWPR')
    b = 20 + (k - 1) * 10
    R(f'R{b}', '1.5k', f'ISENSE_{n}', 'GND', G)                 # R_IPROPI
    C(f'C{b}', '10n', f'ISENSE_{n}', 'GND', G)                  # filtro IPROPI
    R(f'R{b + 1}', '20k', f'{n}_IMODE', 'GND', G)               # ciclo a ciclo + reintento
    C(f'C{b + 1}', '100n 16V', f'{n}_VCP', 'VBAT', G)
    C(f'C{b + 2}', '22n 50V', f'{n}_CPH', f'{n}_CPL', G)
    C(f'C{b + 3}', '100n 50V', 'VBAT', 'GND', G)
    C(f'C{b + 4}', '10u 25V', 'VBAT', 'GND', G, C1206)
    add(f'J{2 + k}', 'Connector_Generic:Conn_01x02', f'MOTOR {k}',
        'Connector_Wire:SolderWire-0.5sqmm_1x02_P4.6mm_D0.9mm_OD2.1mm',
        {'1': f'{n}_OUTA', '2': f'{n}_OUTB'}, G, 'Cable del motor soldado (entra por abajo)')

# ---------------------------------------------------------------- Sensores
G = 'Sensores'
# v1.2: 4,7 k. Los módulos GY-VL53L0XV2 suelen traer sus propias pull-ups de 10 k (a comprobar): con 6
# módulos + 2,2 k el bus pasaba de los 3 mA de sumidero del estándar I²C (revisión PR #3, punto 5).
R('R60', '4.7k', '+3V3', 'I2C_SDA', G)
R('R61', '4.7k', '+3V3', 'I2C_SCL', G)
TOF = [('J7', 'L', 'ToF IZQ'), ('J8', 'FL', 'ToF FRONT-IZQ'), ('J9', 'F', 'ToF FRONTAL'),
       ('J10', 'FR', 'ToF FRONT-DER'), ('J11', 'R', 'ToF DER'), ('J12', 'B', 'ToF TRASERO')]
for ref, s, name in TOF:
    add(ref, 'Connector_Generic:Conn_01x05', name, JST_SH.format(n=5),
        {'1': '+3V3', '2': 'GND', '3': 'I2C_SCL', '4': 'I2C_SDA', '5': f'XSHUT_{s}'}, G, 'JST SH 5P SMD vertical (BM05B-SRSS-TB)')
LINE = [('J13', 'FL', 'LÍNEA FRONT-IZQ'), ('J14', 'FR', 'LÍNEA FRONT-DER'),
        ('J15', 'RL', 'LÍNEA TRAS-IZQ'), ('J16', 'RR', 'LÍNEA TRAS-DER')]
for ref, s, name in LINE:
    add(ref, 'Connector_Generic:Conn_01x03', name, JST_SH.format(n=3),
        {'1': '+3V3', '2': 'GND', '3': f'LINE_{s}'}, G, 'JST SH 3P SMD vertical (BM03B-SRSS-TB)')
# Expansión I2C tipo Qwiic/STEMMA QT (IMU opcional)
add('J18', 'Connector_Generic:Conn_01x04', 'I2C (QWIIC)',
    JST_SH.format(n=4),
    {'1': 'GND', '2': '+3V3', '3': 'I2C_SDA', '4': 'I2C_SCL'}, G, 'JST SH 4P SMD vertical (BM04B-SRSS-TB)')
# Auxiliar: UART de depuración o servo de despliegue
add('J19', 'Connector_Generic:Conn_01x04', 'AUX (UART/servo)', JST_SH.format(n=4),
    {'1': '+5V', '2': 'GND', '3': 'AUX_TX', '4': 'AUX_RX'}, G, 'JST SH 4P SMD vertical (BM04B-SRSS-TB)')

# ---------------------------------------------------------------- Mecánica
G = 'Mecánica'
for i in range(1, 9):
    add(f'H{i}', 'Mechanical:MountingHole', 'M2', 'MountingHole:MountingHole_2.2mm_M2', {}, G)

# Redes que necesitan PWR_FLAG (alimentadas por pines pasivos)
POWER_FLAGS = ['GND', 'VBAT', '+5V', 'VBAT_RAW', 'V5_ESP']
