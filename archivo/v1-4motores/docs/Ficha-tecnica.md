# Ficha técnica del robot (diseño v1.2)

Respuestas a la plantilla del profesor [`Modelo_ficha_técnica_robot.docx`](../Modelo_ficha_t%C3%A9cnica_robot.docx), con el mismo orden de apartados. Sustituye a la ficha entregada en octubre (v1.1, en `entrega/`).

> **Cómo leer esta ficha.** Los valores salen del diseño v1.2 (ficheros del repositorio) y de los cálculos de [08 · Cálculos v1.2](08-Calculos-v1.2.md). El robot **aún no está construido**: lo marcado **(a medir)** es una estimación o un dato del vendedor sin comprobar, y lo marcado **[COMPLETAR]** lo tiene que decidir o aportar el equipo. Nada de esta ficha se ha medido en el robot real.

## 1. Datos generales

| | |
|---|---|
| **Nombre del equipo** | Hombres de las Tabernas (LHDT) |
| **Nombre del robot** | **[COMPLETAR: nombre o número del robot]** (obligatorio, reglamento art. 5.6) |
| **Licencia de hardware libre** | Hardware **CERN-OHL-S v2** · software **MIT** (son las del repositorio y la serigrafía). ⚠️ La ficha entregada en octubre ponía CERN-OHL-P: **[COMPLETAR: confirmar cuál]** |
| **Repositorio** | https://github.com/Mateosmerodes/Mini_Sumo_Robot_LHDLT (esquemáticos, PCB, CAD, firmware y documentación) |

## 2. Especificaciones mecánicas

| Parámetro | Valor nominal |
|---|---|
| **Dimensiones (ancho × largo × alto)** | **9,8 × 9,8 × 5,9 cm** (modelo 3D; la altura incluye la torre del módulo de arranque) |
| **Masa total (con batería)** | **≈ 420–426 g** sin lastre (estimada); **objetivo ≤ 495 g** con lastre **(a pesar)** |
| **Material del chasis** | **PCB de FR4** de 1,6 mm como chasis + piezas de **PETG** impresas (rampa-cuna, cuna trasera, carcasa, techo) + cuchilla de fleje de acero de 0,4 mm + lastre de acero/plomo |
| **Tipo de tracción** | **4WD** (4 motores N20, uno por rueda) |
| **Superficie de ruedas** | **Goma** (ruedas N20 comerciales Ø 30 mm); más adelante, **silicona** colada en molde propio. Sin sustancias adherentes |

