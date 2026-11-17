#!/usr/bin/env bash
out="$1"; exec > >(tee "$out") 2>&1
set +e
h() { echo; echo "### $*"; }
get() { curl -4 -sS -L -m 180 -A "baltic-sea-chart-probe" "$@"; }
B=https://gdi.bsh.de/mapservice_gs/Seezeichen/wfs
get "$B?service=WFS&version=2.0.0&request=GetCapabilities" -o caps.xml; ls -la caps.xml
grep -o -i '<ows:Fees>[^<]*\|<ows:AccessConstraints>[^<]*' caps.xml
for t in $(grep -o '<Name>[^<]*' caps.xml | sed 's/<Name>//'); do
  printf "%s: " "$t"; get "$B?service=WFS&version=2.0.0&request=GetFeature&typeNames=$t&resultType=hits" | grep -o 'numberMatched="[^"]*"'
done
for t in $(grep -o '<Name>[^<]*' caps.xml | sed 's/<Name>//' | head -40); do
  h "sample $t"; get "$B?service=WFS&version=2.0.0&request=GetFeature&typeNames=$t&count=2&outputFormat=application/json&srsName=EPSG:4326" | head -c 1800; echo
done
