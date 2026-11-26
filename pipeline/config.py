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

# ---------------------------------------------------------------------------------------------
# Regions. One build makes one region's package; BSC_REGION selects it (default: baltic).
# Each region has a lon/lat envelope, the IHO sea areas that make its area of interest (by Marine
# Regions id or name; None = the whole envelope), the territory whose waters are left out, the
# national authority sources to use, and the OpenStreetMap extracts to read seamarks from
# (name, openstreetmap.fr path, Geofabrik path, Overpass box).
OSM_BALTIC = [
    ("finland", "europe/finland", "europe/finland", (19.0, 59.5, 30.6, 66.2)),
    ("sweden", "europe/sweden", "europe/sweden", (10.5, 55.2, 24.2, 66.2)),
    ("denmark", "europe/denmark", "europe/denmark", (8.5, 54.5, 15.3, 57.9)),
    ("estonia", "europe/estonia", "europe/estonia", (21.5, 57.5, 28.3, 59.9)),
    ("latvia", "europe/latvia", "europe/latvia", (20.8, 55.6, 24.6, 58.1)),
    ("lithuania", "europe/lithuania", "europe/lithuania", (20.8, 55.2, 21.4, 56.1)),
    ("germany-mv", None, "europe/germany/mecklenburg-vorpommern", (10.5, 53.8, 14.5, 54.8)),
    ("germany-sh", None, "europe/germany/schleswig-holstein", (9.5, 53.9, 11.4, 55.1)),
    ("poland-pomorskie", "europe/poland/pomorskie", "europe/poland/pomorskie", (16.6, 54.2, 19.7, 54.9)),
    ("poland-zachodniopomorskie", "europe/poland/zachodniopomorskie", "europe/poland/zachodniopomorskie",
     (14.1, 53.4, 16.8, 54.6)),
    ("poland-warminsko-mazurskie", "europe/poland/warminsko_mazurskie", "europe/poland/warminsko-mazurskie",
     (19.2, 54.2, 19.9, 54.5)),
]
REGIONS = {
    "baltic": {
        "title": "Baltic Sea",
        "bbox": (8.5, 53.3, 30.6, 66.2),
        "iho_mrgids": [2401, 2402, 2407, 2409, 2374],  # Baltic Sea, Gulf of Bothnia, Gulf of Finland, Gulf of Riga, Kattegat
        "iho_names": None,
        "excluded": "Russia",
        "national": ["fi", "ee", "de"],
        "osm": OSM_BALTIC,
    },
    "norway": {
        "title": "Norway",
        "bbox": (3.5, 57.4, 32.5, 71.5),
        "iho_mrgids": None,
        "iho_names": ["Norwegian Sea", "Skagerrak", "North Sea", "Barents Sea"],
        "excluded": "Russia",
        "national": ["no"],
        "osm": [("norway", "europe/norway", "europe/norway", (3.5, 57.4, 32.5, 71.5))],
    },
    # A small test area (Bergen): the whole pipeline in minutes, for checking sources and symbols
    "probe-norway": {
        "title": "Probe: Bergen",
        "bbox": (4.6, 59.8, 5.9, 60.6),
        "iho_mrgids": None,
        "iho_names": None,
        "excluded": None,
        "national": ["no"],
        # the Norway extract, not Overpass: the public Overpass servers answer 502 for minutes at a time
        "osm": [("norway", "europe/norway", "europe/norway", (4.6, 59.8, 5.9, 60.6))],
    },
}
REGION = os.environ.get("BSC_REGION", "baltic").strip() or "baltic"
R = REGIONS[REGION]
BBOX = R["bbox"]                         # lon/lat envelope used for downloads and land clipping
IHO_MRGIDS = R["iho_mrgids"]
IHO_NAMES = R["iho_names"]
AOI_BUFFER_DEG = 0.12                    # IHO polygons follow a coarse coastline; widen them into archipelagos
EXCLUDED_TERRITORY = R["excluded"]
NATIONAL = R["national"]                 # authority sources: fi (Traficom, Väylävirasto), ee, de, no
OSM_REGIONS = R["osm"]
TERRITORIES = {"fi": "Finland", "ee": "Estonia", "de": "Germany", "no": "Norway"}   # Marine Regions names
FI_TERRITORY, EE_TERRITORY, DE_TERRITORY, NO_TERRITORY = "Finland", "Estonia", "Germany", "Norway"

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

