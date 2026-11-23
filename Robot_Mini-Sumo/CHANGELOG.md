# Registro de cambios

Nada de lo indicado está probado en un robot físico.

## 2026-11-23 · Ficha técnica v2

- Ficha técnica del robot v2 (plantilla del curso rellenada) y anexo de cálculos en `entrega/ficha-tecnica/`.
- Script `hardware/calculos/calculos_v2.py`: corrientes de motores y drivers, bloqueo, potencia máxima (40,5 W), fusible de 7,5 A, regulador LM2940, autonomía (≈ 11 min) y masa (≈ 233 g).
- Aviso: empujando bloqueado al 85 % de PWM más de unos segundos, el TB6612FNG puede llegar a su corte térmico; se recomienda bajar a ~70 % tras 2 s si la corriente de bloqueo medida se acerca a la estimada.

## v2.1 chasis — 23/11/2026

- Base mecánica del equipo en `hardware/chasis/`: chasis impreso de una pieza (cuña de 34° con cuchilla de acero opcional, túnel lateral para la batería, alojamientos de los 2 N20 con abrazadera, soportes de los 2 VL53L0X, huecos de los 2 QRE1113 en la rampa, 4 columnas M3 para la PCB, huecos de lastre y "LHDT" grabado debajo).
- Script paramétrico para **Fusion 360** + STEP/STL + comprobaciones (envolvente 98 × 97,2 mm, 0 choques con las piezas y las patillas de la PCB) e imágenes. Sin imprimir ni probar; el script de Fusion solo se ha probado con una API simulada.

## v2.0 básico — 23/11/2026

Cambio de rumbo: se simplifica el robot al mínimo que cumple.
- Todo el diseño anterior se archiva en `archivo/v1-4motores/` (estado completo en el commit `7e4c077`).
- **2 motores** en vez de 4. Se mantienen la ESP32-S3-DevKitC-1, los N20, los VL53L0X (ahora 2), los QRE1113 (ahora 2), la LiPo 2S con XT30 y el módulo de arranque ST4RT.
- Drivers: **2 módulos TB6612FNG** enchufables, cada uno con sus dos canales en paralelo para un motor (antes 4 DRV8874 SMD).
- 5 V con un **LM2940CT-5.0** (TO-220) en vez del buck SMD. Fusible de cuchilla mini de 7,5 A.
- Placa nueva de **agujero pasante**, 76 × 80 mm, reglas holgadas (pista mínima 0,4 mm), serigrafía con el nombre de cada conector y de cada pin. DRC 0 errores, 0 sin rutar; esquemático y placa iguales pin a pin.
- Firmware nuevo y corto: `firmware/sumo_lhdt_v2/`.
- Documentación en un solo fichero: `docs/01-Diseno-v2-basico.md`.

## v1.x (hasta el 16/11/2026)

Ver [`../archivo/v1-4motores/CHANGELOG.md`](../archivo/v1-4motores/CHANGELOG.md).
