"""Turn the fetched sources into tiled vector layers. Run: python3 -m pipeline.build [step ...]

Steps: areas, land, depth, marks, routes, tiles. Without arguments all steps run in that order.
Intermediate layers are written as GeoJSONSeq into work/mid/, tiles into dist/.
"""
import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import shapely
from osgeo import gdal, ogr, osr
from pyproj import Transformer
from shapely.geometry import LineString, Point, box, mapping, shape
from shapely.ops import unary_union

from . import config as C

gdal.UseExceptions()
RAW, MID, DIST = C.RAW, C.MID, C.DIST
LOG = {}


def say(*a):
    print(*a, flush=True)


def run(cmd):
    say("$ " + " ".join(map(str, cmd)))
    subprocess.run(list(map(str, cmd)), check=True)


def read_geojson(path):
    j = json.loads(Path(path).read_text(encoding="utf-8"))
    return j["features"]


def read_seq(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip().lstrip("\x1e")
            if line:
                yield json.loads(line)


class Writer:
    """GeoJSONSeq writer. Zoom limits are stored as the attributes minzoom/maxzoom and applied with
    a tippecanoe -j filter in step_tiles: tippecanoe's own per-feature "tippecanoe" member merges
    polygons into one feature per tile (seen with tippecanoe 2.49), so it is not used."""

    def __init__(self, name):
        MID.mkdir(parents=True, exist_ok=True)
        self.path = MID / (name + ".geojsonl")
        self.f = open(self.path, "w", encoding="utf-8")
        self.n = 0
        self.name = name
        self.mins, self.maxs = set(), set()

    def add(self, geom, props, minzoom=None, maxzoom=None):
        if geom is None or geom.is_empty:
            return
        props = {k: v for k, v in props.items() if v is not None and v != ""}
        if minzoom:
            props["minzoom"] = int(minzoom)
            self.mins.add(int(minzoom))
        if maxzoom is not None:
            props["maxzoom"] = int(maxzoom)
            self.maxs.add(int(maxzoom))
        ft = {"type": "Feature", "geometry": mapping(geom), "properties": props}
        self.f.write(json.dumps(ft, ensure_ascii=False, separators=(",", ":")) + "\n")
        self.n += 1

    def close(self):
        self.f.close()
        LOG.setdefault("features", {})[self.name] = self.n
        LOG.setdefault("zooms", {})[self.name] = {"min": sorted(self.mins), "max": sorted(self.maxs)}
        say("  %s: %d features" % (self.name, self.n))


def zoom_filter(layers):
    """tippecanoe -j filter that keeps a feature only between its minzoom and maxzoom attributes."""
    zs = LOG.get("zooms", {})
    flt = {}
    for layer in layers:
        z = zs.get(layer, {"min": [], "max": []})
        parts = []
        if z["min"]:
            parts.append(["any", ["!has", "minzoom"]] + [["all", ["==", "minzoom", v], [">=", "$zoom", v]] for v in z["min"]])
        if z["max"]:
            parts.append(["any", ["!has", "maxzoom"]] + [["all", ["==", "maxzoom", v], ["<=", "$zoom", v]] for v in z["max"]])
        if parts:
            flt[layer] = ["all"] + parts
    return json.dumps(flt)


def union_of(features, bounds=C.BBOX):
    """Union of the features, cut to the bounding box first (world-wide zones are huge)."""
    parts = []
    for f in features:
        if not f.get("geometry"):
            continue
        g = shapely.clip_by_rect(shape(f["geometry"]), *bounds)
        if not g.is_empty:
            parts.append(shapely.make_valid(g))
    return unary_union(parts)


# ---------------------------------------------------------------------------------------------
# Areas: where the chart applies, which waters are excluded and where Finnish sources rule.
def load_areas():
    return {k: shapely.from_wkb(bytes.fromhex(v)) for k, v in
            json.loads((MID / "areas.json").read_text()).items()}


def step_areas():
    d = RAW / "regions"
    frame = box(*C.BBOX)
    iho = union_of(read_geojson(d / "iho.geojson")).intersection(frame)
    excluded = unary_union([union_of(read_geojson(p)) for p in sorted(d.glob("excluded_*.geojson"))]).intersection(frame)
    fi = unary_union([union_of(read_geojson(p)) for p in sorted(d.glob("fi_*.geojson"))]).intersection(frame)
    ee = unary_union([union_of(read_geojson(p)) for p in sorted(d.glob("ee_*.geojson"))]).intersection(frame)
    de = unary_union([union_of(read_geojson(p)) for p in sorted(d.glob("de_*.geojson"))]).intersection(frame)
    # Simplify before buffering: the buffer is wide, so detail below ~1 km does not matter, and
    # buffering the full-detail coastline takes many minutes.
    aoi = iho.simplify(0.01).buffer(C.AOI_BUFFER_DEG, 4).intersection(frame).difference(excluded)
    fi_zone = fi.simplify(0.002).buffer(0.005, 4).intersection(aoi)
    ee_zone = ee.simplify(0.002).buffer(0.005, 4).intersection(aoi).difference(fi_zone) if not ee.is_empty else ee
    de_zone = de.simplify(0.002).buffer(0.005, 4).intersection(aoi) if not de.is_empty else de
    areas = {"aoi": aoi, "excluded": excluded, "fi_zone": fi_zone, "ee_zone": ee_zone, "de_zone": de_zone, "iho": iho}
    (MID).mkdir(parents=True, exist_ok=True)
    (MID / "areas.json").write_text(json.dumps({k: shapely.to_wkb(v, hex=True) for k, v in areas.items()}))
    w = Writer("nodata")
    w.add(excluded, {"reason": "excluded_waters", "territory": C.EXCLUDED_TERRITORY})
    w.close()
    LOG["areas_km2"] = {k: round(area_km2(v)) for k, v in areas.items()}
    say("  areas km2:", LOG["areas_km2"])


_to_laea = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)


def to_metric(geom):
    geom = shapely.segmentize(geom, 0.02)   # long straight edges in lon/lat are curves in metres
    return shapely.transform(geom, lambda xy: np.column_stack(_to_laea.transform(xy[:, 0], xy[:, 1])))


def area_km2(geom):
    return to_metric(geom).area / 1e6


