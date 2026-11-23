#!/usr/bin/env bash
# Corrección del tronco de VBAT (16/11/2026), aplicada sobre la placa rutada del commit 84eaf00.
# Ya está aplicada en robot_sumo.kicad_pcb: se guarda solo como registro de lo que se hizo.
# Uso: aplicar.sh <carpeta con una copia de robot_sumo.kicad_pcb y .kicad_pro de 84eaf00>
#   (cargar y guardar en la misma carpeta: si no, pcbnew reescribe el .kicad_pro)
# Comprobación de caídas: python3 solve.py robot_sumo.kicad_pcb VBAT F1.2 U5.11,U6.11,U7.11,U8.11 1 2.44
set -e
D="$(cd "$(dirname "$0")" && pwd)"
cd "$1"
python3 - <<'PY'
import pcbnew
f='robot_sumo.kicad_pcb'; b=pcbnew.LoadBoard(f)
zs={z.GetZoneName():z for z in b.Zones() if z.GetNetname()=='VBAT'}
def setpoly(z,pts):
    o=z.Outline(); o.RemoveAllContours(); o.NewOutline()
    for x,y in pts: o.Append(int(x*1e6),int(y*1e6))
print(sorted(zs))
setpoly(zs['VBAT_sup0'],[(129.5,93),(139.5,93),(139.5,109.5),(137.5,109.5),(137.5,119),(129.5,119)])
setpoly(zs['VBAT_sup1'],[(137.6,89.5),(160.4,89.5),(160.4,109),(137.6,109)]); zs['VBAT_sup1'].SetAssignedPriority(4)
pass
b.Save(f)
PY
python3 "$D"/mod1.py robot_sumo.kicad_pcb
python3 "$D"/mod2.py robot_sumo.kicad_pcb
python3 "$D"/bridge.py robot_sumo.kicad_pcb "[(143.3,99.0),(153.0,99.0),(161.0,107.0),(161.0,109.3),(152.0,109.3),(143.3,100.6)]" "[(151.85,101.65),(152.0,107.25)]" "[]"
python3 "$D"/autovia.py robot_sumo.kicad_pcb 140,98,162,110
python3 "$D"/autovia2.py robot_sumo.kicad_pcb 135,83.5,158,88 B GND 4
kicad-cli pcb drc -o d.rpt robot_sumo.kicad_pcb >/dev/null 2>&1 || true
grep '^\[' d.rpt | grep -v lib_foot | sed 's/:.*//' | sort | uniq -c || true; grep -i 'unconnected pads' d.rpt
