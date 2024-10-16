from flask import Flask, render_template, request, redirect, url_for
import json
import urllib.request
from datetime import datetime, timedelta
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from geopy import Point, Nominatim
import sqlite3, feedparser

app = Flask(__name__)


class t:
    def __init__(self, numer, numer_poj, cel, rozklad_odj, odj_akt, delay):
        self.numer = numer
        self.numer_poj = numer_poj
        self.cel = cel
        self.rozklad_odj = rozklad_odj
        self.odj_akt = odj_akt
        self.delay = delay


@app.route("/odjazdy", methods=["GET", "POST"])
async def odjazdy():
    at: list[t] = []
    con = sqlite3.connect("zkm.db")
    cur = con.cursor()
    if request.method == "POST":
        if "przystanek" and "numer" in request.form:
            przystanek = request.form["przystanek"]
            numer = request.form["numer"]
            cur.execute(
                "SELECT * FROM Przystanki WHERE name = ? AND nr_przys= ?",
                (
                    przystanek,
                    numer,
                ),
            )
            dane = cur.fetchone()
            if dane is None:
                atz = t(
                    numer="Brak takiego przystanku lub błędy numer przystanku, albo przystanek jest niedostępny",
                    numer_poj="",
                    cel="",
                    rozklad_odj="",
                    odj_akt="",
                    delay="",
                )
                at.append(atz)
            else:
                x = requests.get(
                    f"https://ckan2.multimediagdansk.pl/departures?stopId={dane[5]}"
                )
                odj = x.json()
                for odja in odj["departures"]:
                    rozklad_odj_iso = odja["theoreticalTime"]
                    odj_akt_iso = odja["estimatedTime"]
                    rozklad_odj_dt = datetime.fromisoformat(rozklad_odj_iso)
                    odj_akt_dt = datetime.fromisoformat(odj_akt_iso)
                    rozklad_odj_dt += timedelta(hours=2)
                    odj_akt_dt += timedelta(hours=2)
                    rozklad_odj_new = rozklad_odj_dt
                    odj_akt_new = odj_akt_dt
                    if odja["delayInSeconds"] is not None:
                        d = odja["delayInSeconds"]
                        minuty = d // 60
                        sekundy = d % 60
                        delay_str = f"{minuty} min {sekundy} sek"
                    else:
                        delay_str = "Brak danych"
                    atz = t(
                        numer=odja["routeShortName"],
                        numer_poj=odja["vehicleCode"],
                        cel=odja["headsign"],
                        rozklad_odj=rozklad_odj_new.strftime("%d.%m.%y %H:%M:%S"),
                        odj_akt=odj_akt_new.strftime("%d.%m.%y %H:%M:%S"),
                        delay=delay_str,
                    )
                    at.append(atz)
    return render_template("odjazd.html", at=at)


@app.route("/")
async def test():  # informacja kanału
    return render_template("test.html")


@app.route("/przystanek", methods=["GET", "POST"])
async def przystanek():
    con = sqlite3.connect("zkm.db")
    cur = con.cursor()
    if request.method == "POST":
        if "przystanek" in request.form:
            przystanek = request.form["przystanek"]
            cur.execute("SELECT * FROM Przystanki WHERE name = ?", (przystanek,))
            przys = cur.fetchall()
            con.close()  # Don't forget to close the connection
            return render_template("przystanek.html", przys=przys)
        else:
            con.close()  # Don't forget to close the connection
            return "Error: przystanek field not found in request form", 400
    con.close()  # Don't forget to close the connection
    return render_template("przystanek.html")


class loak:
    def __init__(self, lina, nr_pojazdu, cel, adres, lat, lon):
        self.lina: str = lina
        self.nr_pojazdu: str = nr_pojazdu
        self.cel: str = cel
        self.adres: str = adres
        self.lat: str = lat
        self.lon: str = lon


@app.route("/lok_autobusu", methods=["GET", "POST"])
async def lok_autobusu():
    autobus: list[loak] = []
    if request.method == "POST" and "numer" in request.form:
        r = requests.get("https://ckan2.multimediagdansk.pl/gpsPositions?v=2")
        inf = r.json()
        nr = int(request.form["numer"])
        found = False
        for jaz in inf["vehicles"]:
            if str(nr) == jaz["routeShortName"]:
                latitude = jaz["lat"]
                longitude = jaz["lon"]
                point = Point(latitude, longitude)
                geocoder = Nominatim(user_agent="my-app")
                address = geocoder.reverse(point)
                az = loak(
                    lina=jaz["routeShortName"],
                    nr_pojazdu=jaz["vehicleCode"],
                    cel=jaz["headsign"],
                    adres=address[0],
                    lat=latitude,
                    lon=longitude,  # add lat and lon to the loak object
                )
                autobus.append(az)
                found = True

        if not found:
            az = loak(
                lina="Brak takiej lini albo nie kursuje w tym czasie",
                nr_pojazdu=" ",
                cel=" ",
                adres=" ",
                lat=" ",
                lon=" ",
            )
            autobus.append(az)

    return render_template("lok_autous.html", autobus=autobus)