# ---------------------------------------------------------------------------------------------
# Land and coastline (OSM coastline-derived land polygons)
def coast_lines(poly, frame_bounds):
    """Polygon rings minus the stretches that lie on the clipping frame (fast, coordinate based)."""
    x0, y0, x1, y1 = frame_bounds
    eps = 1e-9
    out = []
    for ring in shapely.get_rings(poly):
        xy = shapely.get_coordinates(ring)
        on_x = (np.abs(xy[:, 0] - x0) < eps) | (np.abs(xy[:, 0] - x1) < eps)
        on_y = (np.abs(xy[:, 1] - y0) < eps) | (np.abs(xy[:, 1] - y1) < eps)
        a, b = xy[:-1], xy[1:]
        # a segment is on the frame if both ends share the same frame edge
        frame_seg = ((np.abs(a[:, 0] - x0) < eps) & (np.abs(b[:, 0] - x0) < eps)) | \
                    ((np.abs(a[:, 0] - x1) < eps) & (np.abs(b[:, 0] - x1) < eps)) | \
                    ((np.abs(a[:, 1] - y0) < eps) & (np.abs(b[:, 1] - y0) < eps)) | \
                    ((np.abs(a[:, 1] - y1) < eps) & (np.abs(b[:, 1] - y1) < eps))
        del on_x, on_y
        if not frame_seg.any():
            out.append(LineString(xy))
            continue
        keep = ~frame_seg
        idx = np.flatnonzero(keep)
        if idx.size == 0:
            continue
        # consecutive kept segments form one line
        breaks = np.flatnonzero(np.diff(idx) > 1)
        starts = np.concatenate([[idx[0]], idx[breaks + 1]])
        ends = np.concatenate([idx[breaks], [idx[-1]]])
        for st, en in zip(starts, ends):
            out.append(LineString(xy[st:en + 2]))
    return shapely.MultiLineString(out) if out else None


def step_land():
    w_land, w_coast = Writer("land"), Writer("coastline")
    # Detailed land from zoom 8 on, simplified land below it.
    for ft in read_seq(RAW / "land" / "land_simplified.geojsonl"):
        g = shape(ft["geometry"])
        w_land.add(g, {"src": "osm"}, minzoom=0, maxzoom=7)
    for ft in read_seq(RAW / "land" / "land.geojsonl"):
        g = shape(ft["geometry"])
        if g.is_empty:
            continue
        w_land.add(g, {"src": "osm"}, minzoom=8)
        w_coast.add(coast_lines(g, C.BBOX), {"src": "osm"}, minzoom=6)
    w_land.close()
    w_coast.close()


class LandIndex:
    """Answers: is this lon/lat point at sea, or on land within SHORE_KEEP_M of the coast?

    Land polygons can be continent-sized, so the coastline is cut into short pieces with their own
    spatial index; a distance test then touches only the few pieces near the point."""

    def __init__(self):
        geoms = [to_metric(shape(ft["geometry"])) for ft in read_seq(RAW / "land" / "land.geojsonl")]
        geoms = [g for g in geoms if not g.is_empty]
        for g in geoms:
            shapely.prepare(g)
        self.land = geoms
        self.land_tree = shapely.STRtree(geoms)
        pieces = []
        for g in geoms:
            for ring in shapely.get_rings(g):
                xy = shapely.get_coordinates(ring)
                for i in range(0, len(xy) - 1, 200):
                    seg = xy[i:i + 201]
                    if len(seg) >= 2:
                        pieces.append(LineString(seg))
        self.coast_tree = shapely.STRtree(pieces)

    def keep(self, lon, lat):
        x, y = _to_laea.transform(lon, lat)
        p = Point(x, y)
        if len(self.land_tree.query(p, predicate="intersects")) == 0:
            return True
        return len(self.coast_tree.query(p, predicate="dwithin", distance=C.SHORE_KEEP_M)) > 0


