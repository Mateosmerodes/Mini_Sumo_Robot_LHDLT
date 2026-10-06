# 00 · Requisitos y reglamento

Resumen de lo que **obliga** al diseño. Fuentes: reglamento Mini Sumo OSHWDem rev. 7 (2026) y requisitos de la asignatura (Tecnología Eléctrica, USC).

## Reglamento OSHWDem – Mini Sumo

| Aspecto | Regla | Consecuencia de diseño |
|---|---|---|
| Tamaño | 10 × 10 cm en planta, **altura ilimitada** | Podemos crecer en vertical (sensores altos, electrónica en pisos). |
| Masa | < 500 g al inicio del combate | Apuntar a ~480–495 g con lastre ajustable. |
| Expansión | Se puede expandir **después** del inicio, sin separarse en piezas | Banderas/alas desplegables permitidas (idea futura). |
| Piezas sueltas | < 5 g en total que caigan no penaliza | Tornillería bien sujeta igualmente. |
| **Arranque** | **Por IR, protocolo RC5, mando del juez**, sin retardo | **Receptor IR 38 kHz obligatorio** + decodificador RC5 en firmware. |
| Autonomía | Clase Mini autónoma | Wi-Fi/BT solo para telemetría/ajuste en taller, nunca para controlar en combate. |
| Controlador | Basado en tecnologías abiertas | ESP32-S3 + nuestra PCB publicada (open hardware) ✔. |
| Prohibido | Imanes, vacío, pegamentos, jamming IR, lanzar cosas | Tracción solo por **peso + goma**. |
| Afilados | Permitidos si no dañan y el robot frena de forma fiable | Cuchilla con el filo matado + frenado activo en firmware. |
| Salidas | Asaltos alternos: **de frente, de lado, de espaldas** | Sensores de rival en frontal **y laterales**, sensores de línea delante **y detrás**. |
| Inactividad | Si no te mueves en 5 s pierdes el asalto | Estrategia por defecto siempre en movimiento. |
| Nombre | El robot debe tener nombre o número | Nombre en carcasa y serigrafía. |

### Dohyo

| Diámetro | Altura | Material | Borde blanco | Líneas de salida |
|---|---|---|---|---|
| 77 cm | 19 mm | MDF (negro) | 2,5 cm | 10 cm de largo, 10 cm separación, marrón |

- **Superficie de madera:** imanes inútiles además de prohibidos → todo el empuje sale de **masa × coeficiente de rozamiento**.
- El borde blanco mide 2,5 cm: a 1 m/s se cruza en **25 ms**. Los sensores de línea tienen que leerse a ≥ 1 kHz y estar **delante de las ruedas**.
- Distancia máxima útil al rival: ~77 cm. Cualquier lectura > ~70 cm es ruido o público.

## Requisitos de la asignatura

1. **PCB propia** que interconecte control, sensores y drivers, con **nombre del equipo en serigrafía** → "HOMBRES DE LAS TABERNAS" + logo de la jarra.
2. Se pueden usar módulos y placas de desarrollo.
3. **Estructura base de diseño y fabricación propia** (tornillería comercial OK).
4. Informe de **6 páginas máx.**: equipo + logo, componentes, documentación (electrónica, mecánica, software), costes desglosados, fotos.
5. Repositorio GitHub recomendado → este repo.

### Rúbrica

| Criterio | Puntos |
|---|---|
| Cumple especificaciones | 3 |
| Se mueve y responde a los sensores | 2 |
| Participa y tiene valoración positiva del comité técnico | 3 |
| Participa y hace al menos una batalla | 2 |
| *Ganar el campeonato* | *Exento del examen de teoría* |

> El informe tiene que estar entregado y validado **antes** del campeonato (enero 2027).

## Restricciones del equipo

- Presupuesto: **50–80 €** en total.
- Medios: impresoras FDM, impresora de resina y máquina de corte de madera.
- Software: Linux (sin Fusion 360) → KiCad + FreeCAD/Onshape.
