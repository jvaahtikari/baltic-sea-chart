# Preflight

Result: **OK**

| Source | Check | Result | Seconds | Detail |
| --- | --- | --- | ---: | --- |
| Marine Regions | IHO areas (one request) | OK | 1 | 5 areas |
| EMODnet | WCS capabilities | OK | 1 | coverage listed |
| Väylä | turvalaitteet_uusi | OK | 0 | 35176 features |
| Väylä | loistot_uusi | OK | 0 | 4891 features |
| Väylä | valosektorit_uusi | OK | 0 | 6636 features |
| Väylä | navigointilinjat_uusi | OK | 0 | 12887 features |
| Väylä | vaylaalueet_uusi | OK | 0 | 3810 features |
| Väylä | taululinjat_uusi | OK | 0 | 2632 features |
| Traficom | DepthArea_A | OK | 1 | 149457 features |
| Traficom | DepthContour_L | OK | 1 | 201767 features |
| Traficom | Sounding_P | OK | 1 | 270002 features |
| osmdata | land polygons | OK | 1 | HTTP 200 |
| Estonia | fetch + parse | OK | 3 | 1678 marks, 754 with an IALA category; top: buoy/none 599, buoy/special 175, leading_mark/none 134, light/none 131, spar/port 75, spar/starboard 63, spar/east 53, spar/south 52 |
| Germany (BSH) | fetch + parse | OK | 22 | 9973 marks; top: None/None 2971, spar/port 2009, beacon/special 1262, buoy/starboard 1013, beacon/port 832, spar/starboard 720, light/none 700, spar/special 628; light labels e.g. IQ G 13s / Oc(3) G 12s / Q G 1s / Fl(2+1) G 15s / IQ R 13s / Fl(2) G 9s |
| OSM finland | extract available | OK | 0 | openstreetmap.fr |
| OSM sweden | extract available | OK | 0 | openstreetmap.fr |
| OSM denmark | extract available | OK | 0 | openstreetmap.fr |
| OSM estonia | extract available | OK | 7 | geofabrik |
| OSM latvia | extract available | OK | 1 | geofabrik |
| OSM lithuania | extract available | OK | 1 | geofabrik |
| OSM germany-mv | extract available | OK | 1 | geofabrik |
| OSM germany-sh | extract available | OK | 1 | geofabrik |
| OSM poland-pomorskie | extract available | OK | 0 | openstreetmap.fr |
| OSM poland-zachodniopomorskie | extract available | OK | 0 | openstreetmap.fr |
| OSM poland-warminsko-mazurskie | extract available | OK | 0 | openstreetmap.fr |
| Overpass | overpass-api.de | warning | 5 | download failed: https://overpass-api.de/api/interpreter: curl: (22) The requested URL returned error: 502 |
| Overpass | overpass.private.coffee | warning | 65 | download failed: https://overpass.private.coffee/api/interpreter: curl: (28) Operation timed out after 60002 milliseconds with 0 bytes received |
| Overpass | overpass.kumi.systems | warning | 65 | download failed: https://overpass.kumi.systems/api/interpreter: curl: (28) Operation timed out after 60002 milliseconds with 0 bytes received |
