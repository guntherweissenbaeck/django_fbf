# Fallen Birdy Form

## Inhaltsverzeichnis
1. [Über dieses Projekt](#über-dieses-projekt)
2. [Schnellstart](#schnellstart)
3. [Entwicklungsumgebung einrichten](#entwicklungsumgebung-einrichten)
4. [Tests ausführen](#tests-ausführen)
5. [Dokumentation erzeugen](#dokumentation-erzeugen)
6. [Wildvogelhilfen-Karte](#wildvogelhilfen-karte)
7. [Troubleshooting](#troubleshooting)
8. [Spendenlink](#spendenlink)
9. [Progressive Web App](#progressive-web-app)

## Über dieses Projekt
Fallen Birdy Form ist das Verwaltungsportal der NABU Wildvogelhilfe Jena. Das System unterstützt ehrenamtliche Helferinnen und Helfer bei der Erfassung, Pflege und Auswertung von Patientenvögeln. Wichtige Arbeitsbereiche sind unter anderem:
- Aufnahmeformulare für neue Patienten (inklusive Mehrfachanlage und automatischer Benachrichtigungen)
- Verwaltung von Volieren, Kosten, Kontakten sowie Berichten
- Umfangreiche Statistik- und Exportfunktionen für Behördenmeldungen

Technische Eckdaten:
- Backend: Django 5, PostgreSQL, Docker Compose
- Frontend: Django Templates, Jazzmin für das Admin-Interface
- Tests: Django Test Runner und Pytest (Unit-, Integrations- und Funktionstests)

## Schnellstart
1. Voraussetzungen installieren: Docker Desktop (inkl. Compose) sowie OpenSSL für das Startskript.
2. Repository klonen und in das Projektverzeichnis wechseln.
3. Projekt starten:
   ```bash
   ./start_project.sh
   ```
   Das Skript erstellt bei Bedarf eine `.env`, baut Container, führt Migrationen aus, lädt optional Fixtures, legt einen Admin-Benutzer (`admin` / `admin`) an und sammelt statische Dateien.
4. Nach erfolgreichem Start stehen zur Verfügung:
   - Anwendung: http://localhost:8008
   - Admin-Backend: http://localhost:8008/admin

Projekt stoppen:
```bash
./stop_project.sh
```

## Entwicklungsumgebung einrichten
- Standardbenutzer anlegen: Im Startskript wird ein Test-Admin erstellt. Eigene Zugangsdaten lassen sich über `docker compose exec web python manage.py createsuperuser` erzeugen.
- Testdaten laden:
  ```bash
  docker compose exec web python manage.py loaddata fixtures/data.json
  ```
- Zusätzliche Umgebungsschalter (z. B. Mailserver, CSRF) lassen sich über `.env` setzen. Eine Beispielkonfiguration liegt in `.env.example`.

## Tests ausführen
Empfohlener Komplettlauf:
```bash
./start_test.sh
```
Das Skript prüft zunächst, ob die Container laufen, und führt dann nacheinander aus:
- `docker compose exec web python manage.py test`
- `python3 -m pytest test/ -v`
Anschließend wird ein HTML-Coverage-Report unter `htmlcov/index.html` generiert (aktuelle Gesamtabdeckung: 45 %).

Einzelläufe:
```bash
# Django Tests
docker compose exec web python manage.py test

# Pytest gesamt
PYTHONPATH=app python3 -m pytest test/ -v

# Nur Unit-Tests
PYTHONPATH=app python3 -m pytest test/unit/ -v
```

## Dokumentation erzeugen
Alle relevanten Module enthalten Doxygen-fähige Docstrings. Zur Generierung der HTML-Dokumentation:
```bash
doxygen Doxyfile
```
Das Ergebnis liegt unter `docs/doxygen/html/index.html`. XML-Artefakte für weiterführende Toolchains entstehen im Verzeichnis `docs/doxygen/xml/`.

Die neue App `stations` (Route `/stationen`) ist vollständig mit Doxygen-kompatiblen Docstrings versehen und wird automatisch durch den bestehenden Dokumentationslauf erfasst.

## Wildvogelhilfen-Karte
- Öffentliche Karte unter `https://<SERVER>/stationen` mit Leaflet-Frontend und JSON-Daten aus dem neuen Modell `WildbirdHelpStation`.
- Auf der Login-Seite führt ein zusätzlicher Button direkt zur Karte, sodass keine Zugangsdaten erforderlich sind.
- Pflege der Stationen erfolgt über das Django-Admin (`Wildvogelhilfe-Stationen`). Über die Werkzeugleiste steht eine Schaltfläche **CSV importieren** bereit.
- Für Imports können beliebige semikolon-separierte CSV-Dateien im beschriebenen Format genutzt werden; bestehende Datensätze werden anhand von Name, Ort und Land aktualisiert.
- Ein CSV-Export steht als Admin-Aktion **„Auswahl als CSV exportieren“** zur Verfügung und entspricht dem Importformat (Semikolon-getrennt, UTF-8).
- Besucher können über `/stationen/report` neue Stationen vorschlagen; eingehende Vorschläge landen im Admin unter `/admin/stations/reports` und lassen sich dort prüfen, übernehmen oder ablehnen.
- Im selben Admin-Bereich kann optional eine Benachrichtigungsadresse gepflegt werden, die bei neuen Vorschlägen automatisch informiert wird.
- Koordinaten lassen sich pro Station oder gesammelt über die Admin-Aktion **„Koordinaten automatisch ermitteln“** sowie via Management Command `python manage.py geocode_stations` bestimmen.

### Cache-Busting / Aktuelle Stationsdaten

Im September 2025 trat das Problem auf, dass die JSON-Daten unter `/stationen/daten/` (Route-Name `stations:data`) nur nach Hard-Reload (CMD+Shift+R) aktualisiert wurden. Ursache waren Browser- bzw. Proxy-Caches.

Die View `StationDataView` sendet jetzt strikte Header:

```
Cache-Control: no-store, no-cache, must-revalidate, max-age=0
Pragma: no-cache
Expires: 0
ETag: "<hash>"
Last-Modified: <timestamp>
```

Damit werden veraltete Marker ausgeschlossen; gleichzeitg können Clients bei unverändertem Datenstand per `If-None-Match` einen 304 erhalten. Für späteres, moderates Caching (z. B. 300 Sekunden) kann `Cache-Control` angepasst werden, solange `ETag`/`Last-Modified` bestehen bleiben.

## Troubleshooting
- **Docker-Container starten nicht:** Prüfen, ob Ports 8000, 8008 und 8081 frei sind. Bei Konflikten Ports in `docker-compose.yaml` anpassen.
- **`start_project.sh` bricht ab:** Stellen Sie sicher, dass OpenSSL verfügbar ist (für die Secret-Key-Erzeugung) und Docker Desktop läuft.
- **Tests schlagen fehl, weil Django nicht gefunden wird:** Beim lokalen Pytest-Lauf `PYTHONPATH=app` setzen oder das Projektpaket installieren.
- **E-Mails werden nicht verschickt:** In der Entwicklung kommt der Konsolen-Backend zum Einsatz. Für reale SMTP-Verbindungen die entsprechenden Variablen (`EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`) in `.env` pflegen.
- **Statische Dateien fehlen im Testlauf:** Das Startskript führt `collectstatic` aus. Bei manueller Ausführung `docker compose exec web python manage.py collectstatic` starten.

## Progressive Web App
Die Fallen Birdy Form kann als Progressive Web App (PWA) installiert und offline verwendet werden. Seiten wie das Dashboard, die Login-Maske und die Offline-Hinweisseite werden vom Service Worker vorgehalten.

- **Android (Chrome):** Anwendung im Chrome-Browser öffnen, über das Drei-Punkte-Menü `App installieren` oder `Zum Startbildschirm hinzufügen` auswählen und bestätigen.
- **iOS (Safari):** Anwendung in Safari öffnen, Teilen-Symbol antippten und `Zum Home-Bildschirm` auswählen; optional Namen anpassen und hinzufügen.
- **Desktop:** Moderne Browser (Chrome, Edge, Firefox) zeigen in der Adressleiste einen Installationshinweis oder Menüpunkt `Installieren`. Darüber kann eine Desktop-PWA erstellt werden.

## Spendenlink
Unterstützen Sie die Arbeit der NABU Wildvogelhilfe Jena mit einer Spende:
- NABU Kreisverband Jena e. V. – Wildvogelhilfe Jena
- Spendenportal: https://www.nabu-jena.de/spenden/wvh/
