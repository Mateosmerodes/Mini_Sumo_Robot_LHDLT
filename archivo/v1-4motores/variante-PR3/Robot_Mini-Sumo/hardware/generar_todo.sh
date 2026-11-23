#!/usr/bin/env bash
# Regenera el modelo 3D a partir de la PCB (pcb/robot_sumo.kicad_pcb) y de geometria.py:
#   cajas de los componentes → STEP de la PCB → modelo 3D (FreeCAD) → imágenes de docs/img
# La PCB se edita a mano en KiCad 10: este script no la modifica.
# Uso: hardware/generar_todo.sh            (necesita kicad-cli 10 con su Python, y freecadcmd)
set -eo pipefail
cd "$(dirname "$0")"
python3 mecanica/cad/export_cajas.py
kicad-cli pcb export step --grid-origin --board-only -f -o mecanica/step/pcb.step pcb/robot_sumo.kicad_pcb 2>&1 | grep -E "created|creado" || true
freecadcmd mecanica/cad/robot.py 2>&1 | grep -E "^(Masa|Envolvente|Interferencias)"
python3 mecanica/cad/render.py
python3 calculos/calculos_electricos.py > /dev/null && echo "Cálculos eléctricos actualizados"
