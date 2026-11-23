# Anexo: cálculos de la ficha técnica (robot v2)

**Equipo:** Hombres De Las Tabernas (LHDT) · **Robot:** mini sumo v2, 2 motores N20 con ESP32-S3

Este anexo justifica cada número de la ficha técnica. Todo es **teórico**: el robot no está montado y no se ha medido nada. Los datos marcados 🔶 no tienen hoja oficial (piezas genéricas) o dependen del montaje, y hay que medirlos. Los números salen del script `hardware/calculos/calculos_v2.py` [15]: si cambia un dato (por ejemplo, la corriente de bloqueo medida), se vuelve a ejecutar y salen los nuevos resultados.

> Los valores de las hojas de datos [1]–[14] no se han podido volver a abrir al preparar este anexo (las webs de los fabricantes están bloqueadas desde el entorno de trabajo). Son los valores habituales de esas hojas; si el profesor pide alguno exacto, hay que confirmarlo en la hoja.

---

## 1. Resumen de corrientes

| Elemento | Nominal | Máxima / pico | Apartado |
|---|---|---|---|
| Motor N20, maniobrando 🔶 | 0,4 A | — | 4 |
| Motor N20, bloqueado 🔶 | 1,60 A a 6 V · 1,97 A a 7,4 V | **2,24 A a 8,4 V** | 4 |
| Motor bloqueado con PWM de ataque (85 %) | — | 1,90 A | 4 |
| Motor al invertir el giro de golpe (unos ms) | — | 3,81 A | 4 |
| TB6612FNG, por canal [1] | 1,2 A continuos | 2,0 A (20 ms) · 3,2 A (10 ms) | 5 |
| TB6612FNG, por motor (2 canales en paralelo) | **2,4 A continuos** | 4,0 A (20 ms) · **6,4 A (10 ms)** | 5 |
| Electrónica (raíl de 3,3 V) | 190 mA | 332 mA | 7 |
| Batería, total | 2,0 A (combate típico) | **4,82 A** (2 motores bloqueados) | 6 y 8 |
| Fusible | 7,5 A nominales | útil 5,6 A (75 %) | 6 |

---

## 2. Datos de partida

| Magnitud | Valor | Ref. |
|---|---|---|
| Batería LiPo 2S: tensión por celda nominal / llena / mínima de uso | 3,7 / 4,2 / 3,3 V | química LiPo |
| Capacidad y tasa de descarga | 450 mAh (alternativa 650 mAh), 30 C | 🔶 vendedor |
| Resistencia interna del pack | ≈ 30 mΩ | 🔶 estimado |
| Motor N20 6 V ~500 rpm: corriente de bloqueo a 6 V | 1,6 A | 🔶 referencia Pololu HP 6 V [10], a medir |
| Motor N20: corriente maniobrando | 0,4 A | 🔶 estimado |
| Ruedas | Ø 30 mm, silicona | 🔶 a medir |
| TB6612FNG: tensión de motor VM / de lógica VCC | 2,5–13,5 V (15 V máx. absoluto) / 2,7–5,5 V | [1] |
| TB6612FNG: corriente de salida por canal | 1,2 A medios · 2 A (pulso de 20 ms) · 3,2 A (pulso de 10 ms) | [1], [2] |
| TB6612FNG: caída alto + bajo con 1 A | 0,5 V típ. · 0,7 V máx. (≈ 0,5–0,7 Ω) | [1] |
| TB6612FNG: potencia que disipa el CI solo, a 25 °C | 0,78 W (→ ≈ 160 °C/W hasta 150 °C) | [1] |
| TB6612FNG: corte térmico / consumo de lógica | 175 °C / 1,1 mA | [1] |
| LM2940CT-5.0: entrada máx. / salida / corriente | 26 V / 5 V ± 3 % / 1 A | [3] |
| LM2940: caída (dropout) con 0,2 A / 1 A | ≈ 0,2 V / 0,5 V típ. | [3] |
| LM2940: consumo propio / T_J máx. / R_θJA TO-220 sin disipador | ≈ 10 mA / 125 °C / 50–60 °C/W 🔶 | [3] |
| 1N5819: caída directa con 0,2–0,35 A | 0,30–0,45 V | [13] |
| ESP32-S3 sin Wi-Fi: típico / pico | 100 / 200 mA | 🔶 [4] |
| VL53L0X midiendo: media / pico | 19 / 40 mA | [6], [7] |
| QRE1113: caída del LED / resistencia del módulo | 1,2 V / 100 Ω | [8], [9] |
| ST4RT | ≈ 5 mA | 🔶 sin hoja, lo da el profesor [18] |
| Fusible de cuchilla mini (ATM) | 7,5 A; se usa como máx. al 75 % | [11] |
| XT30 | 15 A continuos | [12] |
| PWM del firmware: ataque / giro / búsqueda | 85 % / 45 % / 40 % | `sumo_lhdt_v2.ino` |
| Masas del modelo 3D | 187,7 g sin lastre · 232,5 g con lastre de acero | [16] |

