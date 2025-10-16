# Stations Modul

Öffentliche Karte & Verwaltung externer Wildvogelhilfestationen.

## Features
- Öffentliche Karte unter `/stationen` (Leaflet)
- JSON Endpoint `/stationen/daten/` liefert strukturierte Stationsliste
- Formular `/stationen/report` für neue Vorschläge ohne Login
- Admin Review Workflow für eingehende Vorschläge
- CSV Import / Update (Semikolon-getrennt, UTF-8)
- CSV Export als Admin Aktion
- Geokodierung (einzeln oder Bulk)

## CSV Import
- Admin -> Liste `Wildvogelhilfe-Stationen` -> Button "CSV importieren"
- Matching: Name + Ort + Land aktualisiert bestehende Einträge
- Neue Datensätze werden angelegt

## CSV Export
- Admin Aktion: Auswahl -> "Auswahl als CSV exportieren"
- Format identisch zum Import (Semikolon, UTF-8)

## Geokodierung
- Admin Aktion "Koordinaten automatisch ermitteln"
- Management Command: `python manage.py geocode_stations`
- Später: Caching externer API Antworten & Rate Limit Handling

## Cache / Aktualität
Zur Vermeidung veralteter Marker: no-store Header + ETag in `StationDataView` (siehe README Abschnitt). Optionale zukünftige Optimierung: 300s Cache + 304 Revalidierung.

## Sicherheit
- Öffentliche Endpoints liefern nur notwendige Felder
- Vorschlagsformular validiert Eingaben und kann Benachrichtigungsmail auslösen

Weiter: [[Import-Export]]
