# Backup with CRON

To execute a Backup Job every Night at 01:00 am you'll have to add a crontab-job like this:

```bash
0 1 * * * /srv/docker/django_fbf/bin/backupDB >/dev/null 2>&1
```
