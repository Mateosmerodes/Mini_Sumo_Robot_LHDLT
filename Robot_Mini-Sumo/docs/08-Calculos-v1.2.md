# 08 · Cálculos del diseño v1.2

Cálculos eléctricos, mecánicos y de rendimiento de la **placa base v1.2** y el robot completo. Sustituye, para la v1.2, a los números del [Anexo de cálculos](Anexo-calculos-ficha-tecnica.md) (entregado con la ficha de la v1.1) y del [Informe de consumos](Informe-consumos-y-calculos.md), que se conservan como registro de lo entregado.

**Reproducible:** todos los números salen de [`hardware/calculos/calculos_electricos.py`](../hardware/calculos/calculos_electricos.py) (datos de entrada con su fuente al principio del script) y se guardan en [`resultados.json`](../hardware/calculos/resultados.json). La masa sale del modelo 3D ([`informe_3d.json`](../hardware/mecanica/cad/informe_3d.json)).

```bash
freecadcmd hardware/mecanica/cad/robot.py        # masa y envolvente (opcional, ya versionado)
python3 hardware/calculos/calculos_electricos.py # todos los cálculos
```

**Leyenda de los datos de entrada:** ✅ hoja de datos oficial (comprobada en la revisión del PR #3, ver [revisión](#fuentes)) · 🟡 dato del fabricante sin hoja completa o leído a través de buscador · 🔶 estimado / a medir (componente genérico o depende del montaje).

> Todo esto es **verificación teórica**. Ningún valor está medido en el robot, que aún no existe físicamente.

---

## 1. Resumen y márgenes

| Magnitud | Resultado | Límite / requisito | Margen | Estado |
|---|---|---|---|---|
| Huella en planta | 98,0 × 98,0 mm | ≤ 100 × 100 mm (art. 5.2) | 1 mm por lado | ✅ teórico (modelo 3D) |
| Altura | 58,6 mm | ilimitada | — | ✅ |
| Masa (modelo 3D + cables y tornillos) | 420–426 g | < 500 g (art. 5.3) | 74–80 g para lastre | 🔶 hay que pesar |
| Corriente de pico de batería (techo ITRIP) | 10,2 A | Fusible 15 A × 0,75 = 11,25 A · XT30 15 A · LiPo 450 mAh 30 C = 13,5 A | +11 % · +48 % · +33 % | ✅ con datos 🔶 del motor |
| Pin 5 V de la DevKit, batería baja, peor caso | 4,46 V | ≥ 3,3 + 1,1 V (AMS1117) = 4,4 V | **+0,06 V** | ⚠️ justo: medir |
| Temperatura de unión del DRV8874 con el motor bloqueado | 95–113 °C | < 150 °C (apagado térmico ~165 °C) | 37–55 °C | 🟡 |
| Alimentación del ST4RT | 3,20–3,28 V | 2,8–5,2 V (anunciado) | +0,4 V | 🟡 sin consumo publicado |
| Nivel alto de START en el GPIO | 3,27 V | V_IH ≥ 2,48 V | +0,79 V | ✅ |
| Frenada ante el borde en crucero (0,63 m/s) | 36–49 mm | 50 mm disponibles | 1–14 mm | ⚠️ depende de μ |
| Frenada ante el borde a fondo (0,97–1,10 m/s) | 63–106 mm | 50 mm | **no cumple** | ❌ ver 6.3 |
| Autonomía, combate típico (40 % empujando) | 5,0 min (450 mAh) | 3 min por combate (art. 7.1) | ×1,65 | 🔶 |
| Bus I²C: corriente de sumidero | 2,7 mA | ≤ 3 mA (I²C estándar/rápido) | 10 % | 🔶 pull-ups de los módulos sin confirmar |

---

## 2. Datos de entrada principales

| Dato | Valor | Fuente |
|---|---|---|
| Batería LiPo 2S | 7,4 V nom., 8,4 V llena, 6,6 V mínima de uso; 450 mAh 30 C; R_int ≈ 30 mΩ | 🔶 química LiPo; R_int estimada |
| Motor N20 6 V 500 rpm | I_stall = 1,6 A a 6 V → R = 3,75 Ω | 🔶 **A medir** (referencia: Pololu HP 6 V, 1,6 A) |
| DRV8874 | A_IPROPI = 455 µA/A; R_DS(on) 2 × 120 mΩ máx. a 25 °C (≈ 0,35 Ω en caliente); OCP 6 A | ✅ [TI DRV8874](https://www.ti.com/product/DRV8874) |
| TPS563201 | V_FB = 0,768 V (0,749–0,787); t_OFF(min) 220/310 ns; f = 580 kHz | ✅ [TI SLVSD90B](https://www.ti.com/product/TPS563201) |
| SS34 (D1) | V_F = 0,40–0,55 V | 🟡 genérico |
| ESP32-S3 | V_IH ≥ 0,75·VDD, V_IL ≤ 0,25·VDD; ADC 0–3,1 V (11 dB) | ✅ [Espressif ESP32-S3 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf) |
| ST4RT | 2,8–5,2 V; consumo **no publicado** (se suponen 2–10 mA) | 🟡/🔶 [Sobotz](https://sobotz.com/en/product/st4rt-sobotz-sumo-start-module/) |
| Rozamiento goma/MDF | μ = 0,8–1,0 (caso pesimista 0,6) | 🔶 a medir con un plano inclinado |
| Rueda | Ø 30 mm | 🔶 diseño (`geometria.py`) |
| Dohyo | Ø 77 cm, borde blanco 2,5 cm | ✅ reglamento art. 3 |

---

## 3. Batería y potencia

**Energía:** E = V_nom · C = 7,4 V × 0,45 Ah = **3,33 Wh** (650 mAh: 4,81 Wh).

**Corriente máxima de la batería:** I_max = C · tasa = 0,45 Ah × 30 C = **13,5 A**.

**Corriente de bloqueo de un motor** (resistencia del bobinado constante): I = V / R → 1,97 A a 7,4 V; **2,24 A a 8,4 V**.

**Límite de corriente del driver:** V_REF = 3,3 V × 10 k / (10 k + 10 k) = 1,65 V;
I_TRIP = V_REF / (A_IPROPI · R_IPROPI) = 1,65 / (455·10⁻⁶ × 1500) = **2,44 A** (9 % por encima del bloqueo estimado a 8,4 V).

**Pico de batería** (4 motores en el límite del driver + electrónica):
I_pico = 4 × I_TRIP + P_elec / V = 4 × 2,44 + 3,32 W / 8,4 V = **10,2 A** → potencia máxima **85 W** (con el bloqueo estimado en lugar de I_TRIP: 9,3 A y 79 W).

**Protecciones (v1.2):**

| Elemento | Nominal | Útil | Margen sobre 10,2 A |
|---|---|---|---|
| Fusible F1 (v1.2: 15 A, antes 10 A) | 15 A | 15 × 0,75 = 11,25 A (reducción habitual para fusibles SMD) | +11 % |
| XT30 | 15 A continuos (🟡 dato del fabricante) | 15 A | +48 % |
| Batería 450 mAh 30 C | 13,5 A | — | +33 % |

**Caídas en el pico:** batería 9,3 A × 30 mΩ = 0,28 V; serie (Q1 15 mΩ + fusible ~5 mΩ + XT30 2 × 1,2 mΩ) = 0,21 V → al motor le llegan ≈ 7,9 V con la batería llena. Disipación de Q1 en el pico: 9,3² × 0,015 = 1,3 W (en régimen breve; TO-252).

---

## 4. Motores y drivers

| Magnitud | Fórmula | 7,4 V | 8,4 V |
|---|---|---|---|
| Velocidad en vacío del motor | n = 500 rpm × V / 6 V | 617 rpm | 700 rpm |
| Velocidad lineal (en vacío, cota superior) | v = n · π · D / 60 | 0,97 m/s | 1,10 m/s |
| Potencia disipada en un motor bloqueado | P = V² / R | 14,6 W | 18,8 W |

**Temperatura del DRV8874** con un motor bloqueado (2,24 A), R_DS(on) en caliente 0,35 Ω, R_θJA 40–50 °C/W en placa de 2 capas (🔶):
P = I² · R_DS(on) = 2,24² × 0,35 = **1,76 W** → T_J = 25 + 1,76 × (40…50) = **95–113 °C**. En el límite I_TRIP: 2,09 W → 109–130 °C. Por debajo del apagado térmico, pero **el motor** (no el driver) es el que sufre: el firmware debe bajar el PWM si el empuje dura más de 2–3 s (pendiente de implementar con datos medidos).

**Lectura de corriente (IPROPI):** 0,6825 V/A; con el ADC de 12 bits (3,1 V / 4096 = 0,76 mV) → **1,1 mA de resolución**. Filtro RC 1,5 kΩ / 10 nF: f_c = 10,6 kHz, atenúa el PWM de 20 kHz solo 6,6 dB → se promedia en el firmware.

---

## 5. Electrónica y cadena de alimentación

### 5.1 Consumo del raíl de 3,3 V

| Carga | Típico | Pico | Fuente |
|---|---|---|---|
| ESP32-S3 (DevKitC-1), Wi-Fi apagado en combate | 100 mA | 350 mA (pico de TX si se activa la radio) | ✅ Espressif |
| 6 × VL53L0X | 114 mA | 114 mA | 🟡 19 mA c/u (lado seguro; Pololu da 10 mA medios) |
| 4 × QRE1113 | 84 mA | 84 mA | ✅ (3,3 − 1,2) / 100 Ω = 21 mA c/u |
| Módulo ST4RT | 2 mA | 10 mA | 🔶 no publicado (supuesto) |
| LED, pull-ups, divisores | 4–6 mA | — | cálculo |
| **Total** | **0,30 A** | **0,56 A** | |

### 5.2 Buck y pin 5 V de la DevKit (cambio v1.2)

v1.1: buck a 5,53 V → D2 → +5V → D1 → pin 5V. La [revisión del PR #3](#fuentes) mostró que, con la batería baja, el buck satura por su t_OFF mínimo y el pin 5V quedaba en ~4,2 V.
**v1.2: se quita D2 y se baja la consigna** a V_out = 0,768 × (1 + 59 k / 10 k) = **5,30 V** (5,17–5,43 V por la tolerancia de V_FB).

| Caso | Fórmula | Resultado |
|---|---|---|
| Ciclo de trabajo máximo del buck | D_max = 1 − t_OFF(min) · f | 87 % típ., **82 %** peor |
| Batería baja en pleno empuje | 6,6 V − caídas (0,28 + 0,21 V) | 6,11 V |
| Salida alcanzable | min(V_out, D_max · V_in) | 5,01 V (peor) |
| Pin 5V de la DevKit | V_buck − V_F(D1) | 4,75–4,90 V normal; **4,46 V** peor caso |
| Margen para un LDO AMS1117 (clones) | 4,46 − 3,3 − 1,1 | **+0,06 V** |

Con la DevKitC-1 **original** de Espressif el LDO es otro (no confirmado cuál: hay que leerlo en el esquema v1.1 o en la placa). **Recomendación:** comprar la DevKit original y medir el pin 5V con la batería a 6,6 V y los motores bloqueados. Si no llega, subir el corte de batería baja del firmware a 3,5 V/celda o cambiar D1 por un Schottky de menor caída.

### 5.3 Módulo de arranque ST4RT {#st4rt}

| Magnitud | Fórmula | Resultado |
|---|---|---|
| Tensión en el módulo | 3,3 V − I · 10 Ω (I = 2–10 mA) | 3,28–3,20 V (> 2,8 V: margen 0,40 V) |
| Nivel alto de START en GPIO18 | 3,3 × 100 k / (100 k + 1 k) | 3,27 V (V_IH = 0,75 × 3,3 = 2,48 V → margen 0,79 V) |
| Corriente de la pull-down | 3,3 V / 100 k | 33 µA |
| Si por error se alimentara el módulo a 5 V | (5 − 3,3 − 0,3) / 1 k | 1,4 mA por el diodo de protección del GPIO (limitado por R63) — **no hacerlo** |
| Retardo de la parada por hardware | t_pd del 74LVC1G08 | ns (despreciable frente a la trama RC5 de ~25 ms) |

### 5.4 Medida de batería

Divisor 100 k / 33 k: 6,6 V → 1,64 V; 8,4 V → 2,08 V (dentro de 0–3,1 V). Resolución 3,05 mV de batería por LSB. Consumo 63 µA. τ = 2,5 ms.

### 5.5 Bus I²C (cambio v1.2)

Pull-ups de la placa 4,7 kΩ (v1.1: 2,2 kΩ) en paralelo con las de los 6 módulos (10 kΩ c/u si las llevan, 🔶): R_eq = 1 / (1/4,7 k + 6/10 k) = **1,23 kΩ** → I = 3,3 / 1,23 k = **2,7 mA** (≤ 3 mA ✔). Tiempo de subida con 150 pF estimados: t_r = 0,8473 · R · C = **156 ns** (≤ 300 ns en modo rápido ✔). Con 2,2 kΩ (v1.1) eran 3,5 mA.

---

## 6. Mecánica y rendimiento

### 6.1 Masa y dimensiones

Modelo 3D (FreeCAD, densidades efectivas de cada material, masas fijas de motores, batería, sensores y módulo): **405,5 g**. Más 15–20 g de cables, tornillos y cinta no modelados (🔶) → **420–426 g**. Lastre añadible: 74–80 g para llegar a ~495 g (plomo en el canal central, ver [03](03-Disposicion-mecanica.md)). **Pesar en el primer montaje antes de añadir lastre.**

Envolvente: 98,0 × 98,0 × 58,6 mm (la torre del ST4RT sube la altura de 55,1 a 58,6 mm; la altura es libre).

### 6.2 Tracción y empuje

F_max = μ · m · g = (0,8…1,0) × 0,495 kg × 9,81 = **3,9–4,9 N**. Por rueda (4WD, peso repartido): 0,97–1,21 N → par necesario en el eje T = F · r = **0,015–0,018 N·m (0,15–0,19 kg·cm)**. El par de bloqueo del N20 elegido no está publicado por el vendedor (🔶): **hay que medirlo**. Si es menor que ~0,4 kg·cm (2× margen) las ruedas no llegarán a patinar y el empuje lo limitará el motor.

Rampa: ángulo = atan(20 mm / 29 mm) = **34,6°** (fijado por la altura de la PCB). Es más empinada que lo habitual (15–25°); se conserva porque bajarla obligaría a bajar la PCB o alargar la rampa, y no hay fondo. Se valorará en pista.

### 6.3 Frenada ante el borde (nuevo en v1.2)

Los sensores de línea delanteros están a y = 22 mm del filo y el eje delantero a y = 47 mm. Desde que el sensor ve el blanco hasta que la rueda delantera sale del dohyo hay **d = 25 mm (franja blanca) + 25 mm = 50 mm**.

Distancia de parada: s = v · t_lat + v² / (2 · μ · g), con t_lat = 3 ms (bucle a 1 kHz + filtro, 🔶) y deceleración limitada por el agarre de las 4 ruedas.

| Modo (firmware) | v | s con μ = 0,8 | s con μ = 0,6 | ¿Cabe en 50 mm? |
|---|---|---|---|---|
| Búsqueda (45 %, compensado a 7,4 V) | 0,44 m/s | 13 mm | 17 mm | ✅ |
| Crucero (65 %, compensado a 7,4 V) | 0,63 m/s | 27 mm | 36 mm | ✅ |
| Crucero sin compensar (75 %, v1.1) a 8,4 V | 0,82 m/s | 46 mm | 60 mm | ❌ con μ = 0,6 |
| Ataque a fondo a 7,4 V / 8,4 V | 0,97 / 1,10 m/s | 63 / 80 mm | 83 / 106 mm | ❌ |

Velocidad máxima segura: v = √(2 · μ · g · d) = **0,89 m/s** (μ = 0,8) / 0,77 m/s (μ = 0,6).

**Decisiones:** el firmware baja el crucero del 75 % al 65 % y **compensa la tensión de batería** (escala el PWM a 7,4 V equivalentes). El ataque a fondo solo se usa con el rival a < 15 cm o con contacto: en ese caso es el rival el que frena al robot. Si el rival esquiva en el último momento, el robot puede salirse: es un riesgo aceptado de la estrategia y se medirá en pista.

### 6.4 Tiempos

- Cruzar el dohyo (77 cm) a 0,97 m/s: **0,79 s**.
- Cruzar la franja blanca (25 mm) a 1,10 m/s: **23 ms** → los sensores de línea se leen en cada vuelta del bucle (≥ 1 kHz).
- ToF: 20 ms por medida en modo continuo (los 6 miden a la vez). A 0,63 m/s el robot avanza 13 mm entre medidas.
- Arranque: 2 muestras de START ≈ 1–2 ms tras el cambio del módulo; los drivers ya están despiertos (t_wake ≈ 1 ms no aplica).

---

## 7. Autonomía

I_media = f · 4 · I_bloqueo(7,4 V) + (1 − f) · 4 · 0,4 A + I_elec, con f = fracción del tiempo empujando (🔶 40 % en un combate típico) y 80 % de capacidad útil.

| Escenario | I media | 450 mAh | 650 mAh |
|---|---|---|---|
| Empujando todo el tiempo | 8,1 A | 2,7 min | 3,8 min |
| Combate típico (40 %) | 4,4 A | **5,0 min** | 7,2 min |
| Solo buscando | 1,8 A | 11,7 min | 16,9 min |

Un combate dura 3 min (art. 7.1): con 450 mAh caben ~1,5 combates típicos. **Llevar 2 baterías** y cargar entre rondas. El cálculo es conservador (con PWM < 100 % la corriente de batería es menor que la del motor) y depende mucho de la corriente de bloqueo real: con 1,0 A a 6 V la autonomía típica sube a 6,8 min; con 2,0 A baja a 4,2 min.

---

## 8. Qué hay que medir para cerrar los cálculos

| Medida | Cómo | Cambia |
|---|---|---|
| Corriente de bloqueo de un N20 a 6 V | Fuente de laboratorio, rueda bloqueada, 1–2 s | I_TRIP (R_IPROPI), fusible, autonomía, temperatura |
| Par de bloqueo del N20 | Brazo de palanca + báscula | Empuje real |
| μ rueda/dohyo | Plano inclinado de MDF: μ = tan(ángulo de deslizamiento) | Empuje, frenada (6.3) |
| Pin 5V de la DevKit con batería a 6,6 V y motores bloqueados | Polímetro / osciloscopio | Margen del LDO (5.2) |
| Consumo y niveles del ST4RT | Polímetro en serie; S y K en cada estado | 5.3, [06](06-Modulo-arranque-ST4RT.md) |
| Masa real | Báscula de cocina (±1 g) | Lastre |
| Distancia de frenada real ante el borde | Vídeo sobre el dohyo a cada velocidad | `config.h` |

## Fuentes

- Reglamento OSHWDem Mini Sumo rev. 7: [rules.oshwdem.org/loita_sumo_es](https://rules.oshwdem.org/loita_sumo_es) ([fuente en GitHub](https://github.com/brico-labs/Regulamentos/blob/gh-pages/loita_sumo_es.md)).
- TI DRV8874: [producto y hoja de datos](https://www.ti.com/product/DRV8874). TI TPS563201: [producto y hoja de datos](https://www.ti.com/product/TPS563201).
- Espressif: [ESP32-S3 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf), [guía de la DevKitC-1](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide.html).
- onsemi QRE1113: [hoja de datos](https://www.onsemi.com/pdf/datasheet/qre1113-d.pdf). ST VL53L0X: [producto](https://www.st.com/en/imaging-and-photonics-solutions/vl53l0x.html).
- Sobotz ST4RT: [página del producto](https://sobotz.com/en/product/st4rt-sobotz-sumo-start-module/). Módulo de referencia: [p1r.se/startmodule](https://p1r.se/startmodule/), [código fuente](https://github.com/p1rse/robot-sumo-start-module).
- Revisión de los cálculos de la v1.1 (PR #3): archivo del proyecto `revision-informe-consumos/revision-PR3.md` (comprobaciones de las hojas de TI, onsemi y Espressif hechas a través del buscador).
- Pololu (referencia de motores N20 6 V HP): [pololu.com/product/998](https://www.pololu.com/product/998).

> Nota: las webs de los fabricantes (TI, ST, onsemi, Espressif, Sobotz) no se pudieron abrir directamente desde el entorno de trabajo; los valores ✅ son los que la revisión del PR #3 comprobó a través del buscador. Conviene repasarlos en los PDF enlazados.
