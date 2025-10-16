# Architektur

Dieses Dokument beschreibt die technische Struktur der Fallen Birdy Form (FBF).

## High-Level Übersicht
Komponenten:
1. Django Backend (Business-Logik, Admin, API/JSON-Views)
2. PostgreSQL Datenbank
3. Admin-UI mit Jazzmin Theme
4. Stations-Kartenfrontend (Leaflet + JSON Endpoint)
5. Reporting & Export (CSV, Behördendateien, automatische Reports)
6. Service Worker / PWA Assets
7. Dokumentation (Doxygen)

## Wichtige Apps (Auswahl)
- `core` – Basiskomponenten, globale Utilities
- `bird` – Patienten-/Fallverwaltung
- `stations` – Wildvogelhilfen-Karte, Geokodierung, öffentliche Vorschläge
- `export` – Datenexporte & Berichtslogik
- `reports` – Automatische und manuelle Berichte / Protokolle
- `costs` – Kostenerfassung & Auswertung
- `contact` – Kontakte & Kommunikationsdaten

## Datenflüsse
- Aufnahmeformular erzeugt Patient (bird) -> Benachrichtigungen -> Statistik Views / Reports
- Stations-Vorschläge (public POST) -> Admin Review -> Übernahme in `WildbirdHelpStation`
- CSV Import/Update (Admin Action) -> Normalisierung -> Geokodierungs-Task (optional)
- Export/Auswertung -> CSV / ReportLog / Behördenformate

## Persistenz
Primär PostgreSQL. Migrations via Django standard. Fixtures zur Erstbefüllung unter `fixtures/`.

## Caching & Performance
Der Stations-JSON Endpoint setzt derzeit auf no-store Header (siehe [[Stations-Modul]]). Später mögliche Einführung kurzer Expiry + ETag Re-Validierung.

## Sicherheit
- Admin-Login zwingend über Django Auth
- Öffentliche Endpoints minimal (Stationsliste, Vorschlagsformular)
- CSRF aktiv für nicht-GET Admin-/Form-Interaktionen
- Siehe [[Security-und-Privacy]] für Details

## Dokumentation
Doxygen generiert HTML & XML aus Docstrings (Befehl: `doxygen Doxyfile`). Ergebnisse unter `docs/doxygen/html/`.

## Erweiterbarkeit
Neue fachliche Module als separate Django Apps anlegen. Namenskonvention: sprechender App-Name, Docstrings im Modul, Admin-Integration & Tests.

Weiter: [[Datenmodell]]
