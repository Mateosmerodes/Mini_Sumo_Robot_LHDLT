#!/usr/bin/env bash
# Genera los ficheros para pedir la placa en hardware/pcb/fabricacion/:
#   Gerber + taladros (ZIP), BOM y esquemático en PDF. No toca el rutado.
# Antes: DRC sin errores (python3 scripts/drc.py) y paridad (python3 scripts/paridad.py).
set -eo pipefail
cd "$(dirname "$0")/.."
OUT=fabricacion
rm -rf "$OUT"; mkdir -p "$OUT/gerber"
PCB=robot_sumo.kicad_pcb
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask --no-x2 -o "$OUT/gerber/" "$PCB" >/dev/null
kicad-cli pcb export drill --format excellon --excellon-separate-th --generate-map --map-format gerberx2 \
  -o "$OUT/gerber/" "$PCB" >/dev/null
(cd "$OUT/gerber" && zip -q ../gerber_LHDT_v2.zip ./*)
python3 scripts/gen_bom.py > "$OUT/bom.md"
cp bom.csv "$OUT/bom.csv"
kicad-cli sch export pdf -o "$OUT/esquematico_LHDT_v2.pdf" robot_sumo.kicad_sch >/dev/null
ls -1 "$OUT"
