#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lavagna del giorno — SunnyCornerinRHome
Genera docs/index.html con meteo, stato metro e treni da Termini.
Ogni sezione è indipendente: se una fonte fallisce, le altre restano.
"""
import datetime as dt
import html
import json
import sys
import urllib.request
import zoneinfo

TZ = zoneinfo.ZoneInfo("Europe/Rome")
NOW = dt.datetime.now(TZ)

# --- Dati della struttura (modifica qui) ---
LAT, LON = 41.887, 12.513   # San Giovanni, Roma

UA = {"User-Agent": "Mozilla/5.0 (lavagna-bnb)"}


def get(url, timeout=15, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    return data if binary else json.loads(data.decode("utf-8"))


# ---------------- METEO (Open-Meteo, senza chiave) ----------------

# descrizione meteo in 5 lingue (chiave = gruppo WMO)
GRP = {0:"sereno",1:"poco_nuv",2:"nuvoloso",3:"coperto",45:"nebbia",48:"nebbia",
       51:"pioviggine",53:"pioviggine",55:"pioviggine",61:"pioggia",63:"pioggia",65:"pioggia_f",
       71:"neve",73:"neve",75:"neve",80:"rovesci",81:"rovesci",82:"temporale",95:"temporale",96:"temporale",99:"temporale"}
T = {
 "it":{"sereno":"Sereno","poco_nuv":"Poco nuvoloso","nuvoloso":"Nuvoloso","coperto":"Coperto","nebbia":"Nebbia","pioviggine":"Pioviggine","pioggia":"Pioggia","pioggia_f":"Pioggia forte","neve":"Neve","rovesci":"Rovesci","temporale":"Temporale",
   "titolo":"Oggi a Roma","meteo":"Meteo Roma · ora","min":"min","max":"max","pioggia_p":"pioggia","vento":"vento","alba":"Alba","tramonto":"Tramonto","percepita":"percepita","umidita":"umidità","raffiche":"raffiche","uv":"UV","dopodomani":"Dopodomani","prossime":"Prossime ore: temperatura e probabilità di pioggia","domani":"Domani","metro":"Metro","regolare":"Servizio regolare","nd":"dati non disponibili","vicino":"San Giovanni e Manzoni (linea A) a 5 minuti a piedi","treni":"Partenze da Roma Termini","termini":"Termini: metro A, 2 fermate","orario":"in orario","info":"Informazioni","wifi":"Wi-Fi","pw":"Password","colazione":"Colazione","agg":"Aggiornato alle",
   "giorni":["lunedì","martedì","mercoledì","giovedì","venerdì","sabato","domenica"],"mesi":["gennaio","febbraio","marzo","aprile","maggio","giugno","luglio","agosto","settembre","ottobre","novembre","dicembre"]},
 "en":{"sereno":"Clear","poco_nuv":"Partly cloudy","nuvoloso":"Cloudy","coperto":"Overcast","nebbia":"Fog","pioviggine":"Drizzle","pioggia":"Rain","pioggia_f":"Heavy rain","neve":"Snow","rovesci":"Showers","temporale":"Thunderstorm",
   "titolo":"Rome today","meteo":"Rome weather · now","min":"low","max":"high","pioggia_p":"rain","vento":"wind","alba":"Sunrise","tramonto":"Sunset","percepita":"feels like","umidita":"humidity","raffiche":"gusts","uv":"UV","dopodomani":"Day after tomorrow","prossime":"Next hours: temperature and chance of rain","domani":"Tomorrow","metro":"Metro","regolare":"Running normally","nd":"no data","vicino":"San Giovanni and Manzoni (line A) 5 minutes on foot","treni":"Departures from Roma Termini","termini":"Termini: metro A, 2 stops","orario":"on time","info":"Information","wifi":"Wi-Fi","pw":"Password","colazione":"Breakfast","agg":"Updated at",
   "giorni":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],"mesi":["January","February","March","April","May","June","July","August","September","October","November","December"]},
 "fr":{"sereno":"Dégagé","poco_nuv":"Peu nuageux","nuvoloso":"Nuageux","coperto":"Couvert","nebbia":"Brouillard","pioviggine":"Bruine","pioggia":"Pluie","pioggia_f":"Forte pluie","neve":"Neige","rovesci":"Averses","temporale":"Orage",
   "titolo":"Rome aujourd'hui","meteo":"Météo Rome · maintenant","min":"min","max":"max","pioggia_p":"pluie","vento":"vent","alba":"Lever","tramonto":"Coucher","percepita":"ressenti","umidita":"humidité","raffiche":"rafales","uv":"UV","dopodomani":"Après-demain","prossime":"Prochaines heures : température et risque de pluie","domani":"Demain","metro":"Métro","regolare":"Service normal","nd":"données indisponibles","vicino":"San Giovanni et Manzoni (ligne A) à 5 minutes à pied","treni":"Départs de Roma Termini","termini":"Termini : métro A, 2 arrêts","orario":"à l'heure","info":"Informations","wifi":"Wi-Fi","pw":"Mot de passe","colazione":"Petit-déjeuner","agg":"Mis à jour à",
   "giorni":["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"],"mesi":["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"]},
 "de":{"sereno":"Klar","poco_nuv":"Leicht bewölkt","nuvoloso":"Bewölkt","coperto":"Bedeckt","nebbia":"Nebel","pioviggine":"Nieselregen","pioggia":"Regen","pioggia_f":"Starker Regen","neve":"Schnee","rovesci":"Schauer","temporale":"Gewitter",
   "titolo":"Rom heute","meteo":"Wetter Rom · jetzt","min":"min","max":"max","pioggia_p":"Regen","vento":"Wind","alba":"Sonnenaufgang","tramonto":"Sonnenuntergang","percepita":"gefühlt","umidita":"Luftfeuchte","raffiche":"Böen","uv":"UV","dopodomani":"Übermorgen","prossime":"Nächste Stunden: Temperatur und Regenwahrscheinlichkeit","domani":"Morgen","metro":"U-Bahn","regolare":"Normaler Betrieb","nd":"keine Daten","vicino":"San Giovanni und Manzoni (Linie A) 5 Minuten zu Fuß","treni":"Abfahrten Roma Termini","termini":"Termini: Metro A, 2 Stationen","orario":"pünktlich","info":"Informationen","wifi":"WLAN","pw":"Passwort","colazione":"Frühstück","agg":"Aktualisiert um",
   "giorni":["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"],"mesi":["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]},
 "es":{"sereno":"Despejado","poco_nuv":"Poco nuboso","nuvoloso":"Nuboso","coperto":"Cubierto","nebbia":"Niebla","pioviggine":"Llovizna","pioggia":"Lluvia","pioggia_f":"Lluvia fuerte","neve":"Nieve","rovesci":"Chubascos","temporale":"Tormenta",
   "titolo":"Roma hoy","meteo":"Tiempo en Roma · ahora","min":"mín","max":"máx","pioggia_p":"lluvia","vento":"viento","alba":"Amanecer","tramonto":"Atardecer","percepita":"sensación","umidita":"humedad","raffiche":"rachas","uv":"UV","dopodomani":"Pasado mañana","prossime":"Próximas horas: temperatura y probabilidad de lluvia","domani":"Mañana","metro":"Metro","regolare":"Servicio normal","nd":"sin datos","vicino":"San Giovanni y Manzoni (línea A) a 5 minutos a pie","treni":"Salidas desde Roma Termini","termini":"Termini: metro A, 2 paradas","orario":"puntual","info":"Información","wifi":"Wi-Fi","pw":"Contraseña","colazione":"Desayuno","agg":"Actualizado a las",
   "giorni":["lunes","martes","miércoles","jueves","viernes","sábado","domingo"],"mesi":["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]},
}
LINGUE = ["it","en","fr","de","es"]
COLAZIONE_T = {"it":"dalle 8.00 alle 11.00 al forno artigianale <b>A QUO</b>","en":"8 to 11 a.m. at the artisan bakery <b>A QUO</b>","fr":"de 8 h à 11 h à la boulangerie artisanale <b>A QUO</b>","de":"8 bis 11 Uhr in der Handwerksbäckerei <b>A QUO</b>","es":"de 8.00 a 11.00 en la panadería artesanal <b>A QUO</b>"}
ICONA = {"sereno":"☀️","poco_nuv":"🌤","nuvoloso":"⛅","coperto":"☁️","nebbia":"🌫","pioviggine":"🌦","pioggia":"🌧","pioggia_f":"🌧","neve":"🌨","rovesci":"🌦","temporale":"⛈"}


def meteo():
    url = ("https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s"
           "&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,wind_gusts_10m"
           "&hourly=precipitation_probability,temperature_2m"
           "&daily=weather_code,temperature_2m_max,temperature_2m_min,"
           "precipitation_probability_max,sunrise,sunset,uv_index_max"
           "&timezone=Europe%%2FRome&forecast_days=3") % (LAT, LON)
    d = get(url)
    cur = d["current"]
    g = GRP.get(cur["weather_code"], "nuvoloso")
    # probabilità pioggia nelle prossime 6 ore
    hours = d["hourly"]["time"]
    probs = d["hourly"]["precipitation_probability"]
    idx = next((i for i, t in enumerate(hours)
                if dt.datetime.fromisoformat(t).replace(tzinfo=TZ) >= NOW), 0)
    temps = d["hourly"]["temperature_2m"]
    prossime = [(hours[i][11:16], probs[i], round(temps[i])) for i in range(idx, min(idx + 8, len(hours)))]
    dom = d["daily"]
    gd = GRP.get(dom["weather_code"][1], "nuvoloso")
    gd2 = GRP.get(dom["weather_code"][2], "nuvoloso")
    return {
        "temp": round(cur["temperature_2m"]), "g": g, "icon": ICONA[g],
        "vento": round(cur["wind_speed_10m"]), "raffiche": round(cur["wind_gusts_10m"]),
        "percepita": round(cur["apparent_temperature"]), "umidita": cur["relative_humidity_2m"],
        "uv": round(dom["uv_index_max"][0]),
        "oggi_max": round(dom["temperature_2m_max"][0]),
        "oggi_min": round(dom["temperature_2m_min"][0]),
        "oggi_pioggia": dom["precipitation_probability_max"][0],
        "alba": dom["sunrise"][0][11:16], "tramonto": dom["sunset"][0][11:16],
        "domani": {"g": gd, "icon": ICONA[gd],
                   "max": round(dom["temperature_2m_max"][1]),
                   "min": round(dom["temperature_2m_min"][1]),
                   "pioggia": dom["precipitation_probability_max"][1]},
        "dopodomani": {"g": gd2, "icon": ICONA[gd2],
                       "max": round(dom["temperature_2m_max"][2]),
                       "min": round(dom["temperature_2m_min"][2]),
                       "pioggia": dom["precipitation_probability_max"][2]},
        "prossime": prossime,
    }


# ---------------- METRO (Roma Mobilità, GTFS-RT service alerts) ----------------
ALERTS_URL = "https://romamobilita.it/sites/default/files/rome_rtgtfs_service_alerts_feed.pb"


def metro():
    from google.transit import gtfs_realtime_pb2  # pip install gtfs-realtime-bindings
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(get(ALERTS_URL, binary=True))
    stato = {"A": [], "B": [], "C": []}
    altri = []
    for e in feed.entity:
        if not e.HasField("alert"):
            continue
        a = e.alert
        testo = ""
        for t in a.header_text.translation:
            if t.language in ("it", "") and t.text:
                testo = t.text
                break
        if not testo and a.header_text.translation:
            testo = a.header_text.translation[0].text
        testo = " ".join(testo.split())
        # a quali linee si riferisce
        linee = set()
        for ie in a.informed_entity:
            rid = (ie.route_id or "").upper()
            for k in stato:
                if rid in ("MEA", "MEB", "MEC", "ME" + k, "METRO" + k, "LINEA" + k) and rid.endswith(k):
                    linee.add(k)
            if rid in ("MEA",): linee.add("A")
            if rid in ("MEB", "MEB1"): linee.add("B")
            if rid in ("MEC",): linee.add("C")
        up = testo.upper()
        for k in stato:
            if ("METRO " + k) in up or ("LINEA " + k) in up:
                linee.add(k)
        if linee:
            for k in linee:
                stato[k].append(testo)
        elif "SCIOPERO" in up or "STRIKE" in up:
            altri.append(testo)
    return {"linee": stato, "altri": altri[:3]}


# ---------------- TRENI DA TERMINI (ViaggiaTreno, API non ufficiale) ----------------
def treni():
    quando = NOW.strftime("%a %b %d %Y %H:%M:%S")
    url = ("http://www.viaggiatreno.it/infomobilita/resteasy/viaggiatreno/partenze/S08409/"
           + urllib.request.quote(quando))
    d = get(url)
    out = []
    for t in d[:12]:
        rit = t.get("ritardo") or 0
        out.append({
            "treno": (t.get("compNumeroTreno") or "").strip(),
            "dest": (t.get("destinazione") or "").title(),
            "ora": (t.get("compOrarioPartenza") or "")[:5],
            "ritardo": int(rit),
            "binario": (t.get("binarioProgrammatoPartenzaDescrizione") or "").strip(),
        })
    return out


# ---------------- HTML (compatibile Safari iOS 9: niente grid, niente ES6) ----------------
CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:#0b1220;color:#eef2ff;font-family:-apple-system,"Helvetica Neue",Helvetica,Arial,sans-serif;height:100%}
body{padding:28px 36px;display:-webkit-flex;display:flex;-webkit-flex-direction:column;flex-direction:column}
.top{display:-webkit-flex;display:flex;-webkit-justify-content:space-between;justify-content:space-between;-webkit-align-items:flex-end;align-items:flex-end;border-bottom:2px solid #22304d;padding-bottom:14px}
.top h1{font-size:30px;font-weight:600;letter-spacing:.5px}
.top .ora{font-size:58px;font-weight:300;line-height:1}
.top .data{font-size:20px;color:#9fb0d6;margin-top:4px}
.row{display:-webkit-flex;display:flex;margin-top:22px}
.card{background:#141d33;border-radius:16px;padding:20px 24px;margin-right:22px;-webkit-flex:1;flex:1}
.card:last-child{margin-right:0}
.card h2{font-size:17px;text-transform:uppercase;letter-spacing:1.5px;color:#9fb0d6;margin-bottom:12px}
.big{font-size:72px;font-weight:200;line-height:1}
.big small{font-size:30px;color:#9fb0d6;margin-left:8px}
.desc{font-size:26px;margin-top:6px}
.sub{font-size:18px;color:#c3cdeb;margin-top:10px;line-height:1.5}
.ore{display:-webkit-flex;display:flex;margin-top:12px}
.ore div{-webkit-flex:1;flex:1;text-align:center;font-size:15px;color:#9fb0d6}
.ore b{display:block;font-size:20px;color:#eef2ff;font-weight:500}
.ore i{display:block;font-style:normal;font-size:14px;color:#7fb3ff}
.linea{display:-webkit-flex;display:flex;-webkit-align-items:center;align-items:center;margin:9px 0}
.pill{width:46px;height:46px;border-radius:23px;font-size:24px;font-weight:700;text-align:center;line-height:46px;margin-right:14px;color:#fff}
.A{background:#e0521f}.B{background:#1f66c7}.C{background:#2a9d4c}
.ok{color:#5ad08a;font-size:22px}.ko{color:#ffb14a;font-size:17px;line-height:1.35}
table{width:100%;border-collapse:collapse;font-size:19px}
td{padding:7px 4px;border-bottom:1px solid #22304d;white-space:nowrap}
td.dest{white-space:normal}
.rit{color:#5ad08a;font-weight:600}.rit.late{color:#ff6b6b}
.foot{margin-top:auto;padding-top:14px;font-size:15px;color:#6f7fa6;display:-webkit-flex;display:flex;-webkit-justify-content:space-between;justify-content:space-between}
.err{color:#6f7fa6;font-size:18px}
"""



