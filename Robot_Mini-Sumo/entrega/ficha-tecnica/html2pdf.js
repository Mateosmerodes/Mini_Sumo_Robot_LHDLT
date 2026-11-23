// Uso: node html2pdf.js entrada.html salida.pdf "texto del pie"
const { chromium } = require('playwright');
(async () => {
  const [, , entrada, salida, pie] = process.argv;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + require('path').resolve(entrada), { waitUntil: 'networkidle' });
  await page.pdf({ path: salida, format: 'A4', preferCSSPageSize: true, printBackground: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: `<div style="font-size:7pt;width:100%;text-align:center;color:#666">${pie || ''} · <span class="pageNumber"></span>/<span class="totalPages"></span></div>` });
  await browser.close();
})();
