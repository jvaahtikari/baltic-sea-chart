# Build summary

Result: **OK**

## Warnings

- OSM seamarks for estonia are from an earlier run (2026-11-26T22:10:10Z)
- OSM seamarks for latvia are from an earlier run (2026-11-26T22:11:07Z)
- OSM seamarks for germany-mv are from an earlier run (2026-11-26T22:11:31Z)
- known major lights missing from the light layer: Bengtskär (FI)

## OSM seamarks per region

| Region | Source | Features |
| --- | --- | ---: |
| finland | openstreetmap.fr | 87039 |
| sweden | openstreetmap.fr | 24095 |
| denmark | openstreetmap.fr | 15605 |
| poland-pomorskie | openstreetmap.fr | 1789 |
| poland-zachodniopomorskie | openstreetmap.fr | 2652 |
| poland-warminsko-mazurskie | openstreetmap.fr | 1916 |
| estonia | previous run (geofabrik) | 1529 |
| latvia | previous run (geofabrik) | 746 |
| lithuania | overpass | 261 |
| germany-mv | previous run (geofabrik) | 13459 |
| germany-sh | overpass | 10515 |

## Features per layer

| Layer | Features |
| --- | ---: |
| nodata | 1 |
| land | 208814 |
| coastline | 198346 |
| danger_area_depth | 0 |
| depth_nat_area | 106808 |
| depth_nat_contour | 135143 |
| sounding | 172518 |
| depth_area | 365 |
| depth_contour | 215409 |
| seamark | 32904 |
| light | 10864 |
| light_sector | 78795 |
| hazard | 27738 |
| danger_area | 0 |
| fairway | 2788 |
| navline | 8335 |
| leading_line | 1425 |
| tss | 266 |

## Package files (MB)

| File | MB |
| --- | ---: |
| README.md | 0.01 |
| chart-style.js | 0.01 |
| chart.pmtiles | 59.26 |
| coastline.pmtiles | 49.09 |
| depth-national.pmtiles | 56.93 |
| depth.pmtiles | 74.01 |
| index.html | 0.01 |
| land.pmtiles | 47.59 |
| lib/LICENSE-maplibre-gl.txt | 0.01 |
| lib/maplibre-gl-worker.mjs | 0.55 |
| lib/maplibre-gl.css | 0.07 |
| lib/maplibre-gl.mjs | 1.11 |
| lib/pmtiles.js | 0.02 |
| overlay.html | 0.0 |
| sources.json | 0.01 |
| sprite.json | 0.01 |
| sprite.png | 0.01 |
| sprite@2x.json | 0.01 |
| sprite@2x.png | 0.03 |
| style-dark.json | 0.01 |
| style.json | 0.01 |

## Build details

