
### EMODnet WCS capabilities
-rw-r--r-- 1 runner runner 15688 Nov 17 12:25 caps.xml
<wcs:CoverageId>emodnet__mean
<wcs:CoverageId>emodnet__mean_2016
<wcs:CoverageId>emodnet__mean_2018
<wcs:CoverageId>emodnet__mean_2020
<wcs:CoverageId>emodnet__mean_2022
<wcs:CoverageId>emodnet__mean_atlas_land
<wcs:CoverageId>emodnet__mean_multicolour
<wcs:CoverageId>emodnet__mean_rainbowcolour

### EMODnet DescribeCoverage emodnet__mean
<?xml version="1.0" encoding="UTF-8"?><wcs:CoverageDescriptions xmlns:wcs="http://www.opengis.net/wcs/2.0" xmlns:ows="http://www.opengis.net/ows/2.0" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:gmlcov="http://www.opengis.net/gmlcov/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:swe="http://www.opengis.net/swe/2.0" xmlns:wcsgs="http://www.geoserver.org/wcsgs/2.0" xsi:schemaLocation=" http://www.opengis.net/wcs/2.0 http://schemas.opengis.net/wcs/2.0/wcsDescribeCoverage.xsd http://www.geoserver.org/wcsgs/2.0 http://ows.emodnet-bathymetry.eu/schemas/wcs/2.0/wcsgs.xsd">
  <wcs:CoverageDescription gml:id="emodnet__mean">
    <gml:description>Generated from ImageMosaic</gml:description>
    <gml:name>Mean depth</gml:name>
    <gml:boundedBy>
      <gml:Envelope srsName="http://www.opengis.net/def/crs/EPSG/0/4326" axisLabels="Lat Long" uomLabels="Deg Deg" srsDimension="2">
        <gml:lowerCorner>11.0 -70.5</gml:lowerCorner>
        <gml:upperCorner>90.0 43.000000000000085</gml:upperCorner>
      </gml:Envelope>
    </gml:boundedBy>
    <wcs:CoverageId>emodnet__mean</wcs:CoverageId>
    <gml:coverageFunction>
      <gml:GridFunction>
        <gml:sequenceRule axisOrder="+2 +1">Linear</gml:sequenceRule>
        <gml:startPoint>0 0</gml:startPoint>
      </gml:GridFunction>
    </gml:coverageFunction>
    <gmlcov:metadata>
      <gmlcov:Extension>
        <ows:Keywords>
          <ows:Keyword>WCS</ows:Keyword>
        </ows:Keywords>
        <ows:Metadata xlink:type="simple" xlink:href="https://sextant.ifremer.fr/geonetwork/srv/eng/csw?request=GetRecordById&amp;elementSetName=full&amp;service=CSW&amp;version=2.0.2&amp;OutputSchema=http://www.isotc211.org/2005/gmd&amp;id=cf51df64-56f9-4a99-b1aa-36b8d7b743a1"/>
      </gmlcov:Extension>
    </gmlcov:metadata>
    <gml:domainSet>
      <gml:RectifiedGrid gml:id="grid00__emodnet__mean" dimension="2">
        <gml:limits>
          <gml:GridEnvelope>
            <gml:low>0 0</gml:low>
            <gml:high>108959 75839</gml:high>
          </gml:GridEnvelope>
        </gml:limits>
        <gml:axisLabels>i j</gml:axisLabels>
        <gml:origin>
          <gml:Point gml:id="p00_emodnet__mean" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
            <gml:pos>89.99947916666666 -70.49947916666666</gml:pos>
          </gml:Point>
        </gml:origin>
        <gml:offsetVector srsName="http://www.opengis.net/def/crs/EPSG/0/4326">0.0 0.0010416666666666667</gml:offsetVector>
        <gml:offsetVector srsName="http://www.opengis.net/def/crs/EPSG/0/4326">-0.0010416666666666667 0.0</gml:offsetVector>
      </gml:RectifiedGrid>
    </gml:domainSet>
    <gmlcov:rangeType>
      <swe:DataRecord xmlns:swe="http://www.opengis.net/swe/2.0">
        <swe:field name="Depth">
          <swe:Quantity>
            <swe:description>Depth</swe:description>
            <swe:nilValues>
              <swe:NilValues>
                <swe:nilValue reason="http://

