"""Modelo 3D paramétrico y desmontable del robot (FreeCAD, sin interfaz gráfica).

Uso:   freecadcmd hardware/mecanica/cad/robot.py
Lee:   hardware/geometria.py, hardware/mecanica/step/pcb.step (exportado de KiCad),
       hardware/mecanica/cad/pcb_componentes.json (cajas de los componentes)
Genera:
    hardware/mecanica/step/<pieza>.step      piezas sueltas (para Onshape/FreeCAD)
    hardware/mecanica/step/robot_ensamblaje.step
    hardware/mecanica/stl/<pieza>.stl        piezas imprimibles
    hardware/mecanica/cad/robot_sumo.FCStd   documento FreeCAD con todas las piezas
    hardware/mecanica/cad/_render/*.stl      mallas para render.py (no se versionan)
    hardware/mecanica/cad/informe_3d.json    masas, interferencias y envolvente

Coordenadas del modelo: X = x del robot, Y = 100 - y (delante = Y alto), Z = altura.
"""
import json
import math
import os
import sys

import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
HW = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HW)
import geometria as g  # noqa: E402

V = App.Vector
OUT_STEP = os.path.join(HW, 'mecanica', 'step')
OUT_STL = os.path.join(HW, 'mecanica', 'stl')
OUT_RENDER = os.path.join(HERE, '_render')
for d in (OUT_STEP, OUT_STL, OUT_RENDER):
    os.makedirs(d, exist_ok=True)


# ------------------------------------------------------------------ primitivas (coordenadas del robot)
def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, 100 - y1, z0))


def prisma_x(perfil_yz, x0, x1):
    """Extruye en X un perfil [(y, z), ...] dado en coordenadas del robot."""
    pts = [V(x0, 100 - y, z) for y, z in perfil_yz]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(x1 - x0, 0, 0))


def cil_x(r, x0, x1, y, z):
    return Part.makeCylinder(r, x1 - x0, V(x0, 100 - y, z), V(1, 0, 0))


def cil_y(r, y0, y1, x, z):
    return Part.makeCylinder(r, y1 - y0, V(x, 100 - y1, z), V(0, 1, 0))


def cil_z(r, z0, z1, x, y):
    return Part.makeCylinder(r, z1 - z0, V(x, 100 - y, z0))


def fuse(*shapes):
    s = shapes[0]
    for t in shapes[1:]:
        s = s.fuse(t)
    return s.removeSplitter()


def cut(s, *tools):
    for t in tools:
        s = s.cut(t)
    return s.removeSplitter()


def espejo_x(shape):
    return shape.mirror(V(50, 0, 0), V(1, 0, 0))


# ------------------------------------------------------------------ piezas
MOTORES = [(lado, eje) for eje in (g.EJE_Y_DEL, g.EJE_Y_TRAS) for lado in ('izq', 'der')]
HOLG = 0.25   # holgura de impresión en alojamientos


def bolsillos_motor(eje):
    """Alojamientos de los dos motores de un eje (abiertos por arriba y por la cara exterior)."""
    w = g.MOTOR_ANCHO / 2 + HOLG
    z0 = g.EJE_Z - g.MOTOR_ALTO / 2 - HOLG
    izq = box(g.MOTOR_IZQ_X[0] - 2, g.MOTOR_IZQ_X[1] + HOLG, eje - w, eje + w, z0, g.PCB_Z0 + 0.1)
    return [izq, espejo_x(izq)]


def insertos(lista):
    """Taladros para insertos roscados M2 (Ø3,2 × 5 mm) desde la cara de apoyo de la PCB."""
    return [cil_z(1.6, g.PCB_Z0 - 5, g.PCB_Z0 + 0.1, x, y) for x, y in lista]


