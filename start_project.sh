#!/bin/bash

# Django FBF Projekt Startup Script
# Dieses Skript startet das Projekt und erstellt einen Admin-Benutzer

set -e  # Script bei Fehlern beenden

echo "🚀 Django FBF Projekt wird gestartet..."

# Überprüfen ob Docker läuft
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker ist nicht gestartet. Bitte starten Sie Docker Desktop."
    exit 1
fi

# .env Datei erstellen falls sie nicht existiert
if [ ! -f .env ]; then
    echo "📝 Erstelle .env Datei..."
    cp .env.example .env
    
    # Secret Key generieren
    SECRET_KEY=$(openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)
    
    # .env Datei mit Entwicklungseinstellungen anpassen
    cat > .env << EOF
# APP URL
APP_URL='http://localhost:8008'

# Allowed Hosts (für Traefik Route - nur ein Host)
ALLOWED_HOSTS='localhost'

# Database
DB_HOST='db'
DB_NAME='db_fbf'
DB_PASSWORD='superSecret'
DB_PORT='5432'
DB_USER='fbf'

# Debugging
DEBUG='True'

# Secrets
SECRET_KEY='${SECRET_KEY}'

# CSRF
CSRF_TRUSTED_ORIGINS='http://localhost:8008,http://127.0.0.1:8008'

# Email (Optional - für lokale Entwicklung)
DEFAULT_FROM_EMAIL='admin@localhost'
EMAIL_HOST_PASSWORD=''
EMAIL_HOST_USER=''
EMAIL_HOST=''
EMAIL_PORT=25
EOF
    echo "✅ .env Datei erstellt"
else
    echo "📄 .env Datei bereits vorhanden"
fi

# Docker Container stoppen falls sie laufen
echo "🛑 Stoppe eventuell laufende Container..."
docker compose down --remove-orphans > /dev/null 2>&1 || true

# Docker Images bauen und Container starten
echo "🔨 Baue Docker Images..."
docker compose build --no-cache

echo "🐳 Starte Docker Container..."
docker compose up -d

# Warten bis die Datenbank bereit ist
echo "⏳ Warte auf Datenbankverbindung..."
until docker compose exec db pg_isready -U fbf -d db_fbf > /dev/null 2>&1; do
    echo "   ... Datenbank startet noch..."
    sleep 2
done

echo "✅ Datenbank ist bereit"

# Warten bis der Web-Container läuft
echo "⏳ Warte auf Web-Container..."
sleep 10

# Django Migrations ausführen
echo "🔄 Führe Django Migrations aus..."
docker compose exec -T web python manage.py makemigrations
docker compose exec -T web python manage.py migrate

# Fixtures laden (falls vorhanden)
if [ -d "app/fixtures" ] && [ "$(ls -A app/fixtures)" ]; then
    echo "📦 Lade Fixtures..."
    for fixture in app/fixtures/*.json; do
        if [ -f "$fixture" ]; then
            echo "   Lade $(basename "$fixture")..."
            docker compose exec -T web python manage.py loaddata "fixtures/$(basename "$fixture")" || true
        fi
    done
fi

# Admin-Benutzer erstellen
echo "👤 Erstelle Admin-Benutzer..."
cat << 'EOF' | docker compose exec -T web python manage.py shell
from django.contrib.auth.models import User

# Überprüfen ob Admin-User bereits existiert
if User.objects.filter(username='admin').exists():
    print("Admin-Benutzer existiert bereits")
    user = User.objects.get(username='admin')
    user.set_password('admin')
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print("Admin-Passwort wurde auf 'admin' zurückgesetzt")
else:
    # Neuen Admin-User erstellen
    User.objects.create_superuser('admin', 'admin@localhost', 'admin')
    print("Admin-Benutzer erstellt")
    print("Benutzername: admin")
    print("Passwort: admin")
EOF

# Static Files sammeln
echo "📁 Sammle Static Files..."
docker compose exec -T web python manage.py collectstatic --noinput --clear

echo ""
echo "🎉 Projekt erfolgreich gestartet!"
echo ""
echo "📋 Informationen:"
echo "   🌐 Anwendung: http://localhost:8008"
echo "   🔧 Admin-Panel: http://localhost:8008/admin"
echo "   👤 Admin-Login:"
echo "      Benutzername: admin"
echo "      Passwort: admin"
echo ""
echo "📝 Nützliche Befehle:"
echo "   docker compose logs -f web    # Logs anzeigen"
echo "   docker compose down           # Projekt stoppen"
echo "   docker compose up -d          # Projekt starten"
echo ""
echo "🔍 Container Status:"
docker compose ps
