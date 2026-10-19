# Ficha técnica del robot

Respuestas al [`Modelo_ficha_técnica_robot.docx`](../Modelo_ficha_t%C3%A9cnica_robot.docx), con los cálculos que hay detrás de cada número.

> Los datos salen del diseño actual (placa base v1.1 con la ESP32-S3-DevKitC-1, modelo 3D de `hardware/mecanica/cad/informe_3d.json`). Lo marcado con **(a medir)** es una estimación hasta que lleguen las piezas: sobre todo la **corriente de bloqueo de los N20**, que en los de AliExpress varía mucho. Cuando la midáis, se rehacen las cuentas de los apartados 3.2 y 3.3 cambiando un solo dato.

## 1. Datos generales

| | |
|---|---|
| **Nombre del equipo / robot** | Hombres de las Tabernas / *[nombre del robot por decidir]* |
| **Licencia de hardware libre** | Hardware **CERN-OHL-S v2** · software **MIT** |
| **Repositorio** | https://github.com/Mateosmerodes/Mini_Sumo_Robot_LHDLT (esquemáticos, PCB, modelo 3D y documentación) |

## 2. Especificaciones mecánicas

| Parámetro | Valor nominal |
|---|---|
| **Dimensiones (ancho × largo × alto)** | **9,8 × 9,8 × 5,5 cm** |
| **Masa total (con batería)** | **≈ 420 g** ahora; **objetivo 480–495 g** con lastre de plomo |
| **Material del chasis** | **PCB de FR4** de 1,6 mm como chasis + piezas de **PETG** impresas (cuña, cunas de motores, carcasa) + lastre de acero/plomo + cuchilla de acero de 0,4 mm |
| **Tipo de tracción** | **4WD** (4 motores N20, uno por rueda) |
| **Superficie de ruedas** | **Goma** (ruedas N20 comerciales de 30 mm); en la v2, **silicona** 20–30 Shore A colada en molde |

**Cálculos:**
- **Dimensiones:** envolvente medida en el modelo 3D: 98 × 98 × 55,1 mm. Deja 1 mm de margen por lado sobre los 10 × 10 cm del reglamento. La altura no tiene límite.
- **Masa:** el modelo 3D suma 403,8 g (lastre de acero 173 g, cuña con cuchilla y QRE 46 g, motores 40 g, PCB con DevKit 33 g, ruedas 33 g, batería 32 g, pieza trasera 24 g, techo y sensores 13 g, paredes 10 g). Faltan cables y tornillería, unos 15–20 g → **≈ 420 g**. Pasando el lastre de acero (7,85 g/cm³) a plomo (11,3 g/cm³), el mismo volumen pesa 173 × 11,3 / 7,85 ≈ 249 g, es decir, +76 g → **≈ 496 g**. El ajuste fino se hace con báscula para no pasar de 500 g.

## 3. Sistema eléctrico y de potencia

### 3.1. Fuente de alimentación (batería)

| | |
|---|---|
| **Tipo** | **LiPo 2S** con conector XT30 |
| **Tensión nominal** | **7,4 V** (2 × 3,7 V) |
| **Tensión máxima a plena carga** | **8,4 V** (2 × 4,2 V) |
| **Capacidad** | **450 mAh** (válida hasta 650 mAh; caben en la bahía de 55 × 31 × 14 mm) |
| **Tasa de descarga (C)** | **30 C** (mínimo necesario: 21 C) |
| **Protección eléctrica** | MOSFET P **AOD4185** contra inversión de polaridad · **fusible rápido de 10 A** (2512) · **limitación de corriente por hardware** en cada driver (ITRIP ≈ 2,4 A) · **medida de tensión de batería** (divisor 100 k / 33 k al ADC) para el **aviso de batería baja** (3,3 V por celda) · apagado por subtensión y temperatura en los drivers |

**Cálculos:**
- **C mínimo:** corriente de pico de la batería ≈ 9,4 A (ver 3.3) → 9,4 A / 0,45 Ah ≈ **21 C**. Con 30 C la batería da 0,45 × 30 = **13,5 A**: margen del 44 %.
- **Fusible:** 9,4 A de pico (en el peor caso teórico, con los 4 motores bloqueados y la batería llena) < 10 A. Un fusible rápido de 10 A aguanta su corriente nominal de forma continua y salta con un cortocircuito.
- **Divisor de batería:** 8,4 V × 33 / (100 + 33) = **2,08 V** en el ADC, por debajo de los 3,3 V del ESP32. Con 6,6 V (3,3 V por celda) se leen 1,64 V: ese es el umbral del aviso.

### 3.2. Actuadores (motores y drivers)

