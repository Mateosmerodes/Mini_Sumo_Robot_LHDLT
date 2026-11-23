"""Geometría del chasis del robot mini-sumo LHDT v2 (fuente única de verdad).

Este fichero NO depende de ningún programa de CAD. Describe cada pieza como un árbol de
operaciones sencillas (cajas, cilindros, cajas giradas, uniones y restas) que luego
construyen dos "motores":

  * ChasisLHDT.py           -> Autodesk Fusion 360 (script de Utilidades > Scripts y complementos)
  * ../../construir_cadquery.py -> CadQuery (STEP, STL, comprobaciones e imágenes, sin Fusion)

Los dos leen estas mismas cotas, así que el modelo de Fusion y los STEP/STL son el mismo.

Sistema de coordenadas del robot (mm), el mismo que en la v1:
    x: de izquierda (0) a derecha (100)
    y: de delante (0, filo de la cuña) a detrás (100)
    z: desde el suelo hacia arriba
En Fusion el robot sale centrado en el origen, con el frente hacia +Y y Z hacia arriba
(X_fusion = x - 50, Y_fusion = 50 - y, Z_fusion = z).

Cotas con 🔶 = NO verificadas con la pieza real: medirlas con el calibre y cambiar aquí.
"""
import math

# =====================================================================================
# 1. PARÁMETROS (todo en mm)
# =====================================================================================

# ---- Reglamento: 10 × 10 cm en planta. Se diseña a 98 × 98 (1 mm de margen por lado).
ENV_X0, ENV_X1 = 1.0, 99.0
ENV_Y0, ENV_Y1 = 1.0, 99.0

# ---- Suelo del chasis
Z_BAJO = 1.5            # cara inferior del chasis (holgura con el suelo del dohyo)
SUELO_GROSOR = 2.0
Z_SUELO = Z_BAJO + SUELO_GROSOR          # 3.5: cara de arriba del suelo (aquí se apoya la batería)

# ---- Ruedas y motores N20
RUEDA_D = 30.0          # 🔶 diámetro exterior de la rueda N20 comprada
RUEDA_ANCHO = 8.0       # 🔶 ancho de la rueda
RUEDA_X_EXT = 1.5       # cara exterior de la rueda izquierda
EJE_Y = 81.0            # posición del eje: atrás, para que la batería pase por delante de las ruedas
EJE_Z = RUEDA_D / 2     # 15
HOLGURA_RUEDA_MOTOR = 1.0
MOTOR_REDUCTORA = 9.0   # largo de la reductora (Pololu/N20: 9 mm)
MOTOR_LATA = 15.0       # largo del motor
MOTOR_TAPA = 2.0        # 🔶 tapa trasera con los terminales
MOTOR_ANCHO = 12.0      # sección 12 × 10 mm (caras planas arriba y abajo)
MOTOR_ALTO = 10.0
EJE_MOTOR_D = 3.0       # eje en D de 3 mm
HOLG = 0.25             # holgura de impresión en alojamientos (por lado)

RUEDA_X_INT = RUEDA_X_EXT + RUEDA_ANCHO                    # 9.5
MOTOR_X0 = RUEDA_X_INT + HOLGURA_RUEDA_MOTOR               # 10.5: cara de la reductora
MOTOR_X1 = MOTOR_X0 + MOTOR_REDUCTORA + MOTOR_LATA + MOTOR_TAPA   # 36.5: tapa trasera
MOTOR_Z0, MOTOR_Z1 = EJE_Z - MOTOR_ALTO / 2, EJE_Z + MOTOR_ALTO / 2   # 10 .. 20

