# Baltic Sea chart – vector map package

**Not for navigation.** This is a chart-style map of the Baltic Sea built automatically from open
data. It is not an official nautical chart and must not be used for navigation or route planning.
Russian waters are not included.

The folder is self-contained: no external servers, CDNs or API keys. Copy it into any repository or
static web server (GitHub Pages works) and open `index.html`. Every file is below 100 MB, so the
folder can be committed to a GitHub repository as it is.

## Files

| File | Content |
| --- | --- |
| `land.pmtiles` | Vector tiles: land and coastline |
| `chart.pmtiles` | Vector tiles: seamarks, lights, light sectors, hazards, fairways, navigation lines, traffic separation, excluded waters |
| `depth.pmtiles` | Vector tiles: depth areas and depth contours outside Finnish waters (EMODnet) and everywhere up to zoom 8 |
| `depth-fi.pmtiles` | Vector tiles: depth areas and depth contours in Finnish waters from zoom 9 (Traficom) |
| `style.json`, `style-dark.json` | MapLibre styles, light (S-52 day) and dark (dusk/night, for dark user interfaces); URLs relative to this folder |
| `chart-style.js` | Helpers: load a style with absolute URLs, add the chart layers to your own map, switch light/dark in place |
| `sprite*.png/json`, `fonts/` | Chart symbols (both themes in one sprite) and label fonts |
| `lib/` | MapLibre GL JS and PMTiles, for the demo pages |
| `sources.json` | Sources, licences, attribution texts, fetch times and feature counts of this build |
| `index.html` | Demo: the chart as a full map, theme follows the system setting (button to override) |
| `overlay.html` | Demo: chart layers on top of another map, with a light/dark switch and layer toggles |

## Use in your own map

The chart as the whole map, following the system light/dark setting:

```html
<link rel="stylesheet" href="baltic/lib/maplibre-gl.css">
<script src="baltic/lib/pmtiles.js"></script>
<script type="module">
  import * as maplibregl from './baltic/lib/maplibre-gl.mjs';
  import { balticStyle, followColorScheme, usePmtiles } from './baltic/chart-style.js';
  usePmtiles(maplibregl, window.pmtiles);
  const map = new maplibregl.Map({ container: 'map', style: await balticStyle({ theme: 'auto' }) });
  followColorScheme(map);
</script>
```

Chart layers on top of an existing map (your own sources, layers and glyph server stay as they are):

```js
import { addBalticLayers, setBalticTheme, usePmtiles } from './baltic/chart-style.js';
usePmtiles(maplibregl, pmtiles);              // once; pmtiles from lib/pmtiles.js or the npm package
map.on('load', async () => {
  await addBalticLayers(map, {
    theme: 'dark',                             // 'light' | 'dark' | 'auto'
    beforeId: 'vessels',                       // keep your own layers on top
    skip: ['land', 'coastline'],               // if your base map already draws land
    fonts: { regular: ['Your Regular'], italic: ['Your Italic'] }   // fonts your glyph server has
  });
});
lightMapSwitch.onchange = e => setBalticTheme(map, e.target.checked ? 'light' : 'dark');
```

Layer ids of the style (for `only`, `skip` and visibility toggles): `depth-area`, `depth-area-fi`,
`depth-area-edge`, `depth-contour`, `depth-contour-fi`, `depth-label`, `depth-label-fi`, `nodata`, `tss-area`, `tss-line`, `fairway`, `fairway-edge`, `land`,
`coastline`, `navline`, `navline-track`, `navline-depth`, `leading-line`, `light-sector-limit`,
`light-sector-arc`, `sounding`, `danger-area`, `danger-area-edge`, `hazard`, `light-flare`, `seamark`, `light-label`, `seamark-name`.

The tiles are ordinary Mapbox Vector Tiles inside PMTiles archives, so they also work in
OpenLayers, Leaflet (protomaps-leaflet), QGIS and GDAL. `pmtiles extract` or `pmtiles convert`
turns them into MBTiles if your tool needs that.

## Layers

`land.pmtiles`

| Layer | Geometry | Fields |
| --- | --- | --- |
| `land` | polygon | `src` |
| `coastline` | line | `src` |

