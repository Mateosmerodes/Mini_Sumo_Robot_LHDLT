"""Definición eléctrica de la placa base del robot (fuente única de verdad).

Cada componente: referencia, símbolo, valor, huella, {pin: red}, grupo del esquemático y MPN.
Los pines que no aparecen en el diccionario se marcan como "sin conexión".
gen_sch.py y gen_pcb.py leen este fichero.
"""

PROJECT = 'robot_sumo'
TITLE = 'Robot Mini-Sumo · Placa base'
COMPANY = 'HOMBRES DE LAS TABERNAS'
REV = 'v1.0'

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
add('F1', 'Device:Fuse', '10A', 'Fuse:Fuse_2512_6332Metric', {'1': 'VBAT_REV', '2': 'VBAT'}, G,
    'Fusible rápido 2512 10 A')
# Reserva en VBAT (además de 10 µF por driver): cerámicos, más bajos que un electrolítico
C('C1', '22u 25V', 'VBAT', 'GND', G, C1206)
C('C2', '22u 25V', 'VBAT', 'GND', G, C1206)
# Medida de batería: 8,4 V -> 2,08 V
R('R3', '100k', 'VBAT', 'VBAT_SENSE', G)
R('R4', '33k', 'VBAT_SENSE', 'GND', G)
C('C3', '100n', 'VBAT_SENSE', 'GND', G)

# Buck 5,4 V (luego diodo OR -> +5V ~5,0 V)
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
add('L1', 'Device:L', '3.3u', 'Inductor_SMD:L_Bourns-SRN4018', {'1': 'BUCK_SW', '2': 'V5_BUCK'}, G,
    'SRN4018-3R3M (3,3 µH, Isat ≥ 2,5 A)')
R('R7', '62k', 'V5_BUCK', 'BUCK_FB', G)   # Vout = 0,768·(1+62k/10k) = 5,53 V
R('R8', '10k', 'BUCK_FB', 'GND', G)
C('C8', '22u 10V', 'V5_BUCK', 'GND', G, C1206)
C('C9', '22u 10V', 'V5_BUCK', 'GND', G, C1206)
add('D2', 'Diode:SS34', 'SS34', 'Diode_SMD:D_SMA', {'1': '+5V', '2': 'V5_BUCK'}, G)

# LDO 3,3 V
G = 'LDO 3,3 V'
add('U3', 'Regulator_Linear:AMS1117-3.3', 'AMS1117-3.3', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
    {'1': 'GND', '2': '+3V3', '3': '+5V'}, G, 'AMS1117-3.3')
C('C10', '22u 10V', '+5V', 'GND', G, C1206)
C('C11', '22u 10V', '+3V3', 'GND', G, C1206)
C('C12', '100n', '+3V3', 'GND', G)
add('D3', 'Device:LED', 'verde', 'LED_SMD:LED_0603_1608Metric', {'1': 'LED_PWR_K', '2': '+3V3'}, G)
R('R9', '1k', 'LED_PWR_K', 'GND', G)

# USB-C (programación y alimentación de banco)
G = 'USB-C'
add('J2', 'Connector:USB_C_Receptacle_USB2.0_16P', 'USB-C',
    'Connector_USB:USB_C_Receptacle_XKB_U262-16XN-4BVC11',
    {'A1': 'GND', 'B1': 'GND', 'A12': 'GND', 'B12': 'GND', 'SH': 'GND',
     'A4': 'VUSB', 'A9': 'VUSB', 'B4': 'VUSB', 'B9': 'VUSB',
     'A5': 'USB_CC1', 'B5': 'USB_CC2',
     'A6': 'USB_DP', 'B6': 'USB_DP', 'A7': 'USB_DN', 'B7': 'USB_DN'}, G, 'XKB U262-161N-4BVC11 (USB-C vertical)')
R('R10', '5.1k', 'USB_CC1', 'GND', G)
R('R11', '5.1k', 'USB_CC2', 'GND', G)
add('U4', 'Power_Protection:USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6',
    {'1': 'USB_DN', '6': 'USB_DN', '3': 'USB_DP', '4': 'USB_DP', '2': 'GND', '5': 'VUSB'}, G)
add('D1', 'Diode:SS34', 'SS34', 'Diode_SMD:D_SMA', {'1': '+5V', '2': 'VUSB'}, G)

