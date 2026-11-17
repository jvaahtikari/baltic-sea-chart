# Baltic Sea chart

Itämeren merikarttamainen vektorikarttapaketti, joka on koottu avoimesta datasta. Venäjän vedet eivät
ole mukana. **Ei navigointikäyttöön**: kyseessä ei ole virallinen merikartta.

Paketti rakennetaan joka maanantai uudelleen GitHub Actionsissa suoraan lähteiden rajapinnoista ja
latauspalveluista. Mitään aineistoa ei ole tallennettu repoon käsin, joten kartta on aina yhtä tuore
kuin lähteet. Valmis paketti julkaistaan kolmella tavalla:

- **Release `latest`**: `baltic-sea-chart.zip`, joka sisältää koko paketin
- **GitHub Pages**: demosivu `index.html` ja upotusesimerkki `overlay.html`
- **haara `run-log`**: viimeisimmän ajon yhteenveto, kuvakaappaukset ja lokit

## Paketin käyttö omassa työkalussa

Paketti on itsenäinen kansio, jossa ei ole ulkoisia palvelimia, CDN-osoitteita eikä API-avaimia. Jokainen
tiedosto on alle 100 Mt, joten kansion voi kopioida sellaisenaan omaan repoon ja palvella samalta
palvelimelta kuin muun sovelluksen.

1. Lataa `baltic-sea-chart.zip` Releasesta `latest` ja pura se oman repon kansioon, esimerkiksi `public/baltic/`.
2. Upota kartta MapLibre GL JS:llä: joko koko karttana (`balticStyle`) tai kerroksina oman taustakartan
   päälle (`addBalticLayers`). Vaalea ja tumma teema ovat molemmat valmiina, ja `setBalticTheme` vaihtaa
   teeman lennossa esimerkiksi sovelluksen "Light map" -valinnasta.
3. Näytä lähdemerkinnät. MapLibren attribuutio-ohjain näyttää ne automaattisesti.

Paketin `README.md` (englanniksi) kuvaa kerrokset, kentät, tyylien kerrostunnukset ja koodiesimerkit.

Pysyäksesi ajan tasalla voit joko hakea zipin uudelleen esimerkiksi viikoittaisella omalla työnkululla
tai forkata koko repon. Forkissa Actions ajaa saman tietoputken itsenäisesti (Actions-välilehdellä
*Build Baltic Sea chart* → *Run workflow*). Salaisuuksia ei tarvita.

## Lähteet

| Aineisto | Lähde ja rajapinta | Lisenssi |
| --- | --- | --- |
| Syvyysalueet ja -käyrät, Suomen vedet | Traficom, merikarttatietokanta (INSPIRE WFS, `DepthArea_A`, `DepthContour_L`) | ei navigointikäyttöön, ei-kaupallinen, lähdemerkintä siirtokuukausineen |
| Syvyysalueet ja -käyrät, muut vedet | EMODnet Bathymetry DTM (WCS, keskisyvyys noin 115 m ruuduin) | avoin, lähdemerkintä |
| Turvalaitteet, loistot, valosektorit, väyläalueet, navigointi- ja taululinjat, Suomi | Väylävirasto (WFS) | CC BY 4.0 |
| Merimerkit, väyläalueet ja väyläosuudet, Viro | Transpordiametin navigointimerkkirekisteri (INSPIRE WFS, Maa- ja Ruumiamet) | Viron avoimen datan lisenssi (CC BY 4.0 -vastine) |
| Merimerkit ja valot sektoreineen, Saksa | BSH, Navigation marks according to S-57 (WFS) | GeoNutzV, lähdemerkintä © BSH |
| Merimerkit, valot, karit, hylyt, liikenteenjakoalueet, muut maat | OpenStreetMap / OpenSeaMap-merkinnät alueittain: openstreetmap.fr- tai Geofabrik-poiminta tai Overpass API | ODbL 1.0 |
| Maa-alueet ja rantaviiva | OpenStreetMap-rantaviivasta tehdyt maapolygonit (osmdata.openstreetmap.de) | ODbL 1.0 |
| Itämeren rajaus ja Venäjän vedet | Marine Regions: IHO-merialueet ja merivyöhykkeet (WFS) | CC BY 4.0 |

Traficomin ehtojen vuoksi paketti kokonaisuutena on vain **ei-kaupalliseen käyttöön**.

## Rajaus

Alue on IHO:n Itämeri (Pohjanlahti, Suomenlahti, Riianlahti ja Tanskan salmet) sekä Kattegat. Venäjän
aluevedet, sisäiset aluevedet ja talousvyöhyke on poistettu, ja ne näkyvät kartalla harmaana. Maa-alueet
piirretään koko rajauslaatikkoon, myös Venäjän puolelle, koska muuten rannikko jäisi aukoksi.

Merimerkit tulevat viranomaisilta siellä, missä ne ovat avoimesti saatavilla: Suomessa Väylävirastolta,
Virossa Transpordiametilta ja Saksassa BSH:lta. Muualla (Ruotsi, Tanska, Latvia, Liettua, Puola)
käytetään OpenStreetMapin merimerkkejä, joiden kattavuus ja ajantasaisuus vaihtelevat maittain. Viron
rekisterissä ei ole valotietoja, joten Viron valot tulevat OpenStreetMapista.

OpenStreetMapin merimerkit haetaan alueittain kolmesta lähteestä siinä järjestyksessä, kuin ne vastaavat.
Jos alue ei onnistu mistään, sille käytetään edellisen onnistuneen ajon tietoja, ja ajon yhteenveto
kertoo sen. Paketti rakennetaan maanantaisin ja torstaisin.

## Rakenne

```
pipeline/preflight.py  pikatesti ennen pitkää ajoa: jokainen lähde pienellä kyselyllä, Viron ja Saksan
                     merimerkit kokonaan haettuina rakennusvaiheen omilla jäsentimillä (muutama minuutti)
pipeline/fetch.py    lähteiden haku rajapinnoista (regions, emodnet, vayla, traficom, osm, land)
pipeline/build.py    rajaus, maa, syvyydet, merimerkit ja reitit GeoJSONSeq-kerroksiksi, tippecanoe -> PMTiles
pipeline/style.py    MapLibre-tyylit (vaalea ja tumma)
pipeline/assets.py   symbolit, fontit, kirjastot, demosivut ja sources.json pakettiin
pipeline/check.py    paketin tarkistus ja ajon yhteenveto
tools/sprite.mjs     merikarttasymbolit (IALA A, ECDIS-värit) SVG:stä spriteksi
tools/shots.mjs      kuvakaappaukset tarkistusta varten
site/                demosivut, upotusapuri ja paketin README
```

Paikallinen ajo vaatii GDAL:n Python-sidoksineen, tippecanoen, osmiumin ja Noden:

```
npm ci
python3 -m pipeline.fetch && python3 -m pipeline.build && python3 -m pipeline.assets
python3 tools/serve.py dist 8000     # http://127.0.0.1:8000/
```
