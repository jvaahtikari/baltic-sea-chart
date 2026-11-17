"""MapLibre style for the package. URLs are relative to style.json; chart-style.js makes them absolute."""

FONT = ["Noto Sans Regular"]
FONT_IT = ["Noto Sans Italic"]

# Palettes after IHO S-52: "light" ~ DAY, "dark" ~ DUSK/NIGHT. Depth bands from shallow to deep.
PALETTES = {
    "light": {
        "depth": ["#7cb9ef", "#9ccbf2", "#bcdcf5", "#d3e8f8", "#e6f2fa", "#f5fafd"],
        "background": "#e3e8ec", "nodata": "#d9d9d9", "land": "#f1e6bf", "coast": "#5b4a2e",
        "contour": "#6f95b8", "area_edge": "#7fa3c4", "ink": "#222222", "fairway": "rgba(255,255,255,0.35)",
        "fairway_edge": "#7a7a7a", "tss": "#c040c0", "depth_text": "#3f6688", "light_text": "#7a1f70",
        "name_text": "#333333", "halo": "#ffffff", "sector_limit": "#555555",
    },
    "dark": {
        "depth": ["#1f4a63", "#1b4058", "#18374c", "#152f41", "#122837", "#0f2130"],
        "background": "#0e171c", "nodata": "#161b1e", "land": "#1e272b", "coast": "#4d5d63",
        "contour": "#2f5770", "area_edge": "#28485c", "ink": "#c9d1d4", "fairway": "rgba(255,255,255,0.05)",
        "fairway_edge": "#6b7b80", "tss": "#b866b8", "depth_text": "#7fa9c6", "light_text": "#d9a3d3",
        "name_text": "#b9c3c7", "halo": "#0e171c", "sector_limit": "#7d8a8f",
    },
}


def depth_fill(c):
    return ["step", ["coalesce", ["get", "drval1"], 0], c[0], 3, c[1], 6, c[2], 10, c[3], 20, c[4], 50, c[5]]

def icon(name_expr, theme):
    """Sprite reference: baltic:<name> (light) or baltic:<name>-dark."""
    suffix = "-dark" if theme == "dark" else ""
    if isinstance(name_expr, str):
        return "baltic:" + name_expr + suffix
    return ["concat", "baltic:", name_expr, suffix]


MARK_ICON = [
    "match", ["get", "kind"],
    "lighthouse", "lighthouse",
    "light", "light",
    "daymark", "daymark",
    "cairn", "cairn",
    "leading_mark", "leading_mark",
    "racon", "racon",
    "light_float", "light_float",
    ["concat", "mark-", ["coalesce", ["get", "cat"], "none"]],
]

FLARE_ICON = [
    "match", ["slice", ["coalesce", ["get", "colour"], "W"], 0, 1],
    "R", "flare-R", "G", "flare-G", "B", "flare-Bu", "flare-W",
]

SECTOR_COLOUR = ["match", ["get", "colour"], "R", "#e2211c", "G", "#13a04a", "Bu", "#2a6fd6", "#e8b400"]


