# 01 · Selección de componentes (y por qué)

> ⚠️ **Documento de la v1.1 (octubre de 2026).** El diseño actual es la **v1.2**: el receptor VS1838B se sustituye por el módulo **Sobotz ST4RT** (J17, con parada por hardware mediante U3), se elimina D2 y el buck pasa a 5,3 V, el fusible pasa a 15 A, J17 y J12 cambian de sitio y GPIO21 se llama DRV_EN. Ver [CHANGELOG](../CHANGELOG.md), [08 · Cálculos v1.2](08-Calculos-v1.2.md) y [12 · Memoria](12-Memoria-rediseno-v1.2.md).

Cada pieza lleva su **elección**, el **porqué** y las **alternativas descartadas**. Los precios son orientativos de AliExpress/LCSC a octubre 2026 y se cerrarán en la lista de compra.

> **Principio de diseño eléctrico:** todo lo que habla con el ESP32 se alimenta a **3,3 V**, así ninguna señal puede superar 3,3 V en un GPIO y **no hace falta ningún adaptador de nivel**. Los 7,4 V de batería solo llegan a los drivers y a los reguladores.

## Resumen

| Bloque | Elección | Cant. | ~€ |
|---|---|---|---|
| Control | **ESP32-S3-DevKitC-1** enchufada en tiras hembra sobre nuestra PCB | 1 | 8–10 |
| Drivers | **TI DRV8874** (uno por motor) en nuestra PCB | 4 (+2 repuesto) | 8 |
| Motores | **N20 6 V ~500 rpm**, reductora metálica, 4WD | 4 | 12 |
| Ruedas | Ruedas N20 de goma ~30 mm → luego silicona moldeada | 4 | 3 |
| Batería | **LiPo 2S 7,4 V 450–650 mAh, XT30** | 1–2 | 7–14 |
| Línea | **QRE1113 analógico** (módulo) | 4 | 4 |
| Rival | **VL53L0X** ToF (módulo GY-VL53L0XV2) | 5 (+1 opc.) | 8–10 |
| Arranque | **VS1838B / TSOP38238** receptor IR 38 kHz | 1 | 0,3 |
| Potencia | Buck 5 V 3 A en la PCB (los 3,3 V salen del LDO de la DevKit) | — | 1,5 |
| PCB | JLCPCB 2 capas, 1,6 mm, ≤100×100 mm | 5 uds | 6–10 |
| Conectores | JST-SH 1,0 SMD (sensores), cable soldado (motores), XT30 vertical, tiras hembra 2,54 mm (DevKit) | — | 3,5 |
| Mecánica | PETG/PLA, chapa de acero para la cuña, tornillería M2/M3, insertos | — | 6 |
| **Total** | | | **~70–84 €** |

## 1. Microcontrolador → ESP32-S3-DevKitC-1 enchufada en la PCB

**Por qué el ESP32-S3 y no el ESP32 "clásico":**
- **USB nativo** (GPIO19/20): se puede programar y depurar sin chip CH340/CP2102 (la DevKit trae además un puerto USB-UART).
- **ADC1 con 10 canales** (GPIO1–10), que siguen funcionando con el Wi-Fi activo. En el ESP32 clásico el ADC2 queda inutilizable con Wi-Fi y el ADC1 solo tiene 6 canales útiles. Necesitamos **9 entradas analógicas**: 4 de línea, 4 de corriente de motor y 1 de batería.
- Más GPIO libres, doble núcleo a 240 MHz: un núcleo para sensores y control, otro para telemetría Wi-Fi.
- **Arduino IDE: sí.** Se instala el core `esp32` de Espressif y se elige la placa "ESP32S3 Dev Module". También funciona con PlatformIO.

**Por qué la DevKitC-1 completa y no el módulo soldado** (cambio del 19/10/2026, detalle en [04 · ESP32-S3-DevKitC-1](04-ESP32-DevKitC-1.md)):
- **Se cambia en segundos:** va pinchada en dos tiras hembra. Si se quema en un combate, se pone otra; no hay que desoldar un módulo castellated.
- **Trae hecho** el USB (nativo + UART), los botones BOOT/RESET, el LED RGB y el LDO de 3,3 V: 13 componentes menos en nuestra PCB.
- **Saca todos los GPIO** que necesitamos (~28). Las placas pequeñas (SuperMini, XIAO) sacan 11–16 y no llegan.
- **Vale cualquier variante** (N8, N8R2, N8R8, N16R8): no usamos GPIO35–37, que son los que ocupa la PSRAM octal de las R8.
- La PCB sigue siendo una **placa base de verdad**: alimentación, drivers, sensores e interconexión son nuestros.
- Coste: mide 25,4 × 62,7 mm y va a 11 mm sobre la PCB, así que el techo sube 5 mm y el robot pesa ~8 g más. Cuesta ~8–10 € frente a ~3,5 € del módulo.

