# Überblick

Das Kartenspiel ist ein einfaches, *rasch* entwickeltes Spiel für agile Teams, um Entscheidungen aus unterschiedlichen Perspektiven spielerisch durchzuprobieren und so flotter zu besseren Entscheidungen zu kommen, die mehr Perspektiven berücksichtigen. Absicht ist, eingeschliffene Entscheidungspfade zu durchbrechen und so besser auf verändernde Rahmenbedingungen zu reagieren.

## Keine Inhalte

Dieses Kartenspiel kommt ohne Inhalte, diese können einfach über ein Webinterface hinzugefügt werden.

## Kurze Erläuterung

Es ist sowohl möglich, dass die Teilnehmer_innen individuell ziehen (aus einem Stapel) als auch moderiert. Bei Wahl der moderierten Spielweise können Mitspieler_innen nicht einzeln ziehen, sondern nur die Moderator*in. Die Spieloptionen sind auf der Startseite (`templates/index.html`) erläutert.

Das Spiel unterscheidet zwischen zwei Arten von Karten: "Leitsätzen" und allen anderen. Beide Stapel können (bei gewählter Option) einzeln gezogen werden.

## Sinnvolle Spieleinstellungen

Per Voreinstellung sind sinnvolle Vorgaben für dezentral / remote arbeitende Teams eingestellt (moderierte Spielweise). Die Darstellung ist darauf ausgelegt, gut in Videokonferenzsoftware wie z. B. Jitsi, Zoom oder Teams zu funktionieren.

# Installation

1. Repositorium kopieren / klonen
2. Abhängigkeiten installieren: `pip install -r requirements.txt`
3. Pfad `basispfad` in `src/init.py` anpassen, ggf. weitere Anpassungen dort. Der Basispfad muss auf das Rumpfverzeichnis zeigen, also unterhalb von `src/`.
4. Datenbanken anlegen: `python setup.py`
5. Unter `static/css` ggf. Bootstrap 5-CSS-Dateien hinzufügen oder über CDN laden; unter `static/js` ggf. Bootstrap 5-Javasscript-Dateien hinzufügen oder über CDN laden. Bei Wahl des CDN bitte unter `templates/basis.html` anpassen.
6. Spiel starten: `python app.py`
7. Das Spiel ist einsatzbereit, über die Weboberfläche können Inhalte hinzugefügt werden. 

Auf dem Mac ist ggf. `pip3` und `python3` zu benutzen. 

Flask läuft voreingestellt auf `Port 2400` im Debugmodus (`app.py`). Template werden bei Veränderungen aktualisiert (`app.config['TEMPLATES_AUTO_RELOAD']` in `src/init.py`)

Für Produktiveinsatz ggf. selbst erledigen: Anbindung des Flaskservers per z. B. uWSGI an den Webserver.


# Dateistruktur

* `app.py`: Startet Flaskserver (`app:main`)
* `setup.py`: Legt Datenbank an

## `db/`: Datenbank
*  `./setup.py` legt `db/datenbank.db` (sqlite) an 

## `src/`

* `src/admin.py`: Definiert Views für die Adminoberfläche
* `src/init.py`: Alle Einstellungen; bei gewünschtem Passwortschutz die markierten Zeilen auskommentieren; hier muss auch `app.config['SECRET_KEY']` gesetzt werden
* `src/modelle.py`: Datenbankmodelle `Karte` und `Sitzung` und fasst Abfragen in `ziehe_aus_stapel` bzw. `abfragen` zusammen
* `src/routen.py`: HTTP-Routen; die Routen sind kommentiert
* `src/spiel.py`: Spiel-Logik; die Funktionen sind kommentiert
* `src/tiere.py`: Hält die Tiernamen (englisch, kopiert von [Lexicalbits](https://gist.github.com/lexicalbits/883f1867985208797be75a873d006bef))

## `static/`: CSS, Javascript-Dateien und Uploadverzeichnis

* `static/css`: Hier Bootstrap 5-CSS-Dateien ablegen; Anpassungen unter `static/css/zusatz.css`
* `static/img`: Uploadfolder für Karten-Hintergrundbilder (Verzeichnis über `src/init.py` änderbar)
* `static/js`: Hier Bootstrap 5-Javascript-Dateien ablegen; Anpassungen unter `static/js/zusatz.js`

## `templates/`: Templates

* `templates/basis.hml`: Rumpf-Template, wird von allen anderen Template eingebunden
* `templates/fehler_404.html`: Fehlermeldung (404)
* `templates/fehler_500.html`: Fehlermeldung (500)
* `templates/index.html`: Startseite, hier auch Optionen einstellbar; bei Änderung der Standardoptionen ggf. `src/spiel:neue_sitzung` anpassen
* `templates/karte_alle.html`: Zeigt alle Karten an zum schnellen Überblick außerhalb des Spiels 
* `templates/karte_basis.html`: Rumpf-Template für alle Karten-Ansichten
* `templates/karte_letzte.html`: Wird verwendet, wenn nur noch eine Karte im Stapel ist, aber zwei Karten gezogen werden sollten
* `templates/karte_zwei.html`: Standardansicht des Kartenspiels, wenn die Option "zwei Karten ziehen" gewählt ist
* `templates/karte.html`: Standardansicht des Kartenspiels in allen anderen Fällen
* `templates/spiel_deck_leer.html`: Es gibt keine Karten im Stapel mehr
* `templates/spiel_einladung.html`: Landingpage bei Einladung zum Spiel bzw. Standardansicht zu Beginn eines Spiels
