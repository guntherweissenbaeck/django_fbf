# Troubleshooting

| Problem | Ursache | Lösung |
|---------|---------|-------|
| Container startet nicht | Port bereits belegt | Ports in `docker-compose.yaml` anpassen |
| Secret Key Fehler | `.env` fehlt | `./start_project.sh` erneut ausführen, legt Datei an |
| Keine statischen Dateien | `collectstatic` nicht gelaufen | `docker compose exec web python manage.py collectstatic` |
| Tests finden Module nicht | `PYTHONPATH` fehlt | `PYTHONPATH=app python3 -m pytest ...` |
| Stationsdaten veraltet | Browser Cache | Hard Reload oder Header-Konfiguration (bereits no-store) |
| Keine E-Mails | Dev Console Backend | SMTP Variablen in `.env` setzen |

Weiter: [[Security-und-Privacy]]