# ---------------------------------------------------------------- ESP32-S3
G = 'ESP32-S3'
esp = {
    '1': 'GND', '40': 'GND', '41': 'GND', '2': '+3V3', '3': 'ESP_EN',
    '27': 'BOOT',                                   # IO0
    '39': 'LINE_FL', '38': 'LINE_FR',               # IO1, IO2
    '15': 'LED_DIN',                                # IO3
    '4': 'LINE_RL', '5': 'LINE_RR',                 # IO4, IO5
    '6': 'ISENSE_M1', '7': 'ISENSE_M2',             # IO6, IO7
    '12': 'ISENSE_M3', '17': 'ISENSE_M4',           # IO8, IO9
    '18': 'VBAT_SENSE',                             # IO10
    '19': 'M1_IN1', '20': 'M1_IN2',                 # IO11, IO12
    '21': 'M2_IN1', '22': 'M2_IN2',                 # IO13, IO14
    '8': 'M3_IN1', '9': 'M3_IN2',                   # IO15, IO16
    '10': 'M4_IN1', '11': 'M4_IN2',                 # IO17, IO18
    '13': 'USB_DN', '14': 'USB_DP',                 # IO19, IO20
    '23': 'DRV_nSLEEP',                             # IO21
    '28': 'XSHUT_R', '29': 'XSHUT_B',               # IO35, IO36
    '30': 'IR_START',                               # IO37
    '31': 'DRV_nFAULT',                             # IO38
    '32': 'I2C_SDA', '33': 'I2C_SCL',               # IO39, IO40
    '34': 'XSHUT_L', '35': 'XSHUT_FL',              # IO41, IO42
    '24': 'XSHUT_F', '25': 'XSHUT_FR',              # IO47, IO48
    '37': 'AUX_TX', '36': 'AUX_RX',                 # TXD0 (IO43), RXD0 (IO44)
    # IO45 (26) e IO46 (16) son pines de arranque: se dejan libres
}
add('U1', 'RF_Module:ESP32-S3-WROOM-1', 'ESP32-S3-WROOM-1-N8R2', 'RF_Module:ESP32-S3-WROOM-1', esp, G,
    'ESP32-S3-WROOM-1-N8R2 (NO usar variantes R8: GPIO35-37)')
C('C13', '22u 10V', '+3V3', 'GND', G, C1206)
C('C14', '100n', '+3V3', 'GND', G)
R('R12', '10k', '+3V3', 'ESP_EN', G)
C('C15', '1u', 'ESP_EN', 'GND', G)
add('SW2', 'Switch:SW_Push', 'RESET', 'Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2', {'1': 'ESP_EN', '2': 'GND'}, G)
R('R13', '10k', '+3V3', 'BOOT', G)
add('SW3', 'Switch:SW_Push', 'BOOT/USER', 'Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2', {'1': 'BOOT', '2': 'GND'}, G)
add('D4', 'LED:WS2812B-2020', 'WS2812B-2020', 'LED_SMD:LED_WS2812B-2020_PLCC4_2.0x2.0mm',
    {'4': '+3V3', '2': 'GND', '3': 'LED_DIN'}, G)
C('C16', '100n', '+3V3', 'GND', G)

# ---------------------------------------------------------------- Drivers de motor
# ITRIP = VREF / (A_IPROPI · R_IPROPI) = 1,65 V / (455 µA/A · 1,5 kΩ) ≈ 2,4 A
G = 'Drivers comunes'
R('R14', '10k', '+3V3', 'DRV_VREF', G)
R('R15', '10k', 'DRV_VREF', 'GND', G)
C('C17', '100n', 'DRV_VREF', 'GND', G)
R('R16', '10k', '+3V3', 'DRV_nFAULT', G)
R('R17', '100k', 'DRV_nSLEEP', 'GND', G)   # motores parados mientras el ESP32 arranca

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
R('R60', '2.2k', '+3V3', 'I2C_SDA', G)
R('R61', '2.2k', '+3V3', 'I2C_SCL', G)
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
# Receptor IR de arranque (RC5) en la carcasa, con filtro RC de alimentación
R('R62', '100', '+3V3', 'IR_VS', G)
C('C62', '4.7u', 'IR_VS', 'GND', G, C0805)
add('J17', 'Connector_Generic:Conn_01x03', 'IR START (VS1838B)', JST_SH.format(n=3),
    {'1': 'IR_VS', '2': 'GND', '3': 'IR_START'}, G, 'JST SH 3P SMD vertical (BM03B-SRSS-TB)')
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
POWER_FLAGS = ['GND', 'VBAT', '+5V', 'VBAT_RAW']