def pieza_frontal():
    y0, y1 = g.CUNA_DEL_Y
    rampa = prisma_x([(g.RAMPA_Y_CUERPO, g.RAMPA_SUELO_Z), (g.RAMPA_Y_CUERPO, g.rampa_z(g.RAMPA_Y_CUERPO)),
                      (g.PCB_Y0, g.PCB_Z0), (g.RAMPA_Y_FIN, g.PCB_Z0), (g.RAMPA_Y_FIN, g.RAMPA_SUELO_Z)],
                     g.ENV_X0, g.ENV_X1)
    cuna = box(g.MOTOR_IZQ_X[0], g.MOTOR_DER_X[1], y0, y1, g.CUNA_Z0, g.PCB_Z0)
    s = fuse(rampa, cuna)
    herr = bolsillos_motor(g.EJE_Y_DEL)
    herr.append(box(g.CANAL_X[0], g.CANAL_X[1], y0, y1 + 0.1, g.CUNA_Z0 - 0.1, g.LASTRE_Z1))   # lastre
    for xm in (g.MOTOR_IZQ_X[1] - 1.5, g.MOTOR_DER_X[0] - 0.6):                                 # cables
        herr.append(box(xm, xm + 2.1, g.EJE_Y_DEL - 3.5, g.EJE_Y_DEL + 3.5, g.EJE_Z, g.PCB_Z0 + 0.1))
    herr += insertos([(x, y) for x, y, p in g.TALADROS if p == 'frontal'])
    qw, ql, qh = g.QRE_MODULO
    for xc, yc in g.LINEA_DEL:   # alojamiento del QRE abierto por abajo + paso de cable hacia arriba
        herr.append(box(xc - qw / 2 - HOLG, xc + qw / 2 + HOLG, yc - ql / 2 - HOLG, yc + ql / 2 + HOLG,
                        g.RAMPA_SUELO_Z - 0.1, g.RAMPA_SUELO_Z + qh + HOLG))
        herr.append(cil_z(1.6, g.RAMPA_SUELO_Z, g.PCB_Z0 + 1, xc, yc + ql / 2 - 1.8))
    for xc in (30.0, 70.0):      # tornillos de la cuchilla
        herr.append(cil_z(1.1, 0, 15, xc, 9.0))
    return cut(s, *herr)


def cuchilla():
    t = g.CUCHILLA_GROSOR / math.cos(math.radians(g.RAMPA_ANGULO))
    y0, y1 = g.ENV_Y0, g.CUCHILLA_Y1
    s = prisma_x([(y0, 0.0), (y1, g.rampa_z(y1)), (y1, g.rampa_z(y1) + t), (y0, t)], g.ENV_X0, g.ENV_X1)
    return cut(s, *[cil_z(1.1, 0, 15, xc, 9.0) for xc in (30.0, 70.0)])


def pieza_trasera():
    y0, y1 = g.CUNA_TRAS_Y
    cuna = box(g.MOTOR_IZQ_X[0], g.MOTOR_DER_X[1], y0, y1, g.CUNA_Z0, g.PCB_Z0)
    parachoques = box(g.MOTOR_IZQ_X[0], g.MOTOR_DER_X[1], 89.5, y1, 1.5, g.PCB_Z0)
    s = fuse(cuna, parachoques)
    herr = bolsillos_motor(g.EJE_Y_TRAS)
    herr.append(box(g.CANAL_X[0], g.CANAL_X[1], y0 - 0.1, 89.0, g.CUNA_Z0 - 0.1, g.LASTRE_Z1))
    for xm in (g.MOTOR_IZQ_X[1] - 1.5, g.MOTOR_DER_X[0] - 0.6):   # cables de los motores hacia delante
        herr.append(box(xm, xm + 2.1, y0 - 0.1, g.EJE_Y_TRAS - 3.0, g.EJE_Z, g.PCB_Z0 + 0.1))
    herr += insertos([(x, y) for x, y, p in g.TALADROS if p == 'trasera'])
    qw, ql, qh = g.QRE_MODULO
    for xc, yc in g.LINEA_TRAS:   # QRE tumbado: 14 mm en X
        herr.append(box(xc - ql / 2 - HOLG, xc + ql / 2 + HOLG, yc - qw / 2 - HOLG, yc + qw / 2 + HOLG,
                        1.4, 1.5 + qh + HOLG))
        herr.append(cil_z(1.6, 1.5, g.PCB_Z0 + 1, xc + ql / 2 - 2.0, yc))
    return cut(s, *herr)


