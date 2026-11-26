// Screenshots of the demo page at fixed places, for checking a build. Usage: node tools/shots.mjs <url> <outdir>
import { chromium } from 'playwright';
import fs from 'node:fs';

const [url = 'http://127.0.0.1:8000/index.html', out = 'shots'] = process.argv.slice(2);
const REGION = process.env.BSC_REGION || 'baltic';
const PLACES_BY_REGION = {
  norway: [
    ['overview', 12.0, 65.0, 4.2], ['oslofjord', 10.6, 59.5, 9], ['bergen', 5.25, 60.35, 10], ['bergen_detail', 5.30, 60.39, 13],
    ['marstein', 5.0, 60.13, 12], ['stavanger', 5.65, 58.97, 11], ['alesund', 6.15, 62.47, 11], ['trondheim', 10.4, 63.45, 11],
    ['lofoten', 14.0, 68.2, 9], ['tromso', 18.95, 69.65, 11], ['nordkapp', 25.8, 71.0, 9], ['skagerrak', 9.0, 58.2, 8],
  ],
  'probe-norway': [
    ['overview', 5.25, 60.2, 9], ['bergen', 5.25, 60.35, 10], ['bergen_detail', 5.30, 60.39, 13], ['bergen_port', 5.31, 60.40, 15],
    ['marstein', 5.0, 60.13, 12], ['askoy', 5.1, 60.45, 12], ['sotra', 4.95, 60.3, 11],
  ],
};
const PLACES_BALTIC = [
  ['overview', 20.5, 59.5, 4.6], ['gulf_of_finland_east', 27.3, 60.1, 8.5], ['helsinki', 24.95, 60.13, 11],
  ['helsinki_detail', 24.975, 60.115, 14], ['turku_archipelago', 21.9, 60.2, 10], ['aland', 19.95, 60.1, 10],
  ['stockholm', 18.6, 59.35, 10], ['tallinn', 24.75, 59.47, 11], ['riga', 24.0, 57.1, 9],
  ['klaipeda', 21.1, 55.7, 10], ['gdansk', 18.7, 54.45, 10], ['kiel', 10.2, 54.4, 10], ['kiel_detail', 10.17, 54.38, 12.5],
  ['rostock', 12.1, 54.18, 12], ['riga_port', 24.03, 57.05, 11], ['parnu', 24.45, 58.33, 11], ['muuga', 24.95, 59.52, 12.5],
  ['copenhagen', 12.65, 55.7, 11], ['kattegat', 11.5, 57.0, 8], ['oulu', 25.3, 65.05, 10],
];
export const PLACES = PLACES_BY_REGION[REGION] || PLACES_BALTIC;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1000, height: 700 } });
const errors = [];
page.on('console', m => { if (m.type() === 'error') errors.push(m.text() + ' @ ' + ((m.location() || {}).url || '')); });
page.on('pageerror', e => errors.push(String(e)));
const result = [];
const DARK = ['overview', 'helsinki', 'stockholm', 'gdansk', 'bergen', 'bergen_detail'];
const overlayUrl = url.replace(/index\.html$/, 'overlay.html');
const jobs = [
  ...PLACES.map(p => [p[0], p[1], p[2], p[3], url]),
  ...PLACES.filter(p => DARK.includes(p[0])).map(p => [p[0] + '_dark', p[1], p[2], p[3], url + '?theme=dark']),
  ...(REGION === 'baltic' ? [['overlay_dark', 21.0, 59.8, 7, overlayUrl], ['overlay_dark_z11', 22.3, 59.9, 11, overlayUrl]] : []),
];
for (const [name, lon, lat, z, base] of jobs) {
  await page.goto(`${base}#${z}/${lat}/${lon}`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.map && window.map.isStyleLoaded(), null, { timeout: 60000 }).catch(() => {});
  const t = Date.now();
  await page.waitForTimeout(base.includes('theme=dark') ? 1500 : 200);
  await page.evaluate(() => new Promise(res => { const m = window.map; if (!m) return res(); if (m.loaded() && m.areTilesLoaded()) setTimeout(res, 300); else m.once('idle', () => setTimeout(res, 300)); setTimeout(res, 45000); }));
  const counts = await page.evaluate(() => {
    const m = window.map; if (!m) return {};
    const c = {};
    for (const l of ['depth-area', 'depth-area-nat', 'depth-contour', 'land', 'seamark', 'light-flare', 'light-sector-arc', 'navline', 'fairway', 'hazard', 'sounding', 'danger-area', 'nodata'])
      c[l] = m.getLayer(l) ? m.queryRenderedFeatures({ layers: [l] }).length : -1;
    return c;
  });
  await page.screenshot({ path: `${out}/${name}.png` });
  result.push({ name, lon, lat, zoom: z, ms: Date.now() - t, rendered: counts });
  console.log(name, JSON.stringify(counts));
}
fs.writeFileSync(`${out}/shots.json`, JSON.stringify({ result, errors: [...new Set(errors)].slice(0, 30) }, null, 1));
await browser.close();