class loaks:
    def __init__(self, lina, nr_pojazdu, cel, adres, lat, lon):
        self.lina: str = lina
        self.nr_pojazdu: str = nr_pojazdu
        self.cel: str = cel
        self.adres: str = adres
        self.lat: str = lat
        self.lon: str = lon


@app.route("/lok_numer_autobusu", methods=["GET", "POST"])
async def lok_numer_autobusu():
    autobuss: list[loaks] = []
    if request.method == "POST" and "numer" in request.form:
        r = requests.get("https://ckan2.multimediagdansk.pl/gpsPositions?v=2")
        inf = r.json()
        nr = int(request.form["numer"])
        found = False
        for jaz in inf["vehicles"]:
            if str(nr) == jaz["vehicleCode"]:
                latitude = jaz["lat"]
                longitude = jaz["lon"]
                point = Point(latitude, longitude)
                geocoder = Nominatim(user_agent="my-app")
                address = geocoder.reverse(point)
                az = loaks(
                    lina=jaz["routeShortName"],
                    nr_pojazdu=jaz["vehicleCode"],
                    cel=jaz["headsign"],
                    adres=address[0],
                    lat=latitude,
                    lon=longitude,  # add lat and lon to the loak object
                )
                autobuss.append(az)
                found = True

        if not found:
            az = loaks(
                lina="Brak takiego numeru pojazdu albo ten pojazd nie kursuje w tym czasie.",
                nr_pojazdu=" ",
                cel=" ",
                adres=" ",
                lat=" ",
                lon=" ",
            )
            autobuss.append(az)
    return render_template("lok_numer_autous.html", autobuss=autobuss)


@app.route("/tabory", methods=["GET", "POST"])
async def tabory():  # informacja filmu/live
    test = []
    if request.method == "POST" and "numer" in request.form:
        num = request.form["numer"]
        urt = "https://files.cloudgdansk.pl/d/otwarte-dane/ztm/baza-pojazdow.json?v=2"
        url = requests.request("GET", urt)
        licz = len(url.json()["results"])
        for i in range(licz):
            zm = url.json()["results"][i]["vehicleCode"]
            if num == zm:
                Numer_tab = num  # numer
                operator = url.json()["results"][i]["carrirer"]  # operator/przewoźnik
                rodzaj = url.json()["results"][i][
                    "transportationType"
                ]  # rodzaj pojazdu
                marka = url.json()["results"][i]["brand"]  # marka
                model = url.json()["results"][i]["model"]  # model
                rok_prodkucji = url.json()["results"][i][
                    "productionYear"
                ]  # rok produkcji
                podloga = url.json()["results"][i]["floorHeight"]  # wysokośc podłogi
                typ = url.json()["results"][i]["vehicleCharacteristics"]  # typ pokazu
                pod2kier = url.json()["results"][i]["bidirectional"]  # dwókierunkowy
                historyczny = url.json()["results"][i]["historicVehicle"]  # historyczny
                dlugosc = url.json()["results"][i]["length"]  # długośc -
                siedzace = url.json()["results"][i]["seats"]  # miejsca siedzące
                stojace = url.json()["results"][i]["standingPlaces"]  # miejsca stojące
                uchwyt = url.json()["results"][i]["bikeHolders"]  # uchwyt na rowery
                klimatyzacja = url.json()["results"][i][
                    "airConditioning"
                ]  # klimatyzacja
                monitoring = url.json()["results"][i]["monitoring"]  # monitoring
                monitor = url.json()["results"][i][
                    "internalMonitor"
                ]  # monitor wewnętrzny
                przyklek = url.json()["results"][i]["kneelingMechanism"]  # przyklęk
                rampa = url.json()["results"][i]["wheelchairsRamp"]  # rampa dla wózków
                drzwi = url.json()["results"][i]["passengersDoors"]  # ilosć drzwi
                usb = url.json()["results"][i]["usb"]  # usb
                glos = url.json()["results"][i][
                    "voiceAnnouncements"
                ]  # zapowiedźi głosowe
                aed = url.json()["results"][i]["aed"]  # aed
                kasownik = url.json()["results"][i]["ticketMachine"]  # kasowniki
                patron = url.json()["results"][i]["patron"]  # patron
                test.append(Numer_tab)
                test.append(operator)
                test.append(rodzaj)
                test.append(marka)
                test.append(model)
                test.append(rok_prodkucji)
                test.append(podloga)
                test.append(typ)
                test.append(pod2kier)
                test.append(historyczny)
                test.append(dlugosc)
                test.append(siedzace)
                test.append(stojace)
                test.append(uchwyt)
                test.append(klimatyzacja)
                test.append(monitoring)
                test.append(monitor)
                test.append(przyklek)
                test.append(rampa)
                test.append(drzwi)
                test.append(usb)
                test.append(glos)
                test.append(aed)
                test.append(kasownik)
                test.append(patron)
                break
    return render_template("tabory.html", test=test)


