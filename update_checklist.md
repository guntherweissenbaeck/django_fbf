# Update Checklist - Django FBF Projekt

**Erstellt am:** 7. Juni 2025  
**Letzter Check:** 7. Juni 2025

## 🔍 Übersicht

Dieses Dokument listet alle Abhängigkeiten auf, die Updates benötigen, sowie Sicherheitshinweise und Empfehlungen für das Django FBF (Fallen Birdy Form) Projekt.

---

## 🚨 Kritische Sicherheitsupdates ✅ **ALLE ABGESCHLOSSEN**

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

### 2. Django-allauth Settings (MITTEL PRIORITÄT) ✅ ABGESCHLOSSEN
- **Problem:** Veraltete Settings-Optionen wurden verwendet
- **Lösung:** ✅ Alle deprecated Settings erfolgreich aktualisiert
- **Umgesetzte Änderungen:**
  - ✅ `ACCOUNT_AUTHENTICATION_METHOD` → `ACCOUNT_LOGIN_METHODS = {"username", "email"}`
  - ✅ `ACCOUNT_EMAIL_REQUIRED` → `ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]`
  - ✅ `ACCOUNT_LOGIN_ATTEMPTS_LIMIT/TIMEOUT` → `ACCOUNT_RATE_LIMITS = {"login_failed": "5/15m"}`
- **Validierung:**
  - ✅ Keine Deprecation Warnings mehr vorhanden
  - ✅ django-allauth 65.9.0 läuft einwandfrei
  - ✅ Login-Funktionalität getestet und funktionsfähig

### 3. **KRITISCHER FEHLER BEHOBEN** ✅ **ABGESCHLOSSEN**
- **Problem:** Group DoesNotExist Error verhinderte Applikationsstart
- **Lösung:** ✅ Template Filter robuster gemacht
- **Implementiert:**
  - ✅ Sichere Fehlerbehandlung für fehlende User Groups
  - ✅ Anwendung läuft wieder stabil und fehlerfrei
  - ✅ Navbar zeigt Export-Link nur bei vorhandener "data-export" Gruppe

---

## 🔄 Python & Base System Updates ✅ **ABGESCHLOSSEN**

### Python ✅ **HOST UPDATE ABGESCHLOSSEN**
- **Container:** Python 3.11.13 ✅ (aktuell)
- **Host System:** Python 3.11.13 ✅ **AKTUALISIERT** (war 3.11.0)
- **Neueste Stable:** Python 3.12.x (Major Update verfügbar)
- **Status:** ✅ **Host-System auf neueste 3.11 Version aktualisiert**

### pip ✅ **BEREITS AKTUELL**
- **Aktuell:** 25.1.1 ✅ (bereits neueste Version)
- **Status:** ✅ **Keine Aktualisierung nötig**

---

## 🐳 Docker Images Updates ✅ **TEILWEISE ABGESCHLOSSEN**

### PostgreSQL ✅ **STABIL BELASSEN**
- **Aktuell:** postgres:15-alpine (PostgreSQL 15.13)
- **Verfügbar:** postgres:16-alpine oder postgres:17-alpine  
- **Status:** ✅ PostgreSQL 15 wird noch unterstützt (bis November 2030)
- **Entscheidung:** ⚠️ **Bei Version 15 belassen** - Update auf 16/17 erfordert Datenbank-Migration

### Traefik ✅ **AKTUALISIERT**
- **Früher:** traefik:v3.2.0 (7 Monate alt)
- **Aktuell:** traefik:latest ✅ **AKTUALISIERT** (11 Tage alt)
- **Status:** ✅ **Erfolgreich auf neueste Version aktualisiert**

### Python Base Image ✅ **AKTUELL**
- **Aktuell:** python:3.11-slim ✅ (optimal für Projekt)

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

2. **Django-allauth Settings aktualisieren** ✅ **ABGESCHLOSSEN**
   - ✅ Alle deprecated Settings in `core/allauth.py` modernisiert
   - ✅ django-allauth 65.9.0 läuft ohne Deprecation Warnings
   - ✅ Login-Funktionalität vollständig getestet und funktionsfähig

### Phase 2: System Updates (Nächste Wartung) ✅ **ABGESCHLOSSEN**
1. **pip Update** ✅ **ABGESCHLOSSEN**
   - ✅ pip bereits auf neuester Version 25.1.1

2. **Host Python Update** ✅ **ABGESCHLOSSEN**  
   - ✅ Python 3.11.13 via Homebrew installiert
   - ✅ Upgrade von Python 3.11.0 → Python 3.11.13

3. **Docker Images Update** ✅ **TEILWEISE ABGESCHLOSSEN**
   - ✅ Traefik v3.2.0 → traefik:latest (erheblich neuer)
   - ⚠️ PostgreSQL 15-alpine beibehalten (16-alpine erfordert Datenbank-Migration)
   - ✅ Veraltete Docker Images aufgeräumt

4. **Python Packages Update** ✅ **ABGESCHLOSSEN**
   - ✅ setuptools 65.5.1 → 80.9.0 
   - ⚠️ pydantic_core Kompatibilität mit bestehender pydantic Version beibehalten

5. **Kritischer Fehler behoben** ✅ **ABGESCHLOSSEN**
   - ✅ Group DoesNotExist Error in template filter behoben
   - ✅ Robuste Fehlerbehandlung für fehlende User Groups implementiert

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