def lastres():
    a = box(g.PCB_X0, g.PCB_X1, g.CUNA_DEL_Y[1] + 0.3, g.CUNA_TRAS_Y[0] - 0.3, g.LASTRE_Z0, g.LASTRE_Z1)
    b = box(g.CANAL_X[0] + 0.2, g.CANAL_X[1] - 0.2, g.CUNA_DEL_Y[0] + 0.3, g.CUNA_DEL_Y[1], g.LASTRE_Z0, g.LASTRE_Z1)
    c = box(g.CANAL_X[0] + 0.2, g.CANAL_X[1] - 0.2, g.CUNA_TRAS_Y[0], 88.7, g.LASTRE_Z0, g.LASTRE_Z1)
    return {'lastre_central': a, 'lastre_canal_del': b, 'lastre_canal_tras': c}


def motor(lado, eje):
    x0 = g.MOTOR_IZQ_X[0]
    w, h = g.MOTOR_ANCHO / 2, g.MOTOR_ALTO / 2
    z = g.EJE_Z
    red = box(x0, x0 + 9, eje - w, eje + w, z - h, z + h)
    lata = box(x0 + 9, x0 + 24, eje - w, eje + w, z - h, z + h)
    tapa = box(x0 + 24, x0 + 26, eje - 4, eje + 4, z - 3, z + 3)
    eje_s = cil_x(1.5, g.RUEDA_X_EXT + 1.5, x0, eje, z)
    s = fuse(red, lata, tapa, eje_s)
    return s if lado == 'izq' else espejo_x(s)


def rueda(lado, eje):
    r_ext, r_llanta = g.RUEDA_D / 2, g.RUEDA_D / 2 - 4.0
    x0, x1 = g.RUEDA_X_EXT, g.RUEDA_X_INT
    llanta = cut(cil_x(r_llanta, x0, x1, eje, g.EJE_Z), cil_x(1.5, x0 - 1, x1 + 1, eje, g.EJE_Z))
    neum = cut(cil_x(r_ext, x0, x1, eje, g.EJE_Z), cil_x(r_llanta, x0 - 1, x1 + 1, eje, g.EJE_Z))
    if lado == 'der':
        llanta, neum = espejo_x(llanta), espejo_x(neum)
    return llanta, neum


TOF_FRONT_X = [25.0, 50.0, 75.0]
TOF_Y = (g.CARCASA_Y0 + g.CARCASA_PARED + 0.2, g.CARCASA_Y0 + g.CARCASA_PARED + 0.2 + g.TOF_MODULO[2])
TOF_FRONT_Z = (19.5, 19.5 + g.TOF_MODULO[1])
TECHO = (g.TECHO_Z, g.TECHO_Z + g.TECHO_GROSOR)
BAHIA = (21.9, 78.1, 45.0, 76.5)          # hueco interior de la batería (x0, x1, y0, y1)
SOPORTE_LAT = (55.0, 73.0)                # tramo y de los soportes de ToF laterales
RIM_H = 6.0


