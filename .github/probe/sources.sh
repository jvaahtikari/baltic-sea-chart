#!/usr/bin/env bash
# One-off probe of candidate seamark sources, run in GitHub Actions. Output: $1 (markdown)
out="$1"; exec > >(tee "$out") 2>&1
set +e
h() { echo; echo "### $*"; }
get() { curl -4 -sS -L -m 120 -A "baltic-sea-chart-probe" "$@"; }
code() { curl -4 -s -o /dev/null -L -m 60 -w "%{http_code} %{size_download}B %{time_total}s" "$1"; echo "  <- $1"; }

h "Reachability (IPv4 / IPv6)"
for u in https://download.geofabrik.de/ https://overpass-api.de/api/status https://overpass.kumi.systems/api/status https://download.openstreetmap.fr/extracts/europe/ https://osmdata.openstreetmap.de/; do
  printf "v4 "; code "$u"; printf "v6 "; curl -6 -s -o /dev/null -m 20 -w "%{http_code}\n" "$u"; done

h "Estonia: TN_veetransport WFS capabilities"
E=https://inspire.geoportaal.ee/geoserver/TN_veetransport/wfs
get "$E?service=WFS&version=2.0.0&request=GetCapabilities" -o ee_caps.xml; ls -la ee_caps.xml
grep -o '<wfs:Name>[^<]*\|<Name>[^<]*' ee_caps.xml | head -40
grep -o -i '<ows:Fees>[^<]*\|<ows:AccessConstraints>[^<]*' ee_caps.xml | head
for t in $(grep -o '<Name>[^<]*' ee_caps.xml | sed 's/<Name>//' | head -20); do
  h "Estonia $t"
  get "$E?service=WFS&version=2.0.0&request=GetFeature&typeNames=$t&resultType=hits" | grep -o 'numberMatched="[^"]*"'
  get "$E?service=WFS&version=2.0.0&request=GetFeature&typeNames=$t&count=2&outputFormat=application/json&srsName=EPSG:4326" | head -c 2500; echo
done

h "BSH: navigation marks WFS page"
get "https://gdi.bsh.de/en/mapservice/Navigation-marks-according-to-S-57-WFS" -o bsh.html; ls -la bsh.html
grep -o 'https\?://[^"<> ]*[Ww][Ff][Ss][^"<> ]*' bsh.html | sort -u | head -20
for u in $(grep -o 'https\?://[^"<> ]*GetCapabilities[^"<> ]*' bsh.html | sed 's/&amp;/\&/g' | sort -u | head -3); do
  h "BSH caps $u"; get "$u" -o bsh_caps.xml; ls -la bsh_caps.xml
  grep -o '<wfs:Name>[^<]*\|<Name>[^<]*' bsh_caps.xml | head -60
  grep -o -i '<ows:Fees>[^<]*\|<ows:AccessConstraints>[^<]*' bsh_caps.xml | head
  base="${u%%\?*}"
  for t in $(grep -o '<Name>[^<]*' bsh_caps.xml | sed 's/<Name>//' | head -40); do
    printf "%s: " "$t"; get "$base?service=WFS&version=2.0.0&request=GetFeature&typeNames=$t&resultType=hits" | grep -o 'numberMatched="[^"]*"'
  done
  t1=$(grep -o '<Name>[^<]*' bsh_caps.xml | sed 's/<Name>//' | grep -i -E 'boy|buoy|light|lights' | head -2)
  for t in $t1; do h "BSH sample $t"; get "$base?service=WFS&version=2.0.0&request=GetFeature&typeNames=$t&count=2&outputFormat=application/json&srsName=EPSG:4326" | head -c 3000; echo; done
done

h "NGA MSI List of Lights API"
for u in "https://msi.nga.mil/api/publications/ngalol/lights-buoys?volume=116&output=json" \
         "https://msi.nga.mil/api/publications/ngalol/lights-buoys?volume=116&output=json&includeRemovals=false" \
         "https://msi.nga.mil/api/publications/ngalol/lights-buoys?volume=PUB+116&output=json"; do
  h "$u"; get "$u" -o nga.json; ls -la nga.json; head -c 2500 nga.json; echo
done

h "openstreetmap.fr extract names"
for p in europe/ europe/germany/ europe/poland/; do echo "-- $p"; get "https://download.openstreetmap.fr/extracts/$p" | grep -o 'href="[^"]*-latest.osm.pbf"' | head -60 | tr '\n' ' '; echo; done
