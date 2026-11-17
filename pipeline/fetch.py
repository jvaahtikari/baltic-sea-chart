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
    print("[%s] %s" % (step, json.dumps(info, ensure_ascii=False)[:3000]), flush=True)


def http_get(url, dest=None, tries=8, timeout=600, data=None):
    """GET (or POST form data) with curl over IPv4 and retries. Returns bytes, or the size written to dest.

    curl -4 is used because GitHub's runners have repeatedly failed to reach some German OSM hosts
    with "Network is unreachable" through Python's own client."""
    last = None
    for i in range(tries):
        cmd = ["curl", "-4", "-sS", "-f", "-L", "--compressed", "--connect-timeout", "30", "--max-time", str(timeout),
               "-A", C.USER_AGENT]
        if data is not None:
            cmd += ["--data-binary", "@-", "-H", "Content-Type: application/x-www-form-urlencoded"]
        tmp = None
        if dest is not None:
            tmp = dest.with_suffix(dest.suffix + ".part")
            cmd += ["-o", str(tmp)]
        cmd.append(url)
        p = subprocess.run(cmd, input=data, capture_output=True)
        if p.returncode == 0:
            if dest is None:
                return p.stdout
            tmp.replace(dest)
            return dest.stat().st_size
        last = p.stderr.decode("utf-8", "replace").strip()[:300]
        wait = min(120, 5 * (i + 1) ** 2)   # up to ~10 minutes in all: brief network outages do happen
        print("  retry %d/%d in %ds: %s (%s)" % (i + 1, tries, wait, url[:160], last), flush=True)
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
        # GeoServer refuses startIndex on layers without a primary key, so page only when needed
        j = wfs_json(base, count=page, startIndex=s, **q) if total > page else wfs_json(base, **q)
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
    for terr, tag in ((C.EXCLUDED_TERRITORY, "excluded"), (C.FI_TERRITORY, "fi"), (C.EE_TERRITORY, "ee"),
                      (C.DE_TERRITORY, "de")):
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


AREA_SEAMARKS = {"fairway", "dredged_area", "separation_zone", "inshore_traffic_zone", "precautionary_area",
                 "restricted_area", "anchorage", "harbour", "production_area", "cable_area", "pipeline_area",
                 "seaplane_landing_area", "marine_farm", "dumping_ground", "military_area", "obstruction", "wreck", "rock"}


def overpass(query):
    data = urllib.parse.urlencode({"data": query}).encode()
    last = None
    for server in [C.OVERPASS[0]] + C.OVERPASS:   # the main server twice: a 429 usually clears in a minute
        try:
            j = json.loads(http_get(server, data=data, tries=1, timeout=300))
            if "elements" not in j:
                raise RuntimeError("no elements: %s" % str(j)[:200])
            if j.get("remark") and "error" in j["remark"].lower():
                raise RuntimeError(j["remark"][:300])
            return server, j["elements"]
        except Exception as e:  # noqa: BLE001
            last = e
            print("  overpass %s: %s" % (server, str(e)[:200]), flush=True)
            time.sleep(60)
    raise RuntimeError("all Overpass servers failed: %s" % last)


def element_feature(el):
    tags = dict(el.get("tags", {}))
    tags["@type"], tags["@id"] = el["type"], el["id"]
    if el["type"] == "node":
        geom = {"type": "Point", "coordinates": [el["lon"], el["lat"]]}
    elif el["type"] == "way" and el.get("geometry"):
        coords = [[p["lon"], p["lat"]] for p in el["geometry"]]
        closed = len(coords) >= 4 and coords[0] == coords[-1]
        if closed and tags.get("seamark:type") in AREA_SEAMARKS:
            geom = {"type": "Polygon", "coordinates": [coords]}
        else:
            geom = {"type": "LineString", "coordinates": coords}
    else:
        return None
    return {"type": "Feature", "properties": tags, "geometry": geom}


OSM_LAST = C.WORK / "osm-last"          # per-region seamarks of earlier runs, kept by the workflow cache


def osm_region_from_extract(name, url, d):
    pbf = d / (name + ".osm.pbf")
    sea = d / (name + "_seamark.osm.pbf")
    out = d / (name + ".geojsonl")
    http_get(url, pbf, tries=2, timeout=1800)
    try:
        run(["osmium", "tags-filter", "--overwrite", "-o", sea, pbf, "nwr/seamark:type"])
    finally:
        pbf.unlink(missing_ok=True)
    run(["osmium", "export", "--overwrite", "-f", "geojsonseq", "-x", "print_record_separator=false",
         "--geometry-types=point,linestring,polygon", "-a", "type,id", "-o", out, sea])
    sea.unlink(missing_ok=True)
    return out


