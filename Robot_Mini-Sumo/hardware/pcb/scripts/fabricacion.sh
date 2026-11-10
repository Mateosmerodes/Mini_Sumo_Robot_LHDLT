#!/usr/bin/env bash
# Genera los ficheros de fabricación de la placa base en hardware/pcb/fabricacion/:
#   Gerber + taladros (ZIP para JLCPCB), posiciones de componentes (CPL), BOM, esquemático en PDF.
# Uso: hardware/pcb/scripts/fabricacion.sh
# Antes de pedir la placa: rutado terminado y DRC sin errores (scripts/check.sh). Ver docs/05-PCB.md.
set -eo pipefail
cd "$(dirname "$0")/.."
OUT=fabricacion
rm -rf "$OUT/gerber"; mkdir -p "$OUT/gerber"
PCB=robot_sumo.kicad_pcb
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask --no-x2 -o "$OUT/gerber/" "$PCB"
kicad-cli pcb export drill --format excellon --excellon-separate-th --generate-map --map-format gerberx2 \
  -o "$OUT/gerber/" "$PCB"
(cd "$OUT/gerber" && rm -f ../robot_sumo_gerber.zip && zip -q ../robot_sumo_gerber.zip ./*)
kicad-cli pcb export pos --side both --format csv --units mm --exclude-dnp -o "$OUT/robot_sumo_posiciones.csv" "$PCB"
cp bom.csv "$OUT/robot_sumo_bom.csv"
kicad-cli sch export pdf -o "$OUT/robot_sumo_esquematico.pdf" robot_sumo.kicad_sch
ls -1 "$OUT"
