"""Everything in the package besides the tiles: style, symbols, fonts, map libraries, demo page,
source list and licences. Run: python3 -m pipeline.assets
"""
import json
import shutil
import subprocess
import urllib.parse
from datetime import datetime, timezone

from . import config as C
from .fetch import http_get
from .style import style

FONTS = ["Noto Sans Regular", "Noto Sans Italic"]
# Latin-1, Latin Extended-A (Baltic and Nordic letters), general punctuation
GLYPH_RANGES = ["0-255", "256-511", "8192-8447"]
FONT_BASE = "https://raw.githubusercontent.com/protomaps/basemaps-assets/main/fonts/"

SOURCES = [
    {"id": "osm", "name": "OpenStreetMap (OpenSeaMap seamark tagging) and OSM land polygons",
     "provider": "OpenStreetMap contributors; land polygons by osmdata.openstreetmap.de",
     "licence": "ODbL 1.0", "licence_url": "https://opendatacommons.org/licenses/odbl/1-0/",
     "attribution": "© OpenStreetMap contributors",
     "layers": ["land", "coastline", "seamark (outside Finland)", "light (outside Finland)", "light_sector (outside Finland)",
                "hazard", "fairway/navline (outside Finland)", "tss"], "step": "osm"},
    {"id": "vayla", "name": "Väylävirasto, vesiväyläaineisto (WFS)", "provider": "Finnish Transport Infrastructure Agency",
     "licence": "CC BY 4.0", "licence_url": "https://creativecommons.org/licenses/by/4.0/",
     "attribution": "Väylävirasto", "layers": ["seamark (Finland)", "light (Finland)", "light_sector (Finland)",
                                              "fairway (Finland)", "navline (Finland)", "leading_line"], "step": "vayla"},
    {"id": "estonia", "name": "Transpordiamet, Eesti navigatsioonimärkide andmekogu (INSPIRE WFS, Maa- ja Ruumiamet)",
     "provider": "Estonian Transport Administration", "licence": "Estonian open data licence (CC BY 4.0 equivalent)",
     "licence_url": "https://geoportaal.maaamet.ee/avaandmete-litsents",
     "attribution": "Transpordiamet / Maa- ja Ruumiamet",
     "layers": ["seamark (Estonia)", "fairway (Estonia)", "navline (Estonia)"], "step": "estonia"},
    {"id": "germany", "name": "BSH, Navigation marks according to S-57 (WFS)",
     "provider": "Bundesamt für Seeschifffahrt und Hydrographie (BSH)",
     "licence": "GeoNutzV (Nutzungsbestimmungen für die Bereitstellung von Geodaten des Bundes); not for navigation",
     "licence_url": "http://www.gesetze-im-internet.de/geonutzv/GeoNutzV.pdf",
     "attribution": "Quelle: © BSH", "layers": ["seamark (Germany)", "light (Germany)", "light_sector (Germany)"],
     "step": "germany"},
    {"id": "traficom", "name": "Traficom, merikarttatietokanta (INSPIRE WFS, rajoitettu)",
     "provider": "Finnish Transport and Communications Agency Traficom",
     "licence": "Traficom hydrographic data licence: not for navigation, non-commercial use only",
     "licence_url": "https://www.traficom.fi/fi/liikenne/merenkulku/merikarttojen-aineistot",
     "attribution": "Sisältää Liikenne- ja viestintäviraston merikarttatietokannan tietoa {month}. Ei navigointikäyttöön. Ei täytä asianmukaisen merikartan vaatimuksia.",
     "layers": ["depth_area (Finland)", "depth_contour (Finland)", "sounding (Finland)"], "step": "traficom"},
    {"id": "mml", "name": "Maanmittauslaitos, maastotietokanta (OGC API Features)", "provider": "National Land Survey of Finland",
     "licence": "CC BY 4.0", "licence_url": "https://creativecommons.org/licenses/by/4.0/",
     "attribution": "Maanmittauslaitos", "layers": ["hazard (rocks, Finland)", "danger_area (Finland)"], "step": "mml"},
    {"id": "kartverket", "name": "Kartverket, Sjøkart - Dybdedata (WFS)", "provider": "Norwegian Mapping Authority",
     "licence": "CC BY 4.0", "licence_url": "https://creativecommons.org/licenses/by/4.0/",
     "attribution": "© Kartverket (Sjøkart - Dybdedata). Ikke godkjent for navigasjon.",
     "layers": ["depth_area (Norway)", "depth_contour (Norway)", "sounding (Norway)", "hazard (rocks, Norway)",
                "danger_area_depth (Norway)"], "step": "norway"},
    {"id": "kystverket", "name": "Kystverket, navigasjonsinstallasjoner (WFS)", "provider": "Norwegian Coastal Administration",
     "licence": "NLOD 2.0", "licence_url": "https://data.norge.no/nlod/no/2.0",
     "attribution": "© Kystverket (navigasjonsinstallasjoner)",
     "layers": ["seamark (Norway)", "light (Norway)", "leading_line (Norway)"], "step": "norway"},
    {"id": "emodnet", "name": "EMODnet Bathymetry Digital Terrain Model (WCS, mean depth)",
     "provider": "EMODnet Bathymetry Consortium", "licence": "Open access, attribution required",
     "licence_url": "https://emodnet.ec.europa.eu/en/emodnet-data-policy",
     "attribution": "EMODnet Bathymetry Consortium: EMODnet Digital Bathymetry (DTM)",
     "layers": ["depth_area (outside Finland)", "depth_contour (outside Finland)"], "step": "emodnet"},
    {"id": "marineregions", "name": "Marine Regions: IHO sea areas and maritime boundaries (WFS)",
     "provider": "Flanders Marine Institute (VLIZ)", "licence": "CC BY 4.0",
     "licence_url": "https://creativecommons.org/licenses/by/4.0/",
     "attribution": "Marine Regions (VLIZ)", "layers": ["nodata", "area of the package"], "step": "regions"},
]