def osm_region_from_overpass(name, box, d):
    """Overpass for the region box, in 2 x 2 slices if the box is large."""
    out = d / (name + ".geojsonl")
    x0, y0, x1, y1 = box
    k = 2 if (x1 - x0) * (y1 - y0) > 4 else 1
    xs = [x0 + (x1 - x0) * i / k for i in range(k + 1)]
    ys = [y0 + (y1 - y0) * i / k for i in range(k + 1)]
    seen = set()
    with open(out, "w", encoding="utf-8") as f:
        for i in range(k):
            for j in range(k):
                bb = "%.4f,%.4f,%.4f,%.4f" % (ys[j], xs[i], ys[j + 1], xs[i + 1])
                q = '[out:json][timeout:300];(node["seamark:type"](%s);way["seamark:type"](%s););out geom;' % (bb, bb)
                _, els = overpass(q)
                for el in els:
                    key = (el["type"], el["id"])
                    if key in seen:
                        continue
                    seen.add(key)
                    ft = element_feature(el)
                    if ft:
                        f.write(json.dumps(ft, ensure_ascii=False, separators=(",", ":")) + "\n")
                time.sleep(15)   # be gentle with the public servers
    return out


def step_osm():
    """OpenStreetMap seamarks region by region. Each region comes from the first source that works:
    openstreetmap.fr extract, Geofabrik extract, Overpass API; failing all, the region's data from the
    last successful run. The result and the source of every region are logged."""
    d = RAW / "osm"
    d.mkdir(parents=True, exist_ok=True)
    OSM_LAST.mkdir(parents=True, exist_ok=True)
    regions = {}

    def save(name, out, src):
        n = sum(1 for _ in open(out, encoding="utf-8"))
        if n == 0:
            raise RuntimeError("no seamarks")
        shutil.copy(out, OSM_LAST / (name + ".geojsonl"))
        info = {"source": src, "features": n, "fetched": now()}
        (OSM_LAST / (name + ".json")).write_text(json.dumps(info))
        return info

    def from_extracts(region):
        """Phase 1, in parallel: the extract downloads."""
        name, osmfr, geofabrik, box = region
        errors = []
        for src, url in (("openstreetmap.fr", C.OSMFR + osmfr + "-latest.osm.pbf" if osmfr else None),
                         ("geofabrik", C.GEOFABRIK + geofabrik + "-latest.osm.pbf")):
            if not url:
                continue
            try:
                return name, save(name, osm_region_from_extract(name, url, d), src), errors
            except Exception as e:  # noqa: BLE001
                errors.append("%s: %s" % (src, str(e)[:160]))
                print("  [osm %s] %s failed: %s" % (name, src, str(e)[:200]), flush=True)
        return name, None, errors

    errors = {}
    with cf.ThreadPoolExecutor(3) as ex:
        for name, info, errs in ex.map(from_extracts, C.OSM_REGIONS):
            errors[name] = errs
            if info:
                regions[name] = info
    # Phase 2, one region at a time with pauses: public Overpass servers answer 429 to parallel queries.
    for name, _, _, box in C.OSM_REGIONS:
        if name in regions:
            continue
        try:
            regions[name] = save(name, osm_region_from_overpass(name, box, d), "overpass")
        except Exception as e:  # noqa: BLE001
            errors[name].append("overpass: %s" % str(e)[:160])
            print("  [osm %s] overpass failed: %s" % (name, str(e)[:200]), flush=True)
            cached = OSM_LAST / (name + ".geojsonl")
            if cached.exists():
                shutil.copy(cached, d / (name + ".geojsonl"))
                meta = OSM_LAST / (name + ".json")
                info = json.loads(meta.read_text()) if meta.exists() else {}
                regions[name] = {"source": "previous run (%s)" % info.get("source"), "fetched": info.get("fetched"),
                                 "features": info.get("features"), "stale": True, "errors": errors[name]}
            else:
                (d / (name + ".geojsonl")).write_text("", encoding="utf-8")
                regions[name] = {"source": None, "features": 0, "missing": True, "errors": errors[name]}

    # merge, dropping objects that appear in two regions
    seen, n = set(), 0
    with open(d / "seamark.geojsonl", "w", encoding="utf-8") as f:
        for name, *_ in C.OSM_REGIONS:
            p = d / (name + ".geojsonl")
            if not p.exists():
                continue
            for line in open(p, encoding="utf-8"):
                line = line.strip().lstrip("\x1e")
                if not line:
                    continue
                pr = json.loads(line).get("properties", {})
                key = (pr.get("@type"), pr.get("@id"))
                if key[1] is not None and key in seen:
                    continue
                seen.add(key)
                f.write(line + "\n")
                n += 1
    log_step("osm", source="openstreetmap.fr / Geofabrik / Overpass, per region", features=n, regions=regions,
             stale=any(r.get("stale") for r in regions.values()),
             missing=all(r.get("missing") for r in regions.values()),
             licence="ODbL 1.0, © OpenStreetMap contributors")


