"""Circuito de la placa v2 «básica» (fuente única de verdad).

Robot de 2 motores. Todo es de agujero pasante (THT) para soldarlo a mano:
módulos enchufados en tiras de pines (ESP32-S3-DevKitC-1 y dos TB6612FNG),
resistencias de 1/4 W, condensadores cerámicos de disco y electrolíticos,
regulador en TO-220. Los sensores de suelo (QRE1113) y de distancia (VL53L0X)
son los módulos que ya tiene el equipo, conectados por cable a tiras de pines.

Cada componente: referencia, símbolo, valor, huella, {pin: red}, grupo del esquemático y nota.
gen_sch.py, gen_pcb.py y gen_bom.py leen este fichero.
"""

PROJECT = 'robot_sumo'
TITLE = 'Robot Mini-Sumo LHDT · Placa basica'
COMPANY = 'LHDT · Los Hombres de las Tabernas'
REV = 'v2.0'

# Huellas THT (librerías estándar de KiCad)
R_THT = 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal'
C_DISCO = 'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm'
CP_8 = 'Capacitor_THT:CP_Radial_D8.0mm_P3.50mm'
CP_6 = 'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm'
TIRA = 'Connector_PinHeader_2.54mm:PinHeader_1x0{n}_P2.54mm_Vertical'

parts = []


def add(ref, lib, value, fp, nets, group, nota='', dnp=False):
    parts.append(dict(ref=ref, lib=lib, value=value, fp=fp, nets=nets, group=group, mpn=nota, dnp=dnp))


def R(ref, value, a, b, group, nota='Resistencia 1/4 W'):
    add(ref, 'Device:R', value, R_THT, {'1': a, '2': b}, group, nota)


def C(ref, value, a, b, group, nota='Condensador cerámico de disco, paso 5 mm'):
    add(ref, 'Device:C', value, C_DISCO, {'1': a, '2': b}, group, nota)


def CP(ref, value, pos, neg, group, fp=CP_8, nota='Electrolítico radial'):
    add(ref, 'Device:C_Polarized', value, fp, {'1': pos, '2': neg}, group, nota)


# ---------------------------------------------------------------- 1. Batería
# LiPo 2S (6,0–8,4 V) con XT30. El robot se enciende al enchufar el XT30.
# El XT30 tiene forma: no se puede enchufar al revés.
G = '1. Bateria'
add('J1', 'Connector_Generic:Conn_01x02', 'BATERIA 2S (XT30)',
    'Connector_AMASS:AMASS_XT30UPB-M_1x02_P5.0mm_Vertical',
    {'1': 'GND', '2': 'VBAT_RAW'}, G, 'AMASS XT30UPB-M macho, vertical, de agujero pasante')
# Fusible de cuchilla mini: 2 motores bloqueados a 8,4 V ≈ 2 × 2,24 A + electrónica ≈ 4,8 A
add('F1', 'Device:Fuse', '7.5A', 'Fuse:Fuseholder_Blade_Mini_Keystone_3568',
    {'1': 'VBAT_RAW', '2': 'VBAT'}, G, 'Portafusibles Keystone 3568 + fusible de cuchilla mini (ATM) de 7,5 A')
CP('C1', '470u 16V', 'VBAT', 'GND', G, nota='Electrolítico 470 µF 16 V, Ø8 mm, paso 3,5 mm (reserva de los motores)')
# Medida de batería: 8,4 V -> 2,08 V en el ADC
R('R1', '100k', 'VBAT', 'VBAT_SENSE', G)
R('R2', '33k', 'VBAT_SENSE', 'GND', G)
C('C3', '100n', 'VBAT_SENSE', 'GND', G)

# ---------------------------------------------------------------- 2. 5 V para la ESP32
# Regulador lineal de baja caída LM2940CT-5.0 (TO-220, patillas 1 IN, 2 GND, 3 OUT, como un 7805).
# Caída ≤ 0,5 V: da 5 V hasta con la batería a 5,5 V. Pide ≥ 22 µF a la salida (C5).
G = '2. Regulador 5 V'
add('U1', 'Regulator_Linear:L7805', 'LM2940CT-5.0', 'Package_TO_SOT_THT:TO-220-3_Vertical',
    {'1': 'VBAT', '2': 'GND', '3': '+5V'}, G, 'LM2940CT-5.0 (TO-220). Mismo patillaje que un 7805')
