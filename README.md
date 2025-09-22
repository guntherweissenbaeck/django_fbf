# Fallen Birdy Form

## Inhaltsverzeichnis
1. [Über dieses Projekt](#über-dieses-projekt)
2. [Schnellstart](#schnellstart)
3. [Entwicklungsumgebung einrichten](#entwicklungsumgebung-einrichten)
4. [Tests ausführen](#tests-ausführen)
5. [Dokumentation erzeugen](#dokumentation-erzeugen)
6. [Troubleshooting](#troubleshooting)
7. [Spendenlink](#spendenlink)

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

## Troubleshooting
- **Docker-Container starten nicht:** Prüfen, ob Ports 8000, 8008 und 8081 frei sind. Bei Konflikten Ports in `docker-compose.yaml` anpassen.
- **`start_project.sh` bricht ab:** Stellen Sie sicher, dass OpenSSL verfügbar ist (für die Secret-Key-Erzeugung) und Docker Desktop läuft.
- **Tests schlagen fehl, weil Django nicht gefunden wird:** Beim lokalen Pytest-Lauf `PYTHONPATH=app` setzen oder das Projektpaket installieren.
- **E-Mails werden nicht verschickt:** In der Entwicklung kommt der Konsolen-Backend zum Einsatz. Für reale SMTP-Verbindungen die entsprechenden Variablen (`EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`) in `.env` pflegen.
- **Statische Dateien fehlen im Testlauf:** Das Startskript führt `collectstatic` aus. Bei manueller Ausführung `docker compose exec web python manage.py collectstatic` starten.

## Spendenlink
Unterstützen Sie die Arbeit der NABU Wildvogelhilfe Jena mit einer Spende:
- NABU Kreisverband Jena e. V. – Wildvogelhilfe Jena
- Spendenportal: https://www.nabu-jena.de/spenden/wvh/
