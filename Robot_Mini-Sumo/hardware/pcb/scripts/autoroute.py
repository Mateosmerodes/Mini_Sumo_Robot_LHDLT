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
    if not pcbnew.ImportSpecctraSES(board, ses):
        raise SystemExit('No se pudo importar el SES')
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    n = sum(1 for t in board.GetTracks() if t.GetClass() == 'PCB_TRACK')
    v = sum(1 for t in board.GetTracks() if t.GetClass() == 'PCB_VIA')
    print(f'rutado importado: {n} pistas, {v} vías')


if __name__ == '__main__':
    main()