---

## 3. Mecánica

**Dimensiones** (modelo 3D del chasis [16]): 98 × 97,2 × 42,5 mm → **9,8 × 9,7 × 4,3 cm**. Cabe en los 10 × 10 cm del reglamento [17] con 1 mm de margen por lado.

**Masa** (estimada, las masas de las piezas compradas son supuestas 🔶):

| Pieza | Masa |
|---|---|
| Chasis impreso (PETG) + 2 abrazaderas | 41,2 g |
| Chapa de acero de la cuña | 4,5 g |
| 2 motores N20 + 2 ruedas | 36 g 🔶 |
| Batería 2S 450 mAh | 30 g 🔶 |
| PCB montada con DevKit y drivers | 55 g 🔶 |
| Sensores, cables y tornillos | 21 g 🔶 |
| **Sin lastre** | **187,7 g** |
| Lastre central de acero | 44,8 g |
| **Con lastre (valor de la ficha)** | **232,5 g ≈ 233 g** |
| Con los huecos de lastre llenos de plomo | 310,7 g |

Queda un margen de 267 g hasta los 500 g. Más masa da más empuje, así que se puede añadir lastre pesando el robot montado.

**Fuerza de empuje.** La limita el agarre de las ruedas (μ ≈ 0,8–1,0 🔶, m = 0,2325 kg):

$$F = \mu\, m\, g = (0{,}8 \ldots 1{,}0) \cdot 0{,}2325 \cdot 9{,}81 = 1{,}82 \ldots 2{,}28\ \text{N}$$

**Par necesario por rueda** (2 ruedas motrices, r = 15 mm):

$$\tau = \frac{F}{2}\, r = \frac{2{,}28}{2} \cdot 0{,}015 = 0{,}017\ \text{N·m} \approx 0{,}17\ \text{kg·cm}$$

Hay que comprobar en la hoja del vendedor que el par de bloqueo del N20 comprado supera este valor.

**Velocidad** (sin carga, proporcional a la tensión; D = 30 mm):

$$\text{rpm}(V) = 500 \cdot \frac{V}{6\ \text{V}} \qquad v = \frac{\text{rpm} \cdot \pi D}{60}$$

| Tensión | rpm | Velocidad | Cruzar el dohyo (77 cm) | Cruzar el borde blanco (25 mm) |
|---|---|---|---|---|
| 6,0 V | 500 | 0,79 m/s | 0,98 s | 32 ms |
| 7,4 V | 617 | 0,97 m/s | 0,79 s | 26 ms |
| 8,4 V | 700 | 1,10 m/s | 0,70 s | 23 ms |

---

## 4. Motores

**Corriente de bloqueo.** Con el motor parado no hay fuerza contraelectromotriz y solo limita la resistencia del bobinado:

$$R = \frac{6\ \text{V}}{1{,}6\ \text{A}} = 3{,}75\ \Omega \qquad I_{bloqueo} = \frac{V}{R}$$

| Tensión | Corriente de bloqueo | Potencia en el bobinado |
|---|---|---|
| 6,0 V | 1,60 A | 9,6 W |
| 7,4 V (nominal) | 1,97 A | 14,6 W |
| **8,4 V (batería llena)** | **2,24 A** | **18,8 W** |
| PWM de ataque 85 % de 8,4 V (7,14 V) | 1,90 A | 13,6 W |

- **Sobretensión**: el motor es de 6 V y la batería llena da 8,4 V (× 1,4). Con el PWM de ataque al 85 % le llegan como mucho 7,1 V.
- Un N20 bloqueado a 8,4 V disipa ≈ 19 W en el bobinado: solo se puede mantener unos segundos.
- **Al arrancar** desde parado, la corriente es la de bloqueo (2,24 A) durante unas decenas de ms: está dentro de los 2,4 A continuos del driver.

**Inversión de giro de golpe** (por ejemplo, de ataque a marcha atrás). Durante unos ms la fuerza contraelectromotriz (≈ la tensión aplicada, girando en vacío) se suma a la de la batería:

$$I_{inv} \approx \frac{V_{PWM} + E}{R} = \frac{7{,}14 + 7{,}14}{3{,}75} = 3{,}81\ \text{A por motor} \;\Rightarrow\; 1{,}91\ \text{A por canal}$$

Está por debajo de los 2 A (20 ms) y 3,2 A (10 ms) de pico de cada canal [1]. Es un caso pesimista: empujando, el motor va lento y la fuerza contraelectromotriz es mucho menor.

---

## 5. Drivers TB6612FNG

Cada TB6612FNG tiene dos canales (A y B). En la placa se unen **los dos canales para un solo motor** (AIN1 con BIN1, AO1 con BO1, etc.), así que cada motor tiene el doble de corriente:

| | Por canal [1] | Por motor (2 canales) |
|---|---|---|
| Continua | 1,2 A | **2,4 A** |
| Pico de 20 ms | 2,0 A | 4,0 A |
| Pico de 10 ms | 3,2 A | **6,4 A** |

**Reparto entre los canales.** Los dos canales son del mismo chip y se reparten la corriente casi a medias; se supone que uno puede llevar hasta el 55 % 🔶:

| Caso | Corriente del motor | Por canal (50 %) | Canal que más lleva (55 %) | ¿Dentro de 1,2 A? |
|---|---|---|---|---|
| Maniobrando | 0,40 A | 0,20 A | 0,22 A | ✔ |
| Bloqueado, PWM 85 % | 1,90 A | 0,95 A | 1,05 A | ✔ |
| Bloqueado, PWM 100 % | 2,24 A | 1,12 A | 1,23 A | ✘ por poco (solo unos segundos) |

**Calor en el driver.** Cada canal tiene una resistencia alto + bajo de 0,5 Ω típ. (0,7 Ω máx.) [1]; con PWM la corriente pasa por el transistor alto o por el bajo, así que siempre hay dos en serie:

$$P = 2\, I_{canal}^2\, R_{on} \qquad R_{\theta} \approx \frac{150 - 25}{0{,}78} \approx 160\ ^\circ\text{C/W}$$

| Caso | P (típ. / máx.) | Temperatura a la que llegaría si siguiera así (típ. / máx.) |
|---|---|---|
| Maniobrando | 0,04 / 0,06 W | 31 / 34 °C ✔ |
| Bloqueado, PWM 85 % | 0,91 / 1,27 W | 170 / 228 °C ✘ |
| Bloqueado, PWM 100 % | 1,25 / 1,76 W | 226 / 306 °C ✘ |

La temperatura de la tabla es la de régimen permanente. Un chip tan pequeño tarda unos segundos en calentarse, así que un empuje corto no es problema; pero **si el robot empuja bloqueado más de unos segundos, el TB6612FNG se apaga solo** al llegar a 175 °C (corte térmico [1]) y vuelve a funcionar al enfriarse. No se rompe, pero el robot se queda parado un momento.

Para que el chip no pase de 125 °C empujando sin parar, la corriente del motor debe quedarse en:

$$I_{motor} \le 2\sqrt{\frac{(125-25)/160}{2 \cdot 0{,}5}} = 1{,}58\ \text{A} \;\Rightarrow\; \text{PWM} \le \frac{1{,}58}{2{,}24} = 71\ \%$$

**Recomendación para el firmware**: atacar al 85 % y, si el empuje dura más de 2 s, bajar a un 70 %. Esto solo hace falta si la corriente de bloqueo medida se acerca a la estimada; muchos N20 de 500 rpm bloquean con menos de 1 A, y entonces el driver va sobrado.

**Pin VM del módulo.** Toda la corriente de un motor entra por un solo pin de la tira de 2,54 mm: 2,24 A como máximo, por debajo de los ≈ 3 A que aguanta un pin de tira normal 🔶.

---

## 6. Potencia máxima, batería y fusible

**Potencia máxima** (los dos motores bloqueados con la batería llena):

| Carga | Cálculo | Potencia |
|---|---|---|
| 2 motores bloqueados | 2 × 8,4 V × 2,24 A | 37,6 W |
| Electrónica en pico | 8,4 V × 0,342 A | 2,9 W |
| **Potencia máxima** | | **40,5 W** |
| Ídem a tensión nominal | 2 × 7,4 V × 1,97 A + 7,4 V × 0,342 A | 31,7 W |

$$I_{bat,pico} = 2 \cdot 2{,}24 + 0{,}342 = 4{,}82\ \text{A} \qquad \text{(con el PWM de ataque al 85 \%: 4{,}15 A)}$$