### EMODnet GetCoverage test (Ahvenanmaa 1x0.5 deg)
t.tif: TIFF image data, big-endian, direntries=16, height=480, bps=32, compression=none, PhotometricInterpretation=BlackIsZero, width=960
-rw-r--r-- 1 runner runner 1966480 Nov 17 12:25 t.tif
Driver: GTiff/GeoTIFF
Files: t.tif
Size is 960, 480
Coordinate System is:
GEOGCRS["WGS 84",
    ENSEMBLE["World Geodetic System 1984 ensemble",
        MEMBER["World Geodetic System 1984 (Transit)"],
        MEMBER["World Geodetic System 1984 (G730)"],
        MEMBER["World Geodetic System 1984 (G873)"],
        MEMBER["World Geodetic System 1984 (G1150)"],
        MEMBER["World Geodetic System 1984 (G1674)"],
        MEMBER["World Geodetic System 1984 (G1762)"],
        MEMBER["World Geodetic System 1984 (G2139)"],
        ELLIPSOID["WGS 84",6378137,298.257223563,
            LENGTHUNIT["metre",1]],
        ENSEMBLEACCURACY[2.0]],
    PRIMEM["Greenwich",0,
        ANGLEUNIT["degree",0.0174532925199433]],
    CS[ellipsoidal,2],
        AXIS["geodetic latitude (Lat)",north,
            ORDER[1],
            ANGLEUNIT["degree",0.0174532925199433]],
        AXIS["geodetic longitude (Lon)",east,
            ORDER[2],
            ANGLEUNIT["degree",0.0174532925199433]],
    USAGE[
        SCOPE["Horizontal component of 3D system."],
        AREA["World."],
        BBOX[-90,-180,90,180]],
    ID["EPSG",4326]]
Data axis to CRS axis mapping: 2,1
Origin = (19.500000000000007,60.499999999999993)
Pixel Size = (0.001041666666667,-0.001041666666667)
Metadata:
  AREA_OR_POINT=Area
  TIFFTAG_RESOLUTIONUNIT=1 (unitless)
  TIFFTAG_XRESOLUTION=1
  TIFFTAG_YRESOLUTION=1
Image Structure Metadata:
  INTERLEAVE=BAND

### EMODnet downloads index
-- /
 
 403 Forbidden 
 
 403 Forbidden 
 nginx/1.30.6 
 
 

-- /v12/
 
 403 Forbidden 
 
 403 Forbidden 
 nginx/1.30.6 
 
 

-- /v11/
 
 403 Forbidden 
 
 403 Forbidden 
 nginx/1.30.6 
 
 

HTTP/2 200  
content-length: 225887506 
last-modified: Wed, 19 Feb 2025 13:22:45 GMT 
 <- https://downloads.emodnet-bathymetry.eu/v12/D1_2024.nc.zip
HTTP/2 200  
content-length: 335377533 
last-modified: Wed, 19 Feb 2025 13:22:50 GMT 
 <- https://downloads.emodnet-bathymetry.eu/v12/D2_2024.nc.zip
HTTP/2 200  
content-length: 298623664 
last-modified: Wed, 19 Feb 2025 13:22:57 GMT 
 <- https://downloads.emodnet-bathymetry.eu/v12/D3_2024.nc.zip
HTTP/2 200  
content-length: 231939977 
last-modified: Wed, 19 Feb 2025 13:23:04 GMT 
 <- https://downloads.emodnet-bathymetry.eu/v12/E1_2024.nc.zip
HTTP/2 200  
content-length: 269490382 
last-modified: Wed, 19 Feb 2025 13:23:10 GMT 
 <- https://downloads.emodnet-bathymetry.eu/v12/E2_2024.nc.zip
HTTP/2 200  
content-length: 438150693 
last-modified: Wed, 19 Feb 2025 13:23:18 GMT 
 <- https://downloads.emodnet-bathymetry.eu/v12/E3_2024.nc.zip
HTTP/2 200  
content-length: 199757140 
last-modified: Wed, 19 Feb 2025 13:22:21 GMT 
 <- https://downloads.emodnet-bathymetry.eu/v12/C1_2024.nc.zip
HTTP/2 200  
content-length: 266390406 
last-modified: Wed, 19 Feb 2025 13:22:27 GMT 
 <- https://downloads.emodnet-bathymetry.eu/v12/C2_2024.nc.zip

