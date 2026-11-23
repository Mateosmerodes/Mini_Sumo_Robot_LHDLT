// Uso: node html2pdf.js entrada.html salida.pdf
const { chromium } = require('playwright');
(async () => {
  const [, , entrada, salida] = process.argv;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + require('path').resolve(entrada), { waitUntil: 'networkidle' });
  await page.pdf({ path: salida, format: 'A4', preferCSSPageSize: true, printBackground: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:7pt;width:100%;text-align:center;color:#666">Anexo de cálculos · Hombres De Las Tabernas · <span class="pageNumber"></span>/<span class="totalPages"></span></div>' });
  await browser.close();
})();