# Norway: Kartverket depth data (WFS 2.0, GML only, no paging; CC BY 4.0) and the Norwegian Coastal
# Administration's aids to navigation (ArcGIS WFS, GeoJSON, paging; NLOD 2.0)
# The depth data comes as one FGDB download from Geonorge (the WFS serves GML only, without paging, and a
# 1 x 0.5 degree window is already hundreds of MB); the Atom feed lists the national and county files.
NO_DEPTH_ATOM = "https://nedlasting.geonorge.no/geonorge/ATOM-feeds/Dybdedata_AtomFeedFGDB.xml"
NO_DEPTH_ZIP = {
    "norway": "https://nedlasting.geonorge.no/geonorge/Basisdata/Dybdedata/FGDB/Basisdata_0000_Norge_4258_Dybdedata_FGDB.zip",
    "probe-norway": "https://nedlasting.geonorge.no/geonorge/Basisdata/Dybdedata/FGDB/Basisdata_46_Vestland_25832_Dybdedata_FGDB.zip",
}
NO_DEPTH_LAYERS = ["Dybdeareal", "Dybdekurve", "Dybdepunkt", "Grunne", "Skjær", "Tørrfall"]
NO_AIDS_WFS = ("https://maps.kystverket.cloudgis.no/enterprise/services/PROD/nfs_sistop_ekstern_prod/"
               "MapServer/WFSServer")
NO_AIDS_PREFIX = "nfs_sistop_ekstern_prod"
NO_AIDS_LAYERS = ["Lys", "IB", "Sektorlinje", "Sektorflate", "Racon", "Fast_sjømerke", "Flytende_merke",
                  "Overettlinje_lys", "Overettlinje_merke"]

# Finnish authorities
VAYLA_WFS = "https://avoinapi.vaylapilvi.fi/vaylatiedot/ows"
TRAFICOM_WFS = "https://julkinen.traficom.fi/inspirepalvelu/rajoitettu/wfs"

# Maanmittauslaitos topographic database (OGC API Features, CC BY 4.0): rocks, rocky areas and shoals in
# Finnish waters. Needs a free API key (https://www.maanmittauslaitos.fi/rajapinnat/api-avaimen-ohje) in the
# environment variable MML_API_KEY; without it the step is skipped and Finnish rocks come from OSM only.
MML_API = "https://avoin-paikkatieto.maanmittauslaitos.fi/maastotiedot/features/v1"
MML_API_KEY = os.environ.get("MML_API_KEY", "").strip()
MML_COLLECTIONS = ["vesikivi", "vesikivikko", "matalikko"]
MML_BBOX = (19.0, 59.6, 30.6, 66.2)      # Finnish sea areas; lakes are dropped in the build by the maritime zone
MML_CELL = (1.0, 0.5)                     # request window (degrees)

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
OSMDATA = "https://osmdata.openstreetmap.de/download/"

# Depth bands (metres). Areas are [d_i, d_i+1); the last band is open-ended.
DEPTH_LEVELS = [0, 3, 6, 10, 15, 20, 30, 50, 100, 200]

# Points closer than this to the coastline are kept even when they lie on land
# (lighthouses, beacons and leading marks stand on shore).
SHORE_KEEP_M = 600

# Size limit for any single file in the package: GitHub refuses files over 100 MB.
MAX_FILE_MB = 95

USER_AGENT = "baltic-sea-chart %s (+https://github.com/jvaahtikari/baltic-sea-chart)" % REGION
