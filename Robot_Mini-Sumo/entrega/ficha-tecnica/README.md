# Entrega de la ficha técnica · robot v2

- [`Entrega_ficha_tecnica_v2_Hombres_De_Las_Tabernas.pdf`](Entrega_ficha_tecnica_v2_Hombres_De_Las_Tabernas.pdf): el PDF que se entrega (portada + ficha + anexo de cálculos).
- [`Ficha_tecnica_robot_v2.docx`](Ficha_tecnica_robot_v2.docx): la plantilla del curso rellenada (se puede retocar en Word).
- [`Anexo-calculos-v2.md`](Anexo-calculos-v2.md): el anexo con todos los cálculos (corrientes de motores y drivers, bloqueo, potencia, fusible, regulador, autonomía, masa).
- Los números salen de [`hardware/calculos/calculos_v2.py`](../../hardware/calculos/calculos_v2.py).

Para regenerarlo todo tras medir algo (cambiar el dato en `DATOS` del script y, si cambia un valor del texto, el anexo):

```bash
./generar_entrega.sh
```

Pendiente antes de entregar: nombres de los integrantes y logo en la portada (`Portada.md`), y fotos cuando el robot esté montado. Todo es teórico: nada está medido.