# ---- PCB v2 (76 × 80 mm, 4 taladros M3). Se atornilla encima de 4 columnas.
PCB_ANCHO, PCB_LARGO, PCB_GROSOR = 76.0, 80.0, 1.6
PCB_X0 = 50.0 - PCB_ANCHO / 2      # 12: centrada (el eje de la DevKit es el eje de la placa)
PCB_Y0 = 18.0                      # borde delantero de la PCB
PCB_Z0 = 25.0                      # cara inferior de la PCB = altura de las columnas
PATAS_THT = 2.5                    # 🔶 lo que sobresalen las patillas soldadas por debajo
# Taladros desde la esquina delantera izquierda de la PCB (Robot_Mini-Sumo/docs/01-Diseno-v2-basico.md)
PCB_TALADROS_LOCAL = [(4.5, 11.0), (71.5, 11.0), (21.0, 76.0), (71.5, 76.0)]
PCB_TALADROS = [(PCB_X0 + x, PCB_Y0 + y) for x, y in PCB_TALADROS_LOCAL]
COLUMNA_D = 7.0
COLUMNA_AGUJERO_D = 2.5            # rosca directa de un tornillo M3 en el plástico
#                                    (para inserto roscado M3 de latón: poner 4.0)
COLUMNA_AGUJERO_FONDO = 12.0

# ---- Cuña (rampa) con cuchilla de acero opcional
RAMPA_ANGULO = 34.0                # grados
RAMPA_Y1 = 24.0                    # fin de la rampa (después, el suelo plano)
TAN = math.tan(math.radians(RAMPA_ANGULO))


def rampa_z(y):
    """Altura de la superficie de la rampa (recta que pasa por el filo y=ENV_Y0, z=0)."""
    return (y - ENV_Y0) * TAN


RAMPA_Z1 = rampa_z(RAMPA_Y1)       # ≈ 15.5
RAMPA_Y_PLASTICO = ENV_Y0 + Z_BAJO / TAN   # el plástico empieza donde la rampa llega a Z_BAJO
CUCHILLA = True                    # chapa de acero de 0,4 mm pegada sobre la rampa
CUCHILLA_GROSOR = 0.4
CUCHILLA_Y1 = 13.0                 # la cuchilla cubre la rampa desde el filo hasta aquí

# ---- Sensores de suelo QRE1113 (módulo analógico), boca abajo en la rampa
QRE_MODULO = (14.0, 7.6, 3.0)      # 🔶 (x, y, alto) del módulo, tumbado a lo ancho
QRE_POS = [(15.0, 13.0), (85.0, 13.0)]   # centros
QRE_CANAL = (4.0, 2.5)             # ranura para el cable por debajo de la rampa (ancho, alto)

# ---- Sensores de distancia VL53L0X, mirando al frente por encima de la rampa
TOF_MODULO = (18.0, 13.0, 1.6)     # 🔶 (ancho, alto, grosor de la placa) del módulo
TOF_COMPONENTES = 1.6              # 🔶 lo que abultan los componentes de la cara trasera
TOF_X = [30.0, 70.0]               # centros
TOF_Y = 26.0                       # cara delantera de la placa del sensor
TOF_ZC = 17.25                     # 🔶 altura del chip (supuesto en el centro del módulo)
TOF_CONO = 25.0                    # campo de visión del VL53L0X (grados, total)
TOF_VENTANA = (10.0, 8.0)          # hueco delante del chip (ancho, alto)
SOPORTE_TOF_Y = (25.0, 31.0)
SOPORTE_TOF_ANCHO = 22.0
SOPORTE_TOF_Z1 = 22.4                # por debajo de las patillas de la PCB (z 22,5)

# ---- Batería LiPo 2S: entra de lado por un túnel bajo la PCB y se sujeta con velcro
BATERIA = (55.0, 31.0, 14.0)       # 🔶 (largo en x, ancho en y, alto) LiPo 2S 450 mAh de la v1
TUNEL_Y = (32.5, 66.0)             # entre el tope delantero y el cuerpo trasero
TOPE_BATERIA_Z1 = 8.0              # altura del murete delantero
BATERIA_Y0 = 33.5

# ---- Cuerpo trasero: cunas de los motores, lastre y columnas traseras
CUERPO_Y = (66.0, 98.0)
CUERPO_X = (11.0, 89.0)
CUERPO_Z1 = MOTOR_Z1               # 20: a ras de la cara de arriba de los motores
HUECO_CABLES_X = 40.4              # el alojamiento sigue hasta aquí: sitio para terminales y cables
LASTRE_CENTRAL = (42.0, 58.0, 67.6, 96.4)          # (x0, x1, y0, y1) entre los motores
LASTRE_TRASERO = [(12.6, 29.0, EJE_Y + 9.6, 96.4), (61.6, 79.4, EJE_Y + 9.6, 96.4)]

