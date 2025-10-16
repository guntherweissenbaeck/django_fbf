# Import & Export

## CSV Exporte
- Stationsdaten (Admin Aktion, siehe [[Stations-Modul]])
- Patienten-/Berichtsrelevante Daten (geplant – Roadmap)

## Geplante Erweiterungen
- Standardisiertes Behörden-Exportformat (Monats-/Jahresbericht)
- Automatisierte periodische Exporte via Management Command + Cron / Scheduler

## Qualitätsanforderungen
- UTF-8 Encoding
- Semikolon als Standardtrennzeichen (Kompatibilität deutschsprachiger Excel-Umgebungen)
- Feldnormalisierung (Trim, Whitespace, Groß-/Kleinschreibung) vor Upsert

## Sicherheit / Datenschutz
- Exporte minimieren personenbezogene Daten (Filterbare Views)

Weiter: [[Tests-und-Qualität]]
