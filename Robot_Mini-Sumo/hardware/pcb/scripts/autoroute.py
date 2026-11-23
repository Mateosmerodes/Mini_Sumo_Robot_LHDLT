"""Rutado automático de la placa base con Freerouting (Specctra DSN/SES).

Uso:   python3 scripts/autoroute.py [ruta/a/freerouting.jar] [pasadas]
Probado con Freerouting 1.9.0 (https://github.com/freerouting/freerouting/releases/tag/v1.9.0) y Java 21.
Freerouting 1.9 necesita una pantalla: sin DISPLAY se lanza con xvfb-run (paquete xvfb).
(Freerouting 2.1 no respeta el número de pasadas y, si se corta por tiempo, guarda un rutado a medias.)

1. Exporta robot_sumo.kicad_pcb (recién generado por gen_pcb.py, con la salida de los drivers ya fija)
   a DSN, con las clases de red del .kicad_pro.
2. Lanza Freerouting.
3. Importa el SES y guarda la placa. Después: scripts/acabado.py (zonas de VBAT, vías de GND, ensanchado).

La placa se abre y se guarda en su sitio, junto a robot_sumo.kicad_pro: si se guardara en otra carpeta,
pcbnew escribiría un .kicad_pro con las clases de red por defecto.
"""
import os
import shutil
import subprocess
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.normpath(os.path.join(HERE, '..', 'robot_sumo.kicad_pcb'))
TMP = os.environ.get('SUMO_TMP', '/tmp/sumo_route')


def importar_ses(board, ses):
    """Lee el SES de Freerouting y añade pistas y vías (KiCad 7 no importa SES desde Python)."""
    import re
    from sexp import parse, find, first
    root = parse(open(ses).read())
    routes = first(root, 'routes')
    res = first(routes, 'resolution')
    k = {'um': 1e-3, 'mm': 1.0, 'mil': 0.0254}[str(res[1])] / float(res[2])   # unidades -> mm
    capas = {'F.Cu': pcbnew.F_Cu, 'B.Cu': pcbnew.B_Cu}
    nets = board.GetNetsByName()
    for net in find(first(routes, 'network_out'), 'net'):
        ni = board.FindNet(net[1])
        for w in find(net, 'wire'):
            path = first(w, 'path')
            layer, width = capas[path[1]], float(path[2]) * k
            pts = [(float(path[i]) * k, -float(path[i + 1]) * k) for i in range(3, len(path), 2)]
            for a, b in zip(pts, pts[1:]):
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(pcbnew.VECTOR2I_MM(*a)); t.SetEnd(pcbnew.VECTOR2I_MM(*b))
                t.SetWidth(pcbnew.FromMM(width)); t.SetLayer(layer); t.SetNet(ni)
                board.Add(t)
        for v in find(net, 'via'):
            d, h = map(float, re.search(r'_(\d+):(\d+)_um', v[1]).groups())
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pcbnew.VECTOR2I_MM(float(v[2]) * k, -float(v[3]) * k))
            via.SetWidth(pcbnew.FromMM(d / 1000)); via.SetDrill(pcbnew.FromMM(h / 1000)); via.SetNet(ni)
            board.Add(via)


def main():
    jar = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('FREEROUTING_JAR', 'freerouting.jar')
    passes = sys.argv[2] if len(sys.argv) > 2 else '60'
    os.makedirs(TMP, exist_ok=True)
    dsn, ses = os.path.join(TMP, 'robot_sumo.dsn'), os.path.join(TMP, 'robot_sumo.ses')
    if os.path.exists(ses):
        os.remove(ses)
    board = pcbnew.LoadBoard(PCB)
    if not pcbnew.ExportSpecctraDSN(board, dsn):
        raise SystemExit('No se pudo exportar el DSN')
    cmd = ['java', '-jar', jar, '-de', dsn, '-do', ses, '-mp', passes, '-mt', '1']
    if not os.environ.get('DISPLAY') and shutil.which('xvfb-run'):
        cmd = ['xvfb-run', '-a'] + cmd
    print(' '.join(cmd), flush=True)
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(ses):
        raise SystemExit('Freerouting no escribió el SES')
    board = pcbnew.LoadBoard(PCB)
    importar_ses(board, ses)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    n = sum(1 for t in board.GetTracks() if t.GetClass() == 'PCB_TRACK')
    v = sum(1 for t in board.GetTracks() if t.GetClass() == 'PCB_VIA')
    print(f'rutado importado: {n} pistas, {v} vías')


if __name__ == '__main__':
    main()