**Fundamento:** envolvente del modelo 3D 98,0 × 98,0 × 58,6 mm (1 mm de margen por lado sobre 10 × 10 cm). Masa del modelo 405,5 g + 15–20 g de cables y tornillos no modelados ([08, 6.1](08-Calculos-v1.2.md#61-masa-y-dimensiones)).

## 3. Sistema eléctrico y de potencia

### 3.1. Fuente de alimentación (batería)

| | |
|---|---|
| **Tipo** | **LiPo 2S** con conector XT30 |
| **Tensión nominal** | **7,4 V** (2 × 3,7 V) |
| **Tensión máxima a plena carga** | **8,4 V** (2 × 4,2 V) |
| **Capacidad** | **450 mAh** (cabe hasta 650 mAh en la bahía de 55 × 31 × 14 mm) — **[COMPLETAR: modelo comprado]** |
| **Tasa de descarga (C)** | **≥ 30 C** (mínimo necesario: 21 C) |
| **Protección eléctrica** | MOSFET P **AOD4185** contra inversión de polaridad · **fusible rápido de 15 A** (v1.2; antes 10 A) · **limitación de corriente por hardware** en cada driver (I_TRIP = 2,44 A) · **medida de tensión de batería** (divisor 100 k / 33 k) con aviso a 3,4 V/celda y potencia limitada al 50 % por debajo de 3,2 V/celda · subtensión y temperatura en los drivers · **parada por hardware** desde el módulo de arranque (KILL → nSLEEP de los drivers) |

**Fundamento:** pico de batería con los 4 drivers en su límite = 4 × 2,44 + 0,4 = **10,2 A** → C mínimo = 10,2 / 0,45 ≈ 23 C con ese techo (21 C con el bloqueo estimado de los motores). Fusible 15 A × 0,75 = 11,25 A útiles (+11 %) ([08, 3](08-Calculos-v1.2.md#3-batería-y-potencia)).

### 3.2. Actuadores (motores y drivers)

| | |
|---|---|
| **Modelo / tipo de motor** | **N20 micromotorreductor** 6 V ~500 rpm, reductora metálica (×4) — **[COMPLETAR: modelo/vendedor exacto]** |
| **Tensión de trabajo** | **6,6–8,4 V** (batería directa por PWM); en búsqueda y crucero el PWM se compensa a 7,4 V equivalentes |
| **Consumo a bloqueo (stall current)** | **≈ 2,0 A a 7,4 V / 2,2 A a 8,4 V por motor (a medir)** — supuesto 1,6 A a 6 V |
| **Controlador de motores (driver)** | **TI DRV8874** (uno por motor, en la PCB propia) |
| **Rango de tensiones admitidas (driver)** | **4,5–37 V** (VM); entradas lógicas compatibles con 3,3 V |
| **Corriente máxima por canal** | **6 A de pico** (protección por sobrecorriente) / **limitada por diseño a 2,44 A** (I_TRIP). Corriente continua: depende de la disipación de la placa (≈ 2,1 A según el diseño v1.1; **sin confirmar en la hoja de TI**) |

**Fundamento:** I_TRIP = V_REF / (A_IPROPI · R_IPROPI) = 1,65 V / (455 µA/A × 1,5 kΩ) = 2,44 A. Con el motor bloqueado a 8,4 V, el driver disipa ≈ 1,8 W → T_unión ≈ 95–113 °C ([08, 4](08-Calculos-v1.2.md#4-motores-y-drivers)).

### 3.3. Consumo eléctrico estimado

| | |
|---|---|
| **Potencia máxima calculada** | **≈ 85 W** (4 motores en el límite de corriente con la batería llena + electrónica); 79 W con el bloqueo estimado |
| **Autonomía estimada en combate continuo** | **≈ 2,7 min** empujando todo el tiempo; **≈ 5,0 min** en un combate típico (40 % empujando) con 450 mAh |
| **Fundamento del cálculo de autonomía** | t = 0,8 · C / I_media. I_media = f · 4 · I_bloqueo(7,4 V) + (1 − f) · 4 · 0,4 A + I_electrónica (0,24 A). Con f = 1: 8,1 A → 2,7 min; con f = 0,4: 4,4 A → 5,0 min. Se usa el 80 % de la capacidad para no bajar de 3,3 V/celda. Conservador: con PWM < 100 % la corriente de batería es menor. Depende de la corriente de bloqueo real **(a medir)** ([08, 7](08-Calculos-v1.2.md#7-autonomía)) |

## 4. Sistema de control y sensado

| Elemento | Tipo / modelo | Tensión admitida / de operación | Corriente nominal |
|---|---|---|---|
| **Placa de control abierta** | **Espressif ESP32-S3-DevKitC-1** enchufada en la placa base propia v1.2 | 5 V por su pin 5V (≈ 4,75–4,90 V en el robot) / ESP32-S3 a 3,3 V | ≈ 100 mA (Wi-Fi apagado) |
| **Módulo del receptor IR** | **Sobotz ST4RT** (lo entrega el profesor), compatible con el start module de p1r.se, protocolo RC5 | 2,8–5,2 V según el fabricante (sin hoja) / **3,3 V** en el robot | **(a medir)**: no publicado |
| **Sensores de borde (línea)** | **onsemi QRE1113** analógico (módulo), × 4: 2 delante, 2 detrás | 3,3 V | ≈ 21 mA c/u (LED IR con 100 Ω) |
| **Sensores de oponente** | **ST VL53L0X** ToF (módulo GY-VL53L0XV2), × 6: 3 frontales, 2 laterales, 1 trasero | 3,3 V | ≈ 19 mA c/u midiendo (cota alta; a medir) |
| **Controladores de motor** | **TI DRV8874** × 4 | VM 6,6–8,4 V; lógica 3,3 V | ver 3.2 |
| **Regulador** | TI TPS563201 (buck a 5,3 V) + LDO de la DevKit (3,3 V) | 6,6–8,4 V de entrada | 0,30 A típ. / 0,56 A pico en 3,3 V |

## 5. Inspección reglamentaria y seguridad

Autoevaluación del equipo (la columna "Notas del inspector" es para el juez). Detalle y evidencias: [11 · Cumplimiento](11-Cumplimiento-normativo.md).

| Criterio | Estado (equipo) | Nota del equipo |
|---|---|---|
| 1. Dispositivos de interferencia (jamming) | [x] CUMPLE | Sin emisores para cegar. Los VL53L0X usan láser IR de clase 1 para medir distancia |
| 2. Daño al dohyo o al oponente/operador | [x] CUMPLE | Cuchilla con el filo matado; parada fiable por hardware |
| 3. Fluidos, polvo, gas u otras sustancias | [x] CUMPLE | — |
| 4. Pirotecnia | [x] CUMPLE | — |
| 5. Lanzamiento de objetos | [x] CUMPLE | — |
| 6. Sustancias pegajosas | [x] CUMPLE | Ruedas de goma/silicona limpias |
| 7. Incremento artificial del efecto suelo | [x] CUMPLE | Sin vacío ni imanes |
| 8. Fuente de energía permitida | [x] CUMPLE | LiPo 2S |
| 9. Dimensiones y masa | [ ] pendiente | 98 × 98 mm y ≈ 420–495 g en el diseño: **medir y pesar el robot construido** |
| 10. Arranque por IR / kill switch | [ ] pendiente | ST4RT integrado (START al ESP32, KILL a los drivers por hardware); corte total desenchufando el XT30. **Pendiente de probar con el módulo y de confirmar con el profesor** si vale como "kill switch accesible" |
| 11. Hardware libre (no obligatorio) | [x] CUMPLE | Repositorio público con PCB, CAD y firmware |