### EMODnet HR-DTM WCS coverages (hrdtm)

### Geofabrik sizes
HTTP/1.1 200 OK 
Content-Length: 777635017 
Last-Modified: Tue, 17 Nov 2026 00:36:38 GMT 
 <- https://download.geofabrik.de/europe/finland-latest.osm.pbf
HTTP/1.1 200 OK 
Last-Modified: Tue, 17 Nov 2026 00:40:39 GMT 
Content-Length: 981804566 
 <- https://download.geofabrik.de/europe/sweden-latest.osm.pbf
HTTP/1.1 200 OK 
Last-Modified: Tue, 17 Nov 2026 00:33:50 GMT 
Content-Length: 498097128 
 <- https://download.geofabrik.de/europe/denmark-latest.osm.pbf
HTTP/1.1 200 OK 
Last-Modified: Tue, 17 Nov 2026 00:22:22 GMT 
Content-Length: 124688962 
 <- https://download.geofabrik.de/europe/estonia-latest.osm.pbf
HTTP/1.1 200 OK 
Last-Modified: Tue, 17 Nov 2026 00:32:43 GMT 
Content-Length: 141738665 
 <- https://download.geofabrik.de/europe/latvia-latest.osm.pbf
HTTP/1.1 200 OK 
Last-Modified: Tue, 17 Nov 2026 00:29:04 GMT 
Content-Length: 224275390 
 <- https://download.geofabrik.de/europe/lithuania-latest.osm.pbf
HTTP/1.1 200 OK 
Last-Modified: Tue, 17 Nov 2026 00:18:45 GMT 
Content-Length: 2119885390 
 <- https://download.geofabrik.de/europe/poland-latest.osm.pbf
HTTP/1.1 200 OK 
Content-Length: 4884969326 
Last-Modified: Tue, 17 Nov 2026 00:22:08 GMT 
 <- https://download.geofabrik.de/europe/germany-latest.osm.pbf
HTTP/1.1 200 OK 
Last-Modified: Tue, 17 Nov 2026 01:14:15 GMT 
Content-Length: 128892645 
 <- https://download.geofabrik.de/europe/germany/mecklenburg-vorpommern-latest.osm.pbf
HTTP/1.1 200 OK 
Last-Modified: Tue, 17 Nov 2026 01:11:52 GMT 
Content-Length: 159419190 
 <- https://download.geofabrik.de/europe/germany/schleswig-holstein-latest.osm.pbf
HTTP/1.1 200 OK 
Last-Modified: Tue, 17 Nov 2026 00:48:13 GMT 
Content-Length: 118565157 
 <- https://download.geofabrik.de/europe/poland/pomorskie-latest.osm.pbf
HTTP/1.1 200 OK 
Last-Modified: Tue, 17 Nov 2026 00:49:07 GMT 
Content-Length: 98094947 
 <- https://download.geofabrik.de/europe/poland/zachodniopomorskie-latest.osm.pbf
HTTP/1.1 200 OK 
Last-Modified: Tue, 17 Nov 2026 00:48:44 GMT 
Content-Length: 85752336 
 <- https://download.geofabrik.de/europe/poland/warminsko-mazurskie-latest.osm.pbf

### osmdata land/coastline
HTTP/2 200  
content-length: 929955224 
last-modified: Tue, 17 Nov 2026 01:52:52 GMT 
 <- https://osmdata.openstreetmap.de/download/land-polygons-split-4326.zip
HTTP/2 200  
content-length: 924779834 
last-modified: Tue, 17 Nov 2026 01:50:02 GMT 
 <- https://osmdata.openstreetmap.de/download/land-polygons-complete-4326.zip
HTTP/2 200  
content-length: 926516976 
last-modified: Tue, 17 Nov 2026 01:47:15 GMT 
 <- https://osmdata.openstreetmap.de/download/coastlines-split-4326.zip
HTTP/2 200  
content-length: 24453025 
last-modified: Tue, 17 Nov 2026 01:57:03 GMT 
 <- https://osmdata.openstreetmap.de/download/simplified-land-polygons-complete-3857.zip
HTTP/2 200  
content-length: 908061660 
last-modified: Tue, 17 Nov 2026 01:55:40 GMT 
 <- https://osmdata.openstreetmap.de/download/water-polygons-split-4326.zip