def carcasa(frontal):
    """Devuelve (paredes, techo): se imprimen por separado y se unen con los 4 tornillos largos."""
    p = g.CARCASA_PARED
    x0, x1, y0, y1 = g.MOTOR_IZQ_X[0], g.MOTOR_DER_X[1], g.CARCASA_Y0, g.ENV_Y1
    paredes = cut(box(x0, x1, y0, y1, 15, g.TECHO_Z), box(x0 + p, x1 - p, y0 + p, y1 - p, 14, g.TECHO_Z + 0.1))
    paredes = cut(paredes,
                  box(0, 100, g.RAMPA_Y_FIN, 100, 0, g.PCB_Z0 + 0.05),             # apoya en cunas
                  box(g.PCB_X0, g.PCB_X1, g.PCB_Y0, g.PCB_Y1, g.PCB_Z0 - 0.1, g.PCB_Z0 + g.PCB_GROSOR + 0.05),
                  frontal,                                                         # sigue la rampa
                  box(40, 60, 95, 100, g.PCB_Z0, 25.5))                            # antena del ESP32
    techo = box(g.ENV_X0, g.ENV_X1, y0, y1, *TECHO)
    # Bahía de la batería (reborde)
    bx0, bx1, by0, by1 = BAHIA
    rim = cut(box(bx0 - p, bx1 + p, by0 - p, by1 + p, TECHO[1], TECHO[1] + RIM_H),
              box(bx0, bx1, by0, by1, TECHO[1] - 1, TECHO[1] + RIM_H + 1),
              box(63.0, 78.0, by1 - 1, by1 + p + 1, TECHO[1] - 1, TECHO[1] + RIM_H + 1),   # paso del USB
              box(44.0, 56.0, by0 - p - 1, by0 + 1, TECHO[1] - 1, TECHO[1] + RIM_H + 1))   # cables XT30
    # Soportes de ToF laterales y trasero
    tw, th, tt = g.TOF_MODULO
    sl = fuse(box(g.ENV_X0, g.ENV_X0 + p, *SOPORTE_LAT, TECHO[1], TECHO[1] + th + 1.5),
              box(g.ENV_X0, g.ENV_X0 + 6, *SOPORTE_LAT, TECHO[1], TECHO[1] + 1.2))
    st = box(41.0, 59.0, y1 - p, y1, TECHO[1], TECHO[1] + th + 1.5)
    # Torretas de los tornillos largos
    torres = [cil_z(2.75, g.PCB_Z0 + g.PCB_GROSOR, g.TECHO_Z, x, y) for x, y in g.TALADROS_CARCASA]
    cuerpo = fuse(paredes, *torres)
    tapa = fuse(techo, rim, sl, espejo_x(sl), st)
    herr = [cil_z(1.1, g.PCB_Z0, TECHO[1] + 1, x, y) for x, y in g.TALADROS_CARCASA]
    herr += [cil_z(2.1, TECHO[1] - 1.8, TECHO[1] + 1, x, y) for x, y in g.TALADROS_CARCASA]   # cabeza
    herr += [
        box(43.5, 56.5, 37.2, 43.4, TECHO[0] - 1, TECHO[1] + 1),      # XT30
        box(64.5, 76.5, 76.6, 86.2, TECHO[0] - 1, TECHO[1] + 1),      # USB-C
        box(14.6, 19.6, 58.0, 70.0, TECHO[0] - 1, TECHO[1] + 1),      # cable ToF izq.
        box(80.4, 85.4, 58.0, 70.0, TECHO[0] - 1, TECHO[1] + 1),      # cable ToF der.
        box(28.0, 40.0, 86.0, 92.0, TECHO[0] - 1, TECHO[1] + 1),      # cables ToF trasero / línea
        box(60.5, 70.5, 87.0, 92.0, TECHO[0] - 1, TECHO[1] + 1),      # cable IR
    ]
    zc = (TOF_FRONT_Z[0] + TOF_FRONT_Z[1]) / 2
    herr += [cil_y(3.0, y0 - 1, y0 + p + 1, x, zc) for x in TOF_FRONT_X]          # ventanas ToF frontales
    zl = TECHO[1] + 1.2 + th / 2
    ym = sum(SOPORTE_LAT) / 2
    herr += [cil_x(3.0, g.ENV_X0 - 1, g.ENV_X0 + p + 1, ym, zl), cil_x(3.0, g.ENV_X1 - p - 1, g.ENV_X1 + 1, ym, zl),
             cil_y(3.0, y1 - p - 1, y1 + 1, 50.0, zl)]
    return cut(cuerpo, *herr), cut(tapa, *herr)


def tofs():
    tw, th, tt = g.TOF_MODULO
    out = {}
    for n, xc in zip(('F_izq', 'F', 'F_der'), TOF_FRONT_X):
        out['tof_' + n] = box(xc - tw / 2, xc + tw / 2, *TOF_Y, *TOF_FRONT_Z)
    p = g.CARCASA_PARED
    z0 = TECHO[1] + 1.2
    out['tof_izq'] = box(g.ENV_X0 + p + 0.2, g.ENV_X0 + p + 0.2 + tt, *SOPORTE_LAT, z0, z0 + th)
    out['tof_der'] = espejo_x(out['tof_izq'])
    out['tof_tras'] = box(50 - tw / 2, 50 + tw / 2, g.ENV_Y1 - p - 0.2 - tt, g.ENV_Y1 - p - 0.2, z0, z0 + th)
    return out


def qres():
    qw, ql, qh = g.QRE_MODULO
    out = {}
    for i, (xc, yc) in enumerate(g.LINEA_DEL):
        out[f'qre_del_{i + 1}'] = box(xc - qw / 2, xc + qw / 2, yc - ql / 2, yc + ql / 2,
                                      g.RAMPA_SUELO_Z + 0.2, g.RAMPA_SUELO_Z + 0.2 + qh)
    for i, (xc, yc) in enumerate(g.LINEA_TRAS):
        out[f'qre_tras_{i + 1}'] = box(xc - ql / 2, xc + ql / 2, yc - qw / 2, yc + qw / 2, 1.6, 1.6 + qh)
    return out


