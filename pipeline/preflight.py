"""Preflight: a few minutes of checks before the long build.

Every source is contacted with the same code the pipeline uses, but with small requests. The two
authority seamark sources (Estonia, Germany) are small, so they are fetched in full and run through
the same parsers the build uses, which shows at once whether the marks come out with sensible types.

Writes work/preflight.md and exits 1 if a required source fails, so a broken run stops in minutes
instead of after an hour. Optional sources only produce warnings, because the build falls back to OSM.

    BSC_WORK=/tmp/pre python3 -m pipeline.preflight
"""
import collections
import json
import subprocess
import sys
import time
import urllib.parse

from . import config as C
from . import fetch as F

rows = []          # (source, check, ok, required, detail, seconds)


def check(source, what, required=True):
    def deco(fn):
        t = time.time()
        try:
            detail = fn()
            ok = True
        except Exception as e:  # noqa: BLE001
            detail, ok = str(e)[:300], False
        rows.append((source, what, ok, required, detail, round(time.time() - t)))
        print("%-4s %-14s %-40s %s" % ("OK" if ok else ("FAIL" if required else "warn"), source, what, detail),
              flush=True)
        return fn
    return deco


def head(url):
    """HTTP status of a HEAD request (curl -4, redirects followed)."""
    r = subprocess.run(["curl", "-4", "-sIL", "-o", "/dev/null", "-w", "%{http_code}", "-m", "60", url],
                       capture_output=True, text=True)
    code = r.stdout.strip()
    if code != "200":
        raise RuntimeError("HTTP %s %s" % (code, url))
    return "HTTP 200"


def hits(base, typename, version="2.0.0"):
    q = dict(service="WFS", version=version, request="GetFeature", resultType="hits",
             **({"typeNames": typename} if version.startswith("2") else {"typeName": typename}))
    txt = F.http_get(F.wfs_url(base, **q), tries=2, timeout=120).decode("utf-8", "replace")
    key = 'numberMatched="' if 'numberMatched="' in txt else 'numberOfFeatures="'
    if key not in txt:
        raise RuntimeError("no feature count in the answer: %s" % txt[:200])
    return int(txt.split(key)[1].split('"')[0])