# ---------------------------------------------------------------------------------------------
# Depth areas and contours
def step_depth():
    A = load_areas()
    aoi, fi_zone = A["aoi"], A["fi_zone"]
    shapely.prepare(fi_zone)
    tdir = RAW / "traficom"
    edir = RAW / "emodnet"
    mdir = C.WORK / "depth"
    mdir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    # 1. Finnish depth areas inside Finnish waters (Traficom), and their coverage for masking EMODnet.
    w_fi_area, w_fi_cnt = Writer("depth_fi_area"), Writer("depth_fi_contour")
    cov_path = mdir / "traficom_cover.geojsonl"
    n_fi = 0
    with open(cov_path, "w", encoding="utf-8") as cov:
        # Features are selected by a representative point instead of being clipped: clipping
        # 150 000 polygons against the detailed zone outline takes far too long, and the zone
        # boundary lies at sea (borders) or on the coast (lakes are left out), so nothing is lost.
        for ft in read_seq(tdir / "DepthArea_A.geojsonl"):
            if not ft.get("geometry"):
                continue
            g = shape(ft["geometry"])
            if g.is_empty or not fi_zone.contains(g.representative_point()):
                continue
            p = ft["properties"]
            d1, d2 = num(p.get("DRVAL1")), num(p.get("DRVAL2"))
            w_fi_area.add(g, {"drval1": d1, "drval2": d2, "src": "traficom"}, minzoom=FI_DETAIL_ZOOM)
            cov.write(json.dumps({"type": "Feature", "properties": {}, "geometry": mapping(g)}) + "\n")
            n_fi += 1
    for ft in read_seq(tdir / "DepthContour_L.geojsonl"):
        if not ft.get("geometry"):
            continue
        g = shape(ft["geometry"])
        if g.is_empty or not fi_zone.contains(g.representative_point()):
            continue
        v = num(ft["properties"].get("VALDCO"))
        w_fi_cnt.add(g, {"depth": v, "src": "traficom"}, minzoom=max(FI_DETAIL_ZOOM + 2, contour_minzoom(v)))
    w_fi_area.close()
    w_fi_cnt.close()
    LOG["traficom_depth_areas_used"] = n_fi
    say("  Traficom done (%.0f s)" % (time.time() - t0))

    # 2. EMODnet grid: depth in metres, masked to the area of interest minus Finnish coverage.
    vrt = mdir / "emodnet.vrt"
    run(["gdalbuildvrt", "-overwrite", vrt] + sorted(edir.glob("chunk_*.tif")))
    src = gdal.Open(str(vrt))
    band = src.GetRasterBand(1)
    nod = band.GetNoDataValue()
    arr = band.ReadAsArray().astype(np.float32)
    if nod is not None:
        arr[arr == nod] = np.nan
    arr[~np.isfinite(arr)] = np.nan
    gt, W, H = src.GetGeoTransform(), src.RasterXSize, src.RasterYSize

    def burn(geom_or_file, all_touched=False):
        drv = gdal.GetDriverByName("MEM")
        ds = drv.Create("", W, H, 1, gdal.GDT_Byte)
        ds.SetGeoTransform(gt)
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(4326)
        ds.SetProjection(sr.ExportToWkt())
        opts = ["ALL_TOUCHED=TRUE"] if all_touched else []
        if isinstance(geom_or_file, Path):
            vds = ogr.Open(str(geom_or_file))
        else:
            vds = ogr.GetDriverByName("Memory").CreateDataSource("m")
            lyr = vds.CreateLayer("m", sr, ogr.wkbUnknown)
            f = ogr.Feature(lyr.GetLayerDefn())
            f.SetGeometry(ogr.CreateGeometryFromWkb(shapely.to_wkb(geom_or_file)))
            lyr.CreateFeature(f)
        gdal.RasterizeLayer(ds, [1], vds.GetLayer(0), burn_values=[1], options=opts)
        return ds.GetRasterBand(1).ReadAsArray().astype(bool)

    in_aoi = burn(aoi)
    fi_cov = burn(cov_path, all_touched=True) & burn(fi_zone, all_touched=True)
    sea = np.isfinite(arr) & in_aoi
    # Sign: EMODnet stores elevation (negative below sea level). Detect rather than assume.
    sample = arr[sea]
    sample = sample[np.isfinite(sample)]
    sign = -1.0 if np.nanmedian(sample) < 0 else 1.0
    LOG["emodnet"] = {"grid": [W, H], "sign": sign, "median_raw": float(np.nanmedian(sample)),
                      "fi_masked_cells": int(fi_cov.sum()), "aoi_cells": int(in_aoi.sum())}
    depth = sign * arr
    del arr
    depth[~sea | (depth < 0)] = np.nan

    def write_tif(path, a):
        drv = gdal.GetDriverByName("GTiff")
        ds = drv.Create(str(path), W, H, 1, gdal.GDT_Float32, ["COMPRESS=DEFLATE", "TILED=YES", "BIGTIFF=IF_SAFER"])
        ds.SetGeoTransform(gt)
        ds.SetProjection(src.GetProjection())
        b = ds.GetRasterBand(1)
        b.SetNoDataValue(-9999)
        b.WriteArray(np.where(np.isfinite(a), a, -9999).astype(np.float32))
        ds = None

    # Overview (zoom <= FI_DETAIL_ZOOM-1): EMODnet everywhere, at a quarter of the resolution.
    # Detail: EMODnet outside Finnish coverage, full resolution.
    write_tif(mdir / "emodnet_overview_full.tif", depth)
    run(["gdal_translate", "-q", "-r", "average", "-outsize", "25%", "25%", "-co", "COMPRESS=DEFLATE",
         mdir / "emodnet_overview_full.tif", mdir / "emodnet_overview.tif"])
    (mdir / "emodnet_overview_full.tif").unlink()
    w_area, w_cnt = Writer("depth_area"), Writer("depth_contour")
    depth[fi_cov] = np.nan
    write_tif(mdir / "emodnet_detail.tif", depth)
    has_data = np.isfinite(depth)
    del depth
    say("  depth rasters written (%.0f s)" % (time.time() - t0))

    top = C.DEPTH_LEVELS[-1]
    for part, zmin, zmax in (("overview", None, FI_DETAIL_ZOOM - 1), ("detail", FI_DETAIL_ZOOM, None)):
        tif = mdir / ("emodnet_%s.tif" % part)
        polys, lines = contour_chunks(tif, mdir / ("chunks_" + part), has_data if part == "detail" else None)
        for poly in polys:
            for ft in ogr_features(poly):
                d1, d2 = snap_level(ft["dmin"]), snap_level(ft["dmax"])
                if d1 is None or (d2 is not None and d2 <= d1):
                    continue
                w_area.add(ft["geom"], {"drval1": d1, "drval2": None if d1 >= top else d2, "src": "emodnet"},
                           minzoom=max(zmin or 0, depth_minzoom(d1)), maxzoom=zmax)
        for line in lines:
            for ft in ogr_features(line):
                v = snap_level(ft["depth"])
                w_cnt.add(ft["geom"], {"depth": v, "src": "emodnet"}, minzoom=max(zmin or 0, contour_minzoom(v)),
                          maxzoom=zmax)
        say("  EMODnet %s contours done (%.0f s)" % (part, time.time() - t0))
    w_area.close()
    w_cnt.close()


FI_DETAIL_ZOOM = 9   # Finnish (Traficom) depth data replaces EMODnet from this zoom on
CHUNK_PX = int(__import__("os").environ.get("BSC_CHUNK_PX", 2048))


def contour_chunks(tif, outdir, has_data=None):
    """Depth areas and contour lines with gdal_contour, in windows of CHUNK_PX pixels run in parallel.
    Polygon assembly slows down sharply with polygon size, so a single run over the whole Baltic takes
    very long. Neighbouring windows share one pixel column/row, so the pieces meet without gaps."""
    import concurrent.futures as cf
    outdir.mkdir(parents=True, exist_ok=True)
    ds = gdal.Open(str(tif))
    W, H = ds.RasterXSize, ds.RasterYSize
    ds = None
    levels = [str(v) for v in C.DEPTH_LEVELS]
    jobs = []
    for y in range(0, H - 1, CHUNK_PX):
        for x in range(0, W - 1, CHUNK_PX):
            w, h = min(CHUNK_PX + 1, W - x), min(CHUNK_PX + 1, H - y)
            if has_data is not None and not has_data[y:y + h, x:x + w].any():
                continue
            jobs.append((x, y, w, h))

    def one(job):
        x, y, w, h = job
        stem = outdir / ("c_%05d_%05d" % (x, y))
        vrt, poly, line = stem.with_suffix(".vrt"), Path(str(stem) + "_a.gpkg"), Path(str(stem) + "_l.gpkg")
        for p in (poly, line):
            if p.exists():
                p.unlink()
        subprocess.run(["gdal_translate", "-q", "-of", "VRT", "-srcwin", str(x), str(y), str(w), str(h), str(tif), str(vrt)], check=True)
        subprocess.run(["gdal_contour", "-q", "-p", "-amin", "dmin", "-amax", "dmax", "-fl"] + levels + [str(vrt), str(poly)], check=True)
        subprocess.run(["gdal_contour", "-q", "-a", "depth", "-fl"] + levels[1:] + [str(vrt), str(line)], check=True)
        return poly, line

    with cf.ThreadPoolExecutor(4) as ex:
        res = list(ex.map(one, jobs))
    say("  %s: %d windows" % (tif.name, len(jobs)))
    return [r[0] for r in res], [r[1] for r in res]