def bateria():
    bl, bw, bh = g.BATERIA
    cx, cy = (BAHIA[0] + BAHIA[1]) / 2, (BAHIA[2] + BAHIA[3]) / 2
    return box(cx - bl / 2, cx + bl / 2, cy - bw / 2, cy + bw / 2, TECHO[1] + 0.2, TECHO[1] + 0.2 + bh)


def receptor_ir():
    return box(47.0, 53.0, 86.5, 91.5, TECHO[1], TECHO[1] + 7.5)


def pcb():
    s = Part.read(os.path.join(OUT_STEP, 'pcb.step'))
    bb = s.BoundBox
    # KiCad exporta con el origen de rejilla en (0, 0) del robot y el eje Y hacia arriba (= -y)
    s.translate(V(0, 100, g.PCB_Z0 - bb.ZMin))
    return s


def componentes():
    with open(os.path.join(HERE, 'pcb_componentes.json')) as f:
        data = json.load(f)
    z0 = g.PCB_Z0 + g.PCB_GROSOR
    return {c['ref']: box(c['bbox'][0], c['bbox'][2], c['bbox'][1], c['bbox'][3], z0, z0 + c['alto'])
            for c in data}


# ------------------------------------------------------------------ montaje, comprobaciones y exportación
# nombre: (forma, material, densidad g/cm³ efectiva, color RGB 0-1, imprimible, grupo de despiece)
def construir():
    frontal = pieza_frontal()
    paredes, techo = carcasa(frontal)
    piezas = {
        'frontal_rampa_cuna': (frontal, 'PETG 40 % relleno', 0.80, (0.85, 0.35, 0.10), True, 'frontal'),
        'trasera_cuna_parachoques': (pieza_trasera(), 'PETG 40 % relleno', 0.80, (0.85, 0.35, 0.10), True, 'trasera'),
        'carcasa_paredes': (paredes, 'PETG 30 % relleno', 0.70, (0.15, 0.15, 0.17), True, 'carcasa'),
        'carcasa_techo': (techo, 'PETG 30 % relleno', 0.70, (0.22, 0.22, 0.25), True, 'techo'),
        'cuchilla_acero': (cuchilla(), 'acero (fleje 0,4 mm)', 7.85, (0.75, 0.77, 0.80), False, 'frontal'),
        'pcb': (pcb(), 'FR4 1,6 mm', 1.85, (0.05, 0.40, 0.15), False, 'pcb'),
        'bateria_lipo_2s': (bateria(), 'LiPo', 1.9, (0.20, 0.35, 0.80), False, 'bateria'),
        'receptor_ir': (receptor_ir(), 'VS1838B', 1.2, (0.1, 0.1, 0.1), False, 'techo'),
    }
    for k, s in lastres().items():
        piezas[k] = (s, 'acero', 7.85, (0.45, 0.47, 0.50), False, 'lastre')
    for lado, eje in MOTORES:
        tag = f"{lado}_{'del' if eje == g.EJE_Y_DEL else 'tras'}"
        piezas['motor_' + tag] = (motor(lado, eje), 'N20 (10 g c/u)', None, (0.80, 0.80, 0.82), False, 'motores')
        llanta, neum = rueda(lado, eje)
        piezas['llanta_' + tag] = (llanta, 'PLA 100 %', 1.24, (0.95, 0.75, 0.10), True, 'ruedas')
        piezas['neumatico_' + tag] = (neum, 'silicona 20-30 ShA', 1.10, (0.10, 0.10, 0.10), False, 'ruedas')
    for k, s in tofs().items():
        piezas[k] = (s, 'VL53L0X', 1.6, (0.55, 0.15, 0.65), False, 'techo' if k[4:5] != 'F' else 'carcasa')
    for k, s in qres().items():
        piezas[k] = (s, 'QRE1113', 1.4, (0.75, 0.10, 0.10), False, 'frontal' if 'del' in k else 'trasera')
    comps = componentes()
    piezas['componentes_pcb'] = (Part.makeCompound(list(comps.values())), 'componentes', 1.2,
                                 (0.25, 0.25, 0.28), False, 'pcb')
    return piezas, comps