def run(cmd):
    print("$ " + " ".join(map(str, cmd)), flush=True)
    subprocess.run(list(map(str, cmd)), check=True)


def sources_with_dates():
    month = datetime.now(timezone.utc).strftime("%m/%Y")
    out = []
    for s in SOURCES:
        s = dict(s)
        s["attribution"] = s["attribution"].replace("{month}", month)
        step = s.pop("step")
        logp = C.RAW / step / "log.json"
        if not logp.exists() and not (C.RAW / step).exists():
            continue      # a source that this region does not use
        if logp.exists():
            lg = json.loads(logp.read_text(encoding="utf-8"))
            s["fetched"] = lg.get("fetched")
            s["endpoint"] = lg.get("source")
            if lg.get("missing") or lg.get("failed"):
                s["status"] = "not available in this build"
            elif lg.get("stale"):
                s["status"] = "from an earlier build (%s)" % lg.get("previous_fetch")
        out.append(s)
    return out


def main():
    D = C.DIST
    D.mkdir(parents=True, exist_ok=True)
    srcs = sources_with_dates()
    by = {s["id"]: s for s in srcs}
    attr_chart = " · ".join(by[k]["attribution"] for k in ("osm", "vayla", "estonia", "germany", "kystverket", "marineregions") if k in by)
    attr_depth = " · ".join(by[k]["attribution"] for k in ("emodnet", "traficom", "kartverket") if k in by)

    # style and source list
    for theme, fname in (("light", "style.json"), ("dark", "style-dark.json")):
        (D / fname).write_text(json.dumps(style(attr_chart, attr_depth, theme), ensure_ascii=False, indent=1), encoding="utf-8")
    build = json.loads((C.MID / "build_log.json").read_text()) if (C.MID / "build_log.json").exists() else {}
    meta = {"name": "Baltic Sea chart", "region": C.REGION, "region_title": C.R["title"], "built": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "not_for_navigation": True, "bbox": C.BBOX, "excluded_waters": C.EXCLUDED_TERRITORY,
            "sources": srcs, "features": build.get("features", {}), "tiles_mb": build.get("tiles_mb", {})}
    (D / "sources.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")

    # symbols
    run(["node", C.ROOT / "tools" / "sprite.mjs", D])

    # fonts (glyph ranges from the Protomaps basemaps-assets repository, OFL fonts)
    for font in FONTS:
        fd = D / "fonts" / font
        fd.mkdir(parents=True, exist_ok=True)
        for r in GLYPH_RANGES:
            http_get(FONT_BASE + urllib.parse.quote(font) + "/" + r + ".pbf", fd / (r + ".pbf"))

    # map libraries (pinned in package.json, copied from node_modules)
    nm = C.ROOT / "node_modules"
    lib = D / "lib"
    lib.mkdir(exist_ok=True)
    for f in ("maplibre-gl.mjs", "maplibre-gl-worker.mjs", "maplibre-gl.css"):
        shutil.copy(nm / "maplibre-gl" / "dist" / f, lib / f)
    shutil.copy(nm / "maplibre-gl" / "LICENSE.txt", lib / "LICENSE-maplibre-gl.txt")
    shutil.copy(nm / "pmtiles" / "dist" / "pmtiles.js", lib / "pmtiles.js")
    lic = nm / "pmtiles" / "LICENSE"
    if lic.exists():
        shutil.copy(lic, lib / "LICENSE-pmtiles.txt")

    # demo page and helper module
    for f in ("index.html", "overlay.html", "chart-style.js"):
        shutil.copy(C.ROOT / "site" / f, D / f)
    shutil.copy(C.ROOT / "site" / "PACKAGE.md", D / "README.md")
    print("assets written to", D)


if __name__ == "__main__":
    main()