**Descartados:**
- *Arduino Nano*: 5 V (habría que adaptar niveles con los sensores de 3,3 V), solo 2 KB de RAM, sin Wi-Fi.
- *ESP32-C3*: muy pocos pines.
- *RP2040*: buen chip, pero sin Wi-Fi y solo 3 ADC.

## 2. Drivers de motor → DRV8874 (uno por motor)

Era tu mayor preocupación: **que el driver aguante la corriente de bloqueo**. Cuando dos robots se empujan, los motores están prácticamente parados y consumen su **corriente de bloqueo (stall)** durante segundos.

| Driver | V motor | Corriente | Protege la sobrecorriente | Pérdidas | Veredicto |
|---|---|---|---|---|---|
| L298N | 5–46 V | 2 A | No | **~2–4 V de caída** (bipolar), necesita disipador | ❌ Se come un tercio de la batería y se calienta |
| TB6612FNG | 2,5–13,5 V | 1,2 A cont. / 3,2 A pico | No limita (solo apagado térmico) | 0,5 Ω | ⚠️ Justo: un N20 bloqueado a 8,4 V puede pasar de 1,2 A |
| DRV8833 | 2,7–10,8 V | 1,5 A RMS / 2 A pico | Sí | 0,36 Ω | ⚠️ Corto de corriente y de margen de tensión |
| DRV8871 | 6,5–45 V | 3,6 A pico | Sí, con R_ILIM | 0,57 Ω | ✔ Válido, pero sin medida de corriente |
| **DRV8874** | **4,5–37 V** | **~2,1 A cont. / 6 A pico** | **Sí, ajustable (ITRIP)** | **0,2 Ω** | ✅ **Elegido** |

**Por qué el DRV8874:**
1. **Limitación de corriente por hardware (ITRIP).** Con una resistencia y una tensión de referencia fijamos el máximo, por ejemplo 2,5 A. Si el motor se bloquea, el driver recorta él solo **sin quemarse y sin quemar el motor**, aunque el firmware falle. Es justo lo que pedías.
2. **Pin IPROPI:** da una tensión proporcional a la corriente del motor, conectada al ADC. Sirve para **detectar el contacto con el rival** (la corriente sube al empujar) y para hacer **control de tracción** (la corriente cae si la rueda patina).
3. **0,2 Ω** de resistencia interna: casi toda la tensión llega al motor y se calienta poco.
4. Avisa de fallos (nFAULT) y se protege contra subtensión y temperatura.
5. Encapsulado HTSSOP-16 con pad térmico: lo soldamos sobre un plano de cobre con vías térmicas, que hace de disipador.

**¿Por qué cuatro drivers y no dos (uno por lado con los motores en paralelo)?** Con uno por motor, cada driver ve como máximo la corriente de bloqueo de **un** motor (~1,5–2,2 A a 8,4 V, según la variante), dentro del rango continuo. Así nunca trabaja al límite. Además permite controlar cada rueda por separado. Cuesta unos 3 € más.

> Hay que comprar el chip suelto (LCSC/AliExpress) o encargar el montaje a JLC. Los módulos de AliExpress con DRV8874 son raros y caros (el de Pololu, ~10 €).

## 3. Motores → 4× N20 6 V ~500 rpm, tracción 4WD

**Cálculo rápido** (masa 0,5 kg, ruedas de 30 mm, rozamiento goma/MDF μ ≈ 0,8–1,0, estimado):
- Fuerza máxima de empuje antes de patinar: F = μ·m·g ≈ **4–5 N**. Ningún motor puede empujar más que eso: **el límite lo pone el agarre, no el motor**.
- Par por rueda para llegar a ese límite con 4WD: 1,2 N × 0,015 m ≈ 0,018 N·m ≈ **0,18 kg·cm**. Un N20 de ~500 rpm da varias veces eso bloqueado ✔.
- Velocidad: 500 rpm × π × 0,03 m ≈ 0,8 m/s a 6 V, unos **0,95 m/s a 7,4 V**. Cruza el dohyo en menos de 1 s.

**Por qué 4WD (cuatro motores) y no 2WD como en el boceto:**
- Con 2WD parte del peso descansa en la cuña o en un apoyo que no tracciona. Con 4WD **todo el peso cae sobre ruedas motrices**, es decir, más empuje con el mismo peso.
- Si un motor muere, el robot sigue luchando.
- Cabe: dos N20 enfrentados (~25 mm cada uno) más los cubos de rueda suman ~75 mm de los 100 disponibles.

