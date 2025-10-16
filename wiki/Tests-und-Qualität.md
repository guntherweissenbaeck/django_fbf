# Tests & Qualität

## Testarten
- Django TestCase (Model, View, Form, Admin)
- Pytest für Integrations- und Funktionstests
- Coverage Report (`htmlcov/index.html`) – derzeit ~45 %

## Ausführung
Komplettlauf:
```bash
./start_test.sh
```
Einzellauf Beispiele:
```bash
docker compose exec web python manage.py test
PYTHONPATH=app python3 -m pytest test/ -v
```

## Zielwerte
- Kurzfristig: >55 % Coverage (kritische Pfade priorisiert)
- Mittelfristig: 70 % (inkl. Fehlerpfade & Edge Cases)

## Qualitätssicherung
- Doxygen für API / interne Dev-Dokumentation
- Geplante Pre-Commit Hooks: Linting (flake8/ruff), isort, black (optional)
- Geplante CI Pipeline: Build + Tests + Coverage Badge

## Edge Case Beispiele
- Mehrfachanlage gleichartiger Patienten in kurzer Zeit
- Ungültige CSV beim Stationsimport (Encoding, fehlende Spalten)
- Geokodierung ohne Treffer / Rate Limit
- Berichtsexport ohne Daten

Weiter: [[Dokumentation]]
