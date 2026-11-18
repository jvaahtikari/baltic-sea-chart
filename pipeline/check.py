"""Checks the finished package and writes a run summary. Run: python3 -m pipeline.check [summary.md]

Fails (exit 1) if a file is too large for a GitHub repository or a layer is suspiciously small.
"""
import json
import sys
from pathlib import Path

from . import config as C

# Lower limits for a full Baltic build; a much smaller count means a source failed silently.
MIN_FEATURES = {"land": 1000, "coastline": 1000, "depth_area": 100, "depth_contour": 10000, "depth_fi_area": 50000,
                "depth_fi_contour": 50000, "seamark": 15000,
                "light": 2000, "light_sector": 3000, "fairway": 1000, "navline": 5000, "nodata": 1}


# Well-known major lights, one or two per country. If one is missing from the light layer, a source or a
# filter has dropped it (this caught the Gulf of Riga lighthouses being taken for inland objects).
KNOWN_LIGHTS = [("Bengtskär (FI)", 21.999, 59.722), ("Landsort (SE)", 17.866, 58.741), ("Keri (EE)", 25.02, 59.70),
                ("Tahkuna (EE)", 22.587, 59.091), ("Daugavgrīva (LV)", 24.024, 57.060),
                ("Klaipėda (LT)", 21.093, 55.729), ("Hel (PL)", 18.809, 54.601), ("Arkona (DE)", 13.432, 54.679),
                ("Kiel lighthouse (DE)", 10.274, 54.500), ("Gedser (DK)", 11.964, 54.559)]


def known_lights_missing():
    """Names of KNOWN_LIGHTS with no major light within about 3 km."""
    lp = C.MID / "light.geojsonl"
    if not lp.exists():
        return [n for n, _, _ in KNOWN_LIGHTS]
    found = set()
    with open(lp, encoding="utf-8") as f:
        for line in f:
            ft = json.loads(line)
            if not ft["properties"].get("major"):
                continue
            x, y = ft["geometry"]["coordinates"][:2]
            for n, lx, ly in KNOWN_LIGHTS:
                if abs(x - lx) < 0.05 and abs(y - ly) < 0.027:
                    found.add(n)
    return [n for n, _, _ in KNOWN_LIGHTS if n not in found]


def main(argv):
    out = Path(argv[0]) if argv else None
    problems = []
    build = json.loads((C.MID / "build_log.json").read_text()) if (C.MID / "build_log.json").exists() else {}
    feats = build.get("features", {})
    for k, v in MIN_FEATURES.items():
        if feats.get(k, 0) < v:
            problems.append("layer %s has %s features, expected at least %d" % (k, feats.get(k), v))
    sizes = {}
    for p in sorted(C.DIST.rglob("*")):
        if p.is_file():
            mb = p.stat().st_size / 1e6
            sizes[str(p.relative_to(C.DIST))] = round(mb, 2)
            if mb > C.MAX_FILE_MB:
                problems.append("%s is %.1f MB (limit %d MB)" % (p.name, mb, C.MAX_FILE_MB))
    for need in ("land.pmtiles", "chart.pmtiles", "depth.pmtiles", "depth-fi.pmtiles", "style.json", "style-dark.json", "sprite.png",
                 "index.html", "chart-style.js", "sources.json"):
        if need not in sizes:
            problems.append("missing " + need)
    shots = C.WORK / "shots" / "shots.json"
    shot_info = json.loads(shots.read_text()) if shots.exists() else None
    if shot_info and shot_info.get("errors"):
        problems.append("browser errors: %s" % shot_info["errors"][:5])

    osm_log = C.RAW / "osm" / "log.json"
    osm = json.loads(osm_log.read_text()) if osm_log.exists() else {}
    warnings = []
    for name, r in (osm.get("regions") or {}).items():
        if r.get("missing"):
            warnings.append("OSM seamarks for %s could not be fetched and no earlier data exists (%s)" % (name, "; ".join(r.get("errors", []))[:300]))
        elif r.get("stale"):
            warnings.append("OSM seamarks for %s are from an earlier run (%s)" % (name, r.get("fetched")))
    for step in ("estonia", "germany", "vayla"):
        lp = C.RAW / step / "log.json"
        lg = json.loads(lp.read_text()) if lp.exists() else {}
        if lg.get("failed"):
            warnings.append("%s authority source failed, OSM seamarks used instead: %s" % (step, lg["failed"][:300]))
    missing = known_lights_missing()
    if missing:
        warnings.append("known major lights missing from the light layer: " + ", ".join(missing))
    if not osm.get("regions") and (osm.get("missing") or osm.get("stale")):
        warnings.append("OSM seamarks: %s" % osm.get("source"))
    lines = ["# Build summary", "", "Result: **%s**" % ("OK" if not problems else "PROBLEMS"), ""]
    lines += ["## Warnings", ""] + ["- " + w for w in warnings] + [""] if warnings else []
    lines += ["## Problems", ""] + ["- " + p for p in problems] + [""] if problems else []
    if osm.get("regions"):
        lines += ["## OSM seamarks per region", "", "| Region | Source | Features |", "| --- | --- | ---: |"]
        lines += ["| %s | %s | %s |" % (k, v.get("source"), v.get("features")) for k, v in osm["regions"].items()]
        lines += [""]
    lines += ["## Features per layer", "", "| Layer | Features |", "| --- | ---: |"]
    lines += ["| %s | %s |" % (k, v) for k, v in feats.items()]
    lines += ["", "## Package files (MB)", "", "| File | MB |", "| --- | ---: |"]
    lines += ["| %s | %s |" % (k, v) for k, v in sizes.items() if not k.startswith("fonts/")]
    lines += ["", "## Build details", "", "```json", json.dumps({k: v for k, v in build.items() if k != "features"},
                                                                indent=1, ensure_ascii=False), "```"]
    if shot_info:
        lines += ["", "## Screenshots", "", "| Place | ms | rendered features |", "| --- | ---: | --- |"]
        lines += ["| %s | %s | %s |" % (r["name"], r["ms"], json.dumps(r["rendered"])) for r in shot_info["result"]]
    text = "\n".join(lines) + "\n"
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