`chart.pmtiles`

| Layer | Geometry | Fields |
| --- | --- | --- |
| `nodata` | polygon | `reason`, `territory` (waters left out of the package) |
| `seamark` | point | `kind` (spar, buoy, beacon, cairn, leading_mark, light, lighthouse, daymark, racon, light_float, other), `cat` (port, starboard, north, south, east, west, isolated_danger, safe_water, special, none; IALA region A), `name`, `ref`, `lit`, `topmark`, `src` |
| `light` | point | `label` (e.g. `Fl(2)WRG 6s`), `colour` (W, R, G, Y, Bu letters), `height` (m), `range` (nm), `major`, `ref`, `src` |
| `light_sector` | line | `colour`, `part` (arc, limit), `src`; each sector is stored three times with a radius per zoom band (2000 m for zooms 11–12, 600 m for 13–14, 200 m from 15), so that the arcs stay about the same size on screen |
| `hazard` | point | `kind` (rock, wreck, obstruction), `water_level` (dry, awash, submerged; OSM values as tagged), `name`, `src` |
| `danger_area` | polygon | `kind` (rocks, shoal), `src` (Finland, MML topographic database) |
| `sounding` | point | `d` (depth, m), `src` (Finland, Traficom) |
| `fairway` | polygon | `depth` (design draught, m), `kind`, `name`, `src` |
| `navline` | line | `depth`, `bearing` (true), `kind`, `name`, `src` |
| `leading_line` | line | `bearing`, `src` (Finland only) |
| `tss` | polygon/line | `kind` (separation_zone, separation_line, …), `src` |

`depth.pmtiles` (EMODnet) and `depth-fi.pmtiles` (Traficom)

| Layer | Geometry | Fields |
| --- | --- | --- |
| `depth_area` / `depth_fi_area` | polygon | `drval1`, `drval2` (depth range, m), `src` |
| `depth_contour` / `depth_fi_contour` | line | `depth` (m), `src` |

Features may also carry `minzoom`/`maxzoom`: the zoom range in which the feature is meant to be shown
(already applied when the tiles were made). In Finnish waters EMODnet depths are shown up to zoom 8 and
Traficom depths from zoom 9.

`src` tells where a feature comes from: `fi` = Väylävirasto, `ee` = Transpordiamet (Estonia), `de` = BSH (Germany), `traficom` = Traficom, `osm` = OpenStreetMap,
`emodnet` = EMODnet Bathymetry, `mml` = Maanmittauslaitos.

A seamark with `cat` = `none` is drawn hollow: the source does not say which kind of mark it is. This is
mostly the case for numbered channel marks in the Estonian register, whose names carry only a number.

## Licences and attribution

Show the attribution texts of `style.json` (MapLibre's attribution control does it) or of
`sources.json` wherever the map is shown.

- **OpenStreetMap** data (land, coastline, seamarks and lights outside Finland, hazards, traffic
  separation): ODbL 1.0, © OpenStreetMap contributors. The tiles are a derivative database: if you
  redistribute them, keep them under ODbL.
- **Väylävirasto** (Finnish seamarks, lights, fairways, navigation lines): CC BY 4.0.
- **Transpordiamet / Maa- ja Ruumiamet** (Estonian seamarks, fairway areas and sections): Estonian open
  data licence (CC BY 4.0 equivalent).
- **BSH** (German seamarks, lights and sectors): GeoNutzV, source note "© BSH"; not for navigation.
- **Traficom** (Finnish depth areas, contours and soundings): not for navigation, non-commercial use only,
  attribution with the month of transfer.
- **Maanmittauslaitos** (Finnish rocks, rocky areas and shoals from the topographic database): CC BY 4.0.
  Present only when the build had an MML API key.
- **EMODnet Bathymetry** (depths outside Finland): open access with attribution.
- **Marine Regions** (sea areas, maritime boundaries): CC BY 4.0.
- MapLibre GL JS and PMTiles: BSD-3-Clause. Noto Sans fonts: SIL Open Font License.

Because of the Traficom terms the package as a whole is for **non-commercial use**.