### Marine Regions WFS layers
<Name>MarineRegions:eez_archipelagic_waters <Name>MarineRegions:arcticmarineareas <Name>MarineRegions:brasdorlakebiospherereserve <Name>MarineRegions:isa_ccz_managementarea <Name>MarineRegions:coasts_subnational <Name>MarineRegions:coasts_per_ocean <Name>MarineRegions:eez_24nm <Name>MarineRegions:comarge <Name>MarineRegions:cross_dateline_polygons <Name>MarineRegions:eca_reg13_nox <Name>MarineRegions:eca_reg14_sox_pm <Name>MarineRegions:eez <Name>MarineRegions:ecs <Name>MarineRegions:ecs_boundaries <Name>MarineRegions:fadaregions <Name>MarineRegions:fao <Name>MarineRegions:tnc_wwf_feow_hydrosheds <Name>MarineRegions:gsas_mediterraneanfishingzones <Name>MarineRegions:longhurst <Name>MarineRegions:goas <Name>MarineRegions:haedatgrids_polygon <Name>MarineRegions:high_seas <Name>MarineRegions:ices_ecoregions <Name>MarineRegions:ices_areas <Name>MarineRegions:ices_statistical_rectangles <Name>MarineRegions:iho <Name>MarineRegions:iho_quadrants_20150810 <Name>MarineRegions:eez_internal_waters <Name>MarineRegions:itmarbiogeogsector_bianchi <Name>MarineRegions:eez_land <Name>MarineRegions:eez_boundaries <Name>MarineRegions:mesopelagiczones <Name>MarineRegions:gazetteer_line <Name>MarineRegions:gazetteer_polygon <Name>MarineRegions:world_countries_coasts <Name>MarineRegions:na_coastalwaterbodies <Name>MarineRegions:ospar_regions <Name>MarineRegions:ospar_boundaries <Name>MarineRegions:mra_nor_blocks <Name>MarineRegions:mra_uk_blocks <Name>MarineRegions:seavox_v16 <Name>MarineRegions:seavox_v17 <Name>MarineRegions:seavox_v18 <Name>MarineRegions:seavox_v19 <Name>MarineRegions:eez_12nm <Name>MarineRegions:lme <Name>MarineRegions:eez_iho <Name>MarineRegions:worldheritagemarineprogramme_v1 <Name>MarineRegions:worldheritagemarineprogramme <Name>MarineRegions:world_bay_gulf <Name>MarineRegions:world_estuary_delta <Name>MarineRegions:worldcountries_esri_2014 <Name>MarineRegions:distritos_ecologicos <Name>MarineRegions:land_v9 

### MR eez Russia
{'mrgid': 5690, 'geoname': 'Russian Exclusive Economic Zone', 'pol_type': '200NM', 'territory1': 'Russia', 'sovereign1': 'Russia'}

### MR eez in Baltic bbox (properties)
{'mrgid': 5687, 'geoname': 'Polish Exclusive Economic Zone', 'pol_type': '200NM', 'territory1': 'Poland'}
{'mrgid': 5683, 'geoname': 'Latvian Exclusive Economic Zone', 'pol_type': '200NM', 'territory1': 'Latvia'}
{'mrgid': 5675, 'geoname': 'Estonian Exclusive Economic Zone', 'pol_type': '200NM', 'territory1': 'Estonia'}
{'mrgid': 5676, 'geoname': 'Finnish Exclusive Economic Zone', 'pol_type': '200NM', 'territory1': 'Finland'}
{'mrgid': 5694, 'geoname': 'Swedish Exclusive Economic Zone', 'pol_type': '200NM', 'territory1': 'Sweden'}
{'mrgid': 5684, 'geoname': 'Lithuanian Exclusive Economic Zone', 'pol_type': '200NM', 'territory1': 'Lithuania'}
{'mrgid': 48977, 'geoname': 'Joint regime area: Sweden / Norway', 'pol_type': 'Joint regime', 'territory1': 'Norway'}
{'mrgid': 5669, 'geoname': 'German Exclusive Economic Zone', 'pol_type': '200NM', 'territory1': 'Germany'}
{'mrgid': 5674, 'geoname': 'Danish Exclusive Economic Zone', 'pol_type': '200NM', 'territory1': 'Denmark'}
{'mrgid': 48978, 'geoname': 'Joint regime area: United States / Russia', 'pol_type': 'Joint regime', 'territory1': 'United States'}
{'mrgid': 5686, 'geoname': 'Norwegian Exclusive Economic Zone', 'pol_type': '200NM', 'territory1': 'Norway'}
{'mrgid': 5690, 'geoname': 'Russian Exclusive Economic Zone', 'pol_type': '200NM', 'territory1': 'Russia'}
{'mrgid': 8463, 'geoname': 'United States Exclusive Economic Zone (Alaska)', 'pol_type': '200NM', 'territory1': 'Alaska'}