def ogr_features(path):
    ds = ogr.Open(str(path))
    lyr = ds.GetLayer(0)
    names = [lyr.GetLayerDefn().GetFieldDefn(i).GetName() for i in range(lyr.GetLayerDefn().GetFieldCount())]
    for f in lyr:
        g = f.GetGeometryRef()
        if g is None:
            continue
        d = {n: f.GetField(n) for n in names}
        d["geom"] = shapely.from_wkb(bytes(g.ExportToWkb()))
        yield d


def snap_level(v):
    """gdal_contour writes the band limits; snap them to our level list (the open ends become None)."""
    if v is None:
        return None
    for lv in C.DEPTH_LEVELS:
        if abs(v - lv) < 1e-3:
            return lv
    return None if v > C.DEPTH_LEVELS[-1] else max([lv for lv in C.DEPTH_LEVELS if lv <= v], default=0)


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def depth_minzoom(d1):
    if d1 is None:
        return 6
    return 0 if d1 >= 20 else 3 if d1 >= 10 else 5


def contour_minzoom(v):
    if v is None:
        return 11
    return 5 if v >= 50 else 7 if v >= 20 else 9 if v >= 10 else 10


# ---------------------------------------------------------------------------------------------
# Seamarks, lights and hazards
VAYLA_NAVL = {1: "port", 2: "starboard", 3: "north", 4: "south", 5: "west", 6: "east",
              7: "isolated_danger", 8: "safe_water", 9: "special"}


def vayla_kind(t, alityyppi):
    t = (t or "").lower()
    if "viitta" in t:
        return "spar"
    if "poiju" in t:
        return "buoy"
    if "kummeli" in t:
        return "cairn"
    if "linjamerkki" in t:
        return "leading_mark"
    if "merimajakka" in t:
        return "lighthouse"
    if "tunnusmajakka" in t:
        return "daymark"
    if "tutkamerkki" in t:
        return "racon"
    if "loisto" in t:
        return "light"
    if "reunamerkki" in t:
        return "beacon"
    return "other"


LIGHT_COLOUR_FI = {"v": "W", "p": "R", "vi": "G", "k": "Y", "si": "Bu"}
OSM_COLOUR = {"white": "W", "red": "R", "green": "G", "yellow": "Y", "blue": "Bu", "orange": "Or", "violet": "Vi"}


def light_label(chr_, colours, period=None, group=None):
    """Light description in chart style: 'Fl (2) 6 s' + 'WRG' -> 'Fl(2) WRG 6s',
    'VQ (6) + LFl 10 s' + 'W' -> 'VQ(6)+LFl W 10s'."""
    chr_ = re.sub(r"\s+", " ", (chr_ or "").strip())
    cols = "".join(colours)
    if not chr_ and not cols:
        return None
    m = re.match(r"^(.*?)\s*(\d+(?:[.,]\d+)?)\s*s\.?$", chr_)
    body, per = (m.group(1), m.group(2)) if m else (chr_, None)
    per = per or period
    body = body.replace(" ", "")
    if group and body and "(" not in body:
        body += "(%s)" % group
    parts = [body, cols, (str(per).replace(",", ".") + "s") if per else ""]
    return " ".join(p for p in parts if p) or None


def sector_geoms(lon, lat, start, end, radius_m=250.0):
    """Arc and two limit legs for a light sector. Angles are bearings from seaward towards the
    light (as in the lists of lights), so the arc lies on the opposite side of the light."""
    a0 = (start + 180.0) % 360.0
    a1 = (end + 180.0) % 360.0
    span = (a1 - a0) % 360.0 or 360.0
    n = max(8, int(span / 4))
    kx = 1.0 / (111320.0 * math.cos(math.radians(lat)))
    ky = 1.0 / 110540.0

    def pt(bearing, r):
        b = math.radians(bearing)
        return (lon + r * math.sin(b) * kx, lat + r * math.cos(b) * ky)

    arc = LineString([pt(a0 + span * i / n, radius_m) for i in range(n + 1)])
    legs = [] if span >= 359.9 else [LineString([(lon, lat), pt(a0, radius_m * 1.6)]),
                                     LineString([(lon, lat), pt(a1, radius_m * 1.6)])]
    return arc, legs


def osm_category(t, tags):
    if t.endswith("_lateral"):
        c = tags.get("seamark:%s:category" % t, "")
        if "port" in c:
            return "port"
        if "starboard" in c:
            return "starboard"
        colour = tags.get("seamark:%s:colour" % t, "")
        return "port" if colour.startswith("red") else "starboard" if colour.startswith("green") else "none"
    if t.endswith("_cardinal"):
        c = tags.get("seamark:%s:category" % t, "")
        return c if c in ("north", "south", "east", "west") else "none"
    for key, cat in (("isolated_danger", "isolated_danger"), ("safe_water", "safe_water"), ("special_purpose", "special")):
        if t.endswith(key):
            return cat
    return "none"


def osm_kind(t, tags):
    if t.startswith("buoy_"):
        shp = tags.get("seamark:%s:shape" % t, "")
        return "spar" if shp in ("spar", "pillar") else "buoy"
    if t.startswith("beacon_"):
        return "beacon"
    if t == "light_major":
        return "lighthouse"
    if t in ("light_minor",):
        return "light"
    if t in ("light_vessel", "light_float"):
        return "light_float"
    if t == "landmark":
        return "daymark"
    if t == "radar_transponder":
        return "racon"
    return None


HAZARDS = {"rock", "wreck", "obstruction"}