def main():
    out = C.WORK / "preflight.md"
    C.WORK.mkdir(parents=True, exist_ok=True)

    # --- required sources: a failure here stops the run ------------------------------------
    @check("Marine Regions", "IHO areas (one request)")
    def _():
        if C.IHO_MRGIDS:
            cql = "mrgid IN (%s)" % ",".join(map(str, C.IHO_MRGIDS))
        elif C.IHO_NAMES:
            cql = "name IN (%s)" % ",".join("'%s'" % n.replace("'", "''") for n in C.IHO_NAMES)
        else:
            return "envelope used as the area (region %s)" % C.REGION
        j = F.wfs_json(C.MR_WFS, service="WFS", version="1.0.0", request="GetFeature",
                       typeName="MarineRegions:iho", outputFormat="application/json", CQL_FILTER=cql)
        if not j["features"]:
            raise RuntimeError("no IHO areas")
        names = sorted(str(f["properties"].get("name")) for f in j["features"])
        if C.IHO_NAMES and len(names) < len(C.IHO_NAMES):
            raise RuntimeError("only %s found of %s" % (names, C.IHO_NAMES))
        return "%d areas: %s" % (len(j["features"]), ", ".join(names))

    @check("EMODnet", "WCS capabilities")
    def _():
        txt = F.http_get(C.EMODNET_WCS + "?service=WCS&request=GetCapabilities&version=2.0.1", tries=2,
                         timeout=120).decode("utf-8", "replace")
        if C.EMODNET_COVERAGE not in txt:
            raise RuntimeError("coverage %s not listed" % C.EMODNET_COVERAGE)
        return "coverage listed"

    if "fi" in C.NATIONAL:
        for tn in F.VAYLA_LAYERS:
            check("Väylä", tn)(lambda tn=tn: "%d features" % hits(C.VAYLA_WFS, "vesivaylatiedot:" + tn))
        for tn in F.TRAFICOM_LAYERS:
            check("Traficom", tn)(lambda tn=tn: "%d features" % hits(C.TRAFICOM_WFS, "rajoitettu:" + tn))
    if "no" in C.NATIONAL:
        for tn in C.NO_AIDS_LAYERS:
            check("Kystverket", tn)(lambda tn=tn: "%d features" % hits(C.NO_AIDS_WFS, C.NO_AIDS_PREFIX + ":" + tn))

        @check("Kartverket", "Dybdeareal, one small window")
        def _():
            url = F.wfs_url(C.NO_DEPTH_WFS, service="WFS", version="2.0.0", request="GetFeature",
                            typeNames="app:Dybdeareal", bbox="60.10,5.00,60.15,5.10,urn:ogc:def:crs:EPSG::4258")
            txt = F.http_get(url, tries=2, timeout=300).decode("utf-8", "replace")
            if "ExceptionReport" in txt[:2000]:
                raise RuntimeError(txt[:300])
            n = txt.count("<app:Dybdeareal")
            if n == 0:
                raise RuntimeError("no features in the window (axis order?): %s" % txt[:300])
            return "%d features, %d kB" % (n, len(txt) // 1000)
    check("osmdata", "land polygons")(lambda: head(C.OSMDATA + "land-polygons-complete-4326.zip"))

    # --- authority seamarks: fetched in full and parsed with the build's own functions -----
    from . import build as B

    @check("Estonia", "fetch + parse", required=False)
    def _():
        if "ee" not in C.NATIONAL:
            return "not used in region " + C.REGION
        F.step_estonia()
        kinds = collections.Counter()
        for layer in ("Beacon", "Buoy"):
            p_ = C.RAW / "estonia" / (layer + ".geojsonl")
            for ft in (B.read_seq(p_) if p_.exists() else []):
                name = ft["properties"].get("geographicalname_geographicalname_spelling_spellingofname_text")
                kinds[B.estonian_mark(name, layer)] += 1
        n = sum(kinds.values())
        named = sum(v for (k, c), v in kinds.items() if c != "none")
        if n == 0:
            raise RuntimeError("no marks")
        return "%d marks, %d with an IALA category; top: %s" % (
            n, named, ", ".join("%s/%s %d" % (k, c, v) for (k, c), v in kinds.most_common(8)))

    @check("Germany (BSH)", "fetch + parse", required=False)
    def _():
        if "de" not in C.NATIONAL:
            return "not used in region " + C.REGION
        F.step_germany()
        kinds, labels = collections.Counter(), []
        gd = C.RAW / "germany"
        for cl in B.DE_CLASS_KIND:
            lit = {}
            pl = gd / ("%s_lights.geojsonl" % cl)
            pm = gd / ("%s_%s.geojsonl" % (cl, cl.lower()))
            for ft in (B.read_seq(pl) if pl.exists() else []):
                p = ft["properties"]
                pt = B.point_of(ft)
                if pt is not None:
                    k = (round(pt.x, 5), round(pt.y, 5))
                    lit[k] = max(lit.get(k, 0), B.num(p.get("valnmr")) or 0.001)
                if len(labels) < 6:
                    labels.append(B.light_label(B.s57_litchr(p.get("litchr")) + str(p.get("siggrp") or "")
                                                .replace("()", "").replace("(1)", ""),
                                                B.s57_colours(p.get("colour")), p.get("sigper")))
            for ft in (B.read_seq(pm) if pm.exists() else []):
                pt = B.point_of(ft)
                rng = lit.get((round(pt.x, 5), round(pt.y, 5))) if pt is not None else None
                kinds[B.s57_mark(cl, ft["properties"], rng)] += 1
        n = sum(v for (k, c), v in kinds.items() if k)
        if n == 0:
            raise RuntimeError("no marks")
        return "%d marks; top: %s; light labels e.g. %s" % (
            n, ", ".join("%s/%s %d" % (k, c, v) for (k, c), v in kinds.most_common(8)), " | ".join(labels))

    # --- OSM: which route each region would take --------------------------------------------
    for name, osmfr, geofabrik, box in C.OSM_REGIONS:
        def region(osmfr=osmfr, geofabrik=geofabrik):
            tried = []
            for src, url in (("openstreetmap.fr", C.OSMFR + osmfr + "-latest.osm.pbf" if osmfr else None),
                             ("geofabrik", C.GEOFABRIK + geofabrik + "-latest.osm.pbf")):
                if not url:
                    continue
                try:
                    head(url)
                    return src
                except Exception as e:  # noqa: BLE001
                    tried.append("%s %s" % (src, str(e)[:60]))
            raise RuntimeError("no extract (Overpass is the fallback): " + "; ".join(tried))
        check("OSM " + name, "extract available", required=False)(region)

    for server in C.OVERPASS:
        def op(server=server):
            q = '[out:json][timeout:25];node["seamark:type"](60.0,24.9,60.1,25.0);out ids 1;'
            data = urllib.parse.urlencode({"data": q}).encode()
            j = json.loads(F.http_get(server, data=data, tries=1, timeout=60))
            return "answers (%d elements)" % len(j.get("elements", []))
        check("Overpass", server.split("/")[2], required=False)(op)

    # --- report -----------------------------------------------------------------------------
    failed = [r for r in rows if not r[2] and r[3]]
    lines = ["# Preflight", "", "Result: **%s**" % ("OK" if not failed else "FAILED"), "",
             "| Source | Check | Result | Seconds | Detail |", "| --- | --- | --- | ---: | --- |"]
    for s, w, ok, req, d, sec in rows:
        lines.append("| %s | %s | %s | %d | %s |" % (s, w, "OK" if ok else ("FAIL" if req else "warning"), sec,
                                                     str(d).replace("|", "/")))
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
