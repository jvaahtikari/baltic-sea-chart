"""Synthetic stand-ins for the sources that are unreachable from a development sandbox
(Marine Regions, EMODnet, Geofabrik, osmdata). Used only for a quick code smoke test."""
import json, sys, shutil
from pathlib import Path
import numpy as np
from osgeo import gdal, osr

work = Path(sys.argv[1]); real = Path(sys.argv[2]) if len(sys.argv) > 2 else None
raw = work / "raw"
for d in ("regions", "emodnet", "osm", "land", "vayla", "traficom"):
    (raw / d).mkdir(parents=True, exist_ok=True)
def poly(x0, y0, x1, y1): return {"type": "Polygon", "coordinates": [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]]}
def fc(*geoms, **props): return {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": dict(props), "geometry": g} for g in geoms]}
# sea area: Gulf of Finland west part 22-27E, 59.3-60.6N ; excluded: east of 27.5
json.dump(fc(poly(21.5, 59.0, 28.5, 60.4), name="Gulf of Finland"), open(raw / "regions/iho.geojson", "w"))
json.dump(fc(poly(27.8, 59.0, 31, 61)), open(raw / "regions/excluded_eez.geojson", "w"))
json.dump(fc(poly(21.5, 59.85, 27.8, 61)), open(raw / "regions/fi_eez.geojson", "w"))
# land: Finnish coast north of 60.25 and Estonian coast south of 59.45, plus an island
lands = [poly(20, 60.25, 31, 61.5), poly(20, 58.5, 31, 59.45), poly(24.9, 60.1, 25.0, 60.15)]
with open(raw / "land/land.geojsonl", "w") as f:
    for g in lands: f.write(json.dumps({"type": "Feature", "properties": {}, "geometry": g}) + "\n")
shutil.copy(raw / "land/land.geojsonl", raw / "land/land_simplified.geojsonl")
# EMODnet: elevation grid, negative at sea, deeper toward 59.85
x0, y0, x1, y1, r = 21.0, 58.9, 29.0, 60.6, 1 / 96
W, H = int((x1 - x0) / r), int((y1 - y0) / r)
yy = y1 - (np.arange(H) + .5) * r
el = -(np.clip(1 - np.abs(yy - 59.85) / 0.45, 0, 1) * 90 + 1)[:, None] * np.ones((1, W))
ds = gdal.GetDriverByName("GTiff").Create(str(raw / "emodnet/chunk_021.000_058.900.tif"), W, H, 1, gdal.GDT_Float32)
ds.SetGeoTransform((x0, r, 0, y1, 0, -r)); s = osr.SpatialReference(); s.ImportFromEPSG(4326); ds.SetProjection(s.ExportToWkt())
ds.GetRasterBand(1).SetNoDataValue(-99999); ds.GetRasterBand(1).WriteArray(el.astype(np.float32)); ds = None
# OSM seamarks in Estonian waters
osm = [
 ({"seamark:type": "buoy_lateral", "seamark:buoy_lateral:category": "port", "seamark:light:colour": "red", "seamark:light:character": "Fl", "seamark:light:period": "3"}, [24.5, 59.5]),
 ({"seamark:type": "buoy_cardinal", "seamark:buoy_cardinal:category": "north"}, [24.6, 59.52]),
 ({"seamark:type": "light_major", "seamark:name": "Keri", "seamark:light:1:colour": "white", "seamark:light:1:sector_start": "10", "seamark:light:1:sector_end": "200", "seamark:light:1:character": "Fl", "seamark:light:1:period": "5", "seamark:light:2:colour": "red", "seamark:light:2:sector_start": "200", "seamark:light:2:sector_end": "250"}, [25.0, 59.69]),
 ({"seamark:type": "rock", "seamark:rock:water_level": "awash"}, [24.7, 59.55]),
 ({"seamark:type": "buoy_lateral", "seamark:buoy_lateral:category": "starboard"}, [29.0, 59.9]),  # Russian waters -> dropped
]
with open(raw / "osm/seamark.geojsonl", "w") as f:
    for t, c in osm: f.write(json.dumps({"type": "Feature", "properties": t, "geometry": {"type": "Point", "coordinates": c}}) + "\n")
    f.write(json.dumps({"type": "Feature", "properties": {"seamark:type": "separation_zone"}, "geometry": poly(23, 59.7, 24, 59.75)}) + "\n")
    f.write(json.dumps({"type": "Feature", "properties": {"seamark:type": "recommended_track", "seamark:recommended_track:orientation": "90"}, "geometry": {"type": "LineString", "coordinates": [[23, 59.6], [24, 59.6]]}}) + "\n")
# Finnish sources: copy the real ones if available
if real:
    for d in ("vayla", "traficom"):
        for p in (real / "raw" / d).glob("*.geojsonl"): shutil.copy(p, raw / d / p.name)
print("ok", work)