def osm_lights(tags):
    """Return (label, colours list, sectors list[(start,end,colour)]) from OSM seamark:light tags."""
    sectors, colours = [], []
    idx = sorted({k.split(":")[2] for k in tags if re.match(r"^seamark:light:\d+:", k)}, key=int)
    chr_ = tags.get("seamark:light:character")
    period = tags.get("seamark:light:period")
    group = tags.get("seamark:light:group")
    for i in idx:
        p = "seamark:light:%s:" % i
        col = OSM_COLOUR.get(tags.get(p + "colour", "").split(";")[0])
        chr_ = chr_ or tags.get(p + "character")
        period = period or tags.get(p + "period")
        group = group or tags.get(p + "group")
        s, e = num(tags.get(p + "sector_start")), num(tags.get(p + "sector_end"))
        if col and col not in colours:
            colours.append(col)
        if s is not None and e is not None and col:
            sectors.append((s, e, col))
    for c in tags.get("seamark:light:colour", "").split(";"):
        c = OSM_COLOUR.get(c.strip())
        if c and c not in colours:
            colours.append(c)
    lit = bool(chr_ or colours or sectors)
    return lit, light_label(chr_, colours, period, group) if lit else None, colours, sectors


def osm_range(tags):
    """Longest nominal range (NM) over seamark:light:range and the numbered light entries."""
    vals = [num(v) for k, v in tags.items() if re.match(r"^seamark:light:(\d+:)?range$", k)]
    vals = [v for v in vals if v is not None]
    return max(vals) if vals else None


