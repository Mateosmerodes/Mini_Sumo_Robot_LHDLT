# Registro de cambios

Formato: versión del diseño, fecha y qué cambia. Nada de lo indicado está probado en un robot físico.

## v1.2 — 10/11/2026 (diseño, sin fabricar)

Motivo principal: el profesor entrega el módulo de arranque IR **Sobotz ST4RT** (principios de diciembre de 2026) y el reglamento OSHWDem rev. 7 exige arranque **y parada** por IR (art. 5.4). Se revisa también todo lo detectado en la revisión del informe de consumos (PR #3).

### Electrónica (`hardware/pcb/scripts/design.py`)
- **Módulo de arranque**: se quita el receptor VS1838B (J17, R62, C62 antiguos). El ST4RT va en **J17, JST-SH de 5 polos** (VCC, GND, S, K, IR) con cable hecho a medida, para no depender del orden de pines del módulo.
  - Alimentación a 3,3 V con filtro RC (R62 = 10 Ω, C62 = 10 µF).
  - S y K con resistencia serie de 1 kΩ (R63, R64) y pull-down de 100 kΩ (R65, R66). Pull-ups R68/R69 **sin montar** por si las salidas fueran de drenador abierto.
  - **Parada por hardware**: puerta AND **74LVC1G08 (U3)**: nSLEEP de los drivers = DRV_EN (GPIO21) · K. Sin K a 1, los motores no pueden moverse aunque el firmware falle.
  - Puente de soldadura **JP1 "BANCO"** (con R67) para fijar K a 1 y probar sin módulo.
  - Pin IR en bruto llevado al punto de prueba **TP1**.
- **5 V de la DevKit**: se elimina el diodo D2 y el buck TPS563201 pasa a 5,30 V (R7 = 59 kΩ). Antes, en el peor caso, el LDO de la DevKit quedaba sin margen.
- **Fusible 15 A** (Littelfuse NANO2 451/453), antes 10 A: el pico de los 4 drivers en su límite es 10,2 A.
- **Pull-ups I²C de 4,7 kΩ** (R60, R61), antes más bajas: corriente de sumidero ≤ 3 mA con los módulos en paralelo.
- R17 (100 kΩ) mantiene DRV_EN a 0 durante el arranque del ESP32.
- Conectores J17 (ST4RT) y J12 (ToF trasero) intercambiados de sitio para que el ST4RT quede bajo su torre.
- Reglas de diseño: zonas sin cobre alrededor de los taladros M2, holguras a agujeros y borde; clases de red Default 0,2/0,15 mm y Potencia 0,8 mm.
- Nuevo `scripts/autoroute.py` (Freerouting). **El rutado no está terminado** (ver [docs/05](docs/05-PCB.md)).
- Herramientas: los scripts funcionan con KiCad 9 y 10 (`check.sh` detecta la versión; librería de símbolos en formato 9).
- `bom.csv` ya no incluye los componentes sin montar (DNP).

### Mecánica (`hardware/geometria.py`, `hardware/mecanica/cad/robot.py`)
- **Torre del ST4RT** en el techo: alojamiento de 10,8 × 10,8 × 4 mm a 12 mm sobre el techo, visible desde arriba y desde todos los lados, con canal para el cable.
- Altura total 58,6 mm (antes ≈ 55 mm); masa del modelo 405,5 g.
- Regenerados STEP, STL, FCStd e imágenes.

### Firmware (nuevo, `firmware/`)
- Primer firmware del robot: máquina de estados de arranque ESPERA → COMBATE → PARADO (enclavada), estrategia con prioridad borde > ataque > búsqueda, compensación de batería, telemetría.
- Pruebas de la lógica en el PC (`firmware/test/test_logica.cpp`).

### Cálculos (`hardware/calculos/calculos_electricos.py`)
- Nuevos apartados: ST4RT, frenada ante el borde, geometría de la rampa, masa leída del modelo 3D.
- Actualizados: buck a 5,3 V, fusible, I²C. Documento: [docs/08](docs/08-Calculos-v1.2.md).

### Documentación
- Nuevos: 05 (PCB), 06 (ST4RT), 07 (firmware), 08 (cálculos v1.2), 09 (compra y presupuesto), 10 (montaje y fabricación), 11 (cumplimiento), 12 (memoria del rediseño), informe académico (borrador).
- Ficha técnica rehecha para la v1.2.
- Los documentos 00–04 y los informes de octubre se conservan como histórico de la v1.1, con un aviso al principio.

## v1.1 — 06/10/2026
- Cambio a ESP32-S3-DevKitC-1 enchufable sobre la placa base; 4 DRV8874; 6 VL53L0X; 4 QRE1113; receptor VS1838B.
- Ficha técnica entregada en octubre (`entrega/`) e informe de consumos (PR #3).