def esc(s):
    return html.escape(str(s))


def card_meteo(m, L):
    if not m:
        return '<div class="card"><h2>%s</h2><p class="err">%s</p></div>' % (L["meteo"], L["nd"])
    ore = "".join('<div>%s<b>%s&deg;</b><i>%s%%</i></div>' % (esc(h), esc(t), esc(p)) for h, p, t in m["prossime"])
    return """<div class="card"><h2>%s</h2>
<div class="big">%s<small>%s&deg;C</small></div>
<div class="desc">%s</div>
<div class="sub">%s %s&deg; &middot; %s %s%% &middot; %s %s km/h (%s %s) &middot; %s %s<br>
%s %s&deg; / %s %s&deg; &middot; %s %s%% &middot; %s %s &middot; %s %s</div>
<div class="sub" style="margin-top:12px;color:#9fb0d6">%s</div>
<div class="ore">%s</div>
<div class="sub" style="margin-top:14px"><b>%s:</b> %s %s, %s&deg; / %s&deg;, %s %s%%<br>
<b>%s:</b> %s %s, %s&deg; / %s&deg;, %s %s%%</div>
</div>""" % (L["meteo"], m["icon"], m["temp"], L[m["g"]],
             L["percepita"], m["percepita"], L["umidita"], m["umidita"], L["vento"], m["vento"], L["raffiche"], m["raffiche"], L["uv"], m["uv"],
             L["min"], m["oggi_min"], L["max"], m["oggi_max"], L["pioggia_p"], m["oggi_pioggia"], L["alba"], m["alba"], L["tramonto"], m["tramonto"],
             L["prossime"], ore,
             L["domani"], m["domani"]["icon"], L[m["domani"]["g"]], m["domani"]["min"], m["domani"]["max"], L["pioggia_p"], m["domani"]["pioggia"],
             L["dopodomani"], m["dopodomani"]["icon"], L[m["dopodomani"]["g"]], m["dopodomani"]["min"], m["dopodomani"]["max"], L["pioggia_p"], m["dopodomani"]["pioggia"])


