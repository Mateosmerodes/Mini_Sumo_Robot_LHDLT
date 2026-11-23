"""Construye el chasis con CadQuery (sin Fusion): STEP, STL, comprobaciones e imágenes.

Uso (desde Robot_Mini-Sumo/hardware/chasis):
    pip install cadquery matplotlib
    python construir_cadquery.py

Lee las cotas de fusion360/ChasisLHDT/geometria_chasis.py (las mismas que usa el script de Fusion)
y las patillas de la PCB de ../pcb/robot_sumo.kicad_pcb.

Genera:
    step/<pieza>.step, step/ensamblaje_chasis.step
    stl/<pieza>.stl                      (solo las piezas que se imprimen)
    informe_chasis.json                  (envolvente, choques, masas, lastre, centro de masas)
    img/*.png                            (vistas del montaje)
Las coordenadas de los STEP/STL son las de Fusion: mm, robot centrado, frente hacia +Y, Z arriba.
"""
import json
import math
import os
import re
import sys

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'fusion360', 'ChasisLHDT'))
import geometria_chasis as g  # noqa: E402

PCB_FILE = os.path.normpath(os.path.join(HERE, '..', 'pcb', 'robot_sumo.kicad_pcb'))
OUT_STEP = os.path.join(HERE, 'step')
OUT_STL = os.path.join(HERE, 'stl')
OUT_IMG = os.path.join(HERE, 'img')


# ------------------------------------------------------------------ árbol -> sólido de CadQuery
def P(x, y, z):
    return cq.Vector(x - 50.0, 50.0 - y, z)


def V(v):
    return cq.Vector(*g.vec_a_fusion(v))


