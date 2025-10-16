# Datenmodell

Überblick über zentrale Modelle (vereinfachte Sicht, nicht vollständig).

## Kernentitäten (Beispiele)
- `Bird` – Patient / Fall (Aufnahmedatum, Fundort, Zustand, Status, Entlassungs-/Sterbedatum)
- `Cost` – Kostenposition mit Bezug zu `Bird` oder allgemeiner Kategorie
- `Contact` – Personen/Organisationen (Pflegestellen, Behörden, Finder)
- `ReportLog` – Protokollierter Bericht / automatischer Versandstatus
- `WildbirdHelpStation` – Externe Wildvogelhilfestation (Name, Ort, Land, Koordinaten, Kontakt, Quelle)
- `StationReport` – Vorschlag für neue Station (pending -> accepted/declined)

## Relationen (Auszug)
- `Cost` n:1 `Bird`
- `ReportLog` referenziert Export-/Berichtstypen oder Zielgruppen
- `StationReport` kann nach Annahme zu `WildbirdHelpStation` überführt werden

## Änderungs-/Historienaspekte
Aktuell einfache Änderungsnachverfolgung durch Timestamp-Felder (`created`, `updated`). Erweiterbar durch Audit Trail (Signal-basiert) oder externe Libraries.

## Geodaten
`WildbirdHelpStation` speichert Koordinaten als numerische Felder (Lat/Lon). Geokodierung via Management Command oder Admin Aktion (siehe [[Stations-Modul]]).

## Performancehinweise
Indexes auf häufig gefilterten Feldern (Name, Ort, Land). Optional: später PostGIS für Distanzabfragen.

Weiter: [[Stations-Modul]]
