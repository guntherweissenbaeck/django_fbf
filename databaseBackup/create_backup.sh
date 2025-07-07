#!/bin/bash

# Django FBF Database Backup Script
# Erstellt ein Backup der aktuellen Django-Datenbank
# 
# Verwendung: ./create_backup.sh [output-name]
# Standard: ./create_backup.sh (erstellt fbf-backup.sql)

set -e  # Stoppe bei Fehlern

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging Funktionen
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Fortschrittsanzeige
show_progress() {
    echo -e "${BLUE}🔄 $1${NC}"
}

# Banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║               Django FBF Database Backup                    ║"
    echo "║                     Version 1.0                             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Datenbank-Konfiguration (aus .env oder Standard-Werte)
get_db_config() {
    # Versuche .env Datei zu laden (sicher)
    if [ -f "../.env" ]; then
        while IFS='=' read -r key value; do
            # Überspringe Kommentare und leere Zeilen
            if [[ ! "$key" =~ ^#.* ]] && [[ -n "$key" ]]; then
                # Entferne Anführungszeichen von value
                value="${value%\'}"
                value="${value#\'}"
                value="${value%\"}"
                value="${value#\"}"
                export "$key=$value"
            fi
        done < <(grep -v '^#' ../.env | grep -v '^$' | grep '=')
    fi
    
    # Standard-Werte setzen falls nicht definiert
    DB_NAME="${DB_NAME:-fbf}"
    DB_USER="${DB_USER:-fbf}"
    DB_PASSWORD="${DB_PASSWORD:-fbfpassword}"
    DB_HOST="${DB_HOST:-localhost}"
    DB_PORT="${DB_PORT:-5432}"
    
    log_info "Datenbank-Konfiguration:"
    echo "  Host: $DB_HOST:$DB_PORT"
    echo "  Datenbank: $DB_NAME"
    echo "  Benutzer: $DB_USER"
}

# Überprüfe Voraussetzungen
check_prerequisites() {
    log_info "Überprüfe Voraussetzungen..."
    
    # Docker und Docker Compose prüfen
    if ! command -v docker &> /dev/null; then
        log_error "Docker ist nicht installiert oder nicht im PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose ist nicht installiert oder nicht im PATH"
        exit 1
    fi
    
    # docker-compose.yaml prüfen
    if [ ! -f "../docker-compose.yaml" ]; then
        log_error "docker-compose.yaml nicht im übergeordneten Verzeichnis gefunden"
        exit 1
    fi
    
    log_success "Alle Voraussetzungen erfüllt"
}

# Container Status prüfen
check_containers() {
    log_info "Überprüfe Container Status..."
    
    cd ..
    
    if ! docker-compose ps | grep -q "django_fbf_db_1.*Up"; then
        log_error "Datenbank-Container läuft nicht. Bitte starte zuerst die Container:"
        echo "  cd .."
        echo "  docker-compose up -d"
        exit 1
    fi
    
    # Teste Datenbankverbindung
    if ! docker-compose exec -T db pg_isready -U "$DB_USER" -d "$DB_NAME" &>/dev/null; then
        log_error "Datenbank ist nicht bereit oder erreichbar"
        exit 1
    fi
    
    cd databaseBackup
    log_success "Container sind bereit und Datenbank ist erreichbar"
}

# Erstelle Backup-Verzeichnisstruktur
create_backup_structure() {
    local current_year=$(date +"%Y")
    local current_month=$(date +"%m")
    local backup_dir="${current_year}/${current_month}"
    
    mkdir -p "$backup_dir"
    
    echo "$backup_dir"
}

# Datenbank-Backup erstellen
create_database_backup() {
    local output_name="${1:-fbf-backup.sql}"
    local backup_dir="$2"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    
    # Entferne .sql Endung falls vorhanden und füge Timestamp hinzu
    local base_name="${output_name%.sql}"
    local timestamped_name="${base_name}_${timestamp}.sql"
    local backup_path="${backup_dir}/${timestamped_name}"
    local full_backup_path="$(pwd)/${backup_path}"
    
    # Erstelle Backup mit pg_dump
    cd ..
    if docker-compose exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" --verbose > "$full_backup_path" 2>/dev/null; then
        cd databaseBackup
    else
        cd databaseBackup
        log_error "Fehler beim Erstellen des Backups"
        exit 1
    fi
    
    # Erstelle zusätzlich eine Kopie mit Standard-Namen
    local standard_path="${base_name}.sql"
    cp "$backup_path" "$standard_path" 2>/dev/null || true
    
    echo "$backup_path"
}

# Backup-Informationen anzeigen
show_backup_info() {
    local backup_path="$1"
    local standard_path="$2"
    
    # Datei-Größe ermitteln
    local file_size=$(stat -f%z "$backup_path" 2>/dev/null || stat -c%s "$backup_path" 2>/dev/null || echo "0")
    local size_display=""
    if command -v numfmt >/dev/null 2>&1; then
        size_display=" ($(numfmt --to=iec $file_size))"
    elif [ "$file_size" -gt 0 ]; then
        size_display=" (${file_size} bytes)"
    fi
    
    # Anzahl Zeilen zählen
    local line_count=$(wc -l < "$backup_path" | tr -d ' ')
    
    echo ""
    log_success "Backup-Informationen:"
    echo "  📁 Archiviert: $backup_path$size_display"
    echo "  📄 Standard: $standard_path"
    echo "  📊 Zeilen: $line_count"
    echo "  🕒 Erstellt: $(date)"
}

# Datenbank-Statistiken anzeigen
show_database_stats() {
    log_info "Datenbank-Statistiken:"
    
    cd ..
    
    # Zähle Datensätze in wichtigen Tabellen (ohne spezifische Zahlen zu zeigen)
    local tables=("auth_user" "bird_bird" "bird_fallenbird" "contact_contact")
    local total_records=0
    
    for table in "${tables[@]}"; do
        local count=$(docker-compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null | tr -d ' \n\r' || echo "0")
        echo "  📦 $table: $count Datensätze"
        if [[ "$count" =~ ^[0-9]+$ ]]; then
            total_records=$((total_records + count))
        fi
    done
    
    echo "  📊 Gesamt (Haupttabellen): $total_records Datensätze"
    
    cd databaseBackup
}

# Backup Zusammenfassung
show_backup_summary() {
    local backup_path="$1"
    local standard_path="$2"
    
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗"
    echo -e "║                  Backup erfolgreich erstellt!               ║"
    echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${BLUE}📋 Backup-Dateien:${NC}"
    echo "  🗄️  Archiv: $backup_path"
    echo "  📄 Standard: $standard_path"
    echo ""
    
    echo -e "${BLUE}📝 Nützliche Befehle:${NC}"
    echo "  ls -la $(dirname "$backup_path")    # Backup-Verzeichnis anzeigen"
    echo "  ./migrate_live_data.sh $standard_path    # Backup wiederherstellen"
    echo "  head -20 $standard_path    # Backup-Inhalt prüfen"
    echo ""
    
    echo -e "${YELLOW}💡 Hinweis: Die Standard-Datei '$standard_path' wird bei jedem Backup überschrieben.${NC}"
    echo -e "${YELLOW}   Das archivierte Backup '$backup_path' bleibt bestehen.${NC}"
}

# Hauptfunktion
main() {
    local output_name="${1:-fbf-backup}"
    
    print_banner
    
    get_db_config
    check_prerequisites
    check_containers
    
    log_info "Erstelle Backup-Verzeichnisstruktur..."
    local backup_dir=$(create_backup_structure)
    log_success "Verzeichnisstruktur erstellt: $backup_dir"
    
    log_info "Erstelle Datenbank-Backup..."
    show_progress "Exportiere Datenbank $DB_NAME..."
    local backup_path=$(create_database_backup "$output_name" "$backup_dir")
    local standard_path="${output_name%.sql}.sql"
    log_success "Backup erfolgreich erstellt: $backup_path"
    log_info "Standard-Kopie erstellt: $standard_path"
    
    show_database_stats
    show_backup_info "$backup_path" "$standard_path"
    show_backup_summary "$backup_path" "$standard_path"
}

# Hilfe anzeigen
show_help() {
    echo "Django FBF Database Backup Script"
    echo ""
    echo "Verwendung: $0 [OPTIONEN] [BACKUP-NAME]"
    echo ""
    echo "OPTIONEN:"
    echo "  -h, --help    Zeige diese Hilfe an"
    echo ""
    echo "BACKUP-NAME:"
    echo "  Name der Backup-Datei (Standard: fbf-backup)"
    echo "  Die .sql Endung wird automatisch hinzugefügt"
    echo ""
    echo "AUSGABE:"
    echo "  Erstellt zwei Dateien:"
    echo "  1. JAHR/MONAT/NAME_TIMESTAMP.sql (archiviert)"
    echo "  2. NAME.sql (überschreibbar für Migration)"
    echo ""
    echo "Beispiele:"
    echo "  $0                           # Erstellt fbf-backup.sql"
    echo "  $0 production-backup         # Erstellt production-backup.sql"
    echo "  $0 test-data                 # Erstellt test-data.sql"
    echo ""
}

# Kommandozeilen-Parameter verarbeiten
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