MASA_FIJA = {'motor_': 10.0, 'componentes_pcb': 14.0, 'bateria_lipo_2s': 32.0, 'tof_': 1.0, 'qre_': 0.6,
             'receptor_ir': 0.5}


def masa(nombre, forma, dens):
    for k, m in MASA_FIJA.items():
        if nombre.startswith(k):
            return m
    return forma.Volume / 1000.0 * dens


# Contactos que son intencionados (apoyos): no cuentan como interferencia
APOYOS = {('frontal_rampa_cuna', 'cuchilla_acero')}


def interferencias(piezas):
    nombres = [n for n in piezas if n != 'componentes_pcb']
    res = []
    for i, a in enumerate(nombres):
        sa = piezas[a][0]
        for b in nombres[i + 1:]:
            if (a, b) in APOYOS or (b, a) in APOYOS:
                continue
            sb = piezas[b][0]
            if not sa.BoundBox.intersect(sb.BoundBox):
                continue
            v = sa.common(sb).Volume
            if v > 0.5:
                res.append((a, b, round(v, 1)))
    comp = piezas['componentes_pcb'][0]
    for n in ('carcasa_paredes', 'carcasa_techo', 'bateria_lipo_2s', 'tof_F_izq', 'tof_F', 'tof_F_der'):
        v = piezas[n][0].common(comp).Volume
        if v > 0.5:
            res.append((n, 'componentes_pcb', round(v, 1)))
    return res


def exportar_stl(forma, path, fino=True):
    """STL binario con mallado controlado (0,02 mm de desviación para imprimir)."""
    import MeshPart
    m = MeshPart.meshFromShape(Shape=forma, LinearDeflection=0.02 if fino else 0.1,
                               AngularDeflection=0.2 if fino else 0.5, Relative=False)
    m.write(path)


def main():
    piezas, comps = construir()
    doc = App.newDocument('robot_sumo')
    objs = []
    for nombre, (forma, mat, dens, color, imprimible, grupo) in piezas.items():
        o = doc.addObject('Part::Feature', nombre)
        o.Shape = forma
        o.Label = nombre
        objs.append(o)
        exportar_stl(forma, os.path.join(OUT_RENDER, nombre + '.stl'), fino=False)
        if imprimible and not nombre.endswith(('der_del', 'izq_tras', 'der_tras')):
            nombre_stl = 'llanta' if nombre.startswith('llanta') else nombre
            forma.exportStep(os.path.join(OUT_STEP, nombre_stl + '.step'))
            exportar_stl(forma, os.path.join(OUT_STL, nombre_stl + '.stl'))
    doc.recompute()
    import Import
    Import.export(objs, os.path.join(OUT_STEP, 'robot_ensamblaje.step'))
    doc.saveAs(os.path.join(HERE, 'robot_sumo.FCStd'))

    masas = {n: round(masa(n, f, d), 1) for n, (f, _, d, *_r) in piezas.items()}
    total = round(sum(masas.values()), 1)
    bb = Part.makeCompound([f for f, *_ in piezas.values()]).BoundBox
    interf = interferencias(piezas)
    informe = {
        'masa_g': masas, 'masa_total_g': total, 'margen_hasta_500g': round(500 - total, 1),
        'envolvente_mm': {'x': [round(bb.XMin, 2), round(bb.XMax, 2)], 'y_robot': [round(100 - bb.YMax, 2), round(100 - bb.YMin, 2)],
                          'z': [round(bb.ZMin, 2), round(bb.ZMax, 2)], 'ancho': round(bb.XLength, 2),
                          'largo': round(bb.YLength, 2), 'alto': round(bb.ZLength, 2)},
        'interferencias_mm3': interf,
        'piezas': {n: {'material': m, 'imprimible': imp, 'grupo': grp, 'color': col}
                   for n, (f, m, d, col, imp, grp) in piezas.items()},
    }
    with open(os.path.join(HERE, 'informe_3d.json'), 'w') as f:
        json.dump(informe, f, indent=1, ensure_ascii=False)
    print(f"Masa estimada: {total} g (margen {informe['margen_hasta_500g']} g)")
    print('Envolvente:', informe['envolvente_mm'])
    print('Interferencias:', interf if interf else 'ninguna')


main()