**Batería:**

| Magnitud | Cálculo | Resultado |
|---|---|---|
| Tensión nominal / máxima / mínima | 2 × 3,7 / 2 × 4,2 / 2 × 3,3 V | **7,4 / 8,4 / 6,6 V** |
| Energía | 7,4 V × 0,45 Ah | 3,33 Wh |
| Corriente que puede dar | 0,45 Ah × 30 C | 13,5 A |
| C necesario | 4,82 A / 0,45 Ah | **10,7 C** → con 30 C sobra |

**Fusible.** Un fusible se usa como máximo al 75 % de su valor para que no salte con el uso normal ni envejezca:

| Elemento | Límite | Frente a 4,82 A |
|---|---|---|
| Fusible de 7,5 A, uso continuo (75 %) | 5,6 A | ✔ +17 % (el pico es el 64 % del valor nominal) |
| Batería 450 mAh 30 C | 13,5 A | ✔ |
| XT30 [12] | 15 A | ✔ |

- **Por qué no uno más pequeño**: con 5 A el pico de 4,82 A estaría al 96 % y saltaría empujando. **Por qué no uno más grande**: el fusible está para proteger la batería y las pistas si hay un cortocircuito; 7,5 A sigue muy por debajo de los 13,5 A de la batería.
- El fusible de 7,5 A deja de tener margen si la corriente de bloqueo de cada motor pasa de **(5,6 − 0,34) / 2 = 2,64 A** a 8,4 V.
- Al invertir el giro de los dos motores a la vez la batería puede dar ≈ 2 × 3,81 + 0,34 = 7,96 A durante unos ms. Un fusible de cuchilla necesita del orden de un segundo con el doble de su corriente para fundir [11], así que no salta por esos picos.

**Caídas de tensión en el pico de 4,82 A** (pack 30 mΩ + fusible ≈ 5 mΩ + XT30 y pistas ≈ 3 mΩ 🔶):

$$\Delta V = 4{,}82 \cdot 0{,}038 = 0{,}18\ \text{V} \;\Rightarrow\; \text{con la batería baja (6{,}6 V) quedan } 6{,}42\ \text{V}$$

**Pistas de la PCB** (IPC-2221 [14], capa exterior, cobre de 1 oz, VBAT y motores a 1,5 mm):

$$I = 0{,}048\, \Delta T^{0{,}44} A^{0{,}725} \qquad A = 59 \cdot 1{,}38 = 81\ \text{mil}^2$$

- Una pista de 1,5 mm aguanta **3,2 A** calentándose 10 °C.
- Pista de un motor bloqueado (2,24 A): se calienta ≈ 4 °C ✔.
- Tramo de VBAT común a los dos motores en el pico (4,82 A): ≈ 25 °C solo mientras los dos están bloqueados ✔ (el FR4 aguanta más de 100 °C).

---

## 7. Electrónica y regulador de 5 V

**Consumo del raíl de 3,3 V** (lo da el regulador de la DevKit a partir de los 5 V):

| Carga | Cálculo | Típica | Pico |
|---|---|---|---|
| ESP32-S3-DevKitC-1, sin Wi-Fi 🔶 | | 100 mA | 200 mA |
| 2 × VL53L0X [6], [7] | 2 × 19 mA (2 × 40 mA) | 38 mA | 80 mA |
| 2 × QRE1113 [8], [9] | 2 × (3,3 − 1,2) V / 100 Ω | 42 mA | 42 mA |
| Lógica de los 2 TB6612FNG [1] | 2 × 1,1 mA | 2 mA | 2 mA |
| ST4RT 🔶 | | 5 mA | 5 mA |
| LED de la DevKit, divisores y pull-downs | | 3 mA | 3 mA |
| **Total** | | **190 mA** | **332 mA** |

Los reguladores son lineales: la corriente que sale por 3,3 V es la que entra por 5 V y la que sale de la batería, más los ≈ 10 mA que consume el LM2940. Desde la batería: **0,20 A típicos (1,5 W) y 0,34 A de pico (2,9 W)**.

**Calor en el LM2940** (TO-220 sin disipador, 50–60 °C/W 🔶, 25 °C de ambiente):

$$P = (V_{bat} - 5\ \text{V})\, I_{5V} + V_{bat}\, I_q$$

