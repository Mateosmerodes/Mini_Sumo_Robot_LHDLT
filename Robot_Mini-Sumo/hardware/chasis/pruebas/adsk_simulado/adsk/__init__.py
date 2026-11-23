"""Imitación mínima de la API de Fusion 360 (adsk.core / adsk.fusion) hecha con CadQuery.

Solo sirve para probar fuera de Fusion la lógica de ChasisLHDT.py: implementa las llamadas que usa
el script, con los mismos nombres y argumentos que la API real. NO comprueba que la API real
acepte esas llamadas (eso solo se puede ver ejecutándolo en Fusion).
"""
from . import core, fusion  # noqa: F401
