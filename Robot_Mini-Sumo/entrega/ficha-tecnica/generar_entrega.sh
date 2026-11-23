#!/usr/bin/env bash
# Genera la entrega de la ficha técnica del robot v2 en un único PDF:
#   1. Portada.md  2. ficha (plantilla .docx rellenada)  3. Anexo-calculos-v2.md
# Requiere: python3 + python-docx, pandoc, LibreOffice (soffice), pdfunite y Node con Playwright.
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
RS="$(cd "$AQUI/../.." && pwd)"          # Robot_Mini-Sumo/
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/img"
cp "$RS/hardware/chasis/img/chasis_montado.png" "$RS/docs/img/pcb_v2_cara_superior.png" "$TMP/img/"

# 0. Cálculos
python3 "$RS/hardware/calculos/calculos_v2.py" >/dev/null

# 1 y 3. Markdown -> HTML (fórmulas en MathML) -> PDF con Chromium
for doc in Portada Anexo-calculos-v2; do
  pandoc "$AQUI/$doc.md" -s --mathml --metadata pagetitle="$doc" --css "$AQUI/estilo.css" -o "$TMP/$doc.html"
done
node "$AQUI/html2pdf.js" "$TMP/Portada.html" "$TMP/portada.pdf" "Hombres De Las Tabernas · Robot v2"
node "$AQUI/html2pdf.js" "$TMP/Anexo-calculos-v2.html" "$AQUI/Anexo-calculos-v2.pdf" "Anexo de cálculos · Hombres De Las Tabernas · Robot v2"

# 2. Ficha: plantilla .docx rellenada -> PDF
python3 "$AQUI/rellenar_ficha.py" "$AQUI/Ficha_tecnica_robot_v2.docx"
soffice --headless --convert-to pdf --outdir "$TMP" "$AQUI/Ficha_tecnica_robot_v2.docx" >/dev/null

pdfunite "$TMP/portada.pdf" "$TMP/Ficha_tecnica_robot_v2.pdf" "$AQUI/Anexo-calculos-v2.pdf" \
  "$AQUI/Entrega_ficha_tecnica_v2_Hombres_De_Las_Tabernas.pdf"
echo "Generado: $AQUI/Entrega_ficha_tecnica_v2_Hombres_De_Las_Tabernas.pdf"