C('C4', '470n', 'VBAT', 'GND', G)
CP('C5', '47u 10V', '+5V', 'GND', G, fp=CP_6, nota='Electrolítico 47 µF 10 V, Ø6,3 mm, paso 2,5 mm')
# Diodo: con el USB de la DevKit enchufado, su 5 V no se mete en el regulador
add('D1', 'Diode:1N5819', '1N5819', 'Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal',
    {'1': 'V5_ESP', '2': '+5V'}, G, 'Diodo Schottky 1N5819 (DO-41)')
# (Sin LED propio: la DevKit ya trae el suyo de alimentación.)

# ---------------------------------------------------------------- 3. ESP32-S3-DevKitC-1
# Placa completa pinchada en dos tiras hembra 1×22 de 2,54 mm (filas a 22,86 mm).
# Pines del símbolo: 1–22 = fila J1 de la DevKit, 23–44 = fila J3 (pin 23 = J3-1).
# La DevKit hace los 3,3 V con su propio regulador y los da por J1-1/J1-2 para los sensores.
G = '3. ESP32-S3-DevKitC-1'
DEVKIT_J1 = {   # pin de la fila J1 -> red   (GPIO en el comentario)
    1: '+3V3', 2: '+3V3',
    4: 'LINEA_IZQ',             # IO4  (ADC)
    5: 'XSHUT_IZQ',             # IO5
    16: 'VBAT_SENSE',           # IO10 (ADC)
    17: 'MI_PWM', 18: 'MI_IN1', 19: 'MI_IN2',   # IO11, IO12, IO13: motor izquierdo
    20: 'MOT_STBY',             # IO14: activa los dos drivers
    10: 'ST_START', 11: 'ST_KILL',              # IO17, IO18: módulo de arranque
    21: 'V5_ESP', 22: 'GND',
}
DEVKIT_J3 = {
    1: 'GND',
    4: 'LINEA_DER',             # IO1  (ADC)
    5: 'XSHUT_DER',             # IO2
    8: 'I2C_SCL', 9: 'I2C_SDA', # IO40, IO39
    16: 'MD_IN2', 17: 'MD_PWM', 18: 'MD_IN1',   # IO48, IO47, IO21: motor derecho
    21: 'GND', 22: 'GND',
}
GPIO = {  # para el firmware y la documentación
    'LINEA_IZQ': 4, 'XSHUT_IZQ': 5, 'VBAT_SENSE': 10, 'MI_PWM': 11, 'MI_IN1': 12, 'MI_IN2': 13,
    'MOT_STBY': 14, 'ST_START': 17, 'ST_KILL': 18, 'LINEA_DER': 1, 'XSHUT_DER': 2,
    'I2C_SCL': 40, 'I2C_SDA': 39, 'MD_IN2': 48, 'MD_PWM': 47, 'MD_IN1': 21,
}
esp = {str(k): v for k, v in DEVKIT_J1.items()}
esp.update({str(22 + k): v for k, v in DEVKIT_J3.items()})
add('U2', 'Sumo:ESP32-S3-DevKitC-1', 'ESP32-S3-DevKitC-1', 'Sumo:ESP32-S3-DevKitC-1_Zocalo', esp, G,
    'ESP32-S3-DevKitC-1 + 2 tiras hembra 1×22 de 2,54 mm')
R('R3', '100k', 'MOT_STBY', 'GND', G)   # motores parados mientras arranca la ESP32

