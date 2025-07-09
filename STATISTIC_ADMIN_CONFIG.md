# Statistic Admin Configuration

## Überblick

Die Statistik-App verfügt jetzt über eine vollständig konfigurierbare Admin-Oberfläche mit drei separaten Bereichen für maximale Flexibilität:

1. **Statistik-Individuen**: Konfiguration der Balkendiagramme für Vogelarten
2. **Statistik-Jahr**: Konfiguration der Jahresstatistik-Karten
3. **Statistik-Insgesamt**: Konfiguration der Gesamtstatistik-Karten

## Neue Modell-Struktur

### StatisticIndividual (Statistik-Individuen)
- **Zweck**: Definiert Gruppierungen von BirdStatus für die Vogelarten-Balkendiagramme
- **Felder**:
  - `name`: Name der Gruppe (z.B. "Gerettet", "Verstorben")
  - `color`: Hex-Farbcode für die Darstellung (z.B. #28a745)
  - `order`: Reihenfolge der Gruppen in den Balkendiagrammen
  - `status_list`: ManyToMany-Beziehung zu BirdStatus
  - `is_active`: Ob diese Gruppe angezeigt werden soll

### StatisticYearGroup (Statistik-Jahr)
- **Zweck**: Definiert Gruppierungen für die Jahresstatistik-Übersichtskarten
- **Felder**:
  - `name`: Name der Jahresgruppe
  - `color`: Hex-Farbcode für die Karten-Darstellung
  - `order`: Reihenfolge der Karten in der Jahresübersicht
  - `status_list`: Welche BirdStatus gehören zu dieser Jahresgruppe
  - `is_active`: Aktivierung/Deaktivierung

### StatisticTotalGroup (Statistik-Insgesamt)
- **Zweck**: Definiert Gruppierungen für die Gesamtstatistik-Übersichtskarten
- **Felder**:
  - `name`: Name der Gesamtgruppe
  - `color`: Hex-Farbcode für die Karten-Darstellung
  - `order`: Reihenfolge der Karten in der Gesamtübersicht
  - `status_list`: Welche BirdStatus gehören zu dieser Gesamtgruppe
  - `is_active`: Aktivierung/Deaktivierung

### StatisticConfiguration (Vereinfacht)
- **Zweck**: Globale Konfiguration für die Statistik-Anzeige
- **Felder**:
  - `show_year_total_patients`: Checkbox für Anzeige der Gesamtanzahl aktuelles Jahr
  - `show_total_patients`: Checkbox für Anzeige der Gesamtanzahl aller Jahre
  - `show_percentages`: Prozentangaben in Balkendiagrammen anzeigen
  - `show_absolute_numbers`: Absolute Zahlen in Balkendiagrammen anzeigen
  - `is_active`: Aktive Konfiguration (nur eine möglich)

## Admin-Interface Struktur

### Statistik-Individuen
- **URL**: `/admin/statistic/statisticindividual/`
- **Zweck**: Konfiguration der Vogelarten-Balkendiagramme
- **Features**: Erweiterte Farbauswahl, Status-Zuordnung, Reihenfolge

### Statistik-Jahr  
- **URL**: `/admin/statistic/statisticyeargroup/`
- **Zweck**: Konfiguration der Jahresstatistik-Karten
- **Features**: Separate Gruppen für Jahresübersicht, eigene Farben

### Statistik-Insgesamt
- **URL**: `/admin/statistic/statistictotalgroup/`
- **Zweck**: Konfiguration der Gesamtstatistik-Karten
- **Features**: Separate Gruppen für Gesamtübersicht, eigene Farben

### Statistik-Konfiguration
- **URL**: `/admin/statistic/statisticconfiguration/`
- **Zweck**: Globale Ein-/Ausschaltung von Bereichen
- **Features**: Checkboxen für Sichtbarkeit der Gesamtanzahl-Karten

## Vollständige Konfigurierbarkeit

Die Statistik-Seite (`http://localhost:8000/statistics/`) ist jetzt vollständig über das Admin-Interface konfigurierbar:

### Jahresstatistik-Bereich
- ✅ **Gesamtanzahl Patienten**: Ein-/Ausschaltbar über Konfiguration
- ✅ **Jahresgruppen**: Beliebig viele konfigurierbare Gruppen mit eigenen Farben
- ✅ **Status-Zuordnung**: Flexible Zuordnung von BirdStatus zu Gruppen

### Gesamtstatistik-Bereich  
- ✅ **Gesamtanzahl aller Patienten**: Ein-/Ausschaltbar über Konfiguration
- ✅ **Gesamtgruppen**: Beliebig viele konfigurierbare Gruppen mit eigenen Farben
- ✅ **Prozentanzeige**: Automatische Berechnung und Anzeige

### Vogelarten-Statistik
- ✅ **Balkendiagramme**: Vollständig konfigurierbare Gruppierungen
- ✅ **Farben**: Individuelle Farbzuordnung pro Gruppe
- ✅ **Legende**: Dynamische Generierung basierend auf Konfiguration

## Standard-Konfiguration

### Statistik-Individuen (Balkendiagramme)
1. **Gerettet** (#28a745 - Grün): Ausgewildert, Übermittelt
2. **Verstorben** (#dc3545 - Rot): Verstorben  
3. **In Behandlung/Auswilderung** (#ffc107 - Gelb): In Behandlung, In Auswilderung

### Statistik-Jahr (Jahresstatistik-Karten)
1. **Gerettet** (#28a745 - Grün): Ausgewildert, Übermittelt
2. **Verstorben** (#dc3545 - Rot): Verstorben
3. **In Behandlung** (#ffc107 - Gelb): In Behandlung, In Auswilderung

### Statistik-Insgesamt (Gesamtstatistik-Karten)  
1. **Erfolgreich gerettet** (#28a745 - Grün): Ausgewildert, Übermittelt
2. **Verstorben** (#dc3545 - Rot): Verstorben
3. **Aktuell in Betreuung** (#17a2b8 - Türkis): In Behandlung, In Auswilderung

## Verwendung

### Neue Jahresgruppe erstellen
1. Admin → Statistic → Statistik-Jahr → Hinzufügen
2. Name eingeben (z.B. "Notfälle")
3. Farbe mit Color Picker auswählen
4. Reihenfolge festlegen  
5. BirdStatus zuordnen
6. Aktivieren und speichern

### Gesamtstatistik anpassen
1. Admin → Statistic → Statistik-Insgesamt → Gruppe bearbeiten
2. Namen ändern oder neue Gruppe erstellen
3. Farben nach Bedarf anpassen
4. Status-Zuordnungen aktualisieren

### Sichtbarkeit steuern
1. Admin → Statistic → Statistik-Konfiguration
2. Checkboxen für Gesamtanzahl-Anzeige setzen/entfernen
3. Anzeige-Optionen für Balkendiagramme konfigurieren

## Migration und Kompatibilität

- ✅ **Automatische Migration**: Bestehende Daten wurden automatisch übernommen
- ✅ **Rückwärtskompatibilität**: Alle bisherigen Funktionen bleiben erhalten
- ✅ **Erweiterte Flexibilität**: Drei separate Konfigurationsbereiche
- ✅ **Vereinfachte Verwaltung**: Nur noch eine Statistik-Konfiguration notwendig

## Technische Details

- **Separate Models**: Getrennte Konfiguration für verschiedene Statistik-Bereiche
- **Dynamisches Rendering**: Template passt sich automatisch an Konfiguration an
- **Color-Coded UI**: Jede Gruppe kann individuelle Farben haben
- **Flexible Status-Zuordnung**: BirdStatus können frei zwischen Gruppen zugeordnet werden
