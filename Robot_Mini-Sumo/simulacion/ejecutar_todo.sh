#!/usr/bin/env bash
# Repite todas las simulaciones de la placa v1.2 y regenera graficas/ y resultados/*.json.
# Necesita: ngspice (con XSPICE), python3 con numpy/scipy/matplotlib, g++ y KiCad 9 (módulo pcbnew).
# Tarda unos 10 minutos. Los ficheros intermedios grandes van a $SIM_TMP (por defecto /tmp/sim_lhdt).
set -e
D="$(cd "$(dirname "$0")" && pwd)"
export SIM_TMP="${SIM_TMP:-/tmp/sim_lhdt}"
mkdir -p "$SIM_TMP/fw" "$D/resultados" "$D/graficas"
PCB="$D/../hardware/pcb"
echo "1/5 cobre (VBAT y GND) y calentamiento"
(cd "$PCB" && python3 "$D/scripts/cobre.py" robot_sumo.kicad_pcb VBAT F1.2 U5.11,U6.11,U7.11,U8.11 1 2.44 "$D/resultados/cobre_VBAT.npz" 2>/dev/null \
  && python3 "$D/scripts/cobre.py" robot_sumo.kicad_pcb GND J1.1 U5.17,U6.17,U7.17,U8.17 1 2.44 "$D/resultados/cobre_GND.npz" 2>/dev/null \
  && python3 "$D/scripts/termico.py" robot_sumo.kicad_pcb "$D/resultados" 2>/dev/null) | tee "$D/resultados/cobre_termico.txt"
(cd "$D/scripts" && python3 graficas_cobre.py)
echo "2/5 entrada de batería y motores (ngspice)"
(cd "$D/spice" && python3 ../scripts/sim_entrada.py > /dev/null)
echo "3/5 buck y arranque de la placa (ngspice)"
(cd "$D/spice" && python3 ../scripts/sim_buck.py > /dev/null)
echo "4/5 VBAT_SENSE e IPROPI (ngspice)"
(cd "$D/spice" && python3 ../scripts/sim_sensado.py > /dev/null)
echo "5/5 lógica del firmware"
g++ -O2 -std=c++17 -I "$D/../firmware/sumo_lhdt" "$D/firmware/sim_combate.cpp" -o "$SIM_TMP/sim_combate"
"$SIM_TMP/sim_combate" "$SIM_TMP/fw" > "$SIM_TMP/fw/firmware.json"
(cd "$D/scripts" && python3 graficas_firmware.py "$SIM_TMP/fw")
echo "Hecho: gráficas en $D/graficas, números en $D/resultados"
