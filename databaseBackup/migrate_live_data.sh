#!/bin/bash

# Django FBF Live Data Migration Script
# Migriert fbf-backup.sql vom Live-Server in den aktuellen Entwicklungsstand
# 
# Verwendung: ./migrate_live_data.sh [backup-file]
# Standard: ./migrate_live_data.sh fbf-backup.sql

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
    echo "║               Django FBF Live Data Migration                ║"
    echo "║                     Version 1.0                             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
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
    if [ ! -f "docker-compose.yaml" ]; then
        log_error "docker-compose.yaml nicht gefunden. Stelle sicher, dass du im Projektverzeichnis bist."
        exit 1
    fi
    
    log_success "Alle Voraussetzungen erfüllt"
}

# Backup-Datei validieren
validate_backup_file() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup-Datei '$backup_file' nicht gefunden"
        exit 1
    fi
    
    # Überprüfe ob es sich um ein PostgreSQL Dump handelt
    if ! head -20 "$backup_file" | grep -q "PostgreSQL database dump"; then
        log_error "Die Datei '$backup_file' scheint kein gültiges PostgreSQL Dump zu sein"
        exit 1
    fi
    
    local file_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null || echo "0")
    local size_display=""
    if command -v numfmt >/dev/null 2>&1; then
        size_display=" ($(numfmt --to=iec $file_size))"
    elif [ "$file_size" -gt 0 ]; then
        size_display=" (${file_size} bytes)"
    fi
    log_info "Backup-Datei: $backup_file$size_display"
    log_success "Backup-Datei validiert"
}

# Container Status prüfen
check_containers() {
    log_info "Überprüfe Container Status..."
    
    if ! docker-compose ps | grep -q "django_fbf_db_1.*Up"; then
        log_warning "Datenbank-Container läuft nicht. Starte Services..."
        docker-compose up -d db
        
        # Warte auf Datenbank
        local timeout=60
        local count=0
        while [ $count -lt $timeout ]; do
            if docker-compose exec -T db pg_isready -U fbf -d postgres &>/dev/null; then
                break
            fi
            echo -n "."
            sleep 1
            ((count++))
        done
        
        if [ $count -ge $timeout ]; then
            log_error "Datenbank-Container konnte nicht gestartet werden"
            exit 1
        fi
    fi
    
    log_success "Container sind bereit"
}

# Backup der aktuellen Datenbank erstellen
backup_current_db() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_name="pre_migration_backup_${timestamp}.sql"
    
    log_info "Erstelle Backup der aktuellen Datenbank..."
    
    if docker-compose exec -T db pg_dump -U fbf -d db_fbf > "$backup_name" 2>/dev/null; then
        log_success "Backup erstellt: $backup_name"
        echo "$backup_name" > .last_backup_file
    else
        log_warning "Konnte kein Backup erstellen (vermutlich keine existierende Datenbank)"
    fi
}

# Datenbank zurücksetzen
reset_database() {
    log_info "Setze Datenbank zurück..."
    
    # Stoppe Web-Container um Verbindungen zu vermeiden
    show_progress "Stoppe Web-Container..."
    docker-compose stop web 2>/dev/null || true
    
    # Lösche und erstelle Datenbank neu
    show_progress "Lösche bestehende Datenbank..."
    docker-compose exec -T db psql -U fbf -d postgres -c "DROP DATABASE IF EXISTS db_fbf;" 2>/dev/null || true
    
    show_progress "Erstelle neue Datenbank..."
    docker-compose exec -T db psql -U fbf -d postgres -c "CREATE DATABASE db_fbf;" 2>/dev/null
    
    log_success "Datenbank zurückgesetzt"
}

# Live-Daten importieren
import_live_data() {
    local backup_file="$1"
    
    log_info "Importiere Live-Daten..."
    
    # Kopiere Backup in Container
    show_progress "Kopiere Backup-Datei in Container..."
    docker cp "$backup_file" django_fbf_db_1:/tmp/backup.sql
    
    # Importiere SQL Backup
    show_progress "Importiere SQL-Daten..."
    if docker-compose exec -T db psql -U fbf -d db_fbf -f /tmp/backup.sql >/dev/null 2>&1; then
        log_success "Live-Daten erfolgreich importiert"
    else
        log_error "Fehler beim Importieren der Live-Daten"
        exit 1
    fi
    
    # Bereinige temporäre Datei
    docker-compose exec -T db rm /tmp/backup.sql 2>/dev/null || true
}

# Django Migrationen anwenden
apply_django_migrations() {
    log_info "Starte Web-Container und wende Django-Migrationen an..."
    
    # Starte Web-Container
    show_progress "Starte Web-Container..."
    docker-compose up -d web
    
    # Warte auf Web-Container
    local timeout=120
    local count=0
    while [ $count -lt $timeout ]; do
        if docker-compose exec -T web python manage.py check --database default &>/dev/null; then
            break
        fi
        echo -n "."
        sleep 1
        ((count++))
    done
    
    if [ $count -ge $timeout ]; then
        log_error "Web-Container konnte nicht gestartet werden"
        exit 1
    fi
    
    # Prüfe und wende Migrationen an
    show_progress "Prüfe Migration Status..."
    docker-compose exec -T web python manage.py showmigrations --plan > /tmp/migration_status.txt 2>/dev/null || true
    
    show_progress "Wende fehlende Migrationen an..."
    if docker-compose exec -T web python manage.py migrate >/dev/null 2>&1; then
        log_success "Django-Migrationen erfolgreich angewendet"
    else
        log_warning "Einige Migrationen konnten nicht angewendet werden (möglicherweise bereits vorhanden)"
    fi
}

