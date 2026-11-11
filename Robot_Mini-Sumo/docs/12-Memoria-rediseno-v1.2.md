# 12 · Memoria del rediseño v1.2

Qué se revisó, qué se encontró, qué se decidió y por qué. Fecha: 10/11/2026.

*English summary: design review of the v1.1 robot after the professor mandated the Sobotz ST4RT IR start module. Key decisions: ST4RT on a 5-pin JST-SH cable connector powered at 3.3 V; KILL gates the drivers' nSLEEP through an AND gate; buck raised to 5.3 V and series diode removed to keep the DevKit LDO in regulation; 15 A fuse; first firmware with a latched start/stop state machine. Nothing has been built or measured.*

> **Alcance y límites.** Todo es revisión de ficheros y cálculo teórico. El robot no está construido; ninguna afirmación de esta memoria significa que algo funcione, quepa o esté validado. Las webs de Sobotz, OSHWDem y de los vendedores no se pudieron abrir desde el entorno de trabajo: el reglamento se leyó de su repositorio oficial en GitHub y los datos del ST4RT de los resultados de un buscador (ver [06](06-Modulo-arranque-ST4RT.md)).

## 1. Revisión del diseño v1.1

| # | Hallazgo | Gravedad | Resolución v1.2 |
|---|---|---|---|
| 1 | El receptor VS1838B con RC5 decodificado en el ESP32 no es el módulo que exige el profesor y no ofrece parada por hardware | Bloqueante | ST4RT en J17 + puerta AND en nSLEEP ([06](06-Modulo-arranque-ST4RT.md)) |
| 2 | Pin 5 V de la DevKit alimentado desde el buck a 5,0 V a través del diodo D2: con batería baja el AMS1117 de la DevKit podía salir de regulación | Alta | Buck a 5,30 V y sin D2: peor caso 4,46 V frente a 4,40 V necesarios ([08, 5.2](08-Calculos-v1.2.md#52-buck-y-pin-5-v-de-la-devkit-cambio-v12)). Sigue justo: **medir** |
| 3 | Fusible de 10 A por debajo del pico teórico (10,2 A con los 4 drivers en su límite) | Alta | Fusible de 15 A (11,25 A útiles con la reducción del 75 %) |
| 4 | Pull-ups I²C demasiado bajas en paralelo con las de los módulos ToF | Media | 4,7 kΩ; pendiente de mirar si los módulos traen las suyas |
| 5 | Sin firmware en el repositorio | Alta | Firmware v1.2 con pruebas de lógica ([07](07-Firmware.md)) |
| 6 | Frenada ante el borde no estudiada | Media | Cálculo nuevo: en crucero cabe justo; **a fondo no cabe** → el firmware solo va a fondo con el rival a < 15 cm o en contacto ([08, 6.3](08-Calculos-v1.2.md#63-frenada-ante-el-borde-nuevo-en-v12)) |
| 7 | Ficha entregada: capacidad escrita "4.50 mAh", sin nombre del robot, licencia CERN-OHL-P frente a CERN-OHL-S del repositorio | Media | Ficha rehecha con marcadores [COMPLETAR] |
| 8 | Scripts de KiCad solo para KiCad 10; ruta de librerías rota en `check.sh` | Baja | Compatibles con KiCad 9 y 10 |
| 9 | PCB sin rutar | Bloqueante para fabricar | **Rutado terminado** (Freerouting 1.9 + scripts propios), DRC 0 infracciones / 0 sin rutar. Falta la revisión humana y pedirla con 2 oz ([05](05-PCB.md)) |
| 10 | Masa ≈ 420 g frente a 500 g permitidos | Oportunidad | Lastre de plomo o arandelas hasta ≈ 495 g, pesando |

## 2. Decisiones y alternativas

### 2.1 Conexión del ST4RT

| Opción | Ventajas | Inconvenientes | Elegida |
|---|---|---|---|
| **A. Cable JST-SH de 5 polos a J17, módulo en una torre del techo** | El orden de pines de la PCB no depende del módulo; el módulo queda arriba, visible para el mando desde cualquier lado; se cambia sin soldar | Hay que hacer el cable; cinta de doble cara para fijarlo | ✅ |
| B. Huella del módulo soldada en la PCB | Sin cable | La PCB queda tapada por el techo y la DevKit: el receptor no vería el mando; orden de pines sin confirmar | ❌ |
| C. Tira de pines de 2,54 mm | Estándar del módulo p1r.se | Ocupa más; mismo problema de orden de pines | ❌ |

### 2.2 Uso de la línea KILL

| Opción | Elegida | Motivo |
|---|---|---|
| **K a una AND con DRV_EN → nSLEEP de los 4 drivers** | ✅ | La parada no depende del firmware (criterio 10 de la plantilla y art. 5.7: parada "rápida, fiable y segura"). Cuesta una puerta SOT-23-5 |
| K solo a un GPIO | ❌ | No hay GPIO libre en la DevKit y la parada dependería del software |
| K cortando la batería con un MOSFET | ❌ | Haría falta un MOSFET de 15 A más; además el robot se reiniciaría |

Con K = 0 los drivers entran en reposo y los motores quedan en rueda libre; el firmware, al ver START = 0, frena antes durante 300 ms. Riesgo aceptado: si el módulo mantiene K a 1 durante la parada (el p1r.se lo baja), la parada queda solo en el firmware.

### 2.3 Alimentación del ST4RT: 3,3 V frente a 5 V

Se alimenta a **3,3 V** (rango anunciado 2,8–5,2 V) para que S y K salgan a niveles de 3,3 V y lleguen al ESP32 y a la AND sin divisores. Alternativa a 5,3 V descartada: superaría los 5,2 V anunciados.

### 2.4 Otras alternativas estudiadas

Ver [09, apartado 4](09-Lista-de-compra-y-presupuesto.md#4-alternativas-consideradas-decisiones-que-afectan-al-coste): JSUMO JS40F frente a VL53L0X, TB6612FNG frente a DRV8874, Pololu HPCB frente a N20 genéricos.

## 3. Mejoras propuestas para una v2 (no hechas)

1. Aumentar el margen del pin 5 V: alimentar la DevKit por su pin 3V3 desde un LDO o buck propio de 3,3 V (elimina el AMS1117 de la cadena).
2. Liberar un GPIO para leer K y el pin IR en bruto (decodificar RC5 como respaldo).
3. ToF frontales laterales girados ±20°.
4. Neumáticos de silicona colada y medida del coeficiente de rozamiento real.
5. Protección térmica de los motores en el firmware con la corriente de bloqueo medida.
6. Llevar Q1 y F1 a la izquierda de la DevKit, o pasar a 4 capas, para que el tronco de VBAT no tenga que cruzar la fila izquierda de pines con pistas de 0,4 mm ([05, 3.1](05-PCB.md#31-anchos-de-las-pistas-de-potencia)).

## 4. Lo que falta para cerrar el diseño

- Revisar en KiCad la placa ya rutada (DRC limpio) y pedirla con cobre de 2 oz ([05](05-PCB.md)).
- Recibir el ST4RT y medir: orden de pines, niveles de S y K, consumo, tipo de salida ([06, 5](06-Modulo-arranque-ST4RT.md)).
- Medir los motores (corriente y par de bloqueo) y los demás valores de [08, apartado 8](08-Calculos-v1.2.md#8-qué-hay-que-medir-para-cerrar-los-cálculos).
- Imprimir, montar, pesar y medir ([10](10-Montaje-y-fabricacion.md)).
- Respuestas del profesor ([11, apartado 4](11-Cumplimiento-normativo.md#4-preguntas-para-el-profesor--organizador)).
