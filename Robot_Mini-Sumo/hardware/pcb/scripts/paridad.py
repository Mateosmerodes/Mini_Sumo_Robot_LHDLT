"""Comprueba que el esquemático y la PCB tienen las mismas conexiones pin a pin.
Uso: python3 scripts/paridad.py   (necesita kicad-cli y pcbnew)"""
import os
import subprocess
import xml.etree.ElementTree as ET
import pcbnew

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
xml = '/tmp/robot_sumo_net.xml'
subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', xml,
                os.path.join(D, 'robot_sumo.kicad_sch')], check=True, capture_output=True)
sch = {}
for net in ET.parse(xml).getroot().iter('net'):
    nombre = net.get('name').lstrip('/')
    for n in net.iter('node'):
        if not n.get('ref').startswith('#'):
            sch[(n.get('ref'), n.get('pin'))] = '' if nombre.startswith('unconnected-') else nombre
pcb = {}
for fp in pcbnew.LoadBoard(os.path.join(D, 'robot_sumo.kicad_pcb')).GetFootprints():
    for p in fp.Pads():
        if p.GetNumber():
            pcb[(fp.GetReference(), p.GetNumber())] = p.GetNetname()
dif = [(k, sch.get(k), pcb.get(k)) for k in sorted(set(sch) | set(pcb)) if (sch.get(k) or '') != (pcb.get(k) or '')]
for d in dif:
    print('DIFERENCIA', d)
print(f'{len(pcb)} pads comparados, {len(dif)} diferencias')
