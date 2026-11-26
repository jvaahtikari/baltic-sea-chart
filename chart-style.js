// Helper for using the Baltic Sea chart in MapLibre GL JS (v4 or newer).
//
// A. The chart as the whole map style:
//   import * as maplibregl from './lib/maplibre-gl.mjs';
//   import { balticStyle, usePmtiles, followColorScheme } from './chart-style.js';
//   usePmtiles(maplibregl, window.pmtiles);              // lib/pmtiles.js defines window.pmtiles
//   const map = new maplibregl.Map({ container: 'map', style: await balticStyle({ theme: 'auto' }) });
//   followColorScheme(map);                               // optional: follow the system light/dark setting
//
// B. Chart layers on top of your own base map (keeps your style, sources and layers):
//   map.on('load', async () => {
//     await addBalticLayers(map, { theme: 'dark', beforeId: 'vessels', fonts: { regular: ['Your Font'] } });
//     ...later: setBalticTheme(map, 'light');            // e.g. from your own "Light map" switch
//   });
//
// theme: 'light', 'dark' or 'auto' (follows prefers-color-scheme). All URLs in the package are relative;
// these helpers make them absolute against the package folder, so the folder can live anywhere.

const PKG = new URL('./', import.meta.url);
export const prefersDark = () => typeof matchMedia === 'function' && matchMedia('(prefers-color-scheme: dark)').matches;
export const resolveTheme = theme => (theme === 'dark' || (theme !== 'light' && prefersDark())) ? 'dark' : 'light';
const cache = {};

async function load(theme, base) {
  const b = new URL(base || PKG, location.href);
  const file = resolveTheme(theme) === 'dark' ? 'style-dark.json' : 'style.json';
  const key = b.href + file;
  if (!cache[key]) {
    cache[key] = fetch(new URL(file, b)).then(r => {
      if (!r.ok) throw new Error(file + ': HTTP ' + r.status);
      return r.json();
    });
  }
  const s = structuredClone(await cache[key]);
  s.sprite = (Array.isArray(s.sprite) ? s.sprite : [{ id: 'default', url: s.sprite }])
    .map(sp => ({ id: sp.id, url: new URL(sp.url, b).href }));
  s.glyphs = new URL(s.glyphs, b).href.replace('%7Bfontstack%7D', '{fontstack}').replace('%7Brange%7D', '{range}');
  for (const src of Object.values(s.sources)) {
    if (src.url && src.url.startsWith('pmtiles://')) src.url = 'pmtiles://' + new URL(src.url.slice(10), b).href;
  }
  return s;
}

// Full MapLibre style object for the chart.
export async function balticStyle(opts = {}) {
  if (typeof opts === 'string' || opts instanceof URL) opts = { base: opts };
  return load(opts.theme || 'auto', opts.base);
}

function withFonts(layer, fonts) {
  if (!fonts || !layer.layout || !layer.layout['text-font']) return layer;
  const f = layer.layout['text-font'].join(' ');
  const pick = /italic/i.test(f) ? (fonts.italic || fonts.regular) : fonts.regular;
  if (pick) layer.layout['text-font'] = pick;
  return layer;
}

// Adds the chart's sources, symbols and layers to a map that already has its own style.
//   theme    'light' | 'dark' | 'auto'
//   beforeId insert below this existing layer (e.g. your vessel layer)
//   only     array of layer ids to add (see style.json), default all except the background
//   skip     array of layer ids to leave out, e.g. ['land', 'coastline'] if your base map draws land
//   fonts    { regular: [...], italic: [...] } font stacks that your style's glyph server provides;
//            needed for labels, because a map has only one glyph source
// Returns the ids of the added layers.
export async function addBalticLayers(map, { base, theme = 'auto', beforeId, only, skip = [], fonts } = {}) {
  const s = await load(theme, base);
  for (const sp of s.sprite) {
    if (typeof map.getSprite === 'function' && map.getSprite().some(x => x.id === sp.id)) continue;
    map.addSprite(sp.id, sp.url);
  }
  for (const [id, src] of Object.entries(s.sources)) if (!map.getSource(id)) map.addSource(id, src);
  const ids = [];
  for (const layer of s.layers) {
    if (layer.type === 'background' || skip.includes(layer.id)) continue;
    if (only && !only.includes(layer.id)) continue;
    if (map.getLayer(layer.id)) continue;
    map.addLayer(withFonts(layer, fonts), beforeId);
    ids.push(layer.id);
  }
  map.__balticLayers = ids;
  return ids;
}

// Switches the added chart layers (or a map using balticStyle) between light and dark in place,
// without reloading your style: only paint and layout properties of the chart layers change.
export async function setBalticTheme(map, theme, { base, fonts } = {}) {
  const s = await load(theme, base);
  for (const layer of s.layers) {
    if (!map.getLayer(layer.id)) continue;
    withFonts(layer, fonts);
    for (const [k, v] of Object.entries(layer.paint || {})) map.setPaintProperty(layer.id, k, v);
    for (const [k, v] of Object.entries(layer.layout || {})) {
      if (k === 'visibility') continue;
      map.setLayoutProperty(layer.id, k, v);
    }
  }
}

// Follows the system light/dark setting. Returns a function that stops following.
export function followColorScheme(map, opts = {}) {
  if (typeof matchMedia !== 'function') return () => {};
  const mq = matchMedia('(prefers-color-scheme: dark)');
  const onChange = () => setBalticTheme(map, mq.matches ? 'dark' : 'light', opts);
  mq.addEventListener('change', onChange);
  return () => mq.removeEventListener('change', onChange);
}

let protocolAdded = false;
export function usePmtiles(maplibregl, pmtiles) {
  if (protocolAdded) return;
  const p = new pmtiles.Protocol();
  maplibregl.addProtocol('pmtiles', p.tile);
  protocolAdded = true;
}
