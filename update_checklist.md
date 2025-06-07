# Update Checklist - Django FBF Projekt

**Erstellt am:** 7. Juni 2025  
**Letzter Check:** 7. Juni 2025

## 🔍 Übersicht

Dieses Dokument listet alle Abhängigkeiten auf, die Updates benötigen, sowie Sicherheitshinweise und Empfehlungen für das Django FBF (Fallen Birdy Form) Projekt.

---

## 🚨 Kritische Sicherheitsupdates

### 1. CKEditor (HOCH PRIORITÄT) ✅ ABGESCHLOSSEN
- **Früher:** django-ckeditor 6.7.3 (bündelte CKEditor 4.22.1)
- **Problem:** CKEditor 4.22.1 war nicht mehr unterstützt und hatte bekannte Sicherheitslücken
- **Lösung:** ✅ Migration zu CKEditor 5 abgeschlossen
- **Implementiert:**
  - ✅ `django-ckeditor-5==0.2.18` installiert
  - ✅ Alle Django Settings auf CKEditor 5 umgestellt
  - ✅ CSP Settings für CKEditor 5 CDN aktualisiert
  - ✅ Migration Files korrigiert und Datenbank migriert
  - ✅ Alle Tests erfolgreich (keine Deprecated Warnings)
  - ✅ Web-Interface funktioniert korrekt mit CKEditor 5

### 2. Django-allauth Settings (MITTEL PRIORITÄT)
- **Problem:** Veraltete Settings-Optionen werden verwendet
- **Deprecation Warnings:**
  - `ACCOUNT_AUTHENTICATION_METHOD` → `ACCOUNT_LOGIN_METHODS`
  - `ACCOUNT_EMAIL_REQUIRED` → `ACCOUNT_SIGNUP_FIELDS`
  - `ACCOUNT_LOGIN_ATTEMPTS_LIMIT/TIMEOUT` → `ACCOUNT_RATE_LIMITS`

---

## 🔄 Python & Base System Updates

### Python
- **Container:** Python 3.11.13 ✅ (aktuell)
- **Host System:** Python 3.11.0 (Minor Update verfügbar → 3.11.13)
- **Neueste Stable:** Python 3.12.x (Major Update verfügbar)
- **Empfehlung:** 
  - Kurzfristig: Update auf Python 3.11.13 (Host)
  - Mittel-/Langfristig: Migration zu Python 3.12.x

### pip
- **Aktuell:** 24.0
- **Verfügbar:** 25.1.1
- **Update Command:** `pip install --upgrade pip`

---

## 🐳 Docker Images Updates

### PostgreSQL
- **Aktuell:** postgres:15-alpine (PostgreSQL 15.13)
- **Neueste:** postgres:16-alpine oder postgres:17-alpine
- **Status:** ✅ PostgreSQL 15 wird noch unterstützt (bis November 2030)
- **Empfehlung:** Update auf PostgreSQL 16 oder 17 in der nächsten größeren Version

### Traefik
- **Aktuell:** traefik:v3.2.0
- **Status:** ✅ Aktuelle Version (Oktober 2024)
- **Empfehlung:** Regelmäßig auf neueste 3.x Version prüfen

### Python Base Image
- **Aktuell:** python:3.11-slim
- **Empfehlung:** Update auf python:3.12-slim erwägen

---

## 📦 Python Package Updates

### Django Core Packages

| Package | Aktuell | Requirement | Status | Priorität |
|---------|---------|-------------|--------|-----------|
| Django | 5.2.2 | >=4.2 | ✅ Aktuell | - |
| django-allauth | 65.9.0 | >=0.55 | ✅ Aktuell | Niedrig |
| django-ckeditor | 6.7.3 | >=6.6 | ❌ Sicherheit | **HOCH** |
| django-crispy-forms | 2.4 | >=1 | ✅ Aktuell | Niedrig |
| django-csp | 4.0 | >=3.7 | ✅ Aktuell | Niedrig |
| django-environ | 0.12.0 | >=0.9 | ✅ Aktuell | Niedrig |
| django-jazzmin | 3.0.1 | >=2.6.0 | ✅ Aktuell | Niedrig |

### Infrastructure Packages

