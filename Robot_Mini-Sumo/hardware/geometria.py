"""Parámetros mecánicos del robot (fuente única para la PCB y el modelo 3D).

Sistema de coordenadas del robot (mm):
    X: de izquierda (0) a derecha (100)
    Y: de delante (0, filo de la cuña) a detrás (100)   ← igual que el eje Y de KiCad (hacia abajo)
    Z: desde el suelo hacia arriba
Todo debe caber en 100 × 100 en planta; diseñamos a 98 × 98 para tener 1 mm de margen por lado.
"""

# ---- Envolvente
ENV_X0, ENV_X1 = 1.0, 99.0
ENV_Y0, ENV_Y1 = 1.0, 99.0

# ---- Ruedas y motores (N20 con reductora)
RUEDA_D = 30.0            # diámetro exterior con neumático
RUEDA_ANCHO = 10.0
RUEDA_X_EXT = 1.5         # cara exterior de la rueda izquierda
MOTOR_LARGO = 26.0        # reductora 9 + motor 15 + tapa/terminales 2
MOTOR_ANCHO = 12.0        # en Y
MOTOR_ALTO = 10.0         # en Z (caras planas arriba/abajo)
EJE_Z = RUEDA_D / 2       # altura del eje
EJE_Y_DEL = 47.0          # eje delantero
EJE_Y_TRAS = 81.0         # eje trasero
HOLGURA_RUEDA_MOTOR = 1.0

RUEDA_X_INT = RUEDA_X_EXT + RUEDA_ANCHO                        # 11.5
MOTOR_IZQ_X = (RUEDA_X_INT + HOLGURA_RUEDA_MOTOR,
               RUEDA_X_INT + HOLGURA_RUEDA_MOTOR + MOTOR_LARGO)   # 12.5 .. 38.5
MOTOR_DER_X = (100 - MOTOR_IZQ_X[1], 100 - MOTOR_IZQ_X[0])        # 61.5 .. 87.5
MOTOR_TOP_Z = EJE_Z + MOTOR_ALTO / 2                              # 20.0

# ---- PCB (base estructural, apoyada sobre los motores)
PCB_X0, PCB_X1 = 13.0, 87.0     # 74 mm: libra las ruedas (cara interior en x = 11.5)
PCB_Y0, PCB_Y1 = 30.0, 92.0     # 62 mm: por delante va la cuña; por detrás, las torretas de la carcasa
PCB_Z0 = MOTOR_TOP_Z            # cara inferior de la PCB
PCB_GROSOR = 1.6
PCB_RADIO_ESQUINA = 2.0

# ---- Tornillería: 8 × M2. Las 4 exteriores atraviesan carcasa + PCB + cuna (tornillo largo).
TALADRO_M2 = 2.2
TALADROS = [
    # (x, y, pieza que hay debajo)
    (17.0, 37.5, 'frontal'), (83.0, 37.5, 'frontal'),
    (17.0, 56.5, 'frontal'), (83.0, 56.5, 'frontal'),
    (17.0, 71.5, 'trasera'), (83.0, 71.5, 'trasera'),
    (17.0, 89.6, 'trasera'), (83.0, 89.6, 'trasera'),
]
TALADROS_CARCASA = [(17.0, 37.5), (83.0, 37.5), (17.0, 89.6), (83.0, 89.6)]

# ---- Cuña (rampa): recta desde el filo (y = ENV_Y0, z = 0) hasta el borde delantero de la PCB
import math as _m
RAMPA_ANGULO = _m.degrees(_m.atan2(PCB_Z0, PCB_Y0 - ENV_Y0))   # ≈ 34,6°
RAMPA_Y_CUERPO = 4.0            # la pieza impresa empieza aquí; delante solo va la cuchilla
RAMPA_Y_FIN = 31.0              # fin de la rampa a todo lo ancho (las ruedas empiezan en y = 32)
RAMPA_SUELO_Z = 1.5             # holgura de la cara inferior (rampa y cunas: fondo plano, se imprime sin soportes)
CUCHILLA_GROSOR = 0.4           # chapa de acero (galga / fleje)
CUCHILLA_Y1 = 16.0              # la cuchilla cubre la rampa hasta aquí


def rampa_z(y):
    """Altura de la superficie de la rampa en la coordenada y."""
    return min(max(0.0, (y - ENV_Y0) * _m.tan(_m.radians(RAMPA_ANGULO))), PCB_Z0)

