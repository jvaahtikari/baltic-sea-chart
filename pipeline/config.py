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

# Estonian Transport Administration aids to navigation (INSPIRE WFS by Maa- ja Ruumiamet)
EE_WFS = "https://inspire.geoportaal.ee/geoserver/TN_veetransport/wfs"
EE_TERRITORY = "Estonia"

# German Federal Maritime and Hydrographic Agency (BSH): navigation marks per S-57 (WFS, GeoNutzV)
DE_WFS = "https://gdi.bsh.de/mapservice_gs/Seezeichen/wfs"
DE_TERRITORY = "Germany"

# Finnish authorities
VAYLA_WFS = "https://avoinapi.vaylapilvi.fi/vaylatiedot/ows"
TRAFICOM_WFS = "https://julkinen.traficom.fi/inspirepalvelu/rajoitettu/wfs"

# OpenStreetMap seamarks are fetched per region, each from the first source that answers:
# the openstreetmap.fr extract, the Geofabrik extract, or the Overpass API for the region's box.
# A region that fails everywhere keeps its seamarks from the last successful run (workflow cache).
OVERPASS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
OSMFR = "https://download.openstreetmap.fr/extracts/"
GEOFABRIK = "https://download.geofabrik.de/"
# name, openstreetmap.fr path, Geofabrik path, Overpass box (lon/lat)
OSM_REGIONS = [
    ("finland", "europe/finland", "europe/finland", (19.0, 59.5, 30.6, 66.2)),
    ("sweden", "europe/sweden", "europe/sweden", (10.5, 55.2, 24.2, 66.2)),
    ("denmark", "europe/denmark", "europe/denmark", (8.5, 54.5, 15.3, 57.9)),
    ("estonia", None, "europe/estonia", (21.5, 57.5, 28.3, 59.9)),
    ("latvia", None, "europe/latvia", (20.8, 55.6, 24.6, 58.1)),
    ("lithuania", None, "europe/lithuania", (20.8, 55.2, 21.4, 56.1)),
    ("germany-mv", None, "europe/germany/mecklenburg-vorpommern", (10.5, 53.8, 14.5, 54.8)),
    ("germany-sh", None, "europe/germany/schleswig-holstein", (9.5, 53.9, 11.4, 55.1)),
    ("poland-pomorskie", "europe/poland/pomorskie", "europe/poland/pomorskie", (16.6, 54.2, 19.7, 54.9)),
    ("poland-zachodniopomorskie", "europe/poland/zachodniopomorskie", "europe/poland/zachodniopomorskie",
     (14.1, 53.4, 16.8, 54.6)),
    ("poland-warminsko-mazurskie", "europe/poland/warminsko_mazurskie", "europe/poland/warminsko-mazurskie",
     (19.2, 54.2, 19.9, 54.5)),
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