# ---- Abrazaderas de los motores (pieza aparte, 2 tornillos M2 cada una)
ABRAZ_X = (21.0, 34.0)             # sobre la lata del motor
ABRAZ_Y = (EJE_Y - 9.4, EJE_Y + 9.4)
ABRAZ_GROSOR = 2.0
ABRAZ_TORNILLOS_Y = (EJE_Y - 8.05, EJE_Y + 8.05)
M2_PASO_D = 2.2
M2_ROSCA_D = 1.7                   # rosca directa en el plástico
M2_FONDO = 8.0

# ---- Texto grabado en la cara inferior (requisito: base hecha por el equipo)
TEXTO_GRANDE = 'LHDT'
TEXTO_PEQUENO = 'LOS HOMBRES DE LAS TABERNAS'
TEXTO_PROFUNDIDAD = 0.6

# ---- Densidades para estimar masas
DENS_PETG = 1.27       # g/cm³
FACTOR_IMPRESION = 0.6  # 🔶 masa real / masa maciza (3 perímetros + 30-40 % de relleno)
DENS_ACERO = 7.85
DENS_PLOMO = 11.3

# =====================================================================================
# 2. PRIMITIVAS (árbol de operaciones; los motores de CAD las interpretan)
# =====================================================================================


def box(x0, x1, y0, y1, z0, z1):
    return ('box', min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))


def cil(eje, r, a0, a1, c1, c2):
    """Cilindro de radio r a lo largo de 'x', 'y' o 'z' entre a0 y a1.
    (c1, c2) = las otras dos coordenadas del eje, en orden (x, y, z) sin la del eje."""
    return ('cyl', eje, r, a0, a1, c1, c2)


def caja_girada_x(x0, x1, yc, zc, largo_y, alto_z, angulo):
    """Caja de ancho x0..x1 cuyo perfil (largo_y × alto_z) está centrado en (yc, zc)
    y girado 'angulo' grados alrededor del eje X (positivo: el lado de +y sube)."""
    a = math.radians(angulo)
    u = (0.0, math.cos(a), math.sin(a))     # dirección del largo
    w = (0.0, -math.sin(a), math.cos(a))    # dirección del alto
    return ('obox', ((x0 + x1) / 2, yc, zc), (1.0, 0.0, 0.0), u, w, x1 - x0, largo_y, alto_z)


def union(*hijos):
    return ('union', list(hijos))


def resta(base, *herramientas):
    return ('cut', base, list(herramientas))


def espejo(op):
    """Simetría respecto al plano x = 50."""
    t = op[0]
    if t == 'box':
        _, x0, x1, y0, y1, z0, z1 = op
        return box(100 - x1, 100 - x0, y0, y1, z0, z1)
    if t == 'cyl':
        _, eje, r, a0, a1, c1, c2 = op
        if eje == 'x':
            return ('cyl', 'x', r, 100 - a1, 100 - a0, c1, c2)
        return ('cyl', eje, r, a0, a1, 100 - c1, c2)
    if t == 'obox':
        _, c, l, u, w, dl, du, dw = op
        f = lambda v: (-v[0], v[1], v[2])
        return ('obox', (100 - c[0], c[1], c[2]), f(l), f(u), f(w), dl, du, dw)
    if t == 'union':
        return ('union', [espejo(h) for h in op[1]])
    if t == 'cut':
        return ('cut', espejo(op[1]), [espejo(h) for h in op[2]])
    raise ValueError(t)


def y_ambos(op):
    """La operación y su simétrica."""
    return [op, espejo(op)]


# =====================================================================================
# 3. PIEZAS IMPRIMIBLES
# =====================================================================================


