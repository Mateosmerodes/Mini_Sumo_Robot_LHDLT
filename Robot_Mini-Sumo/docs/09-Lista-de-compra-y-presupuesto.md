# 09 · Lista de compra y presupuesto

Qué hay que comprar para construir el robot v1.2, dónde, cuánto cuesta aproximadamente y por qué. **El módulo de arranque Sobotz ST4RT no se compra: lo entrega el profesor.**

> **Sobre los precios.** Las tiendas no se pudieron abrir directamente desde el entorno de trabajo. Hay dos tipos de precio:
> - **🔎 Visto (10/11/2026):** precio que aparecía en la ficha de la tienda según un buscador, con enlace. Hay que confirmarlo en la tienda antes de pagar (cambia con el stock, el IVA y el envío).
> - **≈ Estimado:** orden de magnitud habitual en AliExpress/LCSC, **sin comprobar**.
>
> Los **precios pagados** de verdad se apuntan en la columna "Pagado" cuando se compre: son los que van al informe ([Informe académico, apartado 5](../informe/Informe-academico.md)).

## 1. Componentes que hay que comprar

| # | Componente (modelo / referencia) | Cant. | Precio unitario | Dónde | Por qué | Pagado |
|---|---|---|---|---|---|---|
| 1 | **Espressif ESP32-S3-DevKitC-1** (N8 o N8R8, original) | 1 (+1 de repuesto opcional) | 🔎 22,50 € (N8R8, [Botland](https://botland.store/esp32-modules/26547-esp32-s3-devkitc-1-n8r8-wifi-bluetooth-development-board-with-esp32-s3-wroom-1-chip.html)); ≈ 8–12 € un clon "compatible DevKitC-1" en AliExpress | Botland, TinyTronics, Digi-Key; clones en AliExpress | Unidad de control (decisión de la v1.1). Se recomienda la **original**: su LDO y el ancho entre filas (22,86 mm) están documentados; con un clon hay que comprobar ambos (ver [08, 5.2](08-Calculos-v1.2.md#52-buck-y-pin-5-v-de-la-devkit-cambio-v12)) | ☐ |
| 2 | **TI DRV8874PWPR** (HTSSOP-16) | 4 (+2) | 🔎 0,89–1,03 $ ([LCSC C1855818](https://lcsc.com/product-detail/C1855818.html)) | LCSC | Driver con límite de corriente por hardware y medida de corriente, uno por motor | ☐ |
| 3 | Resto de componentes de la placa (TPS563201, AOD4185, 74LVC1G08, fusible 15 A, bobina, pasivos, XT30 vertical, conectores JST-SH) — lista completa en [`hardware/pcb/bom.csv`](../hardware/pcb/bom.csv) | 1 juego | ≈ 8–12 € el juego (los pasivos se venden por tiras de 10–50) | LCSC (o montaje SMT en JLCPCB) | Placa base propia | ☐ |
| 4 | **PCB** placa base v1.2 (2 capas, FR4 1,6 mm, 74 × 62 mm) | 5 (mínimo del fabricante) | 🔎 desde 2 $ los 5 ([JLCPCB](https://jlcpcb.com/help/article/How-do-I-place-an-order)) + envío a España ≈ 15–20 $ y posible aduana | JLCPCB | Requisito académico: PCB propia con el nombre del equipo | ☐ |
| 5 | **Motor N20 6 V ~500 rpm** con reductora metálica, eje D de 3 mm | 4 (+1–2) | 🔎 5,98 $ ([RobotShop, 30:1 6 V 500 rpm](https://www.robotshop.com/products/e-s-motor-301-micro-metal-gearmotor-6v-w-extended-motor-shaft-500-rpm)); ≈ 2–4 € en AliExpress | AliExpress / RobotShop | Tracción 4WD. **Medir la corriente y el par de bloqueo** al recibirlos ([08, apartado 8](08-Calculos-v1.2.md#8-qué-hay-que-medir-para-cerrar-los-cálculos)) | ☐ |
| 6 | Ruedas de goma para N20, Ø 30 mm aprox., eje D 3 mm | 4 | ≈ 1 € c/u | AliExpress | Primeras ruedas (luego, neumáticos de silicona propios) | ☐ |
| 7 | **LiPo 2S 7,4 V 450 mAh ≥ 30 C con XT30** | 2 | 🔎 5,99–9,99 $ (Gaoneng GNB 450 mAh 2S 80C XT30, [WREKD](https://www.racedayquads.com/products/gaoneng-7-4v-2s-450mah-80c-lipo-whoop-micro-battery-w-xt30)); 🔎 7,90 € la SLS XTRON 450 mAh 2S 30C, [Stefansliposhop](https://www.stefansliposhop.de/en/batteries/sls-xtron/sls-xtron-30c/sls-xtron-450mah-2s1p-7-4v-30c-60c::992.html) (comprobar conector) | Tiendas de RC / FPV | Fuente de energía. Dos para cambiar entre combates (≈ 5 min por batería, [08, 7](08-Calculos-v1.2.md#7-autonomía)). **Comprobar las medidas (≤ 55 × 31 × 14 mm)** | ☐ |
| 8 | Cargador LiPo con balanceo 2S | 1 (si el laboratorio no tiene) | ≈ 5 € (tipo B3AC) – 20 € (tipo iMAX B6) | AliExpress / tienda RC | Carga segura | ☐ |
| 9 | **Módulo VL53L0X** (GY-VL53L0XV2 o similar) | 6 (+1) | 🔎 7,95 € + envío en un marketplace europeo ([Fruugo](https://www.fruugo.pt/gy-vl53l0xv2-tempo-de-voo-tof-sensor-de-medicao-de-distancia-a-laser-i2c-iic-modulo-de-alcance-sistema-de-alcance-zegoods/p-385857352-829308227)); ≈ 1,5–2,5 € en AliExpress | AliExpress | Detección del rival. **Mirar si el módulo trae pull-ups I²C** (afecta a R60/R61, [08, 5.5](08-Calculos-v1.2.md#55-bus-i²c-cambio-v12)) | ☐ |
| 10 | **Módulo QRE1113 analógico** | 4 (+1) | 🔎 4,08 $ ([SparkFun ROB-09453](https://www.sparkfun.com/sparkfun-line-sensor-breakout-qre1113-analog.html)), 3,50 $ ([RobotShop](https://ca.robotshop.com/products/qre1113-line-sensor-breakout-board)); ≈ 1 € clones | AliExpress / SparkFun | Detección del borde blanco | ☐ |
| 11 | Cables JST-SH 1,0 mm ya crimpados (3, 4 y 5 polos, 10–15 cm) | ~15 | ≈ 0,3 € c/u | AliExpress | Conexión de sensores y del ST4RT a la placa | ☐ |
| 12 | Tira hembra 2,54 mm 1 × 40, 8,5 mm de alto | 2 | ≈ 0,5 € | AliExpress / LCSC | Zócalo de la DevKit | ☐ |
| 13 | Tornillos M2 × 25 (4), M2 × 6 (4), M2 × 5 avellanados (2), insertos de latón M2 Ø 3,2 × 4 (10) | 1 juego | ≈ 4 € | AliExpress / ferretería | Unión de las piezas | ☐ |
| 14 | Fleje de acero 0,4 mm (cuchilla) | 1 trozo 100 × 20 mm | ≈ 1–2 € | Ferretería | Filo de la cuña | ☐ |
| 15 | Lastre: pletina de acero o plomo (~75 g) | — | ≈ 2 € | Ferretería | Llegar a ~495 g con el peso abajo | ☐ |
| 16 | Filamento PETG (~80 g) | — | ≈ 2 € de filamento | Laboratorio | Piezas impresas | ☐ |

## 2. Lo que NO hay que comprar

| Elemento | Motivo |
|---|---|
| Módulo de arranque **Sobotz ST4RT** | Lo entrega el profesor (principios de diciembre de 2026) |
| Receptor VS1838B / TSOP38238 | Sustituido por el ST4RT en la v1.2 |
| Mando RC5 del juez | Lo aporta la organización |
| Interruptor general | No se usa: el XT30 es el corte de alimentación ([06, riesgo 6](06-Modulo-arranque-ST4RT.md#2-incompatibilidades-y-datos-que-faltan)) |

## 3. Presupuesto orientativo

| Bloque | Estimación | Base |
|---|---|---|
| Control (DevKitC-1 original) | 22,5 € | 🔎 |
| Placa: PCB + componentes + envío | 25–35 € | 🔎 PCB + ≈ componentes + ≈ envío |
| Motores + ruedas | 12–28 € | ≈ AliExpress … 🔎 RobotShop |
| Baterías (2) | 12–16 € | 🔎 |
| Sensores (6 ToF + 4 línea) | 13–25 € | ≈ AliExpress |
| Mecánica (tornillería, insertos, acero, lastre, PETG) | ≈ 10 € | ≈ |
| **Total sin cargador** | **≈ 95–135 €** | |

> El presupuesto del equipo era de 50–80 € ([00](00-Requisitos-y-reglamento.md)). Con los precios vistos se pasa, sobre todo por la DevKit original (22,5 €) y el envío de la PCB. **Opciones para bajar** (ordenadas por ahorro/riesgo):
> 1. Clon "compatible DevKitC-1" de AliExpress (≈ 10 €): −12 €, pero hay que comprobar la separación de filas y el LDO.
> 2. Juntar el pedido de PCB con el de otros equipos (el envío se comparte).
> 3. Montar 5 ToF en lugar de 6 (sin el trasero): −2 €; la salida de espaldas se resuelve girando.
> 4. Una sola batería: −6 €, a costa de esperar a cargar entre combates.

## 4. Alternativas consideradas (decisiones que afectan al coste)

| Decisión | Elegido | Alternativa | Por qué |
|---|---|---|---|
| Sensores de rival | 6 × VL53L0X (≈ 2 € c/u) | JSUMO JS40F (≈ 12–15 € c/u) | ×6 de coste; los ToF bastan a 20 ms por medida |
| Drivers | 4 × DRV8874 en la placa (≈ 1 $ c/u) | 2 × TB6612FNG en módulo | El TB6612 no limita la corriente y se queda corto con el bloqueo a 8,4 V |
| Arranque | ST4RT del profesor | Receptor VS1838B + RC5 propio | Lo impone el profesor; además ahorra el receptor |
| Motores | N20 genéricos | Pololu HPCB (15–25 € c/u) | Fuera de presupuesto; se miden los genéricos |
