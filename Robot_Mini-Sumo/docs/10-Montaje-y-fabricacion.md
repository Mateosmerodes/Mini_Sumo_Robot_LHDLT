# 10 · Fabricación, montaje, conexión y puesta en marcha (v1.2)

Instrucciones para pasar del repositorio al robot. **Ningún paso se ha hecho todavía**: los tiempos, holguras y ajustes son los del modelo y habrá que corregirlos con la primera impresión y el primer montaje. Las casillas ☐ sirven de lista de control.

*English: step-by-step fabrication, assembly, wiring and bring-up. Key safety steps are also given in English.*

## 0. Seguridad / Safety

- Cargar la LiPo **solo con cargador con balanceo**, sobre superficie no inflamable, sin dejarla sola. *Charge LiPo only with a balance charger, never unattended.*
- Programar y depurar **con la batería desenchufada** (solo USB). *Flash with the battery unplugged.*
- Primeras pruebas de motores **con el robot en un soporte y las ruedas en el aire**. *First motor tests with wheels off the ground.*
- No bajar de 3,3 V por celda; guardar las baterías a 3,8 V por celda.

## 1. Fabricar la PCB

> ⚠️ **No pedir la PCB todavía.** El rutado de la v1.2 está **incompleto** (ver [05](05-PCB.md)). Primero hay que terminarlo en KiCad y que el DRC salga sin errores.

1. ☐ Abrir `hardware/pcb/robot_sumo.kicad_pro` con **KiCad 9 o 10**. Terminar el rutado y revisar las pistas de potencia (VBAT, motores) y los retornos de GND bajo los drivers.
2. ☐ `hardware/pcb/scripts/check.sh` → ERC 0 y DRC 0 (sin pistas sin conectar).
3. ☐ Generar los ficheros de fabricación: `hardware/pcb/scripts/fabricacion.sh` (Gerber, taladros, posiciones y BOM en `hardware/pcb/fabricacion/`).
4. ☐ JLCPCB: subir el ZIP de Gerber. 2 capas, FR4, **1,6 mm**, cobre 1 oz (o 2 oz si se puede, por la corriente de los motores), acabado HASL sin plomo o ENIG, serigrafía blanca. Comprobar en el visor que se lee **"HOMBRES DE LAS TABERNAS"**.
5. ☐ Montaje: a mano (soldador de punta fina + aire caliente para los DRV8874, que tienen pad térmico) o SMT de JLCPCB con `bom.csv` y el fichero de posiciones (comprobar referencias LCSC y rotaciones en su visor).

### 1.1 Soldadura (si se monta a mano)

Orden recomendado: de lo más bajo a lo más alto, y la potencia primero para poder probarla sola.

1. ☐ Bloque de potencia: Q1 (AOD4185), F1 (fusible 15 A), condensadores de entrada, J1 (XT30).
2. ☐ Buck: U2 (TPS563201), L1, R5–R8, C4–C9. **Probar** (paso 3.1) antes de seguir.
3. ☐ Drivers U4–U7 (DRV8874, HTSSOP con pad térmico: estaño en el pad y aire caliente) y sus pasivos.
4. ☐ U3 (74LVC1G08) y C15; bloque ST4RT (R62–R67, C62). **R68 y R69 no se montan** salvo que S/K sean de drenador abierto.
5. ☐ Conectores JST-SH J7–J19 y tiras hembra de la DevKit (8,5 mm). Comprobar con la DevKit pinchada que entra recta (filas a 22,86 mm).
6. ☐ Inspección con lupa: puentes en los HTSSOP y en U3; continuidad VBAT–GND **no** debe haber.

## 2. Imprimir y preparar la mecánica

| Pieza | Fichero | Orientación | Relleno |
|---|---|---|---|
| Frontal (rampa + cuna) | `hardware/mecanica/stl/frontal_rampa_cuna.stl` | Cara inferior sobre la cama | PETG 40 %, 4 perímetros |
| Trasera (cuna + parachoques) | `…/stl/trasera_cuna_parachoques.stl` | Cara inferior sobre la cama | PETG 40 % |
| Paredes | `…/stl/carcasa_paredes.stl` | De pie | PETG 30 % |
| Techo con bahía y torre del ST4RT | `…/stl/carcasa_techo.stl` | Boca abajo | PETG 30 %; la torre sale hacia la cama, revisar si el laminador pide soportes en el canal del cable |
| Llanta (×4) | `…/stl/llanta.stl` | Plana | 100 %; probar el ajuste al eje D antes de imprimir las cuatro |

Los fuentes editables son `hardware/mecanica/cad/robot.py` (FreeCAD, paramétrico desde `hardware/geometria.py`) y `robot_sumo.FCStd`; los STEP están en `hardware/mecanica/step/`.

1. ☐ Imprimir primero el **techo** y comprobar que el ST4RT entra en su alojamiento (10,8 × 10,8 mm para un módulo de ~10,2 mm). Si no, cambiar `ST4RT_HOLGURA` en `geometria.py` y regenerar.
2. ☐ Insertos de latón M2 (Ø 3,2 × 4) con el soldador a ~220 °C: 4 esquinas + 4 centrales en las cunas, 2 en la rampa.
3. ☐ Cuchilla: fleje de 0,4 mm cortado a la medida del STEP, doblado y **con el filo matado** (lijado hasta que no corte; requisito de seguridad, art. 5.7). Taladros avellanados para 2 × M2 × 5.
4. ☐ Lastre: pletina cortada para el canal central y los canales delantero y trasero (masas en [03](03-Disposicion-mecanica.md)).