### MR eez_12nm Russia
{'mrgid': 49015, 'geoname': 'Danish 12 NM', 'territory1': 'Denmark'}
{'mrgid': 49017, 'geoname': 'Finnish 12 NM', 'territory1': 'Finland'}
{'mrgid': 49024, 'geoname': 'Latvian 12 NM', 'territory1': 'Latvia'}
{'mrgid': 49016, 'geoname': 'Estonian 12 NM', 'territory1': 'Estonia'}
{'mrgid': 49025, 'geoname': 'Lithuanian 12 NM', 'territory1': 'Lithuania'}
{'mrgid': 49028, 'geoname': 'Polish 12 NM', 'territory1': 'Poland'}
{'mrgid': 49034, 'geoname': 'Swedish 12 NM', 'territory1': 'Sweden'}
{'mrgid': 49177, 'geoname': 'United States 12 NM (Alaska)', 'territory1': 'Alaska'}
{'mrgid': 49242, 'geoname': 'German 12 NM', 'territory1': 'Germany'}
{'mrgid': 49031, 'geoname': 'Russian 12 NM', 'territory1': 'Russia'}
{'mrgid': 49027, 'geoname': 'Norwegian 12 NM', 'territory1': 'Norway'}

### MR iho in Baltic bbox
{'name': 'Bering Sea', 'id': '55', 'area': 2336912, 'mrgid': 4310}
{'name': 'Chukchi Sea', 'id': '12', 'area': 346259, 'mrgid': 4257}
{'name': 'Gulf of Riga', 'id': '1c', 'area': 18692, 'mrgid': 2409}
{'name': 'Baltic Sea', 'id': '1', 'area': 215863, 'mrgid': 2401}
{'name': 'Gulf of Finland', 'id': '1b', 'area': 57077, 'mrgid': 2407}
{'name': 'Gulf of Bothnia', 'id': '1a', 'area': 113419, 'mrgid': 2402}
{'name': 'North Pacific Ocean', 'id': '57', 'area': 65154681, 'mrgid': 1908}
{'name': 'Barentsz Sea', 'id': '7', 'area': 1408430, 'mrgid': 4247}
{'name': 'Greenland Sea', 'id': '5', 'area': 1186456, 'mrgid': 2356}
{'name': 'North Sea', 'id': '4', 'area': 524493, 'mrgid': 2350}
{'name': 'Kattegat', 'id': '2', 'area': 35447, 'mrgid': 2374}
{'name': 'Skagerrak', 'id': '3', 'area': 32040, 'mrgid': 2379}
{'name': 'Norwegian Sea', 'id': '6', 'area': 1437096, 'mrgid': 2353}
-rw-r--r-- 1 runner runner 34341857 Nov 17 12:28 iho.json

### MR licence
		 About Standards Disclaimer LifeWatch Ocean Decade FAQ Contact License, terms of use & citation 
 License 
 Marine Regions’ products have been licensed under CC-BY since Maritime Boundaries version 11 (2019). Please contact us for other uses of the Licensed Material beyond license terms. We kindly request our users not to make our products available for download elsewhere and to always refer to marineregions.org for the most up-to-date products and services. 
 liable for faults, of any nature, that might occur in the usage of Marine Regions. All those who wish to use Marine Regions do so completely at own risk/under own responsibility and according to the License conditions and the Terms of Use. VLIZ expresses no opinion about the legal state neither of any country, territory or area nor concerning its delimitation, frontier or borders. The data has no lega
Marine Regions can be used according to the terms and conditions mentioned in the CC-license (CC-BY). The provisions above in no way replace the provisions of the CC-license. If any of the abovementioned provisions divert from or contradict the provisions of the CC-license in any way, the CC-license provisions prevail.

### Overpass seamark count FI (test)
done
