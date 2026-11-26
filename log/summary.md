# Build summary

Result: **OK**

## OSM seamarks per region

| Region | Source | Features |
| --- | --- | ---: |
| norway | openstreetmap.fr | 139887 |

## Features per layer

| Layer | Features |
| --- | ---: |
| nodata | 0 |
| land | 6486 |
| coastline | 5326 |
| danger_area_depth | 13783 |
| depth_nat_area | 21729 |
| depth_nat_contour | 34440 |
| sounding | 155101 |
| depth_area | 20 |
| depth_contour | 11017 |
| seamark | 1281 |
| light | 437 |
| light_sector | 6327 |
| hazard | 1181 |
| danger_area | 0 |
| fairway | 0 |
| navline | 2 |
| leading_line | 4 |
| tss | 2 |

## Package files (MB)

| File | MB |
| --- | ---: |
| README.md | 0.01 |
| chart-style.js | 0.01 |
| chart.pmtiles | 12.52 |
| coastline.pmtiles | 1.83 |
| depth-national.pmtiles | 8.63 |
| depth.pmtiles | 2.17 |
| index.html | 0.01 |
| land.pmtiles | 1.88 |
| lib/LICENSE-maplibre-gl.txt | 0.01 |
| lib/maplibre-gl-worker.mjs | 0.55 |
| lib/maplibre-gl.css | 0.07 |
| lib/maplibre-gl.mjs | 1.11 |
| lib/pmtiles.js | 0.02 |
| overlay.html | 0.0 |
| sources.json | 0.0 |
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
   "min": [
    11
   ],
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
   "min": [],
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
  "aoi": 6427,
  "excluded": 0,
  "fi_zone": 0,
  "ee_zone": 0,
  "de_zone": 0,
  "no_zone": 4009,
  "nat_zone": 4009,
  "iho": 6427
 },
 "seconds": {
  "areas": 1,
  "land": 2,
  "depth": 61,
  "marks": 7,
  "routes": 0,
  "tiles": 71
 },
 "traficom_depth_areas_used": 0,
 "kartverket_depth_areas_used": 21729,
 "emodnet": {
  "grid": [
   1248,
   768
  ],
  "sign": -1.0,
  "median_raw": -0.8889389038085938,
  "fi_masked_cells": 518676,
  "aoi_cells": 958464
 },
 "estonia_marks": 0,
 "estonia_category_from_osm": 0,
 "germany_marks": 0,
 "germany_lights": 0,
 "norway_marks": {
  "light": 436,
  "mark": 800,
  "sector": 705,
  "skipped": 21952,
  "sector_unplaced": 4
 },
 "mml_features": 0,
 "kartverket_rocks": 0,
 "marks_dropped": {
  "outside": 119982,
  "inland": 0
 },
 "kystverket_leading_lines": 4,
 "tiles_mb": {
  "land.pmtiles": 1.9,
  "coastline.pmtiles": 1.8,
  "chart.pmtiles": 12.5,
  "depth.pmtiles": 2.2,
  "depth-national.pmtiles": 8.6
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
| overview | 912 | {"depth-area": 46, "depth-area-nat": 10573, "depth-contour": 2483, "land": 2698, "seamark": 1, "light-flare": 1, "light-sector-arc": 0, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| bergen | 8343 | {"depth-area": 66, "depth-area-nat": 4262, "depth-contour": 1884, "land": 1210, "seamark": 46, "light-flare": 94, "light-sector-arc": 0, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| bergen_detail | 1917 | {"depth-area": 35, "depth-area-nat": 456, "depth-contour": 70, "land": 6, "seamark": 7, "light-flare": 2, "light-sector-arc": 0, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 141, "danger-area": 0, "nodata": 0} |
| bergen_port | 1989 | {"depth-area": 8, "depth-area-nat": 244, "depth-contour": 10, "land": 2, "seamark": 2, "light-flare": 1, "light-sector-arc": 0, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 225, "danger-area": 0, "nodata": 0} |
| marstein | 1833 | {"depth-area": 13, "depth-area-nat": 261, "depth-contour": 40, "land": 43, "seamark": 8, "light-flare": 4, "light-sector-arc": 31, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 3, "danger-area": 0, "nodata": 0} |
| askoy | 4007 | {"depth-area": 31, "depth-area-nat": 689, "depth-contour": 268, "land": 132, "seamark": 40, "light-flare": 11, "light-sector-arc": 17, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 29, "danger-area": 0, "nodata": 0} |
| sotra | 3749 | {"depth-area": 38, "depth-area-nat": 958, "depth-contour": 306, "land": 442, "seamark": 52, "light-flare": 4, "light-sector-arc": 30, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| overview_dark | 7342 | {"depth-area": 46, "depth-area-nat": 10573, "depth-contour": 2483, "land": 2698, "seamark": 1, "light-flare": 1, "light-sector-arc": 0, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| bergen_dark | 6182 | {"depth-area": 66, "depth-area-nat": 4262, "depth-contour": 1884, "land": 1210, "seamark": 46, "light-flare": 94, "light-sector-arc": 0, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 0, "danger-area": 0, "nodata": 0} |
| bergen_detail_dark | 1909 | {"depth-area": 35, "depth-area-nat": 456, "depth-contour": 70, "land": 6, "seamark": 7, "light-flare": 2, "light-sector-arc": 0, "navline": 0, "fairway": 0, "hazard": 0, "sounding": 141, "danger-area": 0, "nodata": 0} |
