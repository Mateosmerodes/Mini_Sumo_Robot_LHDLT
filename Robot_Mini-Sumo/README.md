# 🍺 Robot Mini-Sumo · Hombres de las Tabernas

Robot mini-sumo autónomo (10 × 10 cm, < 500 g) para **Tecnología Eléctrica**, Grado en Robótica (USC), 2.ª edición. Compite según el reglamento **OSHWDem Mini Sumo rev. 7**.

**Equipo:** Mateo Esmerodes Rodríguez · Paulo Bouza García · Mario Costoya Mera

## Concepto

Rampa (cuña) clásica, **tracción 4WD** con 4 N20, **ESP32-S3** en una **PCB propia que es también el chasis**, 6 sensores ToF para encontrar al rival, 4 de línea y arranque por IR (RC5).

## Documentación

| Doc | Contenido | Estado |
|---|---|---|
| [00 · Requisitos y reglamento](docs/00-Requisitos-y-reglamento.md) | Lo que obliga al diseño | ✅ |
| [01 · Selección de componentes](docs/01-Seleccion-de-componentes.md) | Qué pieza y por qué | ✅ borrador |
| [02 · Arquitectura eléctrica](docs/02-Arquitectura-electrica.md) | Alimentación, interconexión, pinout | ✅ borrador |
| [03 · Disposición mecánica y 3D](docs/03-Disposicion-mecanica.md) | Piezas, niveles, masas, montaje, impresión | ✅ borrador |
| 04 · Diseño de la PCB | Esquemático ✅ (ERC limpio), colocación ✅, rutado ⏳ | 🟡 |
| 05 · Lista de compra | AliExpress + LCSC/JLC | ⏳ |
| 06 · Costes | Desglose para el informe | ⏳ |
| Informe final | 6 páginas | ⏳ |
| [📋 Informe de progreso 06/10/2026](docs/Informe-progreso-2026-10-06.md) | Resumen para el equipo: proceso, compra, útiles, problemas | ✅ |

![Robot montado](docs/img/3d_montado.png)

## Estructura

```
docs/                   Documentación (también es una bóveda de Obsidian)
hardware/geometria.py   Parámetros mecánicos compartidos (PCB + 3D)
hardware/generar_todo.sh  Regenera PCB, 3D, STL/STEP e imágenes
hardware/pcb/           Proyecto KiCad (scripts/design.py = circuito)
hardware/mecanica/cad/  Modelo 3D paramétrico (FreeCAD) y renderizador
hardware/mecanica/step/ Exportaciones STEP (Onshape/FreeCAD)
hardware/mecanica/stl/  Piezas listas para imprimir
firmware/               Código del ESP32-S3 (Arduino/PlatformIO)
media/fotos/            Fotos del proceso
informe/                Informe de entrega
```

## Herramientas (Linux)

```bash
sudo pacman -S --needed kicad kicad-library freecad
```

Opcional, para exportar la PCB a 3D con todos los componentes (~5 GB):

```bash
sudo pacman -S --needed kicad-library-3d
```

Licencias: hardware **CERN-OHL-S v2**, software **MIT**.
