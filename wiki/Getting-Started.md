# Getting Started

Dieser Leitfaden zeigt den schnellsten Weg zur laufenden lokalen Instanz.

## Voraussetzungen
- Docker Desktop (inkl. Compose Plugin)
- Git
- OpenSSL (für Secret Key Erzeugung im Startskript)
- (Optional) Python 3 lokal für isolierte Pytest-Läufe

## Repository klonen
```bash
git clone <REPO_URL> django_fbf
cd django_fbf
```

## Projekt starten
Das Automationsskript übernimmt Build, Migrations, Admin-User, Fixtures & statische Dateien.
```bash
./start_project.sh
```
Bereitstellung:
- App: http://localhost:8008
- Admin: http://localhost:8008/admin (Default Login: `admin` / `admin` bei Erststart)

## Projekt stoppen
```bash
./stop_project.sh
```

## Testdaten laden (optional)
```bash
docker compose exec web python manage.py loaddata fixtures/data.json
```

## Tests ausführen
Komplettlaufskript:
```bash
./start_test.sh
```
Manuell:
```bash
docker compose exec web python manage.py test
PYTHONPATH=app python3 -m pytest test/ -v
```

## Nächste Schritte
- Siehe [[Architektur]] für Komponentenüberblick
- Siehe [[Stations-Modul]] für das neue Stations-Feature
- Siehe [[Tests-und-Qualität]] für Testabdeckung & Strategie