| Caso | Potencia | Temperatura de la unión |
|---|---|---|
| Típico, 7,4 V | 0,53 W | 52–57 °C ✔ |
| Típico, 8,4 V | 0,73 W | 62–69 °C ✔ |
| Pico, 8,4 V | 1,21 W | 86–98 °C ✔ (máx. 125 °C) |

No necesita disipador, pero se calienta: no hay que tocarlo con el robot encendido.

**Tensión mínima de batería.** El LM2940 da 5 V mientras tenga ≈ 0,2 V de margen con 0,2 A [3]: regula hasta **5,2 V** de batería. La LiPo no debe bajar de 6,6 V (6,42 V en el pico de los motores, apartado 6), así que la electrónica nunca se queda sin 5 V.

**5 V en la DevKit** (tras el diodo D1, 1N5819):

| Caso | Cálculo | Tensión |
|---|---|---|
| Normal | 5,0 − 0,35 V | ≈ 4,65 V |
| Peor caso (LM2940 al −3 %, diodo con 0,45 V) | 4,85 − 0,45 | 4,40 V |
| Mejor caso | 5,15 − 0,30 | 4,85 V |

El regulador de 3,3 V de la DevKit necesita una caída que depende de su modelo (no confirmado [5]). Con un AMS1117 (1,1 V, el peor habitual) el margen en el peor caso es 4,40 − 3,3 − 1,1 = **0 V**: justo. En el caso normal sobra (+0,25 V). Hay que medir el pin 5V en el primer montaje; si da menos de 4,5 V, se puede cambiar D1 por un puente.

**Medida de batería** (divisor 100 kΩ / 33 kΩ al ADC):

$$V_{ADC} = V_{BAT} \cdot \frac{33}{100+33} \quad\Rightarrow\quad 8{,}4\ \text{V} \to 2{,}08\ \text{V} \qquad 6{,}6\ \text{V} \to 1{,}64\ \text{V}$$

Siempre por debajo de los 3,1 V que lee el ADC [4]. El divisor gasta 8,4 V / 133 kΩ = 63 µA.

---

## 8. Autonomía

Este apartado es el **fundamento del cálculo de autonomía** que pide la ficha.

1. **Capacidad útil:** se usa el 80 % de la batería para no bajar de 3,3 V por celda: 0,8 × 450 mAh = **360 mAh**.
2. **Perfil de combate:** una fracción *f* del tiempo empujando (2 motores casi bloqueados con PWM al 85 %: 2 × 0,85 × 1,97 A = 3,35 A a 7,4 V), el resto maniobrando (2 × 0,4 A = 0,8 A), y la electrónica (0,20 A):

$$I_{media} = f \cdot 3{,}35 + (1-f)\cdot 0{,}80 + 0{,}20$$

3. **Autonomía:**

$$t = \frac{0{,}8\, C}{I_{media}} \cdot 60\ \text{min}$$

Combate típico (f = 40 %): I_media = 0,4 · 3,35 + 0,6 · 0,80 + 0,20 = 2,02 A → t = 0,36 / 2,02 · 60 = **10,7 min**.

| Escenario | f | Corriente media | 450 mAh | 650 mAh |
|---|---|---|---|---|
| Empujando todo el tiempo | 100 % | 3,55 A | 6,1 min | 8,8 min |
| **Combate típico** | **40 %** | **2,02 A** | **10,7 min** | **15,4 min** |
| Solo buscando | 0 % | 1,00 A | 21,6 min | 31,2 min |

**Sensibilidad a la corriente de bloqueo** (el dato más incierto), combate típico con 450 mAh:

| Bloqueo del N20 a 6 V | 0,7 A | 1,0 A | **1,6 A** (supuesto) | 2,0 A |
|---|---|---|---|---|
| Autonomía | 17,0 min | 14,2 min | **10,7 min** | 9,2 min |

Es una estimación conservadora: supone que la corriente del motor sale entera de la batería, cuando con PWM por debajo del 100 % la de la batería es menor. Un combate dura 3 min, así que una batería cargada aguanta varios combates.

---

## 9. Qué hay que medir y qué cambiar si sale distinto

| Qué | Por qué importa | Si sale distinto |
|---|---|---|
| Corriente de bloqueo del N20 a 8,4 V (fuente de laboratorio, rueda sujeta) | Es la base de casi todos los cálculos | Volver a ejecutar `calculos_v2.py`. Si pasa de 2,4 A, bajar `POT_ATAQUE` en el firmware; si pasa de 2,64 A, el fusible de 7,5 A se queda justo |
| Temperatura del TB6612FNG tras 5 s empujando contra una pared | Comprobar el apartado 5 | Si se apaga, bajar el PWM a ≈ 70 % tras 2 s de empuje |
| Tensión en el pin 5V de la DevKit | Margen del regulador de 3,3 V (apartado 7) | Si es < 4,5 V, puentear D1 (sin USB enchufado a la vez) |
| Masa del robot montado | Ficha y lastre | Ajustar el lastre |
| Consumo del ST4RT (cuando llegue en diciembre) | Presupuesto de 3,3 V | Cambiar `st4rt_mA` en el script |