# ---------------------------------------------------------------- 4 y 5. Drivers de motor
# Módulo TB6612FNG (formato SparkFun ROB-14450: 20,3 × 20,3 mm, dos filas de 8 pines a 15,24 mm).
# Un módulo por motor con sus dos canales EN PARALELO (A y B unidos): 2,4 A continuos y 6,4 A de pico
# por motor, por encima del bloqueo estimado de un N20 a 8,4 V (2,24 A).
# Pines del símbolo = pines del módulo: 1–8 fila de potencia, 9–16 fila de control.
for ref, lado, cref, mref, nom in (('U3', 'MI', 'C6', 'J2', 'IZQUIERDO'), ('U4', 'MD', 'C7', 'J3', 'DERECHO')):
    G = f'{4 if lado == "MI" else 5}. Motor {nom.lower()}'
    add(ref, 'Sumo:TB6612FNG_Modulo', 'TB6612FNG', 'Sumo:TB6612FNG_Modulo' + ('_Girado' if lado == 'MD' else ''), {
        '1': 'GND', '2': f'{lado}_A', '3': f'{lado}_B', '4': f'{lado}_B', '5': f'{lado}_A',   # BO1, BO2, AO2, AO1
        '6': 'GND', '7': '+3V3', '8': 'VBAT',
        '9': f'{lado}_PWM', '10': f'{lado}_IN2', '11': f'{lado}_IN1', '12': 'MOT_STBY',
        '13': f'{lado}_IN1', '14': f'{lado}_IN2', '15': f'{lado}_PWM', '16': 'GND'}, G,
        'Módulo TB6612FNG (SparkFun ROB-14450 o clon con el mismo patillaje) + 2 tiras hembra 1×8')
    CP(cref, '100u 16V', 'VBAT', 'GND', G, fp=CP_6, nota='Electrolítico 100 µF 16 V, Ø6,3 mm, paso 2,5 mm')
    add(mref, 'Connector_Generic:Conn_01x02', f'MOTOR {nom}',
        'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal',
        {'1': f'{lado}_A', '2': f'{lado}_B'}, G, 'Clema de tornillo 2 polos, paso 5,08 mm')

# ---------------------------------------------------------------- 6. Sensores
G = '6. Sensores'
# Bus I²C de los dos VL53L0X. Misma dirección de fábrica (0x29): XSHUT permite cambiarla al arrancar.
R('R4', '4.7k', '+3V3', 'I2C_SDA', G)
R('R5', '4.7k', '+3V3', 'I2C_SCL', G)
for ref, s, nom in (('J4', 'IZQ', 'DISTANCIA IZQ'), ('J5', 'DER', 'DISTANCIA DER')):
    add(ref, 'Connector_Generic:Conn_01x05', nom, TIRA.format(n=5),
        {'1': '+3V3', '2': 'GND', '3': 'I2C_SCL', '4': 'I2C_SDA', '5': f'XSHUT_{s}'}, G,
        'Tira macho 1×5, 2,54 mm. Cable Dupont al módulo VL53L0X')
for ref, s, nom in (('J6', 'IZQ', 'SUELO IZQ'), ('J7', 'DER', 'SUELO DER')):
    add(ref, 'Connector_Generic:Conn_01x03', nom, TIRA.format(n=3),
        {'1': '+3V3', '2': 'GND', '3': f'LINEA_{s}'}, G,
        'Tira macho 1×3, 2,54 mm. Cable Dupont al módulo QRE1113 analógico')

# ---------------------------------------------------------------- 7. Módulo de arranque (ST4RT)
# Lo entrega el profesor. Pines + (2,8–5,2 V), − , S (START) y K (KILL). Orden físico de los pines
# SIN CONFIRMAR: el cable Dupont se hace a medida. Se alimenta a 3,3 V para que S y K no pasen de 3,3 V.
# Pull-down de 100 k: sin módulo, la ESP32 lee "no arrancar".
G = '7. Modulo de arranque'
add('J8', 'Connector_Generic:Conn_01x04', 'ARRANQUE ST4RT', TIRA.format(n=4),
    {'1': '+3V3', '2': 'GND', '3': 'ST_START', '4': 'ST_KILL'}, G,
    'Tira macho 1×4, 2,54 mm. Cable Dupont a medida hasta el módulo')
R('R6', '100k', 'ST_START', 'GND', G)
R('R7', '100k', 'ST_KILL', 'GND', G)

# ---------------------------------------------------------------- Mecánica
G = '8. Taladros'
for i in range(1, 5):
    add(f'H{i}', 'Mechanical:MountingHole', 'M3', 'MountingHole:MountingHole_3.2mm_M3', {}, G)

# Redes alimentadas por pines pasivos (necesitan PWR_FLAG en el ERC)
POWER_FLAGS = ['GND', 'VBAT', 'V5_ESP']
