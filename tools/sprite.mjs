// Builds the chart symbol sprite (sprite.png/json and sprite@2x.png/json) from SVG definitions.
// Symbols follow Finnish paper-chart / IALA region A conventions with ECDIS colours.
// One sprite holds both themes: <name> for the light style and <name>-dark for the dark style.
// Usage: node tools/sprite.mjs <outdir>
import sharp from 'sharp';
import fs from 'node:fs';
import path from 'node:path';

const out = process.argv[2] || 'dist';
let theme = 'light', INK, PAPER, PURPLE, EC;
function setTheme(t) {
  theme = t;
  INK = t === 'dark' ? '#c9d1d4' : '#1a1a1a';
  PAPER = t === 'dark' ? '#0e171c' : '#ffffff';
  PURPLE = t === 'dark' ? '#d07ac6' : '#9b2c8f';
  EC = { r: '#e2211c', g: '#13a04a', y: '#f2c311', b: t === 'dark' ? '#3b4448' : '#111111', w: '#ffffff' };
}
const LIGHT = { W: '#f2c311', Y: '#f2c311', R: '#e2211c', G: '#13a04a', Bu: '#2a6fd6' };

const svg = (w, h, body) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${body}</svg>`;

// Position circle sits at the image centre so MapLibre's default centre anchor is correct.
// Mark canvas 20 x 52: shaft 10..24, position circle at (10, 26).
function bands(cat) {
  return { port: ['r'], starboard: ['g'], north: ['b', 'y'], south: ['y', 'b'], west: ['y', 'b', 'y'], east: ['b', 'y', 'b'],
    isolated_danger: ['b', 'r', 'b'], safe_water: ['rw'], special: ['y'], none: ['b'] }[cat] || ['b'];
}
function topmark(cat) {
  const f = ` fill="${INK}"`;
  switch (cat) {
    case 'port': return `<rect x="8.3" y="3.6" width="3.4" height="6.4" fill="${EC.r}" stroke="${INK}" stroke-width=".7"/>`;
    case 'starboard': return `<path d="M10 2.8L13.2 10H6.8Z" fill="${EC.g}" stroke="${INK}" stroke-width=".7"/>`;
    case 'north': return `<path d="M10 1L12.9 5.3H7.1ZM10 5.9L12.9 10.2H7.1Z"${f}/>`;
    case 'south': return `<path d="M7.1 1H12.9L10 5.3ZM7.1 5.9H12.9L10 10.2Z"${f}/>`;
    case 'west': return `<path d="M7.1 1H12.9L10 5.3ZM10 5.9L12.9 10.2H7.1Z"${f}/>`;
    case 'east': return `<path d="M10 1L12.9 5.3H7.1ZM7.1 5.9H12.9L10 10.2Z"${f}/>`;
    case 'isolated_danger': return `<circle cx="10" cy="3.3" r="2.2"${f}/><circle cx="10" cy="8.1" r="2.2"${f}/>`;
    case 'safe_water': return `<circle cx="10" cy="6.6" r="2.7" fill="${EC.r}" stroke="${INK}" stroke-width=".7"/>`;
    case 'special': return `<path d="M7.4 3.4L12.6 8.6M12.6 3.4L7.4 8.6" stroke="${INK}" stroke-width="2.6"/><path d="M7.4 3.4L12.6 8.6M12.6 3.4L7.4 8.6" stroke="${EC.y}" stroke-width="1.5"/>`;
    default: return '';
  }
}
function base(cx, cy) {
  return `<path d="M${cx - 4.6} ${cy}H${cx - 1.9}M${cx + 1.9} ${cy}H${cx + 4.6}" stroke="${INK}" stroke-width="1.1"/>` +
    `<circle cx="${cx}" cy="${cy}" r="1.9" fill="${PAPER}" stroke="${INK}" stroke-width="1.1"/>`;
}
function mark(cat) {
  const top = (cat === 'starboard' || cat === 'safe_water') ? 10 : 10.2, y1 = 24.1, bs = bands(cat), h = (y1 - top) / bs.length;
  let s = '';
  bs.forEach((c, i) => {
    const y = top + i * h;
    if (c === 'rw') s += `<rect x="8.5" y="${y}" width="1.5" height="${h}" fill="${EC.r}"/><rect x="10" y="${y}" width="1.5" height="${h}" fill="#fff"/>`;
    else s += `<rect x="8.5" y="${y}" width="3" height="${h}" fill="${EC[c]}"/>`;
  });
  s += `<rect x="8.5" y="${top}" width="3" height="${y1 - top}" fill="none" stroke="${INK}" stroke-width=".6"/>`;
  return svg(20, 52, s + topmark(cat) + base(10, 26));
}
// Other symbols are drawn around a centre point (cx, cy) on square canvases.
const cairn = () => svg(20, 20, `<path d="M2 10H18" stroke="${INK}" stroke-width="1.1"/><path d="M6.3 10L7.7 5.2H12.3L13.7 10Z" fill="${INK}"/>`);
const daymark = () => svg(20, 40, `<path d="M6.8 18.2L7.8 4.5H12.2L13.2 18.2" fill="none" stroke="${INK}" stroke-width="1.3"/>` + base(10, 20));
const leading = () => svg(18, 40, `<rect x="6.5" y="2" width="2.5" height="9" fill="${INK}"/><rect x="6.5" y="2" width="5" height="9" fill="none" stroke="${INK}" stroke-width="1.1"/><path d="M9 11V18.1" stroke="${INK}" stroke-width="1.3"/>` + base(9, 20));
const light = () => svg(16, 16, `<circle cx="8" cy="8" r="2.6" fill="${PAPER}" stroke="${INK}" stroke-width="1.3"/><circle cx="8" cy="8" r=".9" fill="${INK}"/>`);
const lighthouse = () => svg(22, 22, `<circle cx="11" cy="11" r="9" fill="none" stroke="${PURPLE}" stroke-width="1.4"/><path d="M11 4.6L16.5 14.1H5.5ZM11 17.4L5.5 7.9H16.5Z" fill="none" stroke="${INK}" stroke-width="1.1"/>`);
const racon = () => svg(18, 18, `<circle cx="9" cy="9" r="7" fill="none" stroke="${PURPLE}" stroke-width="1.6"/><circle cx="9" cy="9" r="1.6" fill="${INK}"/>`);
const lightFloat = () => svg(24, 24, `<path d="M3 14H21L18 18H6Z" fill="${INK}"/><path d="M12 14V6" stroke="${INK}" stroke-width="1.4"/>` + base(12, 12));
const generic = () => svg(16, 16, `<circle cx="8" cy="8" r="2.6" fill="${PAPER}" stroke="${INK}" stroke-width="1.3"/>`);
// Hazards: rock (submerged: cross; awash: cross with dots), wreck, obstruction
const rock = () => svg(16, 16, `<path d="M3 8H13M8 3V13" stroke="${INK}" stroke-width="1.4"/>`);
const rockAwash = () => svg(16, 16, `<path d="M3 8H13M8 3V13" stroke="${INK}" stroke-width="1.4"/><circle cx="4.6" cy="4.6" r="1" fill="${INK}"/><circle cx="11.4" cy="4.6" r="1" fill="${INK}"/><circle cx="4.6" cy="11.4" r="1" fill="${INK}"/><circle cx="11.4" cy="11.4" r="1" fill="${INK}"/>`);
const wreck = () => svg(24, 16, `<path d="M2 8H22M8 4V12M12 3V13M16 4V12" stroke="${INK}" stroke-width="1.3"/>`);
const obstruction = () => svg(18, 18, `<circle cx="9" cy="9" r="6.5" fill="none" stroke="${INK}" stroke-width="1.2" stroke-dasharray="2 1.6"/><text x="9" y="11.6" font-size="7" font-family="sans-serif" text-anchor="middle" fill="${INK}">Obs</text>`);
// Light flare (teardrop) pointing from the light towards 135 degrees, light at the image centre.
const flare = (col) => svg(48, 48, `<g transform="translate(24 24) rotate(-45)"><path d="M0 3.2C-2.9 8 -4 13.4 -3.2 17.6C-2.5 21.2 2.5 21.2 3.2 17.6C4 13.4 2.9 8 0 3.2Z" fill="${col}" stroke="rgba(0,0,0,.45)" stroke-width=".5"/></g>`);

const icons = {};
for (const t of ['light', 'dark']) {
  setTheme(t);
  const sfx = t === 'dark' ? '-dark' : '';
  for (const c of ['port', 'starboard', 'north', 'south', 'east', 'west', 'isolated_danger', 'safe_water', 'special', 'none']) icons['mark-' + c + sfx] = mark(c);
  const more = {
    cairn: cairn(), daymark: daymark(), leading_mark: leading(), light: light(), lighthouse: lighthouse(), racon: racon(),
    light_float: lightFloat(), generic: generic(), rock: rock(), 'rock-awash': rockAwash(), wreck: wreck(), obstruction: obstruction(),
  };
  for (const [k, v] of Object.entries(more)) icons[k + sfx] = v;
  for (const [k, v] of Object.entries(LIGHT)) icons['flare-' + k + sfx] = flare(v);
}

async function build(scale) {
  const items = [];
  for (const [name, s] of Object.entries(icons)) {
    const buf = await sharp(Buffer.from(s), { density: 72 * scale }).png().toBuffer();
    const m = await sharp(buf).metadata();
    items.push({ name, buf, w: m.width, h: m.height });
  }
  const maxW = 512 * scale;
  let x = 0, y = 0, rowH = 0;
  const json = {};
  const comps = [];
  for (const it of items) {
    if (x + it.w > maxW) { x = 0; y += rowH + 2 * scale; rowH = 0; }
    json[it.name] = { x, y, width: it.w, height: it.h, pixelRatio: scale };
    comps.push({ input: it.buf, left: x, top: y });
    x += it.w + 2 * scale; rowH = Math.max(rowH, it.h);
  }
  const H = y + rowH;
  const suffix = scale === 1 ? '' : '@' + scale + 'x';
  await sharp({ create: { width: maxW, height: H, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } } })
    .composite(comps).png().toFile(path.join(out, 'sprite' + suffix + '.png'));
  fs.writeFileSync(path.join(out, 'sprite' + suffix + '.json'), JSON.stringify(json, null, 1));
}
fs.mkdirSync(out, { recursive: true });
await build(1);
await build(2);
console.log('sprite: %d icons -> %s', Object.keys(icons).length, out);
