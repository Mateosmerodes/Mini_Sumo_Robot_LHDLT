#!/usr/bin/env bash
# Regenera TODO el hardware a partir de geometria.py y pcb/scripts/design.py:
#   esquemático + PCB (con ERC/DRC) → STEP de la PCB → modelo 3D (FreeCAD) → imágenes de docs/img
# Uso: hardware/generar_todo.sh [carpeta_de_informes]   (por defecto /tmp/sumo_check)
set -eo pipefail
cd "$(dirname "$0")"
OUT=${1:-/tmp/sumo_check}
pcb/scripts/check.sh "$OUT"
export KICAD_CONFIG_HOME="$OUT/kcfg"
python3 pcb/scripts/export_cajas.py 2>&1 | grep -v assert
kicad-cli pcb export step --grid-origin --board-only -f -o mecanica/step/pcb.step pcb/robot_sumo.kicad_pcb 2>&1 | grep -E "created|creado" || true
freecadcmd mecanica/cad/robot.py 2>&1 | grep -E "^(Masa|Envolvente|Interferencias)"
python3 mecanica/cad/render.py
