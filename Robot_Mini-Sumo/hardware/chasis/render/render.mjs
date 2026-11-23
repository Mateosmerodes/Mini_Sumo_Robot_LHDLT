// Imágenes del chasis: node render/render.mjs  (antes: python construir_cadquery.py y, en render/, npm install)
// Abre index.html en Chromium (Playwright) y guarda las vistas en ../img/.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const AQUI = path.dirname(fileURLToPath(import.meta.url));
const RAIZ = path.resolve(AQUI, '..');
const TIPOS = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.stl': 'application/octet-stream' };

const srv = http.createServer((req, res) => {
  const p = path.join(RAIZ, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(RAIZ) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TIPOS[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0);
const puerto = srv.address().port;

const PCB = ['ref_pcb', 'ref_devkit_esp32'];
const IMPRIMIR = ['chasis', 'abrazadera_motor_izq', 'abrazadera_motor_der'];
const VISTAS = {
  chasis_montado: { cam: [230, 300, 190] },
  chasis_sin_pcb: { cam: [230, 300, 210], ocultar: PCB },
  chasis_trasera: { cam: [-240, -280, 200], ocultar: PCB },
  chasis_solo: { cam: [-210, -260, 260], solo: IMPRIMIR, objetivo: [0, 0, 10] },
  chasis_frente_solo: { cam: [210, 300, 230], solo: IMPRIMIR.concat(['cuchilla_acero']), objetivo: [0, 0, 10] },
  chasis_inferior: { cam: [0, 0, -400], solo: ['chasis', 'cuchilla_acero'], orto: true, up: [0, 1, 0], objetivo: [0, 0, 0] },
  chasis_lateral: { cam: [400, 0, 20], orto: true, objetivo: [0, 0, 22], zoom: 1.15 },
  chasis_planta: { cam: [0, 0, 400], ocultar: PCB, orto: true, up: [0, 1, 0], objetivo: [0, 0, 0] },
  chasis_despiece: {
    cam: [260, 330, 250], objetivo: [0, 0, 30], zoom: 0.82,
    desplaz: { ref_pcb: [0, 0, 45], ref_devkit_esp32: [0, 0, 45], abrazadera_motor_izq: [0, 0, 18],
               abrazadera_motor_der: [0, 0, 18], ref_bateria: [-85, 0, 0], cuchilla_acero: [0, 18, 10],
               'ref_vl53l0x_1': [0, 0, 25], 'ref_vl53l0x_2': [0, 0, 25] },
  },
};

const navegador = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const pag = await navegador.newPage({ viewport: { width: 1400, height: 1050 } });
pag.on('console', (m) => console.log('[pagina]', m.text()));
pag.on('pageerror', (e) => console.log('[error]', e.message));
await pag.goto(`http://localhost:${puerto}/render/index.html`);
await pag.waitForFunction(() => window.listo === true, null, { timeout: 120000 });
fs.mkdirSync(path.join(RAIZ, 'img'), { recursive: true });
for (const [nombre, v] of Object.entries(VISTAS)) {
  await pag.evaluate((v) => window.vista(v), v);
  await pag.locator('canvas').screenshot({ path: path.join(RAIZ, 'img', nombre + '.png') });
  console.log('img/' + nombre + '.png');
}
await navegador.close();
srv.close();