def step_osm_fallback():
    """Used by the workflow only if step_osm crashed or ran out of time: every region from the cache."""
    d = RAW / "osm"
    d.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(d / "seamark.geojsonl", "w", encoding="utf-8") as f:
        for p in sorted(OSM_LAST.glob("*.geojsonl")) if OSM_LAST.exists() else []:
            for line in open(p, encoding="utf-8"):
                if line.strip():
                    f.write(line if line.endswith("\n") else line + "\n")
                    n += 1
    log_step("osm", source="previous runs (OSM fetch failed)", features=n, stale=n > 0, missing=n == 0,
             licence="ODbL 1.0, © OpenStreetMap contributors")


EE_LAYERS = ["Beacon", "Buoy", "FairwayArea", "WaterwayLink"]


def step_estonia():
    """Estonian aids to navigation register (Transpordiamet), INSPIRE WFS. Max 5000 features per request."""
    d = RAW / "estonia"
    d.mkdir(parents=True, exist_ok=True)
    got = {}
    for tn in EE_LAYERS:
        got[tn] = wfs_paged(C.EE_WFS, "TN_veetransport:TN.WaterTransportNetwork." + tn, d / (tn + ".geojsonl"),
                            page=5000, workers=1)
    log_step("estonia", source=C.EE_WFS, layers=got,
             licence="Maa- ja Ruumiamet / Transpordiamet open data (CC BY 4.0 equivalent), fees: none")


DE_CLASSES = ["BOYLAT", "BOYCAR", "BOYISD", "BOYSAW", "BOYSPP", "BCNLAT", "BCNCAR", "BCNISD", "BCNSPP", "LNDMRK"]


def step_germany():
    """BSH navigation marks (S-57 object classes) and their lights, WFS. Only the Baltic part is used later."""
    d = RAW / "germany"
    d.mkdir(parents=True, exist_ok=True)
    got = {}
    x0, y0, x1, y1 = C.BBOX
    for cl in DE_CLASSES:
        for part in (cl.lower(), "lights"):
            tn = "Seezeichen:%s_%s" % (cl, part)
            got[tn] = wfs_paged(C.DE_WFS, tn, d / ("%s_%s.geojsonl" % (cl, part)), page=5000, workers=2)
    log_step("germany", source=C.DE_WFS, layers=got,
             licence="GeoNutzV (Nutzungsbestimmungen für die Bereitstellung von Geodaten des Bundes), Quelle: © BSH; "
                     "not to be used for navigation")


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
         "traficom": step_traficom, "osm": step_osm, "osm_fallback": step_osm_fallback, "estonia": step_estonia,
         "germany": step_germany, "land": step_land}


# Optional authority sources: if one fails, the build falls back to OSM in that area and the run goes on.
OPTIONAL = {"estonia": "estonia", "germany": "germany"}


def main(argv):
    names = argv or list(STEPS)
    for n in names:
        t = time.time()
        try:
            STEPS[n]()
        except Exception as e:  # noqa: BLE001
            if n not in OPTIONAL:
                raise
            shutil.rmtree(RAW / OPTIONAL[n], ignore_errors=True)
            log_step(n, failed=str(e)[:500], fallback="OpenStreetMap seamarks are used in this area")
            print("[%s] FAILED, falling back to OSM: %s" % (n, str(e)[:300]), flush=True)
        print("[%s] done in %.0f s" % (n, time.time() - t), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
