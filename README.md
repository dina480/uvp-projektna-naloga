# Analiza podatkov o nepremičninah
## Opis naloge
Projektna naloga analizira podatke nepremičnin, ki se na spletni strani https://www.nepremicnine.net, oddajajo v najem. Zajem in analiza podatkov sta omejena na najeme, ki so cenovno ugodni za študente.
Analiza je opravljena glede na razmerja med cenami, velikostmi in lokacijami (glede na občino) najemov.

## Zajem podatkov
Datoteka `zajem_podatkov.py` pridobi podatke iz spletne strani in jih shrani ter generira datoteko `rezultati.csv`. V zvezku `analiza_podatkov.ipynb` pa najdemo analizo podatkov.
Zaradi prisotnih blokad na spletni strani https://www.nepremicnine.net sem v kodi za zajem podatkov uporabila Selenium WebDriver, ki brskalnik poganja avtomatsko kot da bi sami "klikali" po spletni strani. To blokadam prepreči, da bi zaznale zbiranje podatkov (ne obtožijo nas robotstva).

### Uporabljene knjižnice
Za delovanje projekta morate imeti naložene naslednje knjižnice:
* pandas
* numpy
* matplotlib.pyplot
* csv
* re
* os
* time
* BeautifulSoup
* selenium
* webdriver-manager

V primeru, da katere od knjižnic nimate naložene, to storite, tako da v terminal vtipkate `pip install <knjižnica>`, kjer `<knjižnica>` zamenjate z ustrezno knjižnico.
Za delovanje morate v kodi (samo v primeru da ne uporabljate Apple računalnika) zamenjati tudi pot do Google Chrome brskalnika (in tega tudi naložiti na računalnik, če ga še nimate). V datoteki `zajem_podatkov.py` je s komentarjem označeno kje to storite.

### Navodila za zagon
Projekt zaženete v datoteki `zajem_podatkov.py`. Samodejno se bo odprl in zagnal brskalnik, ki bo zbral vse trenutno aktualne oglase. Ko to stori se bo ustvarila CSV datoteka z vsemi podatki. Na koncu pa analizo podatkov izvedete v datoteki `analiza_podatkov.ipynb`.