def card_metro(mt, L):
    righe = []
    for k in ("A", "B", "C"):
        if not mt:
            st = '<span class="err">%s</span>' % L["nd"]
        elif mt["linee"][k]:
            st = '<span class="ko">%s</span>' % esc(mt["linee"][k][0][:160])
        else:
            st = '<span class="ok">%s</span>' % L["regolare"]
        righe.append('<div class="linea"><div class="pill %s">%s</div><div>%s</div></div>' % (k, k, st))
    extra = ""
    if mt and mt["altri"]:
        extra = '<div class="sub ko">%s</div>' % esc(mt["altri"][0][:200])
    return ('<div class="card"><h2>%s</h2>%s%s'
            '<div class="sub" style="margin-top:14px">%s</div></div>'
            % (L["metro"], "".join(righe), extra, L["vicino"]))


def card_treni(tr, L):
    if not tr:
        return '<div class="card"><h2>%s</h2><p class="err">%s</p></div>' % (L["treni"], L["nd"])
    righe = []
    for t in tr[:9]:
        if t["ritardo"] > 0:
            rit = '<span class="rit late">+%d min</span>' % t["ritardo"]
        else:
            rit = '<span class="rit">%s</span>' % L["orario"]
        righe.append('<tr><td>%s</td><td class="dest">%s</td><td>%s</td><td>%s</td></tr>'
                     % (esc(t["ora"]), esc(t["dest"]), esc(t["binario"]), rit))
    return ('<div class="card"><h2>%s</h2><table>%s</table>'
            '<div class="sub" style="margin-top:10px;font-size:15px">%s</div></div>'
            % (L["treni"], "".join(righe), L["termini"]))


