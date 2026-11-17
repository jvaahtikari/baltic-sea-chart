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
| `chart.pmtiles` | Vector tiles: land, coastline, seamarks, lights, light sectors, hazards, fairways, navigation lines, traffic separation, excluded waters |
| `depth.pmtiles` | Vector tiles: depth areas and depth contours |
| `style.json` | MapLibre style (URLs relative to this folder) |
| `chart-style.js` | Helper that loads `style.json` with absolute URLs, or adds the layers to your own map |
| `sprite*.png/json`, `fonts/` | Chart symbols and label fonts used by the style |
| `lib/` | MapLibre GL JS and PMTiles, for the demo page |
| `sources.json` | Sources, licences, attribution texts, fetch times and feature counts of this build |
| `index.html` | Demo map |

## Use in your own map

```html
<link rel="stylesheet" href="baltic/lib/maplibre-gl.css">
<script src="baltic/lib/pmtiles.js"></script>
<script type="module">
  import * as maplibregl from './baltic/lib/maplibre-gl.mjs';
  import { balticStyle, addBalticLayers, usePmtiles } from './baltic/chart-style.js';
  usePmtiles(maplibregl, window.pmtiles);
  // whole chart as the map style
  const map = new maplibregl.Map({ container: 'map', style: await balticStyle() });
  // or: chart layers on top of your own base map
  // map.on('load', () => addBalticLayers(map, { only: ['depth-area', 'depth-contour', 'seamark', 'light-flare'] }));
</script>
```

The tiles are ordinary Mapbox Vector Tiles inside PMTiles archives, so they also work in
OpenLayers, Leaflet (protomaps-leaflet), QGIS and GDAL. `pmtiles extract` or `pmtiles convert`
turns them into MBTiles if your tool needs that.

## Layers

`chart.pmtiles`

| Layer | Geometry | Fields |
| --- | --- | --- |
| `land` | polygon | `src` |
| `coastline` | line | `src` |
| `nodata` | polygon | `reason`, `territory` (waters left out of the package) |
| `seamark` | point | `kind` (spar, buoy, beacon, cairn, leading_mark, light, lighthouse, daymark, racon, light_float, other), `cat` (port, starboard, north, south, east, west, isolated_danger, safe_water, special, none; IALA region A), `name`, `ref`, `lit`, `topmark`, `src` |
| `light` | point | `label` (e.g. `Fl(2)WRG 6s`), `colour` (W, R, G, Y, Bu letters), `height` (m), `range` (nm), `major`, `ref`, `src` |
| `light_sector` | line | `colour`, `part` (arc, limit), `src`; arcs are drawn at a fixed 450 m radius |
| `hazard` | point | `kind` (rock, wreck, obstruction), `water_level`, `name`, `src` |
| `fairway` | polygon | `depth` (design draught, m), `kind`, `name`, `src` |
| `navline` | line | `depth`, `bearing` (true), `kind`, `name`, `src` |
| `leading_line` | line | `bearing`, `src` (Finland only) |
| `tss` | polygon/line | `kind` (separation_zone, separation_line, …), `src` |

`depth.pmtiles`

| Layer | Geometry | Fields |
| --- | --- | --- |
| `depth_area` | polygon | `drval1`, `drval2` (depth range, m), `src` (traficom, emodnet) |
| `depth_contour` | line | `depth` (m), `src` |

`src` tells where a feature comes from: `fi` = Väylävirasto, `traficom` = Traficom, `osm` = OpenStreetMap,
`emodnet` = EMODnet Bathymetry.

## Licences and attribution

Show the attribution texts of `style.json` (MapLibre's attribution control does it) or of
`sources.json` wherever the map is shown.

- **OpenStreetMap** data (land, coastline, seamarks and lights outside Finland, hazards, traffic
  separation): ODbL 1.0, © OpenStreetMap contributors. The tiles are a derivative database: if you
  redistribute them, keep them under ODbL.
- **Väylävirasto** (Finnish seamarks, lights, fairways, navigation lines): CC BY 4.0.
- **Traficom** (Finnish depth areas and contours): not for navigation, non-commercial use only,
  attribution with the month of transfer.
- **EMODnet Bathymetry** (depths outside Finland): open access with attribution.
- **Marine Regions** (sea areas, maritime boundaries): CC BY 4.0.
- MapLibre GL JS and PMTiles: BSD-3-Clause. Noto Sans fonts: SIL Open Font License.

Because of the Traficom terms the package as a whole is for **non-commercial use**.