**Por qué motores de 6 V con batería 2S (7,4 V nominal, 8,4 V llena):** es una sobretensión de ~25–40 %, algo habitual en sumo. Da más par y velocidad en los picos. El firmware limita el PWM a ~75 % en marcha continua y deja el 100 % para el ataque. El DRV8874 limita la corriente, así que el bobinado no se fríe.
*Alternativa:* N20 de 12 V a 2S: más lentos y con menos par, pero más vida y menos corriente. Si los de 6 V se calientan en las pruebas, pasamos a estos.

> ⚠️ Como dice el profe: **medir la corriente de bloqueo real** con fuente de laboratorio en cuanto lleguen. Los N20 de AliExpress varían mucho. Con ese dato ajustamos ITRIP.

**Descartados:** Pololu HPCB o JSUMO Titan (mejores, pero 15–25 € cada uno, fuera de presupuesto); servos de rotación continua (lentos y frágiles).

## 4. Batería → LiPo 2S 7,4 V, 450–650 mAh, conector XT30

- **Consumo:** en un combate de 3 min, con una media pesimista de ~3 A, se gastan ~150 mAh. Una de 450 mAh aguanta 2–3 combates. **Conviene llevar dos.**
- **Descarga:** 450 mAh × 30C = 13,5 A, de sobra (los cuatro motores limitados a 2,5 A suman 10 A como peor caso).
- **Tamaño y peso:** ~55 × 30 × 15 mm y ~30 g. Cabe entre los ejes.
- **XT30:** aguanta 15 A+, va polarizado y es barato. Ponemos un XT30 macho **vertical** (XT30UPB-M) directamente en la PCB: la batería se enchufa desde arriba a través del techo. **Enchufar el XT30 es el interruptor de encendido**, como en casi todos los minisumo.

**Descartados:**
- *2× 18650 en portapilas:* los **muelles rebotan con los golpes** y cortan la alimentación unos milisegundos, lo que reinicia el ESP32 en mitad del combate. Además ocupan 65 mm de largo.
- *Pila de 9 V / pilas AA:* resistencia interna altísima; la tensión se hunde al arrancar.
- *3S (11,1 V):* más grande, y los motores de 6 V irían al doble de su tensión. No hace falta.

> 🔌 Hace falta **cargador con balanceo** para 2S (tipo B3AC ~5 € o un iMAX B6 ~20 €). Preguntad si en el laboratorio hay uno antes de comprarlo. Cargar siempre vigilado y no bajar de 3,3 V por celda (lo vigilará el divisor de tensión).

## 5. Sensores de línea → 4× QRE1113 analógico

- **Pequeños** (el módulo mide ~10 × 30 mm). Se colocan muy cerca del suelo, a 1–3 mm, que es su rango óptimo.
- **Analógicos:** se calibra el umbral blanco/negro en el propio dohyo (cambia según la luz y la pintura). El ADC del S3 lee los 4 en microsegundos, de sobra para el borde de 25 ms.
- **Alimentados a 3,3 V** → su salida nunca pasa de 3,3 V → el pin está a salvo.
- **Dónde:** **2 delante** en las esquinas, detrás de la cuña y delante de las ruedas, y **2 detrás**, porque los asaltos de espaldas y los empujones hacia atrás también te sacan.

**Descartados:** *TCRT5000*: más grande y pensado para 2–10 mm; *CNY70*: de agujero pasante y voluminoso; *versiones digitales con comparador*: no se pueden calibrar desde el firmware.

## 6. Sensores de rival → 6× VL53L0X (tiempo de vuelo)

**Por qué ToF:** mide distancia real (hasta ~1,2 m en interiores y ~50–60 cm contra un robot negro, que es lo que importa en un dohyo de 77 cm). No depende del color como un IR de reflexión, cada módulo cuesta ~1,6 € y pesa 1–2 g.

**Disposición (3 frontales + 2 laterales + 1 trasero; posiciones exactas en [03](03-Disposicion-mecanica.md)):**
```
          F-izq  FRENTE  F-der        (±25° aprox.)
   IZQ  ┌───────────────────┐  DER     (90°)
        │                   │
        │                   │
        └───────────────────┘
               (TRASERO opc.)
```
- Los tres frontales dan la **dirección** del rival para girar hacia él. Los laterales cubren la **salida de lado**. Para la salida de espaldas, el robot gira hasta que lo ve un lateral; el trasero opcional lo acelera.
- **I²C compartido + pin XSHUT por sensor:** todos vienen con la dirección 0x29. Al arrancar se apagan todos y se encienden uno a uno para asignarles 0x30, 0x31…
- Ciclo de ~20–33 ms por sensor en modo continuo. Es lento comparado con un sensor digital, pero suficiente para empezar.

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| JSUMO JS40F | Digital, <1 ms, el estándar en sumo | ~12–15 € cada uno | 💸 Fuera de presupuesto ×5 |
| Sharp GP2Y0A21 | Analógico, barato | Grande (45 mm), 5 V, 40 ms, poco preciso | ❌ |
| VL53L1X | 4 m, ROI programable | 4–6 € cada uno, alcance innecesario | Posible mejora |
| VL53L5CX (8×8 zonas) | Un sensor da la dirección | ~12 €, 15 Hz a 8×8 | Idea para v2 |
| HC-SR04 ultrasonidos | Barato | Enorme, lento, rebotes | ❌ |