def pagina(m, mt, tr, lang, succ):
    L = T[lang]
    data = "%s %d %s %d" % (L["giorni"][NOW.weekday()], NOW.day, L["mesi"][NOW.month - 1], NOW.year)
    return """<!DOCTYPE html>
<html lang="%s"><head><meta charset="utf-8">
<meta http-equiv="refresh" content="20;url=%s">
<meta name="viewport" content="width=1024">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<title>SunnyCorner</title>
<style>%s</style></head>
<body>
<div class="top"><div><h1>SunnyCorner &middot; %s</h1><div class="data">%s</div></div>
<div class="ora">%s</div></div>
<div class="row">%s%s</div>
<div class="row">%s
<div class="card"><h2>%s</h2>
<div class="sub" style="font-size:22px">%s: %s</div>
</div></div>
<div class="foot"><span>%s %s &middot; %s</span><span>Open-Meteo &middot; Roma Mobilit&agrave; &middot; Trenitalia</span></div>
</body></html>""" % (lang, succ, CSS, L["titolo"], esc(data), NOW.strftime("%H:%M"), card_meteo(m, L), card_metro(mt, L),
                     card_treni(tr, L), L["info"],
                     L["colazione"], COLAZIONE_T[lang], L["agg"], NOW.strftime("%H:%M"),
                     " &middot; ".join(x.upper() if x == lang else x for x in LINGUE))


def prova(f):
    try:
        return f()
    except Exception as e:  # una fonte giù non deve fermare la lavagna
        print("ATTENZIONE %s: %s" % (f.__name__, e), file=sys.stderr)
        return None


if __name__ == "__main__":
    import os
    os.makedirs("docs", exist_ok=True)
    m, mt, tr = prova(meteo), prova(metro), prova(treni)
    for i, lang in enumerate(LINGUE):
        nxt = LINGUE[(i + 1) % len(LINGUE)]
        nome = "index.html" if lang == "it" else lang + ".html"
        succ = "index.html" if nxt == "it" else nxt + ".html"
        with open("docs/" + nome, "w", encoding="utf-8") as fh:
            fh.write(pagina(m, mt, tr, lang, succ))
    print("docs/index.html generata alle", NOW.strftime("%H:%M"))