---

## 10. Correspondencia con la ficha técnica

| Campo de la ficha | Valor en la ficha | Apartado |
|---|---|---|
| Dimensiones | 9,8 × 9,7 × 4,3 cm | 3 |
| Masa total con batería | ≈ 233 g | 3 |
| Tensión nominal / máxima | 7,4 V / 8,4 V | 6 |
| Capacidad / tasa de descarga | 450 mAh / 30 C (se necesitan 10,7 C) | 6 |
| Protección eléctrica (fusible 7,5 A, divisor de batería) | | 6 y 7 |
| Tensión de trabajo de los motores | 6,6–8,4 V | 4 |
| Corriente de bloqueo | 2,24 A a 8,4 V | 4 |
| Driver: tensiones y corriente | VM 2,5–13,5 V; 1,2 A / 3,2 A por canal; 2,4 A / 6,4 A por motor | 5 |
| Potencia máxima calculada | 40,5 W | 6 |
| Autonomía y su fundamento | ≈ 11 min (10,7 min) | 8 |
| Consumos de control y sensado | 100 / 5 / 21 / 19 mA; regulador 190 mA | 7 |

---

## Referencias

1. Toshiba, *TB6612FNG Driver IC for Dual DC motor*, hoja de datos. <https://toshiba.semicon-storage.com/info/TB6612FNG_datasheet_en_20141001.pdf>
2. SparkFun, *Motor Driver – Dual TB6612FNG (1A)*, ROB-14450 (1,2 A continuos / 3,2 A de pico por canal). <https://www.sparkfun.com/products/14450>
3. Texas Instruments, *LM2940x 1-A Low Dropout Regulator*, hoja de datos. <https://www.ti.com/lit/ds/symlink/lm2940-n.pdf>
4. Espressif Systems, *ESP32-S3 Series Datasheet*. <https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf>
5. Espressif Systems, *ESP32-S3-DevKitC-1 User Guide*. <https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide.html>
6. STMicroelectronics, *VL53L0X Time-of-Flight ranging sensor*, hoja de datos. <https://www.st.com/resource/en/datasheet/vl53l0x.pdf>
7. Pololu, *VL53L0X Time-of-Flight Distance Sensor Carrier*. <https://www.pololu.com/product/2490>
8. onsemi, *QRE1113 Miniature Reflective Object Sensor*, hoja de datos. <https://www.onsemi.com/pdf/datasheet/qre1113-d.pdf>
9. SparkFun, *Line Sensor Breakout – QRE1113 (Analog)*. <https://www.sparkfun.com/sparkfun-line-sensor-breakout-qre1113-analog.html>
10. Pololu, *Micro Metal Gearmotor HP 6V* (referencia para el N20). <https://www.pololu.com/product/998>
11. Littelfuse, *MINI® 297 Series blade fuse*, hoja de datos (curva tiempo-corriente).
12. Amass, *XT30UPB specification*. <https://atta.szlcsc.com/upload/public/pdf/source/20230412/7B5DFEF57C9EA5273853390C734B3AC5.pdf>
13. Vishay, *1N5817, 1N5818, 1N5819 Schottky Barrier Plastic Rectifier*, hoja de datos. <https://www.vishay.com/docs/88525/1n5817.pdf>
14. IPC-2221, *Generic Standard on Printed Board Design* (ancho de pista frente a corriente).
15. Script de cálculo y resultados: `Robot_Mini-Sumo/hardware/calculos/calculos_v2.py` y `resultados_v2.json`. <https://github.com/Mateosmerodes/Mini_Sumo_Robot_LHDLT>
16. Modelo 3D del chasis v2: dimensiones y masas, `Robot_Mini-Sumo/hardware/chasis/informe_chasis.json`.
17. OSHWDem, *Reglamento Mini Sumo* (10 × 10 cm, 500 g). <https://rules.oshwdem.org/loita_sumo_es>
18. Sobotz, *ST4RT Sumo Start Module*. <https://sobotz.com/en/product/st4rt-sobotz-sumo-start-module/>
