#!/usr/bin/env bash
# Regenera todo, pasa ERC/DRC y exporta imágenes de revisión a $1 (por defecto /tmp/sumo_check)
set -eo pipefail
cd "$(dirname "$0")"
OUT=${1:-/tmp/sumo_check}; mkdir -p "$OUT"
# Configuración de KiCad aislada con las tablas de librerías por defecto (no toca la del usuario)
export KICAD_CONFIG_HOME="$OUT/kcfg"; rm -rf "$KICAD_CONFIG_HOME"; mkdir -p "$KICAD_CONFIG_HOME/10.0"
cp /usr/share/kicad/template/sym-lib-table /usr/share/kicad/template/fp-lib-table "$KICAD_CONFIG_HOME/10.0/"
python3 gen_lib.py >/dev/null && python3 gen_pro.py >/dev/null && python3 gen_sch.py && python3 gen_pcb.py 2>&1 | grep -v assert
cd ..
kicad-cli sch erc --severity-all -o "$OUT/erc.rpt" robot_sumo.kicad_sch 2>&1 | grep -E "infracc|violation" || true
kicad-cli pcb drc --severity-all -o "$OUT/drc.rpt" robot_sumo.kicad_pcb 2>&1 | grep -E "infracc|violation|Encontr|Found" || true
kicad-cli pcb export svg --mode-single --fit-page-to-board --exclude-drawing-sheet \
  --layers Edge.Cuts,F.Cu,F.SilkS,F.CrtYd,F.Fab -o "$OUT/top.svg" robot_sumo.kicad_pcb >/dev/null 2>&1
rsvg-convert -w 1600 -b white "$OUT/top.svg" -o "$OUT/top.png"
grep -E "^\[" "$OUT/drc.rpt" | sed 's/\]:.*/]/' | sort | uniq -c | sort -rn