# ---- Pads de los cables de los motores (x del pad 1 y del pad 2, y): a cada lado, junto a su driver.
#      Fuera de las zonas de apoyo de los motores; el cable llega por un canal de la cuna.
PAD_MOTOR_X_IZQ = (21.5, 26.1)
PAD_MOTOR_X_DER = (73.9, 78.5)
PAD_MOTOR_Y_DEL, PAD_MOTOR_Y_TRAS = 55.2, 71.6

# ---- Zonas de la cara inferior de la PCB ocupadas por motores (sin componentes THT)
ZONAS_MOTOR = [
    (MOTOR_IZQ_X[0], EJE_Y_DEL - MOTOR_ANCHO / 2, MOTOR_IZQ_X[1], EJE_Y_DEL + MOTOR_ANCHO / 2),
    (MOTOR_DER_X[0], EJE_Y_DEL - MOTOR_ANCHO / 2, MOTOR_DER_X[1], EJE_Y_DEL + MOTOR_ANCHO / 2),
    (MOTOR_IZQ_X[0], EJE_Y_TRAS - MOTOR_ANCHO / 2, MOTOR_IZQ_X[1], EJE_Y_TRAS + MOTOR_ANCHO / 2),
    (MOTOR_DER_X[0], EJE_Y_TRAS - MOTOR_ANCHO / 2, MOTOR_DER_X[1], EJE_Y_TRAS + MOTOR_ANCHO / 2),
]

# ---- Piezas impresas bajo la PCB
CUNA_DEL_Y = (31.0, 60.0)       # pieza frontal (rampa + cuna de los motores delanteros)
CUNA_TRAS_Y = (68.0, 99.0)      # pieza trasera (cuna de los motores traseros + parachoques)
CUNA_Z0 = RAMPA_SUELO_Z         # cara inferior de las cunas (mismo plano que la rampa)
CANAL_X = (40.5, 59.5)          # canal central entre motores (lastre)

# ---- Lastre: bloques de acero bajo la PCB (entre cunas y en el canal central)
LASTRE_Z0, LASTRE_Z1 = 2.0, 17.0

# ---- Carcasa superior
CARCASA_Y0 = 25.0               # pared frontal (delante de la PCB, apoyada en la rampa)
CARCASA_PARED = 1.6
TECHO_Z = 39.0                  # cara inferior del techo (libra la DevKit: su cara superior queda a ~37,5)
TECHO_GROSOR = 1.6

# ---- Componentes comerciales (cotas aproximadas)
TOF_MODULO = (18.0, 13.0, 1.6)  # VL53L0X tamaño Pololu/mini (ancho, alto, grosor)
QRE_MODULO = (7.6, 14.0, 3.0)   # QRE1113 analógico (tipo SparkFun)
BATERIA = (55.0, 31.0, 14.0)    # LiPo 2S 450-650 mAh
LINEA_DEL = [(17.0, 22.0), (83.0, 22.0)]    # centros de los QRE delanteros (en la rampa, dentro de la carcasa)
LINEA_TRAS = [(25.0, 94.3), (75.0, 94.3)]   # centros de los QRE traseros (en el parachoques)

# ---- ESP32-S3-DevKitC-1 enchufada en tiras hembra, a lo largo del robot y centrada en x.
#      Antena hacia delante, conectores USB hacia la pared trasera (se enchufa el cable por detrás).
#      Cotas relativas al pin J1-1 (x hacia J3, y hacia los USB), según el plano de Espressif v1.1.
DEVKIT_PASO = 2.54
DEVKIT_FILAS = 22.86            # distancia entre las filas J1 y J3 (0,9")
DEVKIT_PLACA = (-1.27, -1.2, 24.13, 61.5)    # placa de la DevKit (x0, y0, x1, y1) ≈ 25,4 × 62,7
DEVKIT_ANTENA = (2.5, -7.0, 20.4, -1.2)      # antena del módulo, que vuela por delante de la placa
DEVKIT_USB_Y1 = 62.8            # cara de los conectores USB
DEVKIT_X = 50.0 - DEVKIT_FILAS / 2           # x del pin J1-1 (fila J1 a la izquierda)
DEVKIT_Y = ENV_Y1 - CARCASA_PARED - DEVKIT_USB_Y1   # y del pin J1-1: USB a ras de la pared trasera
ZOCALO_ALTO = 8.5               # tira hembra estándar
DEVKIT_SEPARADOR = 2.5          # plástico de la tira macho de la DevKit
DEVKIT_Z0 = PCB_Z0 + PCB_GROSOR + ZOCALO_ALTO + DEVKIT_SEPARADOR   # cara inferior de la DevKit
DEVKIT_ALTO = 1.6 + 3.3         # placa + componentes (módulo, USB, botones)