# Datenintegrität prüfen
verify_data_integrity() {
    log_info "Überprüfe Datenintegrität..."
    
    # Zähle Datensätze in wichtigen Tabellen
    local bird_count=$(docker-compose exec -T web python manage.py shell -c "
from bird.models import Bird
print(Bird.objects.count())
" 2>/dev/null | tail -1 | tr -d '\r')
    
    local fallen_bird_count=$(docker-compose exec -T web python manage.py shell -c "
from bird.models import FallenBird
print(FallenBird.objects.count())
" 2>/dev/null | tail -1 | tr -d '\r')
    
    local user_count=$(docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth.models import User
print(User.objects.count())
" 2>/dev/null | tail -1 | tr -d '\r')
    
    local contact_count=$(docker-compose exec -T web python manage.py shell -c "
from contact.models import Contact
print(Contact.objects.count())
" 2>/dev/null | tail -1 | tr -d '\r')
    
    echo ""
    log_success "Datenintegrität überprüft:"
    echo "  📦 Vögel: $bird_count"
    echo "  🐦 Fundvögel: $fallen_bird_count"
    echo "  👤 Benutzer: $user_count"
    echo "  📞 Kontakte: $contact_count"
}

# Admin-Benutzer konfigurieren
setup_admin_user() {
    log_info "Konfiguriere Admin-Benutzer..."
    
    docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth.models import User
admin_user = User.objects.filter(is_superuser=True).first()
if admin_user:
    admin_user.set_password('admin')
    admin_user.save()
    print(f'Admin-Passwort für \"{admin_user.username}\" wurde auf \"admin\" gesetzt')
else:
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Neuer Admin-Benutzer \"admin\" wurde erstellt')
" 2>/dev/null
    
    log_success "Admin-Benutzer konfiguriert"
}

# Sammle Static Files
collect_static_files() {
    log_info "Sammle Static Files..."
    
    if docker-compose exec -T web python manage.py collectstatic --noinput >/dev/null 2>&1; then
        log_success "Static Files gesammelt"
    else
        log_warning "Fehler beim Sammeln der Static Files"
    fi
}

# Migration Zusammenfassung
show_migration_summary() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗"
    echo -e "║                   Migration erfolgreich!                    ║"
    echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    log_success "Die Live-Daten wurden erfolgreich in den aktuellen Entwicklungsstand migriert"
    echo ""
    echo -e "${BLUE}📋 Systemzugriff:${NC}"
    echo "  🌐 Anwendung:    http://localhost:8008"
    echo "  🔧 Admin-Panel:  http://localhost:8008/admin"
    echo ""
    echo -e "${BLUE}👤 Admin-Login:${NC}"
    echo "  Benutzername: admin"
    echo "  Passwort:     admin"
    echo ""
    echo -e "${BLUE}📝 Nützliche Befehle:${NC}"
    echo "  docker-compose logs -f web    # Logs anzeigen"
    echo "  docker-compose down           # Projekt stoppen"
    echo "  docker-compose up -d          # Projekt starten"
    echo ""
    
    if [ -f ".last_backup_file" ]; then
        local backup_file=$(cat .last_backup_file)
        echo -e "${YELLOW}💾 Backup der vorherigen Datenbank: $backup_file${NC}"
        echo ""
    fi
}

# Fehlerbehandlung für Rollback
rollback_migration() {
    local backup_file="$1"
    
    if [ -f ".last_backup_file" ]; then
        local last_backup=$(cat .last_backup_file)
        log_warning "Stelle vorherige Datenbank wieder her..."
        
        docker-compose stop web 2>/dev/null || true
        docker-compose exec -T db psql -U fbf -d postgres -c "DROP DATABASE IF EXISTS db_fbf;" 2>/dev/null || true
        docker-compose exec -T db psql -U fbf -d postgres -c "CREATE DATABASE db_fbf;" 2>/dev/null
        
        if [ -f "$last_backup" ]; then
            docker cp "$last_backup" django_fbf_db_1:/tmp/restore.sql
            docker-compose exec -T db psql -U fbf -d db_fbf -f /tmp/restore.sql >/dev/null 2>&1
            docker-compose exec -T db rm /tmp/restore.sql 2>/dev/null || true
            log_success "Vorherige Datenbank wiederhergestellt"
        fi
        
        rm .last_backup_file
    fi
}

# Trap für Fehlerbehandlung
trap 'log_error "Migration fehlgeschlagen. Führe Rollback durch..."; rollback_migration' ERR

# Hauptfunktion
main() {
    local backup_file="${1:-fbf-backup.sql}"
    
    print_banner
    
    check_prerequisites
    validate_backup_file "$backup_file"
    check_containers
    backup_current_db
    reset_database
    import_live_data "$backup_file"
    apply_django_migrations
    verify_data_integrity
    setup_admin_user
    collect_static_files
    show_migration_summary
    
    # Bereinige temporäre Dateien
    rm -f .last_backup_file /tmp/migration_status.txt
}

# Hilfe anzeigen
show_help() {
    echo "Django FBF Live Data Migration Script"
    echo ""
    echo "Verwendung: $0 [OPTIONEN] [BACKUP-DATEI]"
    echo ""
    echo "OPTIONEN:"
    echo "  -h, --help    Zeige diese Hilfe an"
    echo ""
    echo "BACKUP-DATEI:"
    echo "  Pfad zur fbf-backup.sql Datei (Standard: fbf-backup.sql)"
    echo ""
    echo "Beispiele:"
    echo "  $0                           # Verwendet fbf-backup.sql"
    echo "  $0 /path/to/backup.sql       # Verwendet spezifische Backup-Datei"
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
