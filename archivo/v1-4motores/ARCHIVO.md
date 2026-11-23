# Archivo · Diseño v1 (4 motores, placa SMD)

Esta carpeta guarda **todo el trabajo anterior** al cambio de rumbo del 23/11/2026, cuando el equipo decidió simplificar el robot (ver [`../../Robot_Mini-Sumo/`](../../Robot_Mini-Sumo/)). No se borra nada: aquí está tal cual quedó.

Es una sola versión que junta todo lo que había repartido en ramas y PR:

| Origen | Qué era | Dónde está ahora |
|---|---|---|
| `main` (hasta el 20/11/2026) | Ficha técnica entregada, croquis, PCB `robot_sumo1` ordenada a mano por el equipo | `hardware/pcb/robot_sumo1.*` y `entregas-iniciales/` |
| PR #4 | Anexo de cálculos de la ficha y PDF de entrega | `docs/Anexo-calculos-ficha-tecnica.md`, `entrega/` |
| PR #5 | Rediseño v1.2: 4 motores, 4 DRV8874, buck, 6 ToF, 4 sensores de línea, ST4RT | todo el resto de esta carpeta |
| PR #6 | Corrección del tronco de VBAT de la PCB v1.2 | `hardware/pcb/` |
| PR #7 | Aclaración de que los DRV8874 son chip suelto | `docs/10` |
| PR #8 | Simulaciones de la placa v1.2 | `simulacion/`, `docs/14` |
| PR #3 (última versión) | Limpieza del repo y sistema de versiones sobre la placa `robot_sumo1` | `variante-PR3/` (solo los ficheros que difieren; misma estructura de carpetas) |

Además, el estado completo antes de mover nada está en el commit `7e4c077` (y la última versión del PR #3 en `553044e`). Para marcarlos con etiquetas de git (desde aquí no se pudieron subir), en un ordenador con el repo:

```bash
git tag -a v1-archivo 7e4c077 -m "Diseño v1 completo antes de simplificar"
git tag -a v1-archivo-pr3 553044e -m "Última versión del PR #3"
git push origin v1-archivo v1-archivo-pr3
```

Nota: las rutas internas de los documentos de esta carpeta (por ejemplo `hardware/pcb/...`) son relativas a esta carpeta. Los scripts se escribieron para ejecutarse desde la antigua carpeta `Robot_Mini-Sumo/`; si se quieren volver a usar, copiar la carpeta a ese nombre.