def step_marks():
    A = load_areas()
    aoi, fi_zone = A["aoi"], A["fi_zone"]
    shapely.prepare(aoi)
    shapely.prepare(fi_zone)
    land = LandIndex()
    w_mark, w_light, w_sect, w_haz = Writer("seamark"), Writer("light"), Writer("light_sector"), Writer("hazard")
    vd = RAW / "vayla"
    dropped = {"outside": 0, "inland": 0}

    def ok(lon, lat):
        p = Point(lon, lat)
        if not aoi.contains(p):
            dropped["outside"] += 1
            return False
        if not land.keep(lon, lat):
            dropped["inland"] += 1
            return False
        return True

    # --- Finland: Väylävirasto aids to navigation, lights and sectors
    for ft in read_seq(vd / "turvalaitteet_uusi.geojsonl"):
        pt = point_of(ft)
        if pt is None or not ok(pt.x, pt.y):
            continue
        lon, lat = pt.x, pt.y
        p = ft["properties"]
        cat = VAYLA_NAVL.get(int(p.get("navigointilajikoodi") or 0), "none")
        kind = vayla_kind(p.get("turvalaitetyyppifi"), p.get("alityyppi"))
        w_mark.add(Point(lon, lat), {"kind": kind, "cat": cat, "name": p.get("nimifi") or p.get("nimisv"),
                                     "ref": p.get("turvalaitenumero"), "lit": p.get("valaistu") == "K",
                                     "topmark": p.get("huippumerkki") == "K", "src": "fi"},
                   minzoom=mark_minzoom(kind))
    sect = {}
    for ft in read_seq(vd / "valosektorit_uusi.geojsonl"):
        p = ft["properties"]
        sect.setdefault(p.get("loisto"), []).append((num(p.get("alkukulma")), num(p.get("loppukulma")),
                                                     LIGHT_COLOUR_FI.get(str(p.get("vari") or "").lower(), "W")))
    for ft in read_seq(vd / "loistot_uusi.geojsonl"):
        pt = point_of(ft)
        if pt is None or not ok(pt.x, pt.y):
            continue
        lon, lat = pt.x, pt.y
        p = ft["properties"]
        secs = [s for s in sect.get(p.get("id"), []) if s[0] is not None and s[1] is not None]
        cols = []
        for s in secs:
            if s[2] not in cols:
                cols.append(s[2])
        major = (p.get("laatu") or "").lower().startswith("pää")
        w_light.add(Point(lon, lat), {"label": light_label(p.get("viralvalotunnuse"), cols), "colour": "".join(cols) or "W",
                                      "height": num(p.get("korkeusvedesta")), "range": num(p.get("maantietkanto")),
                                      "major": major, "ref": p.get("turvalaitenumero"), "src": "fi"},
                    minzoom=8 if major else 10)
        for s0, s1, col in secs:
            arc, legs = sector_geoms(lon, lat, s0, s1)
            w_sect.add(arc, {"colour": col, "part": "arc", "src": "fi"}, minzoom=12)
            for leg in legs:
                w_sect.add(leg, {"colour": col, "part": "limit", "src": "fi"}, minzoom=13)

    # --- Estonia: Transpordiamet aids to navigation register (names carry the type; no light data)
    ee_zone = A.get("ee_zone")
    if ee_zone is not None and not ee_zone.is_empty:
        shapely.prepare(ee_zone)
    # The register's names give the category for cardinals, isolated dangers and many lateral marks, but
    # numbered channel marks ('Heltermaa 3') only carry a number. For those the category of the OSM mark at
    # the same position (within about 60 m) is used: the position stays the authority's.
    ee_osm, ee_osm_cat = [], []
    if ee_zone is not None and not ee_zone.is_empty and (RAW / "osm" / "seamark.geojsonl").exists():
        ex0, ey0, ex1, ey1 = ee_zone.bounds
        for ft in read_seq(RAW / "osm" / "seamark.geojsonl"):
            t = ft["properties"].get("seamark:type", "")
            if not (t.startswith("buoy_") or t.startswith("beacon_")) or not ft.get("geometry"):
                continue
            pt = point_of(ft)
            if pt is None or not (ex0 <= pt.x <= ex1 and ey0 <= pt.y <= ey1):
                continue
            c = osm_category(t, ft["properties"])
            if c and c != "none":
                ee_osm.append(pt)
                ee_osm_cat.append(c)
    ee_tree = shapely.STRtree(ee_osm) if ee_osm else None
    n_ee = n_ee_osmcat = 0
    for layer in ("Beacon", "Buoy"):
        p_ = RAW / "estonia" / (layer + ".geojsonl")
        if not p_.exists():
            continue
        for ft in read_seq(p_):
            pt = point_of(ft)
            if pt is None or not ok(pt.x, pt.y):
                continue
            name = ft["properties"].get("geographicalname_geographicalname_spelling_spellingofname_text")
            kind, cat = estonian_mark(name, layer)
            if cat == "none" and kind in ("buoy", "spar", "beacon") and ee_tree is not None:
                i = ee_tree.query_nearest(pt, max_distance=0.0008)
                if len(i):
                    cat = ee_osm_cat[int(i[0])]
                    n_ee_osmcat += 1
            w_mark.add(pt, {"kind": kind, "cat": cat, "name": name, "ref": ft["properties"].get("inspireid_identifier_localid"),
                            "src": "ee"}, minzoom=mark_minzoom(kind))
            n_ee += 1
    LOG["estonia_marks"], LOG["estonia_category_from_osm"] = n_ee, n_ee_osmcat
    use_ee = n_ee > 0 and ee_zone is not None and not ee_zone.is_empty

    # --- Germany: BSH navigation marks and lights (S-57 attributes)
    de_zone = A.get("de_zone")
    if de_zone is not None and not de_zone.is_empty:
        shapely.prepare(de_zone)
    gd = RAW / "germany"
    n_de = n_de_l = 0
    in_de = (lambda pt: de_zone.contains(pt)) if de_zone is not None and not de_zone.is_empty else (lambda pt: False)

    def xy5(pt):
        return round(pt.x, 5), round(pt.y, 5)
    # BSH covers the whole region (Russian, Danish, Swedish lights too); only German waters are taken from
    # it. Wind turbines are landmarks with lights in S-57 (CATLMK 19): neither marks nor lights here.
    wind = set()
    if (gd / "LNDMRK_lndmrk.geojsonl").exists():
        for ft in read_seq(gd / "LNDMRK_lndmrk.geojsonl"):
            pt = point_of(ft)
            if pt is not None and "19" in str(ft["properties"].get("catlmk") or "").split(","):
                wind.add(xy5(pt))
    for cl in DE_CLASS_KIND:
        pm = gd / ("%s_%s.geojsonl" % (cl, cl.lower()))
        pl = gd / ("%s_lights.geojsonl" % cl)
        lit_at = {}
        if pl.exists():
            for ft in read_seq(pl):
                pt = point_of(ft)
                if pt is None or not in_de(pt) or not ok(pt.x, pt.y) or xy5(pt) in wind:
                    continue
                p = ft["properties"]
                cols = s57_colours(p.get("colour"))
                lbl = light_label(s57_litchr(p.get("litchr")) + (p.get("siggrp") or "").replace("()", "").replace("(1)", ""), cols,
                                  p.get("sigper"))
                rng = num(p.get("valnmr"))
                major = (rng or 0) >= 15
                w_light.add(pt, {"label": lbl, "colour": "".join(cols) or "W", "height": num(p.get("height")),
                                 "range": rng, "major": major, "src": "de"}, minzoom=8 if major else 10)
                s1, s2 = num(p.get("sectr1")), num(p.get("sectr2"))
                if s1 is not None and s2 is not None:
                    arc, legs = sector_geoms(pt.x, pt.y, s1, s2)
                    w_sect.add(arc, {"colour": cols[0] if cols else "W", "part": "arc", "src": "de"}, minzoom=12)
                    for leg in legs:
                        w_sect.add(leg, {"colour": cols[0] if cols else "W", "part": "limit", "src": "de"}, minzoom=13)
                k = xy5(pt)
                lit_at[k] = max(lit_at.get(k, 0), rng or 0.001)
                n_de_l += 1
        if not pm.exists():
            continue
        for ft in read_seq(pm):
            pt = point_of(ft)
            if pt is None or not in_de(pt) or not ok(pt.x, pt.y) or xy5(pt) in wind:
                continue
            p = ft["properties"]
            rng = lit_at.get(xy5(pt))
            kind, cat = s57_mark(cl, p, rng)
            if kind is None:
                continue
            w_mark.add(pt, {"kind": kind, "cat": cat, "name": p.get("objnam"), "lit": rng is not None, "src": "de"},
                       minzoom=mark_minzoom(kind))
            n_de += 1
    LOG["germany_marks"], LOG["germany_lights"] = n_de, n_de_l
    use_de = n_de > 0 and de_zone is not None and not de_zone.is_empty

    # --- OpenStreetMap seamarks (outside Finnish waters for marks and lights, everywhere for hazards)
    for ft in read_seq(RAW / "osm" / "seamark.geojsonl"):
        g = shape(ft["geometry"]) if ft.get("geometry") else None
        if g is None or g.is_empty:
            continue
        tags = ft["properties"]
        t = tags.get("seamark:type", "")
        pt = g if g.geom_type == "Point" else g.representative_point()
        lon, lat = pt.x, pt.y
        name = tags.get("seamark:name") or tags.get("name")
        if t in HAZARDS:
            if not ok(lon, lat):
                continue
            wl = tags.get("seamark:%s:water_level" % t)
            w_haz.add(g if g.geom_type == "Point" else pt,
                      {"kind": t, "water_level": wl, "name": name, "src": "osm"}, minzoom=13 if t == "rock" else 12)
            continue
        kind = osm_kind(t, tags)
        lit, label, cols, secs = osm_lights(tags)
        if kind is None and not lit:
            continue
        if fi_zone.contains(pt) or (use_de and de_zone.contains(pt)) or not ok(lon, lat):
            continue
        if kind is not None and not (use_ee and ee_zone.contains(pt)):
            w_mark.add(pt, {"kind": kind, "cat": osm_category(t, tags), "name": name,
                            "ref": tags.get("seamark:light:reference") or tags.get("seamark:reference"),
                            "lit": lit, "topmark": any(k.startswith("seamark:topmark") for k in tags), "src": "osm"},
                       minzoom=mark_minzoom(kind))
        if lit:
            rng = osm_range(tags)
            # light_major is used unevenly across countries (rare in Latvia), so lighthouses and long-range
            # lights count as major too
            major = (t in ("light_major", "light_vessel") or tags.get("man_made") == "lighthouse"
                     or (rng or 0) >= 15)
            w_light.add(pt, {"label": label, "colour": "".join(cols) or "W",
                             "height": num(tags.get("seamark:light:height")), "range": rng,
                             "major": major, "src": "osm"}, minzoom=8 if major else 10)
            for s0, s1, col in secs:
                arc, legs = sector_geoms(lon, lat, s0, s1)
                w_sect.add(arc, {"colour": col, "part": "arc", "src": "osm"}, minzoom=12)
                for leg in legs:
                    w_sect.add(leg, {"colour": col, "part": "limit", "src": "osm"}, minzoom=13)
    for w in (w_mark, w_light, w_sect, w_haz):
        w.close()
    LOG["marks_dropped"] = dropped


