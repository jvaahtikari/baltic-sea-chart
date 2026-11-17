#!/usr/bin/env bash
# Kertaluonteinen lähteiden selvitys GitHub Actionsissa. Tulos tiedostoon $1.
out="$1"; exec > >(tee "$out") 2>&1
set +e
h() { echo; echo "### $*"; }
size() { curl -sIL -m 60 "$1" | grep -i -E '^(HTTP|content-length|last-modified)' | tail -3 | tr '\r' ' '; echo " <- $1"; }

h "EMODnet WCS capabilities"
curl -s -m 120 "https://ows.emodnet-bathymetry.eu/wcs?service=WCS&version=2.0.1&request=GetCapabilities" -o caps.xml; ls -la caps.xml
grep -o '<wcs:CoverageId>[^<]*' caps.xml | head -40
h "EMODnet DescribeCoverage emodnet__mean"
curl -s -m 120 "https://ows.emodnet-bathymetry.eu/wcs?service=WCS&version=2.0.1&request=DescribeCoverage&coverageId=emodnet__mean" | head -c 3000; echo
h "EMODnet GetCoverage test (Ahvenanmaa 1x0.5 deg)"
curl -s -m 300 -o t.tif "https://ows.emodnet-bathymetry.eu/wcs?service=WCS&version=2.0.1&request=GetCoverage&coverageId=emodnet__mean&format=image/tiff&subset=Long(19.5,20.5)&subset=Lat(60,60.5)"; file t.tif; ls -la t.tif; gdalinfo -stats t.tif | head -40
h "EMODnet downloads index"
for p in "" v12/ v11/ ; do echo "-- /$p"; curl -s -m 60 "https://downloads.emodnet-bathymetry.eu/$p" | head -c 2500 | sed 's/<[^>]*>/ /g' | tr -s ' \n' | head -c 1500; echo; done
for t in D1 D2 D3 E1 E2 E3 C1 C2; do size "https://downloads.emodnet-bathymetry.eu/v12/${t}_2024.nc.zip"; done
h "EMODnet HR-DTM WCS coverages (hrdtm)"
grep -o '<wcs:CoverageId>[^<]*' caps.xml | grep -i -E 'hr|high' | head

h "Geofabrik sizes"
for r in finland sweden denmark estonia latvia lithuania poland germany germany/mecklenburg-vorpommern germany/schleswig-holstein poland/pomorskie poland/zachodniopomorskie poland/warminsko-mazurskie; do size "https://download.geofabrik.de/europe/${r}-latest.osm.pbf"; done

h "osmdata land/coastline"
for f in land-polygons-split-4326.zip land-polygons-complete-4326.zip coastlines-split-4326.zip simplified-land-polygons-complete-3857.zip water-polygons-split-4326.zip; do size "https://osmdata.openstreetmap.de/download/$f"; done

h "Marine Regions WFS layers"
curl -s -m 120 "https://geo.vliz.be/geoserver/MarineRegions/wfs?service=WFS&version=2.0.0&request=GetCapabilities" | grep -o '<Name>[^<]*' | head -60 | tr '\n' ' '; echo
h "MR eez Russia"
curl -s -m 300 "https://geo.vliz.be/geoserver/MarineRegions/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=MarineRegions:eez&outputFormat=application/json&propertyName=mrgid,geoname,territory1,sovereign1,pol_type&CQL_FILTER=territory1='Russia'" | python3 -c "import json,sys; d=json.load(sys.stdin); [print(f['properties']) for f in d['features']]"
h "MR eez in Baltic bbox (properties)"
curl -s -m 300 "https://geo.vliz.be/geoserver/MarineRegions/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=MarineRegions:eez&outputFormat=application/json&propertyName=mrgid,geoname,territory1,pol_type&bbox=9,53,31,66.5" | python3 -c "import json,sys; d=json.load(sys.stdin); [print(f['properties']) for f in d['features']]"
h "MR eez_12nm Russia"
curl -s -m 300 "https://geo.vliz.be/geoserver/MarineRegions/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=MarineRegions:eez_12nm&outputFormat=application/json&propertyName=mrgid,geoname,territory1&bbox=9,53,31,66.5" | python3 -c "import json,sys; d=json.load(sys.stdin); [print(f['properties']) for f in d['features']]"
h "MR iho in Baltic bbox"
curl -s -m 300 "https://geo.vliz.be/geoserver/MarineRegions/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=MarineRegions:iho&outputFormat=application/json&bbox=9,53,31,66.5" -o iho.json; python3 -c "import json; d=json.load(open('iho.json')); [print({k:v for k,v in f['properties'].items() if k in ('name','id','mrgid','area')}) for f in d['features']]"; ls -la iho.json
h "MR licence"
curl -s -m 60 "https://www.marineregions.org/disclaimer.php" | sed 's/<[^>]*>/ /g' | tr -s ' \n' | grep -i -o '.\{0,200\}licen.\{0,200\}' | head -5
h "Overpass seamark count FI (test)"
echo done