def _rampa():
    """Cuña maciza a todo lo ancho: caja cortada por un plano inclinado RAMPA_ANGULO."""
    bloque = box(ENV_X0, ENV_X1, RAMPA_Y_PLASTICO, RAMPA_Y1, Z_BAJO, RAMPA_Z1)
    # Caja enorme cuya cara inferior es el plano de la rampa (pasa por y=ENV_Y0, z=0)
    grande = 200.0
    a = math.radians(RAMPA_ANGULO)
    # Punto del plano y normal hacia arriba-delante
    py, pz = ENV_Y0 + 30 * math.cos(a), 30 * math.sin(a)
    ny, nz = -math.sin(a), math.cos(a)
    yc, zc = py + ny * grande / 2, pz + nz * grande / 2
    sobra = caja_girada_x(ENV_X0 - 5, ENV_X1 + 5, yc, zc, grande, grande, RAMPA_ANGULO)
    herr = [sobra]
    qx, qy, qh = QRE_MODULO
    cw, ch = QRE_CANAL
    for xc, yc_ in QRE_POS:
        # Alojamiento del QRE abierto por abajo (el sensor mira al suelo)
        herr.append(box(xc - qx / 2 - HOLG, xc + qx / 2 + HOLG, yc_ - qy / 2 - HOLG, yc_ + qy / 2 + HOLG,
                        Z_BAJO - 1, Z_BAJO + qh + HOLG))
        # Ranura del cable por debajo, hasta la cara trasera de la rampa
        herr.append(box(xc - cw / 2, xc + cw / 2, yc_, RAMPA_Y1 + 1, Z_BAJO - 1, Z_BAJO + ch))
    return resta(bloque, *herr)


def _soporte_tof(xc):
    w2 = SOPORTE_TOF_ANCHO / 2
    y0, y1 = SOPORTE_TOF_Y
    bloque = box(xc - w2, xc + w2, y0, y1, Z_SUELO - 0.5, SOPORTE_TOF_Z1)
    tw, th, tt = TOF_MODULO
    z0 = TOF_ZC - th / 2
    vw, vh = TOF_VENTANA
    herr = [
        # Ranura de la placa del sensor (se mete desde arriba antes de poner la PCB)
        box(xc - tw / 2 - HOLG, xc + tw / 2 + HOLG, TOF_Y, TOF_Y + tt + 2 * HOLG, z0 - HOLG, SOPORTE_TOF_Z1 + 1),
        # Hueco para los componentes de la cara trasera del módulo
        box(xc - tw / 2 + 2, xc + tw / 2 - 2, TOF_Y + tt, TOF_Y + tt + 2 * HOLG + TOF_COMPONENTES,
            z0 + 1, SOPORTE_TOF_Z1 + 1),
        # Ventana delantera
        box(xc - vw / 2, xc + vw / 2, y0 - 1, TOF_Y + 0.1, TOF_ZC - vh / 2, TOF_ZC + vh / 2),
        # Salida de cables por detrás (soldarlos directamente al módulo)
        box(xc - 4, xc + 4, TOF_Y, y1 + 1, z0 + 2, SOPORTE_TOF_Z1 + 1),
    ]
    return resta(bloque, *herr)


def _cuerpo_trasero():
    x0, x1 = CUERPO_X
    y0, y1 = CUERPO_Y
    s = box(x0, x1, y0, y1, Z_BAJO, CUERPO_Z1)
    herr = []
    w = MOTOR_ANCHO / 2 + HOLG
    for h in y_ambos(box(x0 - 1, HUECO_CABLES_X, EJE_Y - w, EJE_Y + w, MOTOR_Z0 - HOLG, CUERPO_Z1 + 1)):
        herr.append(h)                       # alojamiento del motor (abierto por arriba y por fuera)
    lx0, lx1, ly0, ly1 = LASTRE_CENTRAL
    herr.append(box(lx0, lx1, ly0, ly1, Z_SUELO, CUERPO_Z1 + 1))
    for lx0, lx1, ly0, ly1 in LASTRE_TRASERO:
        herr.append(box(lx0, lx1, ly0, ly1, Z_SUELO, CUERPO_Z1 + 1))
    for yt in ABRAZ_TORNILLOS_Y:             # roscas M2 de las abrazaderas
        for h in y_ambos(cil('z', M2_ROSCA_D / 2, CUERPO_Z1 - M2_FONDO, CUERPO_Z1 + 1,
                             sum(ABRAZ_X) / 2, yt)):
            herr.append(h)
    return resta(s, *herr)