def point_of(ft):
    g = ft.get("geometry")
    if not g:
        return None
    g = shape(g)
    if g.is_empty:
        return None
    if g.geom_type == "MultiPoint":
        g = g.geoms[0]
    return g if g.geom_type == "Point" else g.representative_point()


EE_CARDINAL = {"põhja": "north", "lõuna": "south", "ida": "east", "lääne": "west"}

# S-57 codes used by the BSH data
DE_CLASS_KIND = {"BOYLAT": "lat", "BOYCAR": "car", "BOYISD": "isolated_danger", "BOYSAW": "safe_water",
                 "BOYSPP": "special", "BCNLAT": "lat", "BCNCAR": "car", "BCNISD": "isolated_danger",
                 "BCNSPP": "special", "LNDMRK": "landmark"}
S57_COLOUR = {"1": "W", "3": "R", "4": "G", "5": "Bu", "6": "Y", "11": "Or", "12": "Mag"}
S57_LITCHR = {"1": "F", "2": "Fl", "3": "LFl", "4": "Q", "5": "VQ", "6": "UQ", "7": "Iso", "8": "Oc", "9": "IQ",
              "10": "IVQ", "11": "IUQ", "12": "Mo", "13": "FFl", "14": "Fl+LFl", "15": "OcFl", "16": "FLFl",
              "17": "Al.Oc", "18": "Al.LFl", "19": "Al.Fl", "20": "Al.Gr", "25": "Q+LFl", "26": "VQ+LFl",
              "27": "UQ+LFl", "28": "Al", "29": "Al.FFl"}


def s57_colours(v):
    out = []
    for c in str(v or "").split(","):
        c = S57_COLOUR.get(c.strip())
        if c and c not in out:
            out.append(c)
    return out


def s57_litchr(v):
    return S57_LITCHR.get(str(v or "").strip(), "")


def s57_mark(cl, p, lit):
    """(kind, IALA category) for a BSH S-57 object. lit: nominal range of the light at the object (NM, a
    small positive number if unknown) or None if the object carries no light."""
    t = DE_CLASS_KIND[cl]
    if cl == "LNDMRK":
        if lit is None:
            return None, None          # towers, churches etc. without a light are not chart aids here
        cats = str(p.get("catlmk") or "").split(",")
        if "19" in cats:               # wind turbine
            return None, None
        # a lighthouse is a tower carrying a light of some range; a light on a mast, pile or pierhead is a light
        if lit >= 15 or ("17" in cats and lit >= 10):
            return "lighthouse", "none"
        return "light", "none"
    if cl.startswith("BOY"):
        kind = "spar" if str(p.get("boyshp")) in ("4", "5") else "buoy"
    else:
        kind = "beacon"
    if t == "lat":
        c = str(p.get("catlam") or "")
        cat = {"1": "port", "2": "starboard", "3": "port", "4": "starboard"}.get(c, "none")
    elif t == "car":
        cat = {"1": "north", "2": "east", "3": "south", "4": "west"}.get(str(p.get("catcam") or ""), "none")
    else:
        cat = t
    return kind, cat


def estonian_mark(name, layer):
    """Type and IALA category of an Estonian aid from its official name (the register's WFS has no
    separate type fields). Examples: 'Sillamäe sadama parema külje poi' = starboard buoy,
    'Keri lõunatooder' = south cardinal spar, 'Kunda teljepoi' = safe water buoy,
    'Miiduranna vraki eraldiasuva ohu tooder' = isolated danger, 'Kunda sihi alumine tulepaak' = front
    leading light, 'Uhtju tulepaagi radarivastaja' = racon, 'Narva-Jõesuu tuletorn' = lighthouse."""
    n = (name or "").lower()
    if layer == "Buoy":
        kind = "spar" if "tooder" in n else "buoy"
    elif "radarivastaja" in n:
        kind = "racon"
    elif "sihi" in n or "siht" in n:
        kind = "leading_mark"
    elif "tuletorn" in n:
        kind = "lighthouse"
    elif "tulepaak" in n:
        kind = "light"
    elif "päevamärk" in n:
        kind = "daymark"
    else:
        kind = "beacon"
    cat = "none"
    if "parema" in n:
        cat = "starboard"
    elif "vasaku" in n:
        cat = "port"
    else:
        m = re.search(r"(põhja|lõuna|ida|lääne)(poi|tooder)", n)
        m2 = re.search(r"\b([nesw]) (poi|tooder)\b", n)
        if m:
            cat = EE_CARDINAL[m.group(1)]
        elif m2:
            cat = {"n": "north", "e": "east", "s": "south", "w": "west"}[m2.group(1)]
        elif re.search(r"eraldiasuva ohu|ohu ?(poi|tooder)|üksikohu", n):
            cat = "isolated_danger"
        elif re.search(r"telje ?(poi|tooder)|telg", n):
            cat = "safe_water"
        elif re.search(r"eri ?(poi|tooder)|piirirežiimi", n):
            cat = "special"
    return kind, cat


def mark_minzoom(kind):
    return {"lighthouse": 8, "daymark": 9, "light": 10, "racon": 10, "leading_mark": 11, "cairn": 11}.get(kind, 11)


# ---------------------------------------------------------------------------------------------
# Fairways, navigation lines, leading lines and traffic separation
def vayla_name(s):
    m = re.match(r"^\[\s*\d+\s*:\s*(.*?)\]", s or "")
    return m.group(1).strip() if m else None