| Package | Aktuell | Requirement | Status | Priorität |
|---------|---------|-------------|--------|-----------|
| gunicorn | 23.0.0 | >=20.1 | ✅ Aktuell | Niedrig |
| psycopg2-binary | 2.9.10 | >=2.9 | ✅ Aktuell | Niedrig |
| whitenoise | 6.9.0 | >=6.5 | ✅ Aktuell | Niedrig |

### Form & UI Packages

| Package | Aktuell | Requirement | Status | Priorität |
|---------|---------|-------------|--------|-----------|
| crispy-bootstrap5 | 2025.4 | >=0.6 | ✅ Aktuell | Niedrig |
| django-bootstrap-datepicker-plus | 5.0.5 | >=4.0 | ✅ Aktuell | Niedrig |
| django-bootstrap-modal-forms | 3.0.5 | >=2 | ✅ Aktuell | Niedrig |

---

## 🛠️ Empfohlene Update-Reihenfolge

### Phase 1: Kritische Sicherheitsupdates ✅ ABGESCHLOSSEN
1. **CKEditor Migration** ✅ **ABGESCHLOSSEN**
   - ✅ django-ckeditor-5==0.2.18 installiert
   - ✅ Django Settings komplett umgestellt
   - ✅ Migration Files korrigiert
   - ✅ Datenbank erfolgreich migriert
   - ✅ CSP Security Policy aktualisiert  
   - ✅ Web-Interface getestet und funktionsfähig

2. **Django-allauth Settings aktualisieren** 🟡 **NOCH OFFEN**
   - Settings in `core/settings.py` anpassen
   - Deprecated Warnings beheben

### Phase 2: System Updates (Nächste Wartung)
1. **pip Update**
   ```bash
   docker exec django_fbf_web_1 pip install --upgrade pip
   ```

2. **Host Python Update**
   ```bash
   # Auf Host System
   brew upgrade python@3.11  # oder entsprechender Package Manager
   ```

### Phase 3: Größere Updates (Geplante Wartung)
1. **Python 3.12 Migration**
   - Dockerfile aktualisieren: `FROM python:3.12-slim`
   - Tests auf Kompatibilität prüfen
   - Container neu bauen

2. **PostgreSQL Update** (Optional)
   - docker-compose.yaml: `postgres:16-alpine`
   - Datenbank-Backup vor Update
   - Migrationstest durchführen

---

## 🔒 Sicherheitsempfehlungen

### Aktuell erkannte Probleme:
1. **CKEditor 4.22.1** - Bekannte Sicherheitslücken
2. **Veraltete django-allauth Settings** - Funktional aber deprecated

### Präventive Maßnahmen:
1. **Regelmäßige Sicherheitschecks**
   ```bash
   # Dependency-Check alle 2 Wochen
   docker exec django_fbf_web_1 pip check
   docker exec django_fbf_web_1 python manage.py check
   ```

2. **Requirements Pinning**
   - Exakte Versionen in requirements.txt verwenden
   - Sicherheitsupdates kontrolliert einspielen

3. **Automated Security Scanning**
   - GitHub Dependabot aktivieren
   - Oder andere Security-Scanning Tools verwenden

---

## 📋 Maintenance Checklist

### Monatlich:
- [ ] Django System Check ausführen
- [ ] Pip Package Updates prüfen
- [ ] Docker Image Updates prüfen
- [ ] Security Advisories checken

### Quartalsweise:
- [ ] Major Version Updates evaluieren
- [ ] Performance Tests nach Updates
- [ ] Backup-Strategie validieren
- [ ] Documentation Updates

### Jährlich:
- [ ] Python Version Migration planen
- [ ] Database Version Update evaluieren
- [ ] Dependency Audit durchführen
- [ ] Security Penetration Test

---

## 🔗 Nützliche Ressourcen

- [Django Security Releases](https://docs.djangoproject.com/en/stable/releases/security/)
- [Python Security Updates](https://www.python.org/downloads/)
- [PostgreSQL Release Schedule](https://www.postgresql.org/support/versioning/)
- [CKEditor Migration Guide](https://ckeditor.com/docs/ckeditor5/latest/installation/getting-started/migration-from-ckeditor-4.html)

---

**Letztes Update:** 7. Juni 2025  
**Nächster Review:** 7. Juli 2025