def _columnas():
    cols, agujeros = [], []
    for x, y in PCB_TALADROS:
        cols.append(cil('z', COLUMNA_D / 2, Z_SUELO - 0.5, PCB_Z0, x, y))
        agujeros.append(cil('z', COLUMNA_AGUJERO_D / 2, PCB_Z0 - COLUMNA_AGUJERO_FONDO, PCB_Z0 + 1, x, y))
    return cols, agujeros


def _textos():
    """Textos grabados en la cara inferior (se leen mirando el robot por debajo, con el frente arriba).
    (texto, x centro, y centro, alto de letra)"""
    return [(TEXTO_GRANDE, 50.0, 46.0, 9.0), (TEXTO_PEQUENO, 50.0, 57.0, 3.2)]


def chasis():
    """Base: rampa + suelo + soportes de los sensores + túnel de batería + cuerpo trasero + columnas."""
    suelo = box(CUERPO_X[0], CUERPO_X[1], RAMPA_Y1 - 0.5, CUERPO_Y[0] + 0.5, Z_BAJO, Z_SUELO)
    tope = box(CUERPO_X[0], CUERPO_X[1], SOPORTE_TOF_Y[1] - 0.5, TUNEL_Y[0], Z_SUELO - 0.5, TOPE_BATERIA_Z1)
    cols, agujeros = _columnas()
    partes = [_rampa(), suelo, tope, _cuerpo_trasero()] + [_soporte_tof(x) for x in TOF_X] + cols
    return resta(union(*partes), *agujeros)


def abrazadera():
    """Abrazadera del motor izquierdo (la derecha es igual: se imprimen 2)."""
    s = box(ABRAZ_X[0], ABRAZ_X[1], ABRAZ_Y[0], ABRAZ_Y[1], CUERPO_Z1, CUERPO_Z1 + ABRAZ_GROSOR)
    return resta(s, *[cil('z', M2_PASO_D / 2, CUERPO_Z1 - 1, CUERPO_Z1 + ABRAZ_GROSOR + 1, sum(ABRAZ_X) / 2, y)
                      for y in ABRAZ_TORNILLOS_Y])


def cuchilla():
    """Chapa de acero de 0,4 mm sobre la rampa, del filo (z = 0) a CUCHILLA_Y1."""
    a = math.radians(RAMPA_ANGULO)
    largo = (CUCHILLA_Y1 - ENV_Y0) / math.cos(a)
    yc = ENV_Y0 + largo / 2 * math.cos(a) - CUCHILLA_GROSOR / 2 * math.sin(a)
    zc = largo / 2 * math.sin(a) + CUCHILLA_GROSOR / 2 * math.cos(a)
    return caja_girada_x(ENV_X0, ENV_X1, yc, zc, largo, CUCHILLA_GROSOR, RAMPA_ANGULO)


# =====================================================================================
# 4. PIEZAS DE REFERENCIA (no se imprimen: sirven para ver el montaje y buscar choques)
# =====================================================================================


def motor_izq():
    w, h = MOTOR_ANCHO / 2, MOTOR_ALTO / 2
    cuerpo = box(MOTOR_X0, MOTOR_X1 - MOTOR_TAPA, EJE_Y - w, EJE_Y + w, EJE_Z - h, EJE_Z + h)
    tapa = box(MOTOR_X1 - MOTOR_TAPA, MOTOR_X1, EJE_Y - 4, EJE_Y + 4, EJE_Z - 3.5, EJE_Z + 3.5)
    eje = cil('x', EJE_MOTOR_D / 2, RUEDA_X_EXT + 1, MOTOR_X0, EJE_Y, EJE_Z)
    return union(cuerpo, tapa, eje)


