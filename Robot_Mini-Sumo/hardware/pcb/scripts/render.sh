#!/usr/bin/env bash
# Exporta una vista de la cara superior a PNG para revisar: render.sh salida.png [capas]
set -e
cd "$(dirname "$0")/.."
L=${2:-Edge.Cuts,F.Cu,F.SilkS,F.CrtYd}
kicad-cli pcb export svg --exclude-drawing-sheet --page-size-mode 2 --layers $L -o /tmp/claude-0/r.svg robot_sumo.kicad_pcb >/dev/null
cd /tmp/claude-0 && NODE_PATH=$(npm root -g) node svg2png.js /tmp/claude-0/r.svg "$1" ${3:-1400}