| | |
|---|---|
| **Modelo / tipo de motor** | **N20 micro motorreductor**, 6 V, ~500 rpm, reductora metálica (×4) |
| **Tensión de trabajo** | **6,6–8,4 V** (batería directa); PWM limitado a ~75 % en marcha normal (≈ 6 V eficaces) y 100 % en el ataque |
| **Consumo a bloqueo** | **≈ 1,6 A a 6 V → ≈ 2,0 A a 7,4 V → ≈ 2,2 A a 8,4 V** por motor **(a medir)** |
| **Controlador (driver)** | **TI DRV8874**, uno por motor (4 en total) |
| **Rango de tensiones del driver** | **4,5–37 V** (VM); lógica compatible con 3,3 V |
| **Corriente máxima por canal** | **2,1 A continuos / 6 A de pico** (limitada por hardware a **≈ 2,4 A** con ITRIP) |

**Cálculos:**
- **Corriente de bloqueo:** con el motor parado no hay fuerza contraelectromotriz y solo frena la resistencia del bobinado: R = 6 V / 1,6 A ≈ **3,75 Ω**. Entonces I = V / R: 7,4 / 3,75 = **1,97 A** y 8,4 / 3,75 = **2,24 A**.
- **Límite de corriente (ITRIP):** V_REF = 3,3 V × 10 k / (10 k + 10 k) = 1,65 V. I_TRIP = V_REF / (A_IPROPI × R_IPROPI) = 1,65 / (455 µA/A × 1,5 kΩ) = **2,42 A**. Queda por encima del bloqueo estimado (2,24 A): el motor no se recorta en uso normal, pero si sale un N20 con más consumo, el driver lo limita a 2,4 A y no se quema. **Cuando midáis el bloqueo real, se ajusta R_IPROPI.**
- **Por qué este driver aguanta:** cada DRV8874 solo ve la corriente de **un** motor (≤ 2,24 A), dentro de sus 2,1 A continuos con margen hasta los 6 A de pico. Con 0,2 Ω de resistencia interna disipa 2,24² × 0,2 ≈ **1 W** en el peor caso; el pad térmico va sobre un plano de GND con 12 vías.
- **Sobretensión de los motores:** 8,4 V / 6 V = **1,4** (40 % por encima de su tensión nominal) solo con la batería llena y PWM al 100 %; en marcha normal el PWM al 75 % deja ≈ 6 V eficaces.

### 3.3. Consumo eléctrico estimado

| | |
|---|---|
| **Potencia máxima calculada** | **≈ 79 W** de pico teórico (batería llena y 4 motores bloqueados); **≈ 62 W** con la batería a tensión nominal |
| **Autonomía estimada en combate continuo** | **≈ 5 minutos** con la batería de 450 mAh (≈ 7 min con una de 650 mAh) |
| **Fundamento del cálculo** | Ver abajo: capacidad útil del 80 % repartida entre un perfil de combate con un 40 % del tiempo empujando |

**Potencia máxima:**

| Carga | Cálculo | Potencia |
|---|---|---|
| 4 motores bloqueados, batería llena | 4 × 8,4 V × 2,24 A | 75,3 W |
| Electrónica a 3,3 V en pico | 5,53 V × 0,55 A / 0,9 (rendimiento del buck) | 3,4 W |
| **Total** | | **≈ 79 W → 9,4 A de batería** |
| *Igual, a tensión nominal* | 4 × 7,4 V × 1,97 A + 3,4 W | *≈ 62 W* |

En la práctica será algo menos: la tensión de la batería cae con 9 A y el firmware no tiene por qué mantener los cuatro motores bloqueados a la vez.

**Consumo de la electrónica (raíl de 3,3 V):**

| Elemento | Típica | Pico |
|---|---|---|
| ESP32-S3 (DevKitC-1) con Wi-Fi | 100 mA | 350 mA |
| 6 × VL53L0X | 6 × 19 = 114 mA | 114 mA |
| 4 × QRE1113 (LED con 100 Ω: (3,3 − 1,2) / 100) | 4 × 21 = 84 mA | 84 mA |
| Receptor IR, LED de alimentación, pull-ups | ~5 mA | ~5 mA |
| **Total 3,3 V** | **≈ 300 mA** | **≈ 550 mA** |

Sale del LDO de la DevKit (800 mA – 1 A) ✔. Visto desde la batería: 5,53 V × 0,30 A / 0,9 = 1,84 W → **0,25 A** típicos (0,46 A de pico).

**Autonomía (fundamento del cálculo):**

1. **Capacidad útil:** no se descarga por debajo de 3,3 V por celda, así que se cuenta el **80 %**: 0,8 × 450 mAh = **360 mAh**.
2. **Perfil de combate continuo:** 40 % del tiempo **empujando** (motores casi parados, a corriente de bloqueo: 4 × 1,97 A = 7,9 A) y 60 % **buscando o maniobrando** (~0,4 A por motor con aceleraciones: 1,6 A), más la electrónica (0,25 A):
   I_media = 0,4 × 7,9 + 0,6 × 1,6 + 0,25 ≈ **4,4 A**
3. **Autonomía** = capacidad útil / corriente media = 360 mAh / 4 370 mA = 0,082 h ≈ **4,9 min**.

| Escenario | Corriente media | 450 mAh | 650 mAh |
|---|---|---|---|
| Peor caso: empujando todo el rato | 8,1 A | 2,7 min | 3,8 min |
| **Combate típico (40 % empujando)** | **4,4 A** | **4,9 min** | **7,1 min** |
| Solo buscando, sin empujar | 1,9 A | 11,7 min | 16,9 min |

