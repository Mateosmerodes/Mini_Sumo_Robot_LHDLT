# Sistema de versiones

Cómo numeramos el diseño, dónde se apunta la versión y cómo se recupera una versión antigua.

## La regla de oro: los nombres de fichero no cambian

El proyecto KiCad se llama siempre `hardware/pcb/robot_sumo.kicad_pro` (`_sch`, `_pcb`). **Nunca** `robot_sumo1`, `robot_sumo_v2`, `final`, `final_de_verdad`… Las versiones anteriores no se guardan como copias: las guarda git y se recuperan con su etiqueta.

## Numeración: `vMAYOR.MENOR.PARCHE`

| Parte | Cuándo sube | Ejemplo |
|---|---|---|
| **MAYOR** | Placa de otra generación: cambian el contorno, los taladros o la mecánica que la rodea. Las piezas impresas de la versión anterior ya no valen. | v2.0: PCB de 4 capas con otra forma |
| **MENOR** | Cambio de diseño dentro de la misma generación: circuitos, componentes, rutado. | v1.2: rutado a mano y módulo de arranque |
| **PARCHE** | Corrección sin cambio de funcionalidad. | v1.2.1: devolver D3 y R9 a su sitio |

Los cambios que **solo** tocan documentación no cambian la versión del hardware: se apuntan en el CHANGELOG, en «Sin publicar».

## Dónde va la versión

Cada versión tiene que estar igual en estos cuatro sitios:

1. **Cajetín de KiCad**, campo *Revisión*, en el esquemático **y** en la PCB (Archivo → Configuración de página). Por ejemplo, `v1.2`.
2. **Serigrafía de la PCB**: el texto `Mini-Sumo v1.2 · 2026` de la cara inferior. Así cada placa fabricada lleva su versión impresa.
3. **[CHANGELOG.md](../CHANGELOG.md)**: qué cambió, qué se quitó y qué queda pendiente.
4. **Etiqueta de git** (`v1.2`) en el commit de `main` que contiene esa versión.

Si se fabrica una versión, además se crea una **Release** en GitHub con esa etiqueta y se adjuntan: los Gerber y taladros en zip, la BOM, el esquemático en PDF y la posición de componentes (si la monta JLC).

## Cómo sacar una versión nueva

1. Trabajar en una rama: `git switch -c v1.2.1-fix-led`.
2. Hacer los cambios en KiCad y pasar **ERC y DRC** sin errores.
3. Subir la revisión en el cajetín (esquemático y PCB) y en la serigrafía.
4. En el CHANGELOG, convertir «Sin publicar» en la nueva versión, con la fecha.
5. Exportar la BOM desde KiCad a `hardware/pcb/bom.csv`.
6. Si cambia algo que afecta a la mecánica (contorno, taladros, posición de la DevKit), llevarlo a `hardware/geometria.py` y ejecutar `hardware/generar_todo.sh`.
7. Abrir un pull request y fusionarlo en `main`.
8. Etiquetar el commit fusionado y subir la etiqueta:

```bash
git switch main && git pull
git tag -a v1.2.1 -m "v1.2.1: D3 y R9 en su sitio"
git push origin v1.2.1
```

## Cómo ver o recuperar una versión antigua

```bash
git tag -n                                    # lista de versiones con su descripción
git switch --detach v1.1                      # ver el repositorio tal como estaba en la v1.1
git switch -                                  # volver a donde estabas
git show v1.1:Robot_Mini-Sumo/hardware/pcb/robot_sumo.kicad_pcb > /tmp/placa_v1.1.kicad_pcb   # sacar un fichero suelto
```

También desde GitHub: botón de rama → pestaña **Tags** → elegir la versión.

## Revisiones de diseño

Cada revisión de una versión se guarda en `docs/revisiones/` con el nombre `AAAA-MM-DD_Revision_PCB_vX.Y.pdf`. Los problemas que encuentra se copian al CHANGELOG, en «Pendiente», hasta que se corrigen.

## Lo que no entra en git

Lo lista el `.gitignore` de la raíz: copias de seguridad de KiCad y FreeCAD, preferencias locales (`*.kicad_prl`), cachés de Python y las mallas intermedias del renderizador (`hardware/mecanica/cad/_render/`). Todo eso se regenera solo.
