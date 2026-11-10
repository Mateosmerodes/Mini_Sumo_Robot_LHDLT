"""Rutado automático de la placa base con Freerouting (Specctra DSN/SES).

Uso:   python3 scripts/autoroute.py [ruta/a/freerouting.jar] [pasadas] [tiempo hh:mm:ss]
Necesita Java 21 y Freerouting 2.x (https://github.com/freerouting/freerouting/releases).
Freerouting 2.1 no respeta el número de pasadas: el trabajo termina (y escribe el SES) al agotar el tiempo.
Por defecto 3 min: en esta placa el número de conexiones sin rutar deja de bajar tras unas pocas pasadas.

1. Exporta robot_sumo.kicad_pcb (recién generado por gen_pcb.py) a DSN, con las clases de red
   del .kicad_pro (Potencia 1,0 mm, Alimentacion 0,5 mm, Default 0,25 mm).
2. Lanza Freerouting sin interfaz gráfica.
3. Importa el SES, vuelve a rellenar los planos de GND y guarda la placa.

El resultado es un punto de partida: hay que revisarlo en KiCad (DRC, pistas de potencia, retornos de
GND bajo los drivers) antes de fabricar. Ver docs/05-PCB.md.
"""
import os
import subprocess
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.normpath(os.path.join(HERE, '..', 'robot_sumo.kicad_pcb'))
TMP = os.environ.get('SUMO_TMP', '/tmp/sumo_route')


def main():
    jar = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('FREEROUTING_JAR', 'freerouting.jar')
    passes = sys.argv[2] if len(sys.argv) > 2 else '25'
    tiempo = sys.argv[3] if len(sys.argv) > 3 else '00:03:00'
    os.makedirs(TMP, exist_ok=True)
    dsn, ses = os.path.join(TMP, 'robot_sumo.dsn'), os.path.join(TMP, 'robot_sumo.ses')
    board = pcbnew.LoadBoard(PCB)
    if not pcbnew.ExportSpecctraDSN(board, dsn):
        raise SystemExit('No se pudo exportar el DSN')
    cmd = ['java', '-jar', jar, '-de', dsn, '-do', ses, '-mp', passes, '-mt', '4',
           '--gui.enabled=false', f'--router.max_passes={passes}', '--router.optimizer.max_passes=5',
           f'--router.job_timeout={tiempo}']
    print(' '.join(cmd), flush=True)
    subprocess.run(cmd, check=True)
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
