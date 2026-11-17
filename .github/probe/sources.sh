#!/usr/bin/env bash
out="$1"; exec > >(tee "$out") 2>&1
set +e
h() { echo; echo "### $*"; }
get() { curl -4 -sS -L -m 120 -A "baltic-sea-chart-probe" "$@"; }
h "BSH page content"
get -i "https://gdi.bsh.de/en/mapservice/Navigation-marks-according-to-S-57-WFS" | head -40
for u in "https://gdi.bsh.de/mapservice_gs/NAUTHIS_AidsAndServices/wfs?service=WFS&request=GetCapabilities" \
         "https://gdi.bsh.de/mapservice_gs/NAUTHIS_Seezeichen/wfs?service=WFS&request=GetCapabilities" \
         "https://gdi.bsh.de/mapservice_gs/Seezeichen/wfs?service=WFS&request=GetCapabilities"; do
  h "$u"; get "$u" | head -c 1500; echo; done
h "BSH metadata xml"
get "https://gdi.bsh.de/de/metadata/Navigation-marks-according-to-S-57-WFS.xml" | grep -o 'https\?://[^<"]*' | sort -u | head -30
h "Estonia names"
E=https://inspire.geoportaal.ee/geoserver/TN_veetransport/wfs
for t in Beacon Buoy; do
  get "$E?service=WFS&version=2.0.0&request=GetFeature&typeNames=TN_veetransport:TN.WaterTransportNetwork.$t&count=5000&outputFormat=application/json&srsName=EPSG:4326" -o $t.json
  python3 - "$t.json" <<'PY'
import json,sys,collections,re
d=json.load(open(sys.argv[1])); f=d['features']
print(sys.argv[1], len(f))
keys=collections.Counter(k for x in f for k in x['properties']); print(sorted(keys))
names=[x['properties'].get('geographicalname_geographicalname_spelling_spellingofname_text','') for x in f]
words=collections.Counter(w for n in names for w in re.findall(r'[\w-]+', n.lower()) if len(w)>2)
print(words.most_common(80))
print(names[:60])
PY
done