def style(attribution_chart, attribution_depth, theme="light"):
    P = PALETTES[theme]
    return {
        "version": 8,
        "name": "Baltic Sea chart (%s)" % theme,
        "metadata": {"baltic-sea-chart": "Not for navigation.", "theme": theme},
        "sprite": [{"id": "baltic", "url": "sprite"}],
        "glyphs": "fonts/{fontstack}/{range}.pbf",
        "center": [20.5, 59.5],
        "zoom": 5,
        "sources": {
            "land": {"type": "vector", "url": "pmtiles://land.pmtiles", "attribution": "© OpenStreetMap contributors"},
            "chart": {"type": "vector", "url": "pmtiles://chart.pmtiles", "attribution": attribution_chart},
            "depth": {"type": "vector", "url": "pmtiles://depth.pmtiles", "attribution": attribution_depth},
        },
        "layers": [
            {"id": "background", "type": "background", "paint": {"background-color": P["background"]}},
            {"id": "depth-area", "type": "fill", "source": "depth", "source-layer": "depth_area",
             "paint": {"fill-color": depth_fill(P["depth"]), "fill-antialias": False}},
            {"id": "depth-area-edge", "type": "line", "source": "depth", "source-layer": "depth_area", "minzoom": 9,
             "filter": ["==", ["get", "src"], "traficom"],
             "paint": {"line-color": P["area_edge"], "line-width": ["interpolate", ["linear"], ["zoom"], 9, 0.2, 13, 0.6]}},
            {"id": "nodata", "type": "fill", "source": "chart", "source-layer": "nodata",
             "paint": {"fill-color": P["nodata"], "fill-opacity": 0.9}},
            {"id": "depth-contour", "type": "line", "source": "depth", "source-layer": "depth_contour",
             "paint": {"line-color": P["contour"], "line-width": ["interpolate", ["linear"], ["zoom"], 6, 0.3, 12, 0.8]}},
            {"id": "tss-area", "type": "fill", "source": "chart", "source-layer": "tss",
             "filter": ["==", ["geometry-type"], "Polygon"],
             "paint": {"fill-color": P["tss"], "fill-opacity": 0.18}},
            {"id": "tss-line", "type": "line", "source": "chart", "source-layer": "tss",
             "paint": {"line-color": P["tss"], "line-width": 1, "line-dasharray": [4, 2]}},
            {"id": "fairway", "type": "fill", "source": "chart", "source-layer": "fairway",
             "paint": {"fill-color": P["fairway"]}},
            {"id": "fairway-edge", "type": "line", "source": "chart", "source-layer": "fairway", "minzoom": 11,
             "paint": {"line-color": P["fairway_edge"], "line-width": 0.5, "line-dasharray": [3, 3]}},
            {"id": "land", "type": "fill", "source": "land", "source-layer": "land",
             "paint": {"fill-color": P["land"]}},
            {"id": "coastline", "type": "line", "source": "land", "source-layer": "coastline",
             "paint": {"line-color": P["coast"], "line-width": ["interpolate", ["linear"], ["zoom"], 6, 0.3, 12, 0.9]}},
            {"id": "navline", "type": "line", "source": "chart", "source-layer": "navline",
             "filter": ["!=", ["get", "kind"], "recommended_track"],
             "paint": {"line-color": P["ink"], "line-width": ["interpolate", ["linear"], ["zoom"], 10, 0.6, 14, 1.4]}},
            {"id": "navline-track", "type": "line", "source": "chart", "source-layer": "navline",
             "filter": ["==", ["get", "kind"], "recommended_track"],
             "paint": {"line-color": P["ink"], "line-width": ["interpolate", ["linear"], ["zoom"], 10, 0.6, 14, 1.4],
                       "line-dasharray": [4, 3]}},
            {"id": "leading-line", "type": "line", "source": "chart", "source-layer": "leading_line",
             "paint": {"line-color": P["ink"], "line-width": 0.7, "line-dasharray": [6, 4]}},
            {"id": "light-sector-limit", "type": "line", "source": "chart", "source-layer": "light_sector",
             "filter": ["==", ["get", "part"], "limit"],
             "paint": {"line-color": P["sector_limit"], "line-width": 0.6, "line-dasharray": [4, 3]}},
            {"id": "light-sector-arc", "type": "line", "source": "chart", "source-layer": "light_sector",
             "filter": ["==", ["get", "part"], "arc"],
             "paint": {"line-color": SECTOR_COLOUR, "line-width": 3, "line-opacity": 0.85}},
            {"id": "depth-label", "type": "symbol", "source": "depth", "source-layer": "depth_contour", "minzoom": 11,
             "layout": {"symbol-placement": "line", "text-field": ["to-string", ["get", "depth"]], "text-font": FONT_IT,
                        "text-size": 10, "symbol-spacing": 350},
             "paint": {"text-color": P["depth_text"], "text-halo-color": P["halo"], "text-halo-width": 1.2}},
            {"id": "navline-depth", "type": "symbol", "source": "chart", "source-layer": "navline", "minzoom": 12,
             "filter": ["has", "depth"],
             "layout": {"symbol-placement": "line", "text-field": ["concat", ["to-string", ["get", "depth"]], " m"],
                        "text-font": FONT, "text-size": 10, "symbol-spacing": 400},
             "paint": {"text-color": P["ink"], "text-halo-color": P["halo"], "text-halo-width": 1.2}},
            {"id": "hazard", "type": "symbol", "source": "chart", "source-layer": "hazard",
             "layout": {"icon-image": icon(["match", ["get", "kind"], "wreck", "wreck", "obstruction", "obstruction",
                                             ["match", ["get", "water_level"], ["awash", "covers", "dry"], "rock-awash", "rock"]], theme),
                        "icon-allow-overlap": True}},
            {"id": "light-flare", "type": "symbol", "source": "chart", "source-layer": "light",
             "layout": {"icon-image": icon(FLARE_ICON, theme), "icon-allow-overlap": True, "icon-ignore-placement": True,
                        "icon-size": ["interpolate", ["linear"], ["zoom"], 8, 0.6, 13, 1]}},
            {"id": "seamark", "type": "symbol", "source": "chart", "source-layer": "seamark",
             "layout": {"icon-image": icon(MARK_ICON, theme), "icon-allow-overlap": True,
                        "icon-size": ["interpolate", ["linear"], ["zoom"], 9, 0.6, 14, 1]}},
            {"id": "light-label", "type": "symbol", "source": "chart", "source-layer": "light", "minzoom": 11,
             "filter": ["has", "label"],
             "layout": {"text-field": ["get", "label"], "text-font": FONT, "text-size": 10,
                        "text-anchor": "left", "text-offset": [1.1, 0.6], "text-optional": True},
             "paint": {"text-color": P["light_text"], "text-halo-color": P["halo"], "text-halo-width": 1.2}},
            {"id": "seamark-name", "type": "symbol", "source": "chart", "source-layer": "seamark", "minzoom": 13,
             "filter": ["has", "name"],
             "layout": {"text-field": ["get", "name"], "text-font": FONT_IT, "text-size": 10,
                        "text-anchor": "right", "text-offset": [-1, -0.4], "text-optional": True},
             "paint": {"text-color": P["name_text"], "text-halo-color": P["halo"], "text-halo-width": 1.2}},
        ],
    }
