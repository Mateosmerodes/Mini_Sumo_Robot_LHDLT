# 11 · Lista de comprobación: reglamento y requisitos académicos

Estado de cada requisito para el diseño **v1.2** (10/11/2026).

| Símbolo | Significado |
|---|---|
| ✅ **Confirmado (teórico)** | El diseño lo cumple según los ficheros y cálculos; falta comprobarlo en el robot físico |
| 🟡 **Pendiente de confirmar** | Depende de una medida, de una prueba o de una respuesta del profesor/organizador |
| ❌ **No cumple** | Hay que cambiar algo |

Reglamento: OSHWDem Mini Sumo, revisión 7 (2026), [rules.oshwdem.org/loita_sumo_es](https://rules.oshwdem.org/loita_sumo_es) ([texto fuente](https://github.com/brico-labs/Regulamentos/blob/gh-pages/loita_sumo_es.md)).

## 1. Reglamento OSHWDem (Sección 3: robots)

| # | Requisito (artículo) | Estado | Evidencia |
|---|---|---|---|
| R1 | Placa controladora basada en tecnologías abiertas (5.1) | ✅ | ESP32-S3-DevKitC-1: esquemas publicados por Espressif; placa base propia publicada en este repo con licencia CERN-OHL-S v2 |
| R2 | Cabe en 10 × 10 cm en planta, altura libre (5.2) | ✅ teórico | Envolvente del modelo 3D 98,0 × 98,0 × 58,6 mm ([`informe_3d.json`](../hardware/mecanica/cad/informe_3d.json)). 🟡 Medir el robot impreso (contracción del PETG, rueda real) |
| R3 | Puede expandirse tras el inicio sin separarse; piezas sueltas < 5 g (5.2) | ✅ | No hay partes desplegables. Tornillería M2 con insertos |
| R4 | Masa < 500 g al inicio (5.3) | 🟡 | Modelo 3D 405,5 g + 15–20 g de cables = 420–426 g ([08, 6.1](08-Calculos-v1.2.md#61-masa-y-dimensiones)). **Pesar** antes de añadir lastre; objetivo ≤ 495 g |
| R5 | Clase Mini autónoma; activación y desactivación por IR con RC5 y mando del juez (5.4) | 🟡 | Módulo ST4RT del profesor integrado en PCB, firmware y carcasa ([06](06-Modulo-arranque-ST4RT.md)). **Pendiente:** que el mando del juez use el protocolo del módulo (direcciones 0x07/0x0B) y pruebas con el módulo real |
| R6 | Comienza sin retraso (5.5, 8) | ✅ teórico | Firmware: arranca 1–2 ms después del cambio de START, drivers ya despiertos ([07](07-Firmware.md)). 🟡 Medir en vídeo |
| R7 | Nombre o número del robot (5.6) | 🟡 | **Falta decidir el nombre del robot** (la ficha entregada usaba el nombre del equipo). Marcador en la [ficha técnica](Ficha-tecnica.md). Irá en la serigrafía y la carcasa |
| R8 | Elementos afilados permitidos si no dañan y el robot se detiene de forma rápida, fiable y segura (5.7) | ✅ / 🟡 | Cuchilla de fleje de 0,4 mm con el filo **matado** (lijado, sin filo cortante). Parada: el módulo duerme los drivers por hardware (U3) y el firmware frena. 🟡 Medir la distancia de parada |
| R9 | Sin jamming IR (6.1) | ✅ | No hay emisores IR para cegar al rival. Los VL53L0X emiten un láser de 940 nm de clase 1 **para medir distancia**, uso habitual en minisumo; los QRE1113 apuntan al suelo. 🟡 Confirmar con el juez si tienen alguna objeción |
| R10 | Sin partes que dañen el dohyo, ni daño intencionado (6.2) | ✅ | Cuchilla sin filo; ruedas de goma/silicona |
| R11 | Sin fluidos, polvo, gas (6.3) | ✅ | No hay depósitos |
| R12 | Sin pirotecnia (6.4) | ✅ | — |
| R13 | Sin proyectiles (6.5) | ✅ | — |
| R14 | Sin sustancias pegajosas para la tracción (6.6) | ✅ | Neumáticos de goma o silicona **limpios**, sin tratar. La cinta de doble cara solo fija el ST4RT y la batería |
| R15 | Sin efecto suelo: vacío, imanes (6.7) | ✅ | No hay imanes ni ventiladores. (Los motores N20 tienen imanes internos, que no actúan sobre el dohyo de MDF) |
| R16 | Energía solo de pilas o baterías (6.8) | ✅ | LiPo 2S |
| R17 | Se mueve antes de 5 s (14) | ✅ teórico | La estrategia nunca da velocidad 0 en combate (prueba `estrategia_busca_y_se_mueve`) |
| R18 | No girar sobre sí mismo como forma de ataque (Objetivo) | ✅ / 🟡 | El giro en el sitio solo se usa para buscar u orientarse. Si el juez lo interpreta de otra forma, se cambia la búsqueda a arcos |
| R19 | Salidas de frente, de lado y de espaldas (7.3) | ✅ teórico | 3 ToF frontales, 2 laterales y 1 trasero; 2 sensores de línea delante y 2 detrás |

## 2. Plantilla de inspección del profesor (ficha técnica, apartado 5)

| Criterio de la plantilla | Estado | Nota |
|---|---|---|
| 1. Interferencias (jamming) | ✅ | R9 |
| 2. Daño al dohyo / oponente | ✅ | R8, R10 |
| 3. Fluidos, polvo, gas | ✅ | R11 |
| 4. Pirotecnia | ✅ | R12 |
| 5. Lanzamiento de objetos | ✅ | R13 |
| 6. Sustancias pegajosas | ✅ | R14 |
| 7. Efecto suelo | ✅ | R15 |
| 8. Fuente de energía | ✅ | R16 |
| 9. Dimensiones y masa | 🟡 | R2, R4: medir y pesar |
| 10. Arranque IR **e incluye Kill Switch accesible** | 🟡 | Arranque: R5. Kill: la línea K del ST4RT duerme los drivers por hardware y el XT30 (accesible desde arriba) corta toda la alimentación. **Preguntar al profesor si eso vale como "kill switch accesible"** o hace falta un interruptor físico |
| 11. Hardware libre | ✅ | R1 |

## 3. Requisitos académicos (Tecnología Eléctrica, USC)

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| A1 | PCB diseñada y fabricada por el equipo que interconecte unidad de control, sensores y controladores de motores | 🟡 | Diseño v1.2 en [`hardware/pcb`](../hardware/pcb): la DevKit, los 6 ToF, los 4 QRE, el ST4RT y los 4 DRV8874 se conectan a través de ella ([05](05-PCB.md)). **Pendiente:** revisar el rutado (terminado, DRC limpio), fabricar y montar |
| A2 | Nombre del equipo en la serigrafía | ✅ | "HOMBRES DE LAS TABERNAS" en la cara inferior (1,8 mm) y en la superior (1,0 mm); ver `gen_pcb.py` y [05](05-PCB.md) |
| A3 | Se pueden usar módulos y placas de desarrollo | ✅ | DevKitC-1, módulos ToF y QRE, ST4RT |
| A4 | Estructura base de diseño y fabricación propios (tornillería comercial permitida) | ✅ diseño / 🟡 fabricación | Rampa-cuna, cuna trasera, carcasa, techo y llantas diseñados por el equipo ([`hardware/mecanica`](../hardware/mecanica)); la PCB es además el chasis. Falta imprimir |
| A5 | Informe de ≤ 6 páginas: presentación (nombre y logo), componentes del equipo, construcción (electrónica, mecánica, software), costes desglosados, fotos | 🟡 | Borrador en [`informe/Informe-academico.md`](../informe/Informe-academico.md) con marcadores para logo, fotos y costes pagados |
| A6 | Informe entregado y validado antes del campeonato | 🟡 | Depende del equipo y del profesor |

## 4. Preguntas para el profesor / organizador

1. ¿Qué mando usará el juez? ¿Sigue el protocolo del start module (RC5, dirección 0x07 para inicio/parada y 0x0B para programar)? ¿Se programa un id de dohyo antes de cada combate?
2. ¿Basta con la línea KILL del módulo (que duerme los drivers por hardware) y el conector de batería accesible como "kill switch accesible", o se exige un interruptor físico?
3. ¿Se confirma que el ST4RT puede alimentarse a 3,3 V? ¿Qué orden de pines y qué conector trae?
4. ¿Se permite fijar el módulo con cinta de doble cara? ¿Hay alguna posición obligatoria (visible desde arriba)?
5. ¿Hay alguna objeción a los sensores ToF (láser IR de clase 1) respecto a la regla de jamming?
6. Entre asaltos hay que reiniciar la alimentación del módulo tras la parada: ¿está previsto en el procedimiento del juez?
7. ¿El dohyo del campeonato es el OSHWDem estándar (77 cm, MDF negro, borde blanco de 2,5 cm)?
