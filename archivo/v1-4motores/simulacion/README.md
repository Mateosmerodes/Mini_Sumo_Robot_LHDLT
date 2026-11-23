# Simulaciones de la placa v1.2

Resultados y explicación: [docs/14-Simulaciones.md](../docs/14-Simulaciones.md). **Solo simulación**: nada medido en una placa real.

| Carpeta | Qué hay |
|---|---|
| `spice/` | Modelos y netlists de ngspice (simplificados, no de fabricante) |
| `scripts/` | Python que lanza ngspice y dibuja; `cobre.py` y `termico.py` leen la PCB con KiCad |
| `firmware/` | `sim_combate.cpp`: el firmware real (arranque y estrategia) sobre un dohyo virtual |
| `graficas/` | Las gráficas de docs/14 |
| `resultados/` | Los números de cada simulación (JSON y texto) |

```bash
./ejecutar_todo.sh   # necesita ngspice, python3 (numpy, scipy, matplotlib), g++ y KiCad 9
```
