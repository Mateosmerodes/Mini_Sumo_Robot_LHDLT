#!/usr/bin/env bash
# Genera el PDF de entrega de la ficha técnica en este orden:
#   1. croquis_2_conft.pdf (portada: equipo, componentes, logo y croquis)
#   2. ficha_técnica_robot.docx convertida a PDF
#   3. docs/Anexo-calculos-ficha-tecnica.md convertido a PDF
# Requiere: pandoc, LibreOffice (soffice), pdfunite (poppler) y Node con Playwright.
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$AQUI/../.." && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

# 3. Anexo de cálculos: Markdown -> HTML (fórmulas en MathML) -> PDF con Chromium
( cd "$AQUI/../docs" && pandoc Anexo-calculos-ficha-tecnica.md -s --mathml \
    --metadata pagetitle="Anexo de cálculos" --css "$AQUI/anexo.css" -o "$TMP/anexo.html" )
cp -r "$AQUI/../docs/img" "$TMP/img"
node "$AQUI/html2pdf.js" "$TMP/anexo.html" "$AQUI/Anexo-calculos-ficha-tecnica.pdf"

# 2. Ficha técnica: .docx -> PDF
soffice --headless --convert-to pdf --outdir "$TMP" "$RAIZ/ficha_técnica_robot.docx" >/dev/null
# 1 + 2 + 3
pdfunite "$RAIZ/croquis_2_conft.pdf" "$TMP/ficha_técnica_robot.pdf" \
  "$AQUI/Anexo-calculos-ficha-tecnica.pdf" "$AQUI/Entrega_ficha_tecnica_Hombres_De_Las_Tabernas.pdf"
echo "Generado: $AQUI/Entrega_ficha_tecnica_Hombres_De_Las_Tabernas.pdf"