def solido(op):
    t = op[0]
    if t == 'box':
        _, x0, x1, y0, y1, z0, z1 = op
        return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, P(x0, y1, z0))
    if t == 'cyl':
        _, eje, r, a0, a1, c1, c2 = op
        if eje == 'x':
            return cq.Solid.makeCylinder(r, a1 - a0, P(a0, c1, c2), cq.Vector(1, 0, 0))
        if eje == 'y':
            return cq.Solid.makeCylinder(r, a1 - a0, P(c1, a1, c2), cq.Vector(0, 1, 0))
        return cq.Solid.makeCylinder(r, a1 - a0, P(c1, c2, a0), cq.Vector(0, 0, 1))
    if t == 'obox':
        _, c, l, u, w, dl, du, dw = op
        c, l, u, w = P(*c), V(l), V(u), V(w)
        base = c - w * (dw / 2)
        pts = [base + l * (sl * dl / 2) + u * (su * du / 2) for sl, su in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        cara = cq.Face.makeFromWires(cq.Wire.makePolygon(pts, close=True))
        return cq.Solid.extrudeLinear(cara, w * dw)
    if t == 'union':
        s = solido(op[1][0])
        for h in op[1][1:]:
            s = s.fuse(solido(h))
        return s.clean()
    if t == 'cut':
        s = solido(op[1])
        for h in op[2]:
            s = s.cut(solido(h))
        return s.clean()
    raise ValueError(t)


def grabar_textos(s):
    """Textos en la cara inferior: se leen mirando el robot desde abajo con el frente hacia arriba."""
    for texto, x, y, alto in g.textos():
        c = P(x, y, g.Z_BAJO + g.TEXTO_PROFUNDIDAD)
        t = (cq.Workplane(cq.Plane(origin=c, xDir=(-1, 0, 0), normal=(0, 0, -1)))
             .text(texto, alto, g.TEXTO_PROFUNDIDAD + 0.02, combine=False, halign='center', valign='center'))
        s = s.cut(t.val())
    return s


# ------------------------------------------------------------------ patillas de la PCB (del fichero de KiCad)
def pads_pcb():
    t = open(PCB_FILE, encoding='utf-8').read()
    idx = [m.start() for m in re.finditer(r'\(footprint "', t)] + [len(t)]
    pads = []
    for a, b in zip(idx, idx[1:]):
        blk = t[a:b]
        m = re.search(r'\(at ([\d.\-]+) ([\d.\-]+)(?: ([\d.\-]+))?\)', blk)
        fx, fy, fr = float(m.group(1)), float(m.group(2)), math.radians(float(m.group(3) or 0))
        ref = (re.search(r'\(property "Reference" "([^"]+)"', blk)
               or re.search(r'\(fp_text reference "([^"]+)"', blk)).group(1)
        for pm in re.finditer(r'\(pad "([^"]*)" thru_hole \w+ \(at ([\d.\-]+) ([\d.\-]+)', blk):
            dx, dy = float(pm.group(2)), float(pm.group(3))
            x = fx + dx * math.cos(fr) + dy * math.sin(fr) - 100.0
            y = fy - dx * math.sin(fr) + dy * math.cos(fr) - 100.0
            pads.append((ref, pm.group(1), g.PCB_X0 + x, g.PCB_Y0 + y))
    return pads


def patillas(pads):
    s = None
    for _, _, x, y in pads:
        c = cq.Solid.makeCylinder(1.2, g.PATAS_THT, P(x, y, g.PCB_Z0 - g.PATAS_THT))
        s = c if s is None else s.fuse(c)
    return s


# ------------------------------------------------------------------ utilidades
def bbox_robot(s):
    b = s.BoundingBox()
    return dict(x=(round(b.xmin + 50, 2), round(b.xmax + 50, 2)), y=(round(50 - b.ymax, 2), round(50 - b.ymin, 2)),
                z=(round(b.zmin, 2), round(b.zmax, 2)))


def choque(a, b):
    try:
        v = a.intersect(b).Volume()
    except Exception:
        return None
    return round(v, 2)


def main():
    for d in (OUT_STEP, OUT_STL, OUT_IMG):
        os.makedirs(d, exist_ok=True)
    inf = {'aviso': 'Comprobación teórica del modelo 3D. Nada de esto está montado ni probado.'}

    piezas = {}
    for nombre, (op, imprimir, color) in g.piezas().items():
        s = solido(op)
        if nombre == 'chasis':
            s = grabar_textos(s)
        piezas[nombre] = (s, imprimir, color)
    refs = {n: solido(op) for n, op in g.referencias().items()}
    pads = pads_pcb()
    tails = patillas(pads)

    # ---- exportar
    asm = cq.Assembly(name='chasis_LHDT_v2')
    for nombre, (s, imprimir, color) in piezas.items():
        cq.exporters.export(s, os.path.join(OUT_STEP, nombre + '.step'))
        if imprimir:
            cq.exporters.export(s, os.path.join(OUT_STL, nombre + '.stl'), tolerance=0.02, angularTolerance=0.1)
        asm.add(s, name=nombre, color=cq.Color(*color))
    for nombre, s in refs.items():
        col = next(v for k, v in g.COLORES_REF.items() if nombre.startswith(k))
        asm.add(s, name='ref_' + nombre, color=cq.Color(*col))
    asm.save(os.path.join(OUT_STEP, 'ensamblaje_chasis.step'))

    # ---- envolvente
    todo = cq.Compound.makeCompound([p[0] for p in piezas.values()] + list(refs.values()))
    bb = bbox_robot(todo)
    inf['envolvente_mm'] = bb
    ancho, largo = bb['x'][1] - bb['x'][0], bb['y'][1] - bb['y'][0]
    inf['planta_mm'] = [round(ancho, 2), round(largo, 2)]
    inf['cabe_en_10x10'] = ancho <= 100 and largo <= 100
    inf['pcb_patillas'] = len(pads)

    # ---- choques (volumen en mm³; 0 = no se tocan)
    ch = {}
    chasis = piezas['chasis'][0]
    for nombre, s in refs.items():
        if nombre == 'pcb':
            continue
        ch['chasis/' + nombre] = choque(chasis, s)
    for lado in ('izq', 'der'):
        a = piezas['abrazadera_motor_' + lado][0]
        ch[f'abrazadera_{lado}/motor_{lado}'] = choque(a, refs['motor_' + lado])
        ch[f'abrazadera_{lado}/patillas_pcb'] = choque(a, tails)
        ch[f'abrazadera_{lado}/chasis'] = choque(a, chasis)
    ch['chasis/patillas_pcb'] = choque(chasis, tails)
    for i in range(len(g.TOF_X)):
        ch[f'vl53l0x_{i + 1}/patillas_pcb'] = choque(refs[f'vl53l0x_{i + 1}'], tails)
    ch['bateria/patillas_pcb'] = choque(refs['bateria'], tails)
    # La batería entra y sale de lado: su recorrido (de x=-60 a x=160) no puede tocar las ruedas
    l, an, h = g.BATERIA
    barrido = solido(g.box(-60, 160, g.BATERIA_Y0, g.BATERIA_Y0 + an, g.Z_SUELO, g.Z_SUELO + h))
    for lado in ('izq', 'der'):
        ch[f'recorrido_bateria/rueda_{lado}'] = choque(barrido, refs['rueda_' + lado])
    if 'cuchilla_acero' in piezas:
        ch['cuchilla/chasis'] = choque(piezas['cuchilla_acero'][0], chasis)
    for lado in ('izq', 'der'):
        ch[f'rueda_{lado}/pcb'] = choque(refs['rueda_' + lado], refs['pcb'])
    inf['choques_mm3'] = ch
    # Las columnas tocan la PCB por diseño (es donde apoya): se comprueba que no haya patillas encima.
    inf['choques_ok'] = all(v is not None and v < 0.01 for v in ch.values())

    # ---- holguras
    inf['holguras_mm'] = {
        'rueda_interior_a_chasis_x': round(g.CUERPO_X[0] - g.RUEDA_X_INT, 2),
        'rueda_interior_a_pcb_x': round(g.PCB_X0 - g.RUEDA_X_INT, 2),
        'bajo_chasis_al_suelo': g.Z_BAJO,
        'bateria_a_patillas_pcb_z': round(g.PCB_Z0 - g.PATAS_THT - g.Z_SUELO - g.BATERIA[2], 2),
        'bateria_holgura_y': round(g.CUERPO_Y[0] - g.TUNEL_Y[0] - g.BATERIA[1], 2),
        'bateria_max_alto': round(g.PCB_Z0 - g.PATAS_THT - g.Z_SUELO - 0.5, 2),
    }
    # Rayo inferior del VL53L0X frente a la rampa (lo pisa si queda por debajo de la superficie)
    medio = math.radians(g.TOF_CONO / 2)
    peor = min((g.TOF_ZC - (g.TOF_Y - y) * math.tan(medio)) - g.rampa_z(y)
               for y in [g.ENV_Y0 + i * 0.1 for i in range(int((g.RAMPA_Y1 - g.ENV_Y0) * 10) + 1)])
    inf['vl53l0x_margen_sobre_rampa_mm'] = round(peor, 2)
    inf['rampa'] = {'angulo_grados': g.RAMPA_ANGULO, 'alto_mm': round(g.RAMPA_Z1, 2),
                    'filo_y_mm': g.ENV_Y0}

    # ---- masas
    masas = {}
    for nombre, (s, imprimir, _) in piezas.items():
        vol = s.Volume() / 1000
        if imprimir:
            masas[nombre] = dict(volumen_cm3=round(vol, 2), maciza_g=round(vol * g.DENS_PETG, 1),
                                 impresa_estimada_g=round(vol * g.DENS_PETG * g.FACTOR_IMPRESION, 1))
        else:
            masas[nombre] = dict(volumen_cm3=round(vol, 3), acero_g=round(vol * g.DENS_ACERO, 1))
    inf['masas_piezas'] = masas
    huecos = [g.LASTRE_CENTRAL] + list(g.LASTRE_TRASERO)
    alto = g.CUERPO_Z1 - g.Z_SUELO
    vol_lastre = sum((x1 - x0) * (y1 - y0) * alto for x0, x1, y0, y1 in huecos) / 1000
    inf['lastre'] = dict(volumen_huecos_cm3=round(vol_lastre, 2),
                         acero_g=round(vol_lastre * g.DENS_ACERO, 0),
                         plomo_g=round(vol_lastre * g.DENS_PLOMO, 0),
                         nota='Si se llena con perdigones/pletina, cuenta ~60-90 % de esto.')

    # ---- centro de masas estimado (masas de componentes 🔶: pesar y corregir)
    m_chasis = masas['chasis']['impresa_estimada_g']
    comp = [  # (qué, g, y del centro)
        ('chasis', m_chasis, 0.0),
        ('abrazaderas', 2 * masas['abrazadera_motor_izq']['impresa_estimada_g'], sum(g.ABRAZ_Y) / 2),
        ('cuchilla', masas.get('cuchilla_acero', {}).get('acero_g', 0), (g.ENV_Y0 + g.CUCHILLA_Y1) / 2),
        ('motores N20 (2 × 10 g 🔶)', 20, g.EJE_Y),
        ('ruedas (2 × 8 g 🔶)', 16, g.EJE_Y),
        ('bateria 2S 450 mAh (30 g 🔶)', 30, g.BATERIA_Y0 + g.BATERIA[1] / 2),
        ('PCB montada con DevKit y drivers (55 g 🔶)', 55, g.PCB_Y0 + g.PCB_LARGO / 2),
        ('sensores y cables (15 g 🔶)', 15, 35.0),
        ('tornillos (6 g 🔶)', 6, 70.0),
    ]
    comp[0] = ('chasis (impreso, estimada)', m_chasis, 50 - cq.Shape.centerOfMass(chasis).y)
    total = sum(m for _, m, _ in comp)
    ycm = sum(m * y for _, m, y in comp) / total
    # lastre central lleno de acero al 75 %
    ml = round(0.75 * (g.LASTRE_CENTRAL[1] - g.LASTRE_CENTRAL[0]) * (g.LASTRE_CENTRAL[3] - g.LASTRE_CENTRAL[2])
               * alto / 1000 * g.DENS_ACERO, 1)
    yl = (g.LASTRE_CENTRAL[2] + g.LASTRE_CENTRAL[3]) / 2
    ycm2 = (ycm * total + ml * yl) / (total + ml)

    def reparto(y):  # fracción del peso sobre las ruedas (apoyos: filo de la cuña y eje)
        return round((y - g.ENV_Y0) / (g.EJE_Y - g.ENV_Y0), 3)

    inf['centro_masas'] = dict(
        componentes=[dict(que=q, g=round(m, 1), y=round(y, 1)) for q, m, y in comp],
        sin_lastre=dict(masa_g=round(total, 1), y_mm=round(ycm, 1), peso_en_ruedas=reparto(ycm)),
        con_lastre_central_acero=dict(lastre_g=ml, masa_g=round(total + ml, 1), y_mm=round(ycm2, 1),
                                      peso_en_ruedas=reparto(ycm2)),
        nota='Apoyos: filo de la cuña (y=1) y eje de las ruedas (y=%.0f). Si el centro de masas pasa por '
             'detrás del eje, el robot se echa hacia atrás y la cuña se levanta.' % g.EJE_Y)

    with open(os.path.join(HERE, 'informe_chasis.json'), 'w', encoding='utf-8') as f:
        json.dump(inf, f, ensure_ascii=False, indent=2)
    print(json.dumps(inf, ensure_ascii=False, indent=2))

    # ---- mallas para las imágenes (render/render.mjs las pinta con three.js en Chromium)
    out_r = os.path.join(HERE, '_render')
    os.makedirs(out_r, exist_ok=True)
    man = []
    for nombre, (s, imprimir, color) in piezas.items():
        cq.exporters.export(s, os.path.join(out_r, nombre + '.stl'), tolerance=0.03, angularTolerance=0.15)
        man.append(dict(nombre=nombre, color=color, ref=False))
    for nombre, s in refs.items():
        col = next(v for k, v in g.COLORES_REF.items() if nombre.startswith(k))
        cq.exporters.export(s, os.path.join(out_r, 'ref_' + nombre + '.stl'), tolerance=0.03, angularTolerance=0.15)
        man.append(dict(nombre='ref_' + nombre, color=col, ref=True))
    with open(os.path.join(out_r, 'manifest.json'), 'w') as f:
        json.dump(man, f)
    print('Mallas en _render/. Imágenes: node render/render.mjs')


if __name__ == '__main__':
    main()
