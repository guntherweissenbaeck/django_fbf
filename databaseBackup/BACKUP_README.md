# Database Backup Script

Das `create_backup.sh` Script erstellt automatisierte Backups der aktuellen Django-Datenbank mit organisierter Archivierung.

## 📋 Übersicht

Das Script erstellt:
1. **Archiviertes Backup**: `JAHR/MONAT/NAME_TIMESTAMP.sql` (permanent)
2. **Standard-Backup**: `NAME.sql` (überschreibbar für Migration)

## 🚀 Verwendung

### Standard-Backup erstellen
```bash
cd databaseBackup
./create_backup.sh
```
Erstellt: `fbf-backup.sql` und `2025/07/fbf-backup_TIMESTAMP.sql`

### Backup mit eigenem Namen
```bash
./create_backup.sh production-backup
```
Erstellt: `production-backup.sql` und `2025/07/production-backup_TIMESTAMP.sql`

### Hilfe anzeigen
```bash
./create_backup.sh --help
```

## 📁 Verzeichnisstruktur

```
databaseBackup/
├── create_backup.sh           # Backup-Script
├── migrate_live_data.sh       # Migration-Script
├── fbf-backup.sql            # Standard-Backup (überschreibbar)
├── test-backup.sql           # Weiteres Standard-Backup
└── 2025/                     # Archiv-Verzeichnis
    └── 07/                   # Monat
        ├── fbf-backup_20250707_231754.sql
        └── test-backup_20250707_231826.sql
```

## ✅ Features

- **🔧 Automatische Konfiguration**: Liest .env Datei oder verwendet Standard-Werte
- **📊 Datenbank-Statistiken**: Zeigt Datensatz-Anzahl pro Tabelle
- **📦 Organisierte Archivierung**: Jahr/Monat-Struktur
- **🔄 Kompatibilität**: Funktioniert mit migrate_live_data.sh
- **⚡ Docker-Integration**: Nahtlose Container-Verwaltung
- **📝 Ausführliche Logs**: Farb-kodierte Fortschrittsanzeige

## 📊 Backup-Informationen

Das Script zeigt automatisch:
- Dateigröße des Backups
- Anzahl der Zeilen
- Datensatz-Statistiken pro Tabelle
- Erstellungszeit

## 🔧 Konfiguration

### Automatische .env Erkennung
Das Script liest automatisch die `.env` Datei aus dem übergeordneten Verzeichnis:
```bash
DB_HOST='db'
DB_NAME='db_fbf'
DB_USER='fbf'
DB_PASSWORD='superSecret'
```

### Standard-Werte (wenn .env nicht vorhanden)
```bash
DB_HOST=localhost
DB_NAME=fbf
DB_USER=fbf
DB_PASSWORD=fbfpassword
DB_PORT=5432
```

## 🔄 Integration mit Migration

Die erstellten Backups sind vollständig kompatibel mit dem Migration-Script:

```bash
# Backup erstellen
./create_backup.sh

# Backup wiederherstellen
./migrate_live_data.sh fbf-backup.sql
```

## 📋 Voraussetzungen

- Docker und Docker Compose installiert
- Laufende Container (wird automatisch geprüft)
- Schreibberechtigung im databaseBackup Verzeichnis

## 🛠️ Problembehandlung

### Container nicht bereit
```bash
cd ..
docker-compose up -d
cd databaseBackup
./create_backup.sh
```

### Backup-Verzeichnis anzeigen
```bash
ls -la 2025/07/
```

### Backup-Inhalt prüfen
```bash
head -20 fbf-backup.sql
```

### Manual Database Access
```bash
cd ..
docker-compose exec db psql -U fbf -d db_fbf
```

## 📈 Backup-Workflow

1. **Script starten** → Automatische Konfiguration
2. **Container prüfen** → Status-Validierung  
3. **Verzeichnis erstellen** → Jahr/Monat-Struktur
4. **Datenbank exportieren** → pg_dump via Docker
5. **Dateien erstellen** → Archiv + Standard-Kopie
6. **Statistiken anzeigen** → Daten-Übersicht
7. **Zusammenfassung** → Erfolgs-Bestätigung

## 💡 Tipps

- **Regelmäßige Backups**: Fügen Sie das Script zu Cron-Jobs hinzu
- **Archiv-Management**: Alte Backups regelmäßig bereinigen
- **Standard-Backups**: Ideal für schnelle Migrations-Tests
- **Archiv-Backups**: Permanente Sicherung mit Zeitstempel

## 🎯 Nächste Schritte

Nach dem Backup können Sie:
- Das Backup mit `migrate_live_data.sh` testen
- Die Datenbank mit anderen Daten füllen
- Bei Problemen schnell zum Backup zurückkehren
