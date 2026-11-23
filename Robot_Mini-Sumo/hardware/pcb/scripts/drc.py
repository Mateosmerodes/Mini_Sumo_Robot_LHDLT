"""DRC con pcbnew (kicad-cli de KiCad 7 no tiene DRC): python3 scripts/drc.py [informe.rpt]"""
import os
import sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.join(HERE, '..', 'robot_sumo.kicad_pcb')
out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/drc.rpt'
b = pcbnew.LoadBoard(PCB)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.WriteDRCReport(b, out, pcbnew.EDA_UNITS_MILLIMETRES, True)
print(open(out).read().split('\n** Found')[0][-200:] if False else '', end='')
for line in open(out):
    if line.startswith('**') or line.startswith('['):
        print(line.rstrip())