def step_routes():
    A = load_areas()
    aoi, fi_zone = A["aoi"], A["fi_zone"]
    shapely.prepare(aoi)
    shapely.prepare(fi_zone)
    vd = RAW / "vayla"
    w_fw, w_nav, w_lead, w_tss = Writer("fairway"), Writer("navline"), Writer("leading_line"), Writer("tss")

    def clip(g):
        """Keep features whose representative point is in the area (no costly clipping)."""
        if g.is_empty or not aoi.contains(g.representative_point()):
            return None
        return g

    for ft in read_seq(vd / "vaylaalueet_uusi.geojsonl"):
        g = clip(shape(ft["geometry"]))
        if g is None:
            continue
        p = ft["properties"]
        w_fw.add(g, {"depth": num(p.get("mitoitussyvays")), "kind": p.get("tyyppi"), "name": vayla_name(p.get("vaylan_nimi")),
                     "src": "fi"}, minzoom=9)
    for ft in read_seq(vd / "navigointilinjat_uusi.geojsonl"):
        g = clip(shape(ft["geometry"]))
        if g is None:
            continue
        p = ft["properties"]
        w_nav.add(g, {"depth": num(p.get("mitoitussyvays")), "bearing": num(p.get("tosisuunta")),
                      "kind": p.get("tyyppi"), "name": vayla_name(p.get("vaylan_nimi")), "src": "fi"}, minzoom=10)
    for ft in read_seq(vd / "taululinjat_uusi.geojsonl"):
        g = clip(shape(ft["geometry"]))
        if g is None:
            continue
        p = ft["properties"]
        w_lead.add(g, {"bearing": num(p.get("suunta")), "src": "fi"}, minzoom=10)

    ed = RAW / "estonia"
    nm = "geographicalname_geographicalname_spelling_spellingofname_text"
    if (ed / "FairwayArea.geojsonl").exists():
        for ft in read_seq(ed / "FairwayArea.geojsonl"):
            g = clip(shape(ft["geometry"])) if ft.get("geometry") else None
            if g is not None:
                w_fw.add(g, {"kind": "fairway", "name": ft["properties"].get(nm), "src": "ee"}, minzoom=9)
    if (ed / "WaterwayLink.geojsonl").exists():
        for ft in read_seq(ed / "WaterwayLink.geojsonl"):
            g = clip(shape(ft["geometry"])) if ft.get("geometry") else None
            if g is not None:
                w_nav.add(g, {"kind": "fairway", "name": ft["properties"].get(nm), "src": "ee"}, minzoom=10)

    for ft in read_seq(RAW / "osm" / "seamark.geojsonl"):
        if not ft.get("geometry") or ft["geometry"]["type"] == "Point":
            continue
        tags = ft["properties"]
        t = tags.get("seamark:type", "")
        g = shape(ft["geometry"])
        if t.startswith("separation_") or t in ("inshore_traffic_zone", "precautionary_area"):
            g = clip(g)
            if g is not None:
                w_tss.add(g, {"kind": t, "src": "osm"}, minzoom=6)
            continue
        if t not in ("fairway", "recommended_track", "navigation_line", "dredged_area"):
            continue
        g = clip(g)
        if g is None or fi_zone.intersects(g.centroid):
            continue
        if t in ("fairway", "dredged_area") and g.geom_type in ("Polygon", "MultiPolygon"):
            w_fw.add(g, {"depth": num(tags.get("seamark:%s:minimum_depth" % t)), "kind": t,
                         "name": tags.get("seamark:name") or tags.get("name"), "src": "osm"}, minzoom=9)
        else:
            w_nav.add(g, {"bearing": num(tags.get("seamark:%s:orientation" % t)), "kind": t,
                          "depth": num(tags.get("seamark:%s:depth" % t) or tags.get("seamark:%s:minimum_depth" % t)),
                          "name": tags.get("seamark:name") or tags.get("name"), "src": "osm"}, minzoom=10)
    for w in (w_fw, w_nav, w_lead, w_tss):
        w.close()


# ---------------------------------------------------------------------------------------------
def step_tiles():
    """Three or four PMTiles archives, each below MAX_FILE_MB. If an archive comes out too large, it is
    rebuilt with coarser settings (more simplification, then one zoom level less, then without its
    optional layers), so the weekly run keeps working as the sources grow."""
    DIST.mkdir(parents=True, exist_ok=True)
    m = lambda n: MID / (n + ".geojsonl")  # noqa: E731
    LOG["tiles_mb"], LOG["tiles_settings"] = {}, {}

    def tiles(fname, name, maxzoom, layers, extra, optional=(), simp=2):
        out = DIST / fname
        tries = [(maxzoom, simp, layers), (maxzoom, simp * 2, layers), (maxzoom - 1, simp * 2, layers)]
        if optional:
            tries.append((maxzoom - 1, simp * 2, [x for x in layers if x not in optional]))
        for z, sm, lyrs in tries:
            run(["tippecanoe", "-q", "-o", out, "--force", "-Z0", "-z%d" % z, "--name", name,
                 "--attribution", "see sources.json", "-r1", "--simplification=%d" % sm] + extra +
                sum([["-L", "%s:%s" % (lyr, m(lyr))] for lyr in lyrs], []) + ["-j", zoom_filter(lyrs)])
            mb = out.stat().st_size / 1e6
            say("  %s: %.1f MB (maxzoom %d, simplification %d, layers %s)" % (fname, mb, z, sm, ",".join(lyrs)))
            LOG["tiles_mb"][fname] = round(mb, 1)
            LOG["tiles_settings"][fname] = {"maxzoom": z, "simplification": sm, "layers": lyrs}
            if mb <= C.MAX_FILE_MB:
                return
        say("  WARNING: %s is still over %d MB" % (fname, C.MAX_FILE_MB))

    tiles("land.pmtiles", "Baltic Sea chart: land", 13, ["land", "coastline"],
          ["--detect-shared-borders", "--no-tile-size-limit"])
    tiles("chart.pmtiles", "Baltic Sea chart: seamarks and routes", 14,
          ["nodata", "seamark", "light", "light_sector", "hazard", "fairway", "navline", "leading_line", "tss"],
          ["--no-tile-size-limit", "--no-feature-limit"])
    tiles("depth.pmtiles", "Baltic Sea chart: depth (EMODnet)", 12, ["depth_area", "depth_contour"],
          ["--detect-shared-borders", "--no-tile-size-limit"], simp=4)
    tiles("depth-fi.pmtiles", "Baltic Sea chart: depth in Finnish waters (Traficom)", 12,
          ["depth_fi_area", "depth_fi_contour"], ["--detect-shared-borders", "--no-tile-size-limit"],
          optional=("depth_fi_contour",), simp=4)
    say("  tiles MB:", LOG["tiles_mb"])


STEPS = {"areas": step_areas, "land": step_land, "depth": step_depth, "marks": step_marks,
         "routes": step_routes, "tiles": step_tiles}


def main(argv):
    names = argv or list(STEPS)
    logp = MID / "build_log.json"
    if logp.exists():
        LOG.update(json.loads(logp.read_text()))
    for n in names:
        t = time.time()
        say("== build %s" % n)
        STEPS[n]()
        LOG.setdefault("seconds", {})[n] = round(time.time() - t)
        MID.mkdir(parents=True, exist_ok=True)
        logp.write_text(json.dumps(LOG, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
