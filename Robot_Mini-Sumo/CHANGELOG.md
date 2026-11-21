# CHANGELOG

Historial de versiones del robot. Cómo se numera y cómo se recupera una versión antigua: [docs/VERSIONES.md](docs/VERSIONES.md).

Cada versión tiene su etiqueta de git (`v1.0`, `v1.1`, `v1.2`). Lo que aparece en **Quitado** ya no está en el repositorio, pero se puede recuperar desde la etiqueta indicada.

---

## [Sin publicar]

### Añadido
- **Sistema de versiones**: este CHANGELOG, [docs/VERSIONES.md](docs/VERSIONES.md), etiquetas de git `v1.0`, `v1.1` y `v1.2`, y `.gitignore` en la raíz.
- [Informe de consumos y cálculos](docs/Informe-consumos-y-calculos.md) pieza a pieza, con fuentes oficiales, y su script `hardware/calculos/calculos_electricos.py`.
- [Revisión de la PCB v1.2](docs/revisiones/2026-11-21_Revision_PCB_v1.2.pdf) (PDF con imágenes).
- `hardware/pcb/bom.csv` regenerada a partir del esquemático v1.2: 96 piezas en 48 líneas; R68 y R69 van sin montar.
- Imágenes de la placa v1.2: `docs/img/pcb_v1.2_cara_superior.png` y `pcb_v1.2_cara_inferior.png`.

### Cambiado
- **`robot_sumo1.*` pasa a llamarse `robot_sumo.*`**. Nombre del proyecto actualizado dentro del esquemático y del `.kicad_pro`, como hace KiCad con «Guardar como». En el cajetín, el comentario «Generado con gen_sch.py» pasa a «Diseño mantenido a mano en KiCad 10». El diseño no cambia.
- `export_cajas.py` se mueve a `hardware/mecanica/cad/` (es lo único que usa la PCB para el 3D) y ya no depende del generador borrado.
- `hardware/generar_todo.sh` ya **no regenera la PCB**: solo el 3D, los STL/STEP, las imágenes y los cálculos.
- Las entregas de la asignatura pasan a `docs/entregas/`: `Ficha_tecnica_robot.docx` (antes `ficha_técnica_robot.docx`, en la raíz), `Croquis_robot.pdf` (antes `croquis_2_conft.pdf`, en la raíz) y `Modelo_ficha_tecnica_robot.docx`.
- README reescrito con la estructura real y la versión actual.
- Corrección del factor A_IPROPI del DRV8874: 450 µA/A según TI, así que ITRIP = 2,44 A.

### Quitado (recuperable desde la etiqueta indicada)
| Qué | Por qué | Recuperar desde |
|---|---|---|
| Placa v1.1 autogenerada: `hardware/pcb/robot_sumo.kicad_pcb/_sch/_pro/_prl` | Sustituida por la v1.2 rutada a mano | `v1.1` |
| Generadores de la PCB: `hardware/pcb/scripts/` (`design.py`, `gen_sch.py`, `gen_pcb.py`, `gen_pro.py`, `gen_lib.py`, `gen_bom.py`, `libsym.py`, `sexp.py`, `check.sh`) | Desde la v1.2 la PCB se edita a mano: ejecutarlos machacaría el rutado | `v1.1` |
| `docs/Informe-progreso-2026-10-06.md` | Describía la v1.0 (WROOM soldado, USB-C…); superado por los docs 01–04 | `v1.2` |
| `docs/img/pcb_cara_superior.png`, `pcb_cara_inferior.png`, `pcb_esquematico.png`, `pcb_render_3d.png` | Imágenes de la v1.0 | `v1.0` |
| `docs/img/pcb_v1.1_cara_superior.png`, `pcb_v1.1_cara_inferior.png` | Imágenes de la v1.1, sustituidas por las de la v1.2 | `v1.1` |
| `hardware/mecanica/cad/_render/` (35 STL), `__pycache__/`, `robot_sumo.20261006-145430.FCBak` | Ficheros intermedios o de copia de seguridad; se regeneran | `v1.2` |

