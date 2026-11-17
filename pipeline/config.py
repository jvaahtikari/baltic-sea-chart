"""Shared settings for the Baltic Sea chart pipeline.

Every source is fetched from its live service on each run (see fetch.py), so the package is
always as current as the sources themselves. Nothing here is a hand-made data file.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORK = Path(os.environ.get("BSC_WORK", ROOT / "work"))   # downloads and intermediate files (not committed)
RAW = WORK / "raw"
MID = WORK / "mid"            # processed GeoJSONSeq per layer
DIST = Path(os.environ.get("BSC_DIST", ROOT / "dist"))   # the publishable package (copy this folder anywhere)

# Area of interest: Baltic Sea in the IHO sense (incl. Gulf of Bothnia, Gulf of Finland,
# Gulf of Riga, Danish straits) plus the Kattegat. Russian waters are removed.
BBOX = (8.5, 53.3, 30.6, 66.2)          # lon/lat envelope used for downloads and land clipping
IHO_MRGIDS = [2401, 2402, 2407, 2409, 2374]  # Baltic Sea, Gulf of Bothnia, Gulf of Finland, Gulf of Riga, Kattegat
AOI_BUFFER_DEG = 0.12                    # IHO polygons follow a coarse coastline; widen them into archipelagos
EXCLUDED_TERRITORY = "Russia"
FI_TERRITORY = "Finland"

# Marine Regions (VLIZ) WFS, CC BY 4.0
MR_WFS = "https://geo.vliz.be/geoserver/MarineRegions/wfs"

# EMODnet Bathymetry DTM via WCS (mean depth, 1/16 arc minute grid)
EMODNET_WCS = "https://ows.emodnet-bathymetry.eu/wcs"
EMODNET_COVERAGE = "emodnet__mean"
EMODNET_CHUNK_DEG = 2.0

# Finnish authorities
VAYLA_WFS = "https://avoinapi.vaylapilvi.fi/vaylatiedot/ows"
TRAFICOM_WFS = "https://julkinen.traficom.fi/inspirepalvelu/rajoitettu/wfs"

# OpenStreetMap. Seamarks come from the Overpass API (only the seamark objects, a few tens of MB);
# the Geofabrik extracts are the fallback if every Overpass server fails.
OVERPASS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
GEOFABRIK = "https://download.geofabrik.de/europe/"
OSM_REGIONS = [
    "finland", "sweden", "denmark", "estonia", "latvia", "lithuania",
    "germany/mecklenburg-vorpommern", "germany/schleswig-holstein",
    "poland/pomorskie", "poland/zachodniopomorskie", "poland/warminsko-mazurskie",
]
OSMDATA = "https://osmdata.openstreetmap.de/download/"

# Depth bands (metres). Areas are [d_i, d_i+1); the last band is open-ended.
DEPTH_LEVELS = [0, 3, 6, 10, 15, 20, 30, 50, 100, 200]

# Points closer than this to the coastline are kept even when they lie on land
# (lighthouses, beacons and leading marks stand on shore).
SHORE_KEEP_M = 600

# Size limit for any single file in the package: GitHub refuses files over 100 MB.
MAX_FILE_MB = 95

USER_AGENT = "baltic-sea-chart (+https://github.com/jvaahtikari/baltic-sea-chart)"
