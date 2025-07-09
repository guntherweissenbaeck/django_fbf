# Manuelle "Sofort senden" Funktion für Automatische Reports

## Übersicht

Die neue "Sofort senden" Aktion im Django Admin ermöglicht es Administratoren, automatische Reports manuell und sofort zu versenden, ohne auf den geplanten Zeitpunkt warten zu müssen.

## Verwendung

1. **Admin-Bereich öffnen**: Navigieren Sie zu `/admin/reports/automaticreport/`
2. **Reports auswählen**: Wählen Sie einen oder mehrere automatische Reports aus der Liste aus
3. **Aktion ausführen**: Wählen Sie aus dem Aktions-Dropdown "Ausgewählte Reports sofort senden"
4. **Bestätigen**: Klicken Sie auf "Ausführen"

## Funktionalität

### Automatische Zeitraumberechnung
Die Aktion berechnet automatisch den Zeitraum basierend auf der Frequenz des Reports:

- **Wöchentlich**: Letzte 7 Tage
- **Monatlich**: Letzter Monat (vom 1. des Vormonats bis heute)
- **Vierteljährlich**: Letztes Quartal (3 Monate zurück)

### Validierung und Filterung
Vor dem Versenden wird überprüft:

- ✅ **Aktivierung**: Report muss aktiv sein (`is_active = True`)
- ✅ **E-Mail-Adressen**: Mindestens eine E-Mail-Adresse muss konfiguriert sein
- ✅ **Filter**: Die konfigurierten Filter (Naturschutz-/Jagdbehörde) werden angewendet

### Rückmeldungen
Das System gibt detaillierte Rückmeldungen:

- ✅ **Erfolgreich**: Anzahl gesendeter E-Mails, Zeitraum, Patientenzahl
- ⚠️ **Übersprungen**: Grund für das Überspringen (deaktiviert, keine E-Mail-Adressen)
- ❌ **Fehler**: Detaillierte Fehlermeldungen bei Problemen

### Protokollierung
- Alle versendeten Reports werden in `ReportLog` protokolliert
- Das `last_sent` Feld des AutomaticReport wird aktualisiert
- CSV-Dateien werden gespeichert und können später heruntergeladen werden

## Technische Details

### Implementierung
- **Datei**: `/app/reports/admin.py`
- **Methode**: `send_report_now()`
- **Service**: Verwendet `ReportGenerator` aus `reports.services`

### Sicherheit
- Nur Administratoren mit entsprechenden Berechtigungen können diese Aktion ausführen
- Deaktivierte Reports werden automatisch übersprungen
- Umfassende Fehlerbehandlung verhindert Systemausfälle

## Beispiel-Ausgaben

### Erfolgreicher Versand
```
✅ Report 'Monatlicher Naturschutzbericht' erfolgreich gesendet (letzter Monat, 15 Patienten, 3 Empfänger).
✅ Zusammenfassung: 1 Report(s) erfolgreich gesendet.
```

### Übersprungener Report
```
⚠️ Report 'Deaktivierter Report' ist deaktiviert und wurde übersprungen.
ℹ️ Alle 1 ausgewählten Reports wurden übersprungen (deaktiviert oder keine E-Mail-Adressen).
```

### Fehler beim Versand
```
❌ Fehler beim Senden von 'Fehlerhafter Report': SMTP-Server nicht erreichbar.
❌ Alle 1 Reports konnten nicht gesendet werden.
```

## Troubleshooting

### Häufige Probleme

1. **"Report ist deaktiviert"**
   - Lösung: Report in der Detail-Ansicht aktivieren (`is_active = True`)

2. **"Keine E-Mail-Adressen"**
   - Lösung: E-Mail-Adressen im Report konfigurieren

3. **"'Emailadress' object has no attribute 'email'"**
   - Technischer Fehler: Das Emailadress-Model verwendet `email_address` statt `email`
   - Lösung: Wurde in Version 1.1 behoben

4. **"SMTP-Fehler"**
   - Lösung: E-Mail-Konfiguration in `settings.py` überprüfen

5. **"Keine Patienten gefunden"**
   - Normal: Report wird trotzdem versendet, zeigt 0 Patienten an

### Log-Überprüfung
- Alle Versandaktivitäten werden in `/admin/reports/reportlog/` protokolliert
- Bei Fehlern die Django-Logs überprüfen

## Entwickler-Hinweise

### Anpassungen
- Zeitraumberechnung kann in der `send_report_now()` Methode angepasst werden
- Zusätzliche Validierungen können hinzugefügt werden
- E-Mail-Templates befinden sich in `/templates/reports/email/`

### Erweiterungen
- Mögliche Erweiterung: Benutzerdefinierte Zeiträume
- Mögliche Erweiterung: Vorschau vor dem Versand
- Mögliche Erweiterung: Stapelverarbeitung mit Fortschrittsanzeige