### Pendiente (para la v1.2.1)
- 🔴 **D3 y R9 movidos después de rutar**: provocan cortos de +3V3 y de ST_IR_RAW con GND, y dejan el LED sin conectar. Devolverlos a (131, 127) y (131, 129) en la hoja de KiCad. Detalle en la [revisión](docs/revisiones/2026-11-21_Revision_PCB_v1.2.pdf).
- Bajar la holgura del netclass a 0,15 mm, que es la del rutado (ahora salen ~240 avisos de DRC).
- I²C: bus a 100 kHz, o pull-ups de 2,2 kΩ.
- Pasar ERC y DRC en KiCad 10.
- Regenerar el 3D desde la v1.2 con `hardware/generar_todo.sh`: los STEP/STL y `pcb_componentes.json` son todavía de la colocación v1.1.
- Unificar la licencia: la ficha entregada dice CERN-OHL-P y el repositorio y la PCB dicen CERN-OHL-S v2.

---

## [v1.2] · 2026-11-20 · Placa rutada a mano (Paulo)

Primera versión **rutada**. Proyecto `robot_sumo1` en KiCad 10; desde ahora se mantiene a mano. Etiqueta en el commit `c50a422`.

### Añadido
- **Módulo de arranque de 5 pines (J17 «ST4RT»)** con START, KILL e IR en bruto (TP1).
- **Corte de motores por hardware**: puerta AND 74LVC1G08 (U3) entre GPIO21 y KILL → nSLEEP de los drivers. Sin módulo, KILL = 0 (R66) y los motores no arrancan.
- **JP1 «banco sin módulo»** + R67, para probar los motores sin módulo. R68 y R69 van sin montar.
- R63/R64 de 1 kΩ en serie y R65/R66 de 100 kΩ a GND en START y KILL; filtro R62 de 10 Ω + C62 de 10 µF en la alimentación del módulo; C15.
- Rutado completo: 1135 tramos, 204 vías y planos de GND y VBAT.

### Cambiado
- Quitado el diodo D2 del buck y **R7 = 59k** → +5V ≈ 5,30 V (más margen para el regulador de la DevKit).
- Fusible **Littelfuse NANO2 de 15 A** (antes 2512 de 10 A).
- Pull-ups de I²C de 4,7 kΩ (antes 2,2 kΩ).
- Grupos de los drivers más compactos (C21/C22 en 0402); J12 (ToF trasero) y J17 intercambian el sitio.
- Netclasses reducidas a «Default».

## [v1.1] · 2026-10-19 · ESP32-S3-DevKitC-1 enchufable

Etiqueta en `c3d4341`. Detalle en [docs/04](docs/04-ESP32-DevKitC-1.md).

### Cambiado
- El ESP32 pasa de módulo WROOM soldado a **DevKitC-1 completa en tiras hembra**. Fuera de la PCB: USB-C, USBLC6, botones, WS2812 y LDO (de 109 a 96 componentes).
- Pinout fuera de GPIO35–37 (vale cualquier variante, también las R8).
- Mecánica: techo a 39 mm, ventana USB trasera, XT30 delante a la izquierda, canales de cable de motor y tornillos M2 × 25.

### Añadido
- Ficha técnica (`docs/Ficha-tecnica.md`) y entregas del equipo: ficha rellena, croquis y modelo de ficha.

## [v1.0] · 2026-10-06 · Primera versión

Etiqueta en `1dc1bc6`.

- Documentación 00–03, selección de componentes y arquitectura eléctrica.
- PCB **generada por script** (`design.py` → esquemático y colocación, sin rutar) con módulo ESP32-S3-WROOM-1 soldado, USB-C, 4 × DRV8874 y buck + LDO.
- Modelo 3D paramétrico en FreeCAD, STL/STEP e informe de progreso del 06/10.

[Sin publicar]: https://github.com/Mateosmerodes/Mini_Sumo_Robot_LHDLT/compare/v1.2...main
[v1.2]: https://github.com/Mateosmerodes/Mini_Sumo_Robot_LHDLT/tree/v1.2
[v1.1]: https://github.com/Mateosmerodes/Mini_Sumo_Robot_LHDLT/tree/v1.1
[v1.0]: https://github.com/Mateosmerodes/Mini_Sumo_Robot_LHDLT/tree/v1.0
