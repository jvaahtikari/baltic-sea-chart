"""Download every source from its live service. Run: python3 -m pipeline.fetch [step ...]

Steps: regions, emodnet, vayla, traficom, osm, land. Without arguments all steps run.
Each step writes into work/raw/<step>/ and records what it fetched in work/raw/<step>/log.json.
"""
import concurrent.futures as cf
import json
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from . import config as C

RAW = C.RAW


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_step(step, **info):
    d = RAW / step
    d.mkdir(parents=True, exist_ok=True)
    info.setdefault("fetched", now())
    (d / "log.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print("[%s] %s" % (step, json.dumps(info, ensure_ascii=False)[:600]), flush=True)


def http_get(url, dest=None, tries=8, timeout=600):
    """GET with retries. Returns bytes (dest None) or writes to dest and returns its size."""
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": C.USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                if dest is None:
                    return r.read()
                tmp = dest.with_suffix(dest.suffix + ".part")
                with open(tmp, "wb") as f:
                    shutil.copyfileobj(r, f, 1 << 20)
                tmp.replace(dest)
                return dest.stat().st_size
        except Exception as e:  # noqa: BLE001 - network errors of every kind are retried
            last = e
            wait = min(120, 5 * (i + 1) ** 2)   # up to ~10 minutes in all: brief network outages do happen
            print("  retry %d/%d in %ds: %s (%s)" % (i + 1, tries, wait, url[:160], e), flush=True)
            time.sleep(wait)
    raise RuntimeError("download failed: %s: %s" % (url, last))


def wfs_url(base, **q):
    return base + "?" + urllib.parse.urlencode(q)


def wfs_json(base, **q):
    data = http_get(wfs_url(base, **q))
    j = json.loads(data)
    if "features" not in j:
        raise RuntimeError("WFS response without features: %s" % data[:300])
    return j


def wfs_paged(base, typename, dest, page=5000, workers=4, **extra):
    """Fetch all features of a WFS 2.0 layer page by page into GeoJSONSeq (one feature per line)."""
    q = dict(service="WFS", version="2.0.0", request="GetFeature", typeNames=typename,
             outputFormat="application/json", srsName="EPSG:4326", **extra)
    hits = http_get(wfs_url(base, resultType="hits", **{k: v for k, v in q.items() if k != "outputFormat"})).decode("utf-8", "replace")
    total = int(hits.split('numberMatched="')[1].split('"')[0])
    starts = list(range(0, total, page))

    def one(s):
        j = wfs_json(base, count=page, startIndex=s, **q)
        return s, j["features"]

    n = 0
    with open(dest, "w", encoding="utf-8") as f, cf.ThreadPoolExecutor(workers) as ex:
        for s, feats in sorted(ex.map(one, starts), key=lambda t: t[0]):
            for ft in feats:
                f.write(json.dumps(ft, ensure_ascii=False, separators=(",", ":")) + "\n")
            n += len(feats)
    if n < total:
        raise RuntimeError("%s: got %d of %d features" % (typename, n, total))
    return n


# ---------------------------------------------------------------------------------------------
def step_regions():
    """IHO sea areas for the area of interest and the maritime zones of Russia and Finland."""
    d = RAW / "regions"
    d.mkdir(parents=True, exist_ok=True)
    got = {}

    def mr(layer, cql, name):
        j = wfs_json(C.MR_WFS, service="WFS", version="1.0.0", request="GetFeature",
                     typeName="MarineRegions:" + layer, outputFormat="application/json", CQL_FILTER=cql)
        (d / (name + ".geojson")).write_text(json.dumps(j), encoding="utf-8")
        got[name] = {"layer": layer, "filter": cql, "features": len(j["features"]),
                     "names": sorted({str(f["properties"].get("geoname") or f["properties"].get("name")) for f in j["features"]})}
        if not j["features"]:
            raise RuntimeError("Marine Regions returned nothing for %s %s" % (layer, cql))

    mr("iho", "mrgid IN (%s)" % ",".join(map(str, C.IHO_MRGIDS)), "iho")
    for terr, tag in ((C.EXCLUDED_TERRITORY, "excluded"), (C.FI_TERRITORY, "fi")):
        mr("eez", "territory1='%s'" % terr, tag + "_eez")
        mr("eez_12nm", "territory1='%s'" % terr, tag + "_12nm")
        try:
            mr("eez_internal_waters", "territory1='%s'" % terr, tag + "_internal")
        except RuntimeError as e:  # some territories have no internal-waters polygon
            got[tag + "_internal"] = {"error": str(e)}
    log_step("regions", source=C.MR_WFS, licence="CC BY 4.0 (Marine Regions, VLIZ)", layers=got)


def step_emodnet():
    """EMODnet Bathymetry DTM as GeoTIFF chunks from the WCS."""
    d = RAW / "emodnet"
    d.mkdir(parents=True, exist_ok=True)
    x0, y0, x1, y1 = C.BBOX
    step = C.EMODNET_CHUNK_DEG
    jobs = []
    x = x0
    while x < x1:
        y = y0
        while y < y1:
            jobs.append((round(x, 4), round(y, 4), round(min(x + step, x1), 4), round(min(y + step, y1), 4)))
            y += step
        x += step

    def one(b):
        out = d / ("chunk_%07.3f_%07.3f.tif" % (b[0], b[1]))
        if out.exists() and out.stat().st_size > 1000:
            return out.stat().st_size
        url = wfs_url(C.EMODNET_WCS, service="WCS", version="2.0.1", request="GetCoverage",
                      coverageId=C.EMODNET_COVERAGE, format="image/tiff")
        url += "&subset=Long(%s,%s)&subset=Lat(%s,%s)" % (b[0], b[2], b[1], b[3])
        n = http_get(url, out)
        with open(out, "rb") as f:
            if f.read(2) not in (b"II", b"MM"):
                raise RuntimeError("not a TIFF: %s" % url)
        return n

    with cf.ThreadPoolExecutor(4) as ex:
        sizes = list(ex.map(one, jobs))
    log_step("emodnet", source=C.EMODNET_WCS, coverage=C.EMODNET_COVERAGE, chunks=len(jobs),
             mb=round(sum(sizes) / 1e6, 1), licence="EMODnet Bathymetry, open access with attribution")


VAYLA_LAYERS = ["turvalaitteet_uusi", "loistot_uusi", "valosektorit_uusi", "navigointilinjat_uusi",
                "vaylaalueet_uusi", "taululinjat_uusi"]


def step_vayla():
    d = RAW / "vayla"
    d.mkdir(parents=True, exist_ok=True)
    got = {}
    for tn in VAYLA_LAYERS:
        got[tn] = wfs_paged(C.VAYLA_WFS, "vesivaylatiedot:" + tn, d / (tn + ".geojsonl"), page=20000, workers=2)
    log_step("vayla", source=C.VAYLA_WFS, layers=got, licence="CC BY 4.0 (Väylävirasto)")


TRAFICOM_LAYERS = ["DepthArea_A", "DepthContour_L"]


def step_traficom():
    d = RAW / "traficom"
    d.mkdir(parents=True, exist_ok=True)
    got = {}
    for tn in TRAFICOM_LAYERS:
        got[tn] = wfs_paged(C.TRAFICOM_WFS, "rajoitettu:" + tn, d / (tn + ".geojsonl"), page=5000, workers=4,
                            sortBy="IDENTIFIER")
    log_step("traficom", source=C.TRAFICOM_WFS, layers=got,
             licence="Traficom merikarttatietokanta: not for navigation, non-commercial use, attribution with transfer date")


def run(cmd, **kw):
    print("$ " + " ".join(map(str, cmd)), flush=True)
    subprocess.run(list(map(str, cmd)), check=True, **kw)


def step_osm():
    """OpenStreetMap seamark objects (OpenSeaMap tagging) from the Geofabrik extracts."""
    d = RAW / "osm"
    d.mkdir(parents=True, exist_ok=True)
    parts = []

    def one(region):
        name = region.replace("/", "_")
        pbf = d / (name + ".osm.pbf")
        sea = d / (name + "_seamark.osm.pbf")
        http_get(C.GEOFABRIK + region + "-latest.osm.pbf", pbf, timeout=1800)
        run(["osmium", "tags-filter", "--overwrite", "-o", sea, pbf, "nwr/seamark:type"])
        pbf.unlink()
        return sea

    with cf.ThreadPoolExecutor(3) as ex:
        parts = list(ex.map(one, C.OSM_REGIONS))
    merged = d / "seamark.osm.pbf"
    run(["osmium", "merge", "--overwrite", "-o", merged] + parts)
    out = d / "seamark.geojsonl"
    run(["osmium", "export", "--overwrite", "-f", "geojsonseq", "-x", "print_record_separator=false",
         "--geometry-types=point,linestring,polygon", "-a", "type,id", "-o", out, merged])
    n = sum(1 for _ in open(out, encoding="utf-8"))
    log_step("osm", source=C.GEOFABRIK, regions=C.OSM_REGIONS, features=n,
             licence="ODbL 1.0, © OpenStreetMap contributors")


def step_land():
    """OSM coastline-derived land polygons (osmdata.openstreetmap.de), clipped to the bounding box."""
    d = RAW / "land"
    d.mkdir(parents=True, exist_ok=True)
    x0, y0, x1, y1 = C.BBOX
    full = d / "land-polygons-complete-4326.zip"
    simp = d / "simplified-land-polygons-complete-3857.zip"
    http_get(C.OSMDATA + full.name, full, timeout=1800)
    http_get(C.OSMDATA + simp.name, simp, timeout=600)
    run(["ogr2ogr", "-f", "GeoJSONSeq", "-overwrite", d / "land.geojsonl",
         "/vsizip/%s/land-polygons-complete-4326/land_polygons.shp" % full,
         "-clipsrc", x0, y0, x1, y1, "-explodecollections", "-lco", "RS=NO"])
    run(["ogr2ogr", "-f", "GeoJSONSeq", "-overwrite", d / "land_simplified.geojsonl",
         "/vsizip/%s/simplified-land-polygons-complete-3857/simplified_land_polygons.shp" % simp,
         "-t_srs", "EPSG:4326", "-clipdst", x0 - 2, y0 - 2, x1 + 2, y1 + 2,
         "-explodecollections", "-lco", "RS=NO"])
    full.unlink()
    log_step("land", source=C.OSMDATA, files=[full.name, simp.name], licence="ODbL 1.0, © OpenStreetMap contributors")


STEPS = {"regions": step_regions, "emodnet": step_emodnet, "vayla": step_vayla,
         "traficom": step_traficom, "osm": step_osm, "land": step_land}


def main(argv):
    names = argv or list(STEPS)
    for n in names:
        t = time.time()
        STEPS[n]()
        print("[%s] done in %.0f s" % (n, time.time() - t), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