def rueda_izq():
    return resta(cil('x', RUEDA_D / 2, RUEDA_X_EXT, RUEDA_X_INT, EJE_Y, EJE_Z),
                 cil('x', RUEDA_D / 2 - 6, RUEDA_X_EXT - 1, RUEDA_X_EXT + 2, EJE_Y, EJE_Z))


def bateria():
    l, a, h = BATERIA
    return box(50 - l / 2, 50 + l / 2, BATERIA_Y0, BATERIA_Y0 + a, Z_SUELO, Z_SUELO + h)


def pcb():
    s = box(PCB_X0, PCB_X0 + PCB_ANCHO, PCB_Y0, PCB_Y0 + PCB_LARGO, PCB_Z0, PCB_Z0 + PCB_GROSOR)
    return resta(s, *[cil('z', 1.6, PCB_Z0 - 1, PCB_Z0 + 3, x, y) for x, y in PCB_TALADROS])


def patillas_pcb():
    """Zona bajo la PCB donde asoman las patillas soldadas (no puede haber plástico salvo columnas)."""
    return box(PCB_X0, PCB_X0 + PCB_ANCHO, PCB_Y0, PCB_Y0 + PCB_LARGO, PCB_Z0 - PATAS_THT, PCB_Z0)


def devkit():
    """ESP32-S3-DevKitC-1 pinchada (pin J1-1 en (26,57; 13) de la PCB; USB hacia atrás)."""
    x1 = PCB_X0 + 26.57 - 1.27
    y1 = PCB_Y0 + 13.0 - 1.2
    z0 = PCB_Z0 + PCB_GROSOR + 8.5 + 2.5
    return box(x1, x1 + 25.4, y1, y1 + 62.7, z0, z0 + 4.9)


def tof(xc):
    tw, th, tt = TOF_MODULO
    return box(xc - tw / 2, xc + tw / 2, TOF_Y, TOF_Y + tt, TOF_ZC - th / 2, TOF_ZC + th / 2)


def qre(xc, yc):
    qx, qy, qh = QRE_MODULO
    return box(xc - qx / 2, xc + qx / 2, yc - qy / 2, yc + qy / 2, Z_BAJO, Z_BAJO + qh)


# =====================================================================================
# 5. LISTA DE PIEZAS
# =====================================================================================

# nombre: (función, ¿se imprime?, color RGB para las imágenes)
def piezas():
    p = {
        'chasis': (chasis(), True, (0.95, 0.55, 0.10)),
        'abrazadera_motor_izq': (abrazadera(), True, (0.20, 0.20, 0.22)),
        'abrazadera_motor_der': (espejo(abrazadera()), True, (0.20, 0.20, 0.22)),
    }
    if CUCHILLA:
        p['cuchilla_acero'] = (cuchilla(), False, (0.75, 0.77, 0.80))
    return p


def referencias():
    r = {
        'motor_izq': motor_izq(), 'motor_der': espejo(motor_izq()),
        'rueda_izq': rueda_izq(), 'rueda_der': espejo(rueda_izq()),
        'bateria': bateria(), 'pcb': pcb(), 'devkit_esp32': devkit(),
    }
    for i, x in enumerate(TOF_X):
        r[f'vl53l0x_{i + 1}'] = tof(x)
    for i, (x, y) in enumerate(QRE_POS):
        r[f'qre1113_{i + 1}'] = qre(x, y)
    return r


COLORES_REF = {'motor': (0.80, 0.80, 0.82), 'rueda': (0.10, 0.10, 0.10), 'bateria': (0.15, 0.35, 0.85),
               'pcb': (0.05, 0.45, 0.20), 'devkit': (0.15, 0.15, 0.15), 'vl53l0x': (0.55, 0.20, 0.65),
               'qre1113': (0.20, 0.60, 0.80)}


def textos():
    return _textos()


def a_fusion(x, y, z):
    """Coordenadas del robot (mm) -> coordenadas de Fusion (cm, centrado, frente hacia +Y)."""
    return ((x - 50.0) / 10.0, (50.0 - y) / 10.0, z / 10.0)


def vec_a_fusion(v):
    return (v[0], -v[1], v[2])