```json
{
 "zooms": {
  "nodata": {
   "min": [],
   "max": []
  },
  "land": {
   "min": [
    8
   ],
   "max": [
    7
   ]
  },
  "coastline": {
   "min": [
    6
   ],
   "max": []
  },
  "danger_area_depth": {
   "min": [],
   "max": []
  },
  "depth_nat_area": {
   "min": [
    9
   ],
   "max": []
  },
  "depth_nat_contour": {
   "min": [
    11
   ],
   "max": []
  },
  "sounding": {
   "min": [
    12,
    13
   ],
   "max": []
  },
  "depth_area": {
   "min": [
    3,
    5,
    9
   ],
   "max": [
    8
   ]
  },
  "depth_contour": {
   "min": [
    5,
    7,
    9,
    10
   ],
   "max": [
    8
   ]
  },
  "seamark": {
   "min": [
    8,
    9,
    10,
    11
   ],
   "max": []
  },
  "light": {
   "min": [
    8,
    10
   ],
   "max": []
  },
  "light_sector": {
   "min": [
    11,
    12,
    13,
    15
   ],
   "max": [
    12,
    14
   ]
  },
  "hazard": {
   "min": [
    12,
    13
   ],
   "max": []
  },
  "danger_area": {
   "min": [],
   "max": []
  },
  "fairway": {
   "min": [
    9
   ],
   "max": []
  },
  "navline": {
   "min": [
    10
   ],
   "max": []
  },
  "leading_line": {
   "min": [
    10
   ],
   "max": []
  },
  "tss": {
   "min": [
    6
   ],
   "max": []
  }
 },
 "areas_km2": {
  "aoi": 521460,
  "excluded": 24869,
  "fi_zone": 86580,
  "ee_zone": 37305,
  "de_zone": 16636,
  "no_zone": 0,
  "nat_zone": 86580,
  "iho": 417107
 },
 "seconds": {
  "areas": 15,
  "land": 68,
  "depth": 359,
  "marks": 914,
  "routes": 3,
  "tiles": 341
 },
 "traficom_depth_areas_used": 106808,
 "kartverket_depth_areas_used": 0,
 "emodnet": {
  "grid": [
   21216,
   12384
  ],
  "sign": -1.0,
  "median_raw": -27.059999465942383,
  "fi_masked_cells": 8433542,
  "aoi_cells": 74839140
 },
 "estonia_marks": 1104,
 "estonia_category_from_osm": 17,
 "germany_marks": 3081,
 "germany_lights": 1985,
 "mml_features": 0,
 "kartverket_rocks": 0,
 "marks_dropped": {
  "outside": 51293,
  "inland": 3188
 },
 "kystverket_leading_lines": 0,
 "tiles_mb": {
  "land.pmtiles": 47.6,
  "coastline.pmtiles": 49.1,
  "chart.pmtiles": 59.3,
  "depth.pmtiles": 74.0,
  "depth-national.pmtiles": 56.9
 },
 "tiles_settings": {
  "land.pmtiles": {
   "maxzoom": 13,
   "simplification": 2,
   "layers": [
    "land"
   ]
  },
  "coastline.pmtiles": {
   "maxzoom": 13,
   "simplification": 2,
   "layers": [
    "coastline"
   ]
  },
  "chart.pmtiles": {
   "maxzoom": 15,
   "simplification": 2,
   "layers": [
    "nodata",
    "seamark",
    "light",
    "light_sector",
    "hazard",
    "danger_area",
    "danger_area_depth",
    "sounding",
    "fairway",
    "navline",
    "leading_line",
    "tss"
   ]
  },
  "depth.pmtiles": {
   "maxzoom": 12,
   "simplification": 4,
   "layers": [
    "depth_area",
    "depth_contour"
   ]
  },
  "depth-national.pmtiles": {
   "maxzoom": 12,
   "simplification": 4,
   "layers": [
    "depth_nat_area",
    "depth_nat_contour"
   ]
  }
 }
}
```

## Screenshots

