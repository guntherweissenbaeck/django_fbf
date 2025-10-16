# Security & Privacy

## Prinzipien
- Minimale Angriffsfläche (wenige öffentliche Views)
- Prinzip der geringsten Rechte (Admin nur für interne Nutzer)
- Datenschutz: Minimierung personenbezogener Daten in Exporten

## Authentifizierung
- Django Session Auth
- Admin: Benutzeranlage via `createsuperuser` oder Startskript

## CSRF & Formularschutz
- Standard Django CSRF aktiv
- Öffentliche Suggest-Formulare validieren Input

## Header / Cache Kontrolle
- `StationDataView` setzt `Cache-Control: no-store` + ETag -> verhindert veraltete Kartenmarker

## Geplante Maßnahmen
- Security Headers Hardening (Content-Security-Policy, Referrer-Policy)
- Rate Limiting für öffentliche Vorschlags-Endpoints
- Brute Force Schutz (django-axes o. ä.)
- Optionale 2FA für Admin Accounts

## Logging & Monitoring
- Standard Logging (stdout in Container)
- Geplant: strukturierte JSON Logs + Filter für personenbezogene Daten

Weiter: [[Roadmap]]
