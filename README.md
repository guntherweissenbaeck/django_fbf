# The Fallen Birdy Form

## 🚀 Schneller Einstieg

Für einen schnellen Start des Projekts verwenden Sie die bereitgestellten Skripte:

### Start des Projekts
```bash
./start_project.sh
```

Das Start-Skript führt automatisch folgende Schritte aus:
- Erstellt eine `.env` Datei mit Entwicklungseinstellungen
- Baut und startet alle Docker Container (Web, Datenbank, Traefik)
- Führt Django Migrations aus
- Lädt Testdaten (Fixtures)
- Erstellt einen Admin-Benutzer
- Sammelt statische Dateien

**Nach dem Start ist die Anwendung verfügbar unter:**
- **Hauptanwendung**: [http://localhost:8008](http://localhost:8008)
- **Admin-Panel**: [http://localhost:8008/admin](http://localhost:8008/admin)

**Standard Admin-Zugang:**
- Benutzername: `admin`
- Passwort: `admin`

### Stop des Projekts
```bash
./stop_project.sh
```

Das Stop-Skript stoppt alle Container und räumt auf.

---

## 🧪 Tests ausführen

Das Projekt verfügt über eine umfassende Test-Suite mit verschiedenen Test-Arten:

### Einfachster Weg (Empfohlen)
Verwenden Sie das bereitgestellte Test-Skript für einen vollständigen Test-Durchlauf:
```bash
./start_test.sh
```

Das Test-Skript führt automatisch folgende Tests aus:
- Django Tests (13 Tests im Docker Container)
- Pytest Unit Tests (77 Tests)
- Pytest Integration Tests (11 Tests) 
- Pytest Functional Tests (6 Tests)
- Generiert einen HTML Coverage Report

### Django Tests (im Docker Container)
Führen Sie die Standard Django Tests aus:
```bash
docker exec django_fbf_web_1 python manage.py test
```

### Komplette Test-Suite (Unit, Integration, Functional)
Für die vollständige Test-Suite (94 Tests):
```bash
python3 -m pytest test/ -v
```

### Nur Unit Tests
```bash
python3 -m pytest test/unit/ -v
```

### Nur Integration Tests
```bash
python3 -m pytest test/integration/ -v
```

### Nur Functional Tests
```bash
python3 -m pytest test/functional/ -v
```

### Test-Coverage Report
Um einen Bericht über die Test-Abdeckung zu erhalten:
```bash
python3 -m pytest test/ --cov=app --cov-report=html
```

**Hinweis:** Stellen Sie sicher, dass das Projekt läuft (`./start_project.sh`) bevor Sie die Tests ausführen.

---

## 📊 Reports System

Das Django FBF verfügt über ein vollständiges Reports-System für die Wildvogelhilfe Jena:

### Features
- **Manuelle Reports**: Interaktive Erstellung mit Datumsbereich und Filteroptionen
- **Automatische Reports**: Wiederkehrende Reports (wöchentlich/monatlich/quartalsweise)
- **E-Mail-Versand**: Professional formatierte E-Mails mit CSV-Anhang
- **Report-Protokoll**: Vollständige Audit-Spur aller generierten Reports
- **Admin-Integration**: Nahtlose Integration in Django Admin

### Verwendung
1. **Admin-Panel öffnen**: [http://localhost:8008/admin/reports/](http://localhost:8008/admin/reports/)
2. **Manuelle Reports**: "Report erstellen" → Datum wählen → Filter setzen → Herunterladen/E-Mail
3. **Automatische Reports**: Wiederkehrende Reports konfigurieren mit E-Mail-Verteilern
4. **Report-Logs**: Verlauf aller Reports mit Download-Möglichkeit

### CSV-Export
Reports enthalten folgende Felder: Vogel, Alter, Geschlecht, Gefunden am, Fundort, Fundumstände, Diagnose bei Fund, Status

---

## Throw old database
In case you've got an preexisting database, delete it and do the following:

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

## Add Test Data
To add testdata, use the loaddata functionality of django:

```bash
python3 manage.py loaddata fixtures/data.json
```

## Test Account
The test account you can use:

- user: admin
- password: abcdef

## Deployment
This is a little reminder what you will need to deploy the app.

### Secret Key
Generate Secret Key:
```bash
openssl rand -base64 36
```

### Environment
```
# .env
# URL
APP_URL='fbf.nabu-jena.de'

# Switch off debugging in production
DEBUG=False

# Security from checks
SECRET_KEY='LaLaLa'
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS='https://fbf.nabu-jena.de'

# Email
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='smtp.strato.de'
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER='postmaster@nabu-jena.de'
EMAIL_HOST_PASSWORD='LaLaLa'
DEFAULT_FROM_EMAIL="fbf-admin@nabu-jena.de"% 
```

### Settings in Django Core
```
import os
...
DEBUG = False
ALLOWED_HOSTS = ['*']
...
STATICFILES_DIRS = [BASE_DIR / "static", ]
STATIC_ROOT = '/static/'
STATIC_URL = '/static/'
...
# Email backend
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_HOST=os.getenv('EMAIL_HOST')
EMAIL_PORT=os.getenv('EMAIL_PORT')
EMAIL_USE_TLS=os.getenv('EMAIL_USE_TLS')
EMAIL_HOST_USER=os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD=os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL=os.getenv('DEFAULT_FROM_EMAIL')

# CSRF
CSRF_TRUSTED_ORIGINS=[os.getenv('CSRF_TRUSTED_ORIGINS')]
```

## How to use this project?

### Einfachster Weg (Empfohlen)
Verwenden Sie die bereitgestellten Skripte für einen schnellen Start:
```bash
./start_project.sh  # Projekt starten
./stop_project.sh   # Projekt stoppen
```

### Manueller Weg

#### Development

Build the images and spin up the containers:

```sh
$ docker-compose up -d --build
```

Test it out:

1. [http://localhost:8008/](http://localhost:8008/) - Hauptanwendung
1. [http://localhost:8081/](http://localhost:8081/) - Traefik Dashboard

### Production

Update the domain in *docker-compose.prod.yml*, and add your email to *traefik.prod.toml*.

Build the images and run the containers:

```sh
$ docker-compose -f docker-compose.prod.yml up -d --build
```

https://testdriven.io/blog/django-docker-traefik/