| Place | ms | rendered features |
| --- | ---: | --- |
| overview | 590 | {"depth-area": 55, "depth-area-nat": 0, "depth-contour": 0, "land": 4235, "seamark": 0, "light-flare": 0, "light-sector-arc": 0, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 3} |
| gulf_of_finland_east | 2241 | {"depth-area": 32, "depth-area-nat": 0, "depth-contour": 283, "land": 1061, "seamark": 5, "light-flare": 200, "light-sector-arc": 0, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 5} |
| helsinki | 3789 | {"depth-area": 14, "depth-area-nat": 336, "depth-contour": 45, "land": 527, "seamark": 453, "light-flare": 113, "light-sector-arc": 125, "navline": 336, "fairway": 160, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| helsinki_detail | 2153 | {"depth-area": 0, "depth-area-nat": 16, "depth-contour": 0, "land": 5, "seamark": 8, "light-flare": 4, "light-sector-arc": 9, "navline": 26, "fairway": 23, "hazard": 6, "sounding": 19, "danger-area": 0, "nodata": 0} |
| turku_archipelago | 6113 | {"depth-area": 29, "depth-area-nat": 4596, "depth-contour": 1008, "land": 1967, "seamark": 31, "light-flare": 166, "light-sector-arc": 0, "navline": 422, "fairway": 202, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| aland | 4197 | {"depth-area": 22, "depth-area-nat": 1707, "depth-contour": 306, "land": 1281, "seamark": 20, "light-flare": 65, "light-sector-arc": 0, "navline": 204, "fairway": 100, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| stockholm | 4087 | {"depth-area": 49, "depth-area-nat": 0, "depth-contour": 4954, "land": 2727, "seamark": 68, "light-flare": 93, "light-sector-arc": 0, "navline": 10, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| tallinn | 1668 | {"depth-area": 29, "depth-area-nat": 0, "depth-contour": 81, "land": 12, "seamark": 75, "light-flare": 57, "light-sector-arc": 15, "navline": 20, "fairway": 2, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| riga | 1423 | {"depth-area": 34, "depth-area-nat": 0, "depth-contour": 22, "land": 8, "seamark": 3, "light-flare": 7, "light-sector-arc": 0, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| klaipeda | 1475 | {"depth-area": 35, "depth-area-nat": 0, "depth-contour": 114, "land": 7, "seamark": 25, "light-flare": 58, "light-sector-arc": 0, "navline": 6, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| gdansk | 1969 | {"depth-area": 41, "depth-area-nat": 0, "depth-contour": 520, "land": 14, "seamark": 50, "light-flare": 108, "light-sector-arc": 0, "navline": 6, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| kiel | 1623 | {"depth-area": 18, "depth-area-nat": 0, "depth-contour": 248, "land": 4, "seamark": 34, "light-flare": 233, "light-sector-arc": 0, "navline": 2, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| kiel_detail | 1615 | {"depth-area": 15, "depth-area-nat": 0, "depth-contour": 42, "land": 4, "seamark": 71, "light-flare": 83, "light-sector-arc": 57, "navline": 1, "fairway": 0, "hazard": 12, "sounding": 0, "danger-area": 0, "nodata": 0} |
| rostock | 1360 | {"depth-area": 32, "depth-area-nat": 0, "depth-contour": 86, "land": 7, "seamark": 69, "light-flare": 67, "light-sector-arc": 9, "navline": 7, "fairway": 0, "hazard": 8, "sounding": 0, "danger-area": 0, "nodata": 0} |
| riga_port | 1698 | {"depth-area": 28, "depth-area-nat": 0, "depth-contour": 39, "land": 5, "seamark": 30, "light-flare": 28, "light-sector-arc": 1, "navline": 12, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| parnu | 1402 | {"depth-area": 11, "depth-area-nat": 0, "depth-contour": 42, "land": 23, "seamark": 18, "light-flare": 5, "light-sector-arc": 1, "navline": 3, "fairway": 1, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| muuga | 1510 | {"depth-area": 27, "depth-area-nat": 0, "depth-contour": 32, "land": 6, "seamark": 17, "light-flare": 15, "light-sector-arc": 3, "navline": 7, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| copenhagen | 1614 | {"depth-area": 28, "depth-area-nat": 0, "depth-contour": 118, "land": 67, "seamark": 214, "light-flare": 106, "light-sector-arc": 51, "navline": 3, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| kattegat | 2132 | {"depth-area": 52, "depth-area-nat": 0, "depth-contour": 296, "land": 472, "seamark": 9, "light-flare": 25, "light-sector-arc": 0, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| oulu | 2458 | {"depth-area": 5, "depth-area-nat": 444, "depth-contour": 0, "land": 160, "seamark": 8, "light-flare": 91, "light-sector-arc": 0, "navline": 107, "fairway": 60, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| overview_dark | 1905 | {"depth-area": 55, "depth-area-nat": 0, "depth-contour": 0, "land": 4235, "seamark": 0, "light-flare": 0, "light-sector-arc": 0, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 3} |
| helsinki_dark | 2933 | {"depth-area": 14, "depth-area-nat": 336, "depth-contour": 45, "land": 527, "seamark": 453, "light-flare": 113, "light-sector-arc": 125, "navline": 336, "fairway": 160, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| stockholm_dark | 4157 | {"depth-area": 49, "depth-area-nat": 0, "depth-contour": 4954, "land": 2727, "seamark": 68, "light-flare": 93, "light-sector-arc": 0, "navline": 10, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| gdansk_dark | 1852 | {"depth-area": 41, "depth-area-nat": 0, "depth-contour": 520, "land": 14, "seamark": 50, "light-flare": 108, "light-sector-arc": 0, "navline": 6, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| overlay_dark | 2602 | {"depth-area": 54, "depth-area-nat": 0, "depth-contour": 5416, "land": 3300, "seamark": 0, "light-flare": 0, "light-sector-arc": 0, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| overlay_dark_z11 | 4033 | {"depth-area": 24, "depth-area-nat": 1286, "depth-contour": 202, "land": 1301, "seamark": 130, "light-flare": 41, "light-sector-arc": 48, "navline": 94, "fairway": 48, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