## 3. Montaje

Detalle mecánico en [03 · Orden de montaje](03-Disposicion-mecanica.md#orden-de-montaje). Resumen con los conectores:

| Elemento | Conector | Pines (1 → n) |
|---|---|---|
| Batería LiPo 2S | J1 (XT30) | + / − |
| ToF izq., front-izq., frontal, front-der., der., trasero | J7, J8, J9, J10, J11, J12 | 3V3, GND, SCL, SDA, XSHUT |
| Línea front-izq., front-der., tras-izq., tras-der. | J13, J14, J15, J16 | 3V3, GND, salida |
| **ST4RT** | **J17** | **VCC (3,3 V), GND, S, K, IR** |
| I²C de expansión (Qwiic) | J18 | GND, 3V3, SDA, SCL |
| UART / auxiliar | J19 | 5 V, GND, TX, RX |
| Motores 1–4 (izq. del., izq. tras., der. del., der. tras.) | J3–J6, pads para soldar el cable (serigrafía M1–M4) | OUTA, OUTB |

### 3.1 Cable del ST4RT (el paso más delicado)

> El orden de pines del ST4RT **no está confirmado**. La web anuncia K, S, −, + (más IR) con la disposición del módulo p1r.se. **Antes de hacer el cable, identificar los pines con el módulo en la mano** (serigrafía del módulo, continuidad de "−" con la masa del receptor, foto a la documentación del profesor).

1. ☐ Cable JST-SH de 5 polos de 15 cm, crimpado por un lado.
2. ☐ Soldar en el módulo: **J17-1 → +**, **J17-2 → −**, **J17-3 → S**, **J17-4 → K**, **J17-5 → IR** (si el módulo no tiene pin IR, dejarlo al aire).
3. ☐ Con el cable sin enchufar, medir que no hay corto entre + y −.
4. ☐ Pasar el cable por el canal de la torre y fijar el módulo con cinta de doble cara, con el receptor hacia arriba (**pendiente de que el profesor confirme que vale la cinta**).

## 4. Puesta en marcha (bring-up)

Cada paso con el anterior aprobado. Apuntar las medidas: cierran los cálculos de [08, apartado 8](08-Calculos-v1.2.md#8-qué-hay-que-medir-para-cerrar-los-cálculos).

1. ☐ **Sin DevKit, sin sensores, fuente de laboratorio a 7,4 V limitada a 100 mA en J1**: consumo en vacío < 20 mA; buck a **5,30 V ± 0,1 V**. Polaridad invertida → consumo 0 (Q1).
2. ☐ Pinchar la DevKit, **sin batería**, solo USB. Cargar el firmware ([07](07-Firmware.md#2-compilar-y-cargar)). En la consola: telemetría cada 100 ms, estado ESPERA.
3. ☐ Fuente a 6,6 V con DevKit: medir el pin 5V de la DevKit (≥ 4,4 V) y el 3V3 (3,3 V ± 0,1 V).
4. ☐ Sensores uno a uno: la telemetría debe mostrar los 6 ToF con distancias y los 4 QRE con mV sobre negro y blanco. Si un ToF no aparece, revisar su cable y su XSHUT.
5. ☐ **Sin ST4RT, puente JP1 cerrado** (K = 1 fijo): ruedas en el aire, comprobar `SIGNO_M` (ver [07, 5](07-Firmware.md#5-parámetros-a-ajustar-configh)). Sin módulo, START está a 0 por R65: para mover los motores en banco hay que forzar START a 3,3 V con un cable a través de 1 kΩ. **Abrir JP1 al terminar.**
6. ☐ **Con ST4RT**: alimentar, LED apagado. Con el mando: inicio → START = 1 y K = 1; parada → START = 0, K = 0 y el LED parpadea. Medir con el polímetro los niveles en J17-3 y J17-4 y el consumo del módulo (resistencia R62 de 10 Ω: 10 mV = 1 mA).
7. ☐ **Prueba de la parada por hardware**: con el robot en combate (ruedas en el aire), mandar parada; los motores deben detenerse. Repetir manteniendo el ESP32 en reset (botón RST pulsado de la DevKit no sirve: deja DRV_EN a 0); la prueba útil es medir nSLEEP (salida de U3, pin 4) = 0 con K = 0 aunque DRV_EN siga a 1.
8. ☐ Pesar (< 500 g; objetivo ≈ 495 g con lastre) y medir la huella (≤ 100 × 100 mm).
9. ☐ En el dohyo: calibración de línea, frenada ante el borde a cada velocidad, ajuste de `POT_CRUCERO` y de los tiempos de borde.
10. ☐ Combate de 3 min con la batería de 450 mAh: tensión final por celda.

## 5. Procedimiento en competición

Ver [06, apartado 4](06-Modulo-arranque-ST4RT.md#4-procedimiento-en-competición-propuesto-a-validar). Lo esencial: enchufar el XT30 con el LED del módulo **apagado**; tras la parada, **desenchufar el XT30** para que el módulo pueda volver a arrancar. Entre asaltos hay 30 s (art. 13): tener la batería de repuesto cargada.