## 7. Receptor de arranque IR → VS1838B / TSOP38238 (obligatorio)

El reglamento exige **activar y parar el robot con el mando IR del juez (RC5)**. Basta un receptor de 38 kHz alimentado a 3,3 V conectado a un GPIO, y el protocolo RC5 se decodifica en el firmware. Va **arriba y a la vista** para que el juez apunte bien. Cuesta unos 0,10 €.

## 8. Alimentación en la PCB

| Raíl | Componente | Para qué | Por qué |
|---|---|---|---|
| VBAT 6,6–8,4 V | Directo desde la batería tras la protección | DRV8874 (motores) | Sin pérdidas |
| 5 V / 3 A | **Buck síncrono** (tipo TPS563201 o MP1584) | Pin 5V de la DevKit, servos futuros | Un LDO de 8,4 a 3,3 V disiparía >1,5 W → calor |
| 3,3 V | **LDO de la DevKit** (800 mA – 1 A), alimentado desde 5 V por su pin 5V | ESP32-S3 (picos ~350 mA con Wi-Fi), sensores | Salida limpia sin rizado para el ADC; un componente menos en nuestra PCB |

Además:
- **Protección contra inversión de polaridad:** MOSFET P.
- **Sin interruptor de potencia:** se quitó para ganar sitio en la PCB; el robot se enciende al enchufar el XT30.
- **Divisor de tensión** VBAT → ADC (p. ej. 100 k / 33 k: 8,4 V → 2,1 V) para la alarma de batería baja.
- **Condensadores de reserva** junto a los drivers y de 100 nF en bornes de cada motor, para que el arranque de los motores **no reinicie el ESP32**.
- **USB de la DevKit:** se programa con la batería desconectada y, con el USB solo, funcionan también los sensores. Un diodo entre nuestro +5V y el pin 5V de la DevKit evita que USB y buck se peleen.

El esquema detallado y el pinout están en [02-Arquitectura-electrica](02-Arquitectura-electrica.md).

## 9. IMU (opcional) → conector I²C de expansión

En lugar de soldar ya una IMU, dejamos un **conector I²C de 4 pines**. Ahí se puede enchufar un GY-521 (MPU-6050, ~1,5 €) o un LSM6DS3 para detectar que nos levantan o nos empujan de lado. Si funciona, en la v2 se suelda en la placa.

## 10. Mecánica

| Pieza | Material / proceso | Por qué |
|---|---|---|
| Base estructural | **La propia PCB** (FR4, 1,6 mm) | Cuenta como fabricación propia, es rígida y ahorra peso y altura |
| Carrocería, soportes de motor y sensores | **PETG** en FDM (PLA en prototipos) | El PETG aguanta golpes sin partirse; el PLA es quebradizo |
| Cuña | Impresa en FDM + **lámina de acero** de 0,3–0,5 mm atornillada e **intercambiable** | Filo bajo pegado al suelo; se sustituye si se dobla |
| Moldes de ruedas | **Resina** (alta precisión) → silicona o poliuretano colado | Ruedas a medida con el máximo agarre; primero ruedas comerciales |
| Lastre | Placas de acero o plomo en la parte baja, atornilladas | Para llegar a ~495 g: **masa = empuje** |
| Plantillas y prototipos | Corte de madera (láser/CNC) | Pruebas rápidas de tamaño y posición |
| Unión | Insertos roscados de latón M2/M3 en el plástico | **Desmontable** sin pasar de rosca el plástico |

**Peso estimado sin lastre:** motores 40 g + ruedas 30 g + batería 30 g + PCB montada 40 g + impresos 70 g + sensores 15 g + cuña 15 g + tornillería 20 g ≈ **260 g**. Sobran **~230 g para lastre**. Eso es bueno: permite poner el peso donde queremos (bajo y sobre las ruedas).

## 11. Software CAD/EDA (Linux)

- **KiCad 9** para la PCB (ver README para instalarlo).
- **3D:** **Onshape** (en el navegador, licencia educativa gratis, **colaborativo** para los tres) o **FreeCAD**. Yo genero las piezas por código (CadQuery) y las exporto a **STEP/STL**, que se importan en cualquiera de los dos.
