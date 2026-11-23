# Registro de cambios

Nada de lo indicado está probado en un robot físico.

## v2.0 básico — 23/11/2026

Cambio de rumbo: se simplifica el robot al mínimo que cumple.
- Todo el diseño anterior se archiva en `archivo/v1-4motores/` (y etiquetas `v1-archivo` y `v1-archivo-pr3`).
- **2 motores** en vez de 4. Se mantienen la ESP32-S3-DevKitC-1, los N20, los VL53L0X (ahora 2), los QRE1113 (ahora 2), la LiPo 2S con XT30 y el módulo de arranque ST4RT.
- Drivers: **2 módulos TB6612FNG** enchufables, cada uno con sus dos canales en paralelo para un motor (antes 4 DRV8874 SMD).
- 5 V con un **LM2940CT-5.0** (TO-220) en vez del buck SMD. Fusible de cuchilla mini de 7,5 A.
- Placa nueva de **agujero pasante**, 76 × 80 mm, reglas holgadas (pista mínima 0,4 mm), serigrafía con el nombre de cada conector y de cada pin. DRC 0 errores, 0 sin rutar; esquemático y placa iguales pin a pin.
- Firmware nuevo y corto: `firmware/sumo_lhdt_v2/`.
- Documentación en un solo fichero: `docs/01-Diseno-v2-basico.md`.

## v1.x (hasta el 16/11/2026)

Ver [`../archivo/v1-4motores/CHANGELOG.md`](../archivo/v1-4motores/CHANGELOG.md).