Un combate son 3 min de asaltos con pausas, así que **una batería de 450 mAh aguanta un combate** con margen (incluso en el peor caso casi llega). **Hay que llevar dos baterías** y cargar entre combates.

## 4. Sistema de control y sensado

| Elemento | Tipo / modelo | Tensiones admitidas y de operación | Corriente nominal |
|---|---|---|---|
| **Placa de control abierta** | **Espressif ESP32-S3-DevKitC-1** (ESP32-S3, doble núcleo 240 MHz, Wi-Fi + BLE), enchufada en nuestra PCB base | Entrada 5 V por el pin 5V o USB (nosotros le damos ≈ 4,7 V); el chip trabaja a **3,3 V** (3,0–3,6 V) | ≈ 100 mA (350 mA de pico con Wi-Fi) |
| **Receptor IR de arranque** | **VS1838B / TSOP38238**, 38 kHz, protocolo **RC5** | Admite 2,7–5,5 V; trabaja a **3,3 V** (con filtro RC 100 Ω + 4,7 µF) | ≈ 1 mA |
| **Sensores de borde (línea)** | **QRE1113 analógico** (módulo), × 4: 2 delante y 2 detrás | Admite 3,3–5 V; trabaja a **3,3 V** | ≈ 21 mA cada uno (LED IR) |
| **Sensores de oponente** | **VL53L0X ToF** (módulo GY-VL53L0XV2), × 6: 3 frontales, 2 laterales, 1 trasero | Admite 2,6–5,5 V (regulador propio); trabaja a **3,3 V**, I²C | ≈ 19 mA cada uno midiendo |
| **Drivers de motor** | **TI DRV8874** × 4, con sensado de corriente (IPROPI) | Potencia 4,5–37 V (trabaja a 6,6–8,4 V); entradas lógicas a **3,3 V** | Hasta 2,4 A por motor (limitado) |
| **Regulador de 5 V** | **TI TPS563201** (buck síncrono) | Entrada 4,5–17 V (trabaja a 6,6–8,4 V); salida 5,5 V | Hasta 3 A |
| **Expansión** | Conector I²C tipo Qwiic para IMU opcional (MPU-6050 / LSM6DS3) | 3,3 V | ~4 mA |

> **Todo lo que habla con el ESP32 está alimentado a 3,3 V**, así que ninguna señal puede pasar de 3,3 V en un GPIO y no hace falta ningún adaptador de nivel.

## 5. Inspección reglamentaria y seguridad

| Criterio | Estado | Justificación (para el inspector) |
|---|---|---|
| **1. Dispositivos de interferencia (jamming)** | ☑ CUMPLE | No hay emisores para cegar al rival. Los únicos emisores IR son los de nuestros propios sensores: los VL53L0X (láser de clase 1, pulsos de baja potencia para medir) y los QRE1113, que apuntan al suelo. |
| **2. Daño al dohyo o al oponente** | ☑ CUMPLE | La cuchilla de acero de 0,4 mm tiene el **filo matado**: está pensada para meterse por debajo, no para cortar. Sin partes punzantes. Frenado activo por firmware. |
| **3. Fluidos, polvo, gas u otras sustancias** | ☑ CUMPLE | No lleva ningún depósito ni mecanismo de este tipo. |
| **4. Pirotecnia** | ☑ CUMPLE | Nada pirotécnico ni inflamable. La batería LiPo va protegida por fusible y limitación de corriente. |
| **5. Lanzamiento de objetos** | ☑ CUMPLE | Sin mecanismos de lanzamiento. Todas las piezas van atornilladas. |
| **6. Sustancias pegajosas** | ☑ CUMPLE | Ruedas de goma/silicona limpias, sin productos adherentes. |
| **7. Incremento artificial del "efecto suelo"** | ☑ CUMPLE | Sin vacío, succión ni imanes. El agarre sale solo de **peso × rozamiento** (lastre bajo la PCB). |
| **8. Fuente de energía permitida** | ☑ CUMPLE | Solo una batería LiPo 2S. |
| **9. Dimensiones y masa** | ☑ CUMPLE | 9,8 × 9,8 cm en planta (altura 5,5 cm, sin límite). Masa ≈ 420 g ahora, se ajustará con báscula a < 500 g. |
| **10. Arranque por infrarrojos / kill switch** | ☑ CUMPLE | Receptor IR de 38 kHz con decodificación **RC5** del mando del juez para **arrancar y parar**. **Kill switch:** desenchufar el **XT30**, accesible desde arriba por el techo, corta toda la alimentación. ⚠️ Confirmar con la organización si aceptan el XT30 como kill switch o quieren un interruptor. |
| **11. Filosofía hardware libre** | ☑ CUMPLE | ESP32-S3 programado con Arduino/ESP-IDF (abiertos) y PCB, modelo 3D y código publicados en el repositorio con licencias CERN-OHL-S v2 y MIT. |