class Tablica:
    def __init__(self, godziny, link):
        self.godziny: str = godziny
        self.link: str = link


@app.route("/rozklad", methods=["GET", "POST"])
async def rozklad():  # informacja filmu/live
    tab: list[Tablica] = []
    if request.method == "POST" and "link" in request.form:
        link = request.form["link"]
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        quote_elements = soup.find_all("div", class_="container")
        for quote_element in quote_elements:
            text = quote_element.find_all("div", class_="row")
            texty = text
        for test in texty:
            con = test.find("div", class_="col", id="content")
        for te in con:
            te = con.find_all("div", class_="departures")
        for ta in te:
            ty = ta.find_all("div", class_="departures-set")
        for przystanek in te:  # wyszukiwanie przysatnku z linku oraz kierunek
            przy = przystanek.find("div")
            licz = len(przy.text)
            liczw = licz - 20
            tekstowa = przy.text[0:liczw]
            print(tekstowa)
            for meh in ty:
                bober = meh.find_all("div", class_="m")
            tagi = []
            for bobers in bober:
                tag = bobers.a
                tagi.append(tag)
            for tags in tagi:
                wyn = tags.get("aria-label")[
                    0:5
                ]  # wyciągniecie z tekstu godziny odjazdu
                link_href = tags.get("href")  # pobierz link z atrybutu href
                tab.append(
                    Tablica(
                        godziny=wyn, link=f"https://ztm.gda.pl/rozklady/{link_href}"
                    )
                )  # dodaj link do Tablica
    return render_template("rozklad.html", tab=tab)


@app.route("/bus_stops", methods=["GET", "POST"])
def bus_stops():
    bus_stops = []
    if request.method == "POST":
        line_number = request.form["line_number"]
        url = f"https://ztm.gda.pl/rozklady/linia-{line_number}.html"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"role": "presentation"})

        if table:
            for row in table.find_all("tr")[1:]:  # skip the header row
                for cell in row.find_all("td"):
                    street = cell.find("div", {"class": "route_street"})
                    street_name = street.text.strip() if street else ""
                    for link in cell.find_all("a"):
                        bus_stop = link.text.strip()
                        href = link.get("href")
                        full_link = f"https://ztm.gda.pl/rozklady/{href}"
                        bus_stops.append(
                            {
                                "street": street_name,
                                "bus_stop": bus_stop,
                                "link": full_link,
                            }
                        )
        else:
            bus_stops.append(
                {
                    "street": "Error",
                    "bus_stop": "No bus stops found for this line.",
                    "link": "",
                }
            )

    return render_template("bus_stops.html", bus_stops=bus_stops)


from bs4 import BeautifulSoup
import requests


@app.route("/odjazy_przys", methods=["GET", "POST"])
async def odjazdy_przys():
    if request.method == "POST" and "link" in request.form:
        link = request.form["link"]
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        table = soup.find("table", {"class": "kurstab", "role": "presentation"})

        if table:
            rows = table.find_all("tr")
            data = []
            for row in rows[1:]:  # skip the header row
                cols = row.find_all("td")
                cols = [col.text.strip() for col in cols]
                data.append(cols)
            return render_template("odczyt_tabeli.html", data=data)
        else:
            return "Tabela nie znaleziona"
    return render_template("odczyt_tabeli.html")


if __name__ == "__main__":
    app.run(host="192.168.0.185")  # wprowadz adres ip komputera
