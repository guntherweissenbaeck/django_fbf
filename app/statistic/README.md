# Statistik App

Die Statistik-App bietet umfassende Übersichten über die Patientendaten in der FBF (Fallen Birdy) Anwendung.

## 📊 Funktionen

### 1. Übersicht aktuelles Jahr
- **Aufgenommene Patienten**: Anzahl der neu aufgenommenen Patienten im aktuellen Jahr
- **In Behandlung/Auswilderung**: Aktuell aktive Fälle (Status: "In Behandlung" oder "In Auswilderung")
- **Gerettete Tiere**: Erfolgreich behandelte Patienten (Status: "Ausgewildert" oder "Übermittelt")

### 2. Gesamtübersicht (alle Jahre)
- **Patienten insgesamt**: Gesamtanzahl aller jemals erfassten Patienten
- **Erfolgreiche Rettungen**: Gesamtanzahl geretteter Tiere mit Erfolgsquote in Prozent

### 3. Statistik pro Vogelart (aufklappbar)
- **Interaktives Balkendiagramm** mit zweifarbigen Balken:
  - 🟢 **Grün**: Gerettete Vögel (ausgewildert + übermittelt)
  - 🔴 **Rot**: Verstorbene Vögel
- **Detaillierte Zahlen** an jedem Balken
- **Sortierung** nach Gesamtanzahl der Patienten (absteigend)
- **Zusatzinformationen**: Lateinischer Artname (falls verfügbar)

## 🎨 Design-Features

- **Responsive Design**: Optimiert für Desktop, Tablet und Mobile
- **Animierte Karten**: Hover-Effekte und sanfte Übergänge
- **Farbkodierung**: Intuitive Farben für verschiedene Statuskategorien
- **Aufklappbare Bereiche**: Übersichtliche Darstellung großer Datenmengen
- **Bootstrap 5**: Moderne, konsistente Benutzeroberfläche

## 🔧 Technische Details

### Datenmodell
Die Statistiken basieren auf folgenden Modellen:
- `FallenBird`: Patientendaten mit Status und Funddatum
- `Bird`: Vogelarten/Bezeichnungen
- `BirdStatus`: Status-Definitionen (In Behandlung, Ausgewildert, etc.)

### Status-Kategorien
1. **In Behandlung** (ID: 1) - Aktive Patienten
2. **In Auswilderung** (ID: 2) - Vorbereitung zur Entlassung
3. **Ausgewildert** (ID: 3) - Erfolgreich freigelassen
4. **Übermittelt** (ID: 4) - An andere Einrichtungen weitergegeben
5. **Verstorben** (ID: 5) - Nicht gerettete Patienten

### View-Logik
```python
# Beispiel für Jahresstatistik
patients_this_year = FallenBird.objects.filter(
    date_found__year=current_year
).count()

# Beispiel für Erfolgsrate
rescued_count = FallenBird.objects.filter(
    status__id__in=[3, 4]  # Ausgewildert, Übermittelt
).count()
```

## 📍 Navigation

Die Statistik-App ist in der Hauptnavigation zwischen **"Volieren"** und **"Kosten"** positioniert.

**URL**: `/statistik/`

## 🔍 Datenanalyse

### Aktueller Datenstand (Beispiel)
- **Gesamte Patienten**: 1.267
- **Vogelarten**: 112 verschiedene Arten
- **Dieses Jahr (2025)**: 393 neue Patienten
- **Erfolgsquote**: ~62% (780 von 1.267 gerettet)

### Status-Verteilung
- In Behandlung: 143 Patienten
- Ausgewildert: 683 Patienten
- Übermittelt: 97 Patienten  
- Verstorben: 344 Patienten

## 🎯 Zukünftige Erweiterungen

Mögliche weitere Features:
- **Zeitreihen-Diagramme**: Entwicklung über mehrere Jahre
- **Monatsstatistiken**: Saisonale Verteilungen
- **Fundort-Analyse**: Geografische Statistiken
- **Kosten-Integration**: Behandlungskosten pro Art
- **Export-Funktionen**: PDF/Excel-Reports
- **Interaktive Charts**: D3.js oder Chart.js Integration

## 📱 Responsive Verhalten

- **Desktop**: Drei-spaltige Kartenlayouts
- **Tablet**: Zwei-spaltige Anordnung
- **Mobile**: Ein-spaltige Darstellung
- **Balkendiagramm**: Automatische Anpassung der Beschriftungen

Die Statistik-App bietet eine umfassende, benutzerfreundliche Übersicht über alle wichtigen Kennzahlen der Wildvogel-Rettungsstation.
