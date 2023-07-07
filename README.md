# The Fallen Birdy Form

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

### Docker Stack
```docker
# docker-compose.yaml
version: '3.7'

services:
  django_gunicorn:
    build:
      context: .
    env_file:
      - .env
    volumes:
      - static:/static
      - ./django_project:/app
    restart: always
    container_name: lvr_django

  nginx:
    build: ./nginx
    volumes:
      - static:/static
    depends_on:
      - django_gunicorn
    restart: always
    container_name: lvr_nginx
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.whoami-http.entrypoints=web"
      - "traefik.http.routers.whoami-http.rule=Host(`${APP_URL}`)"
      - "traefik.http.routers.whoami.rule=Host(`${APP_URL}`)"
      - "traefik.http.routers.whoami.tls.certresolver=default"
      - "traefik.http.routers.whoami.tls=true"
    networks:
      - traefik_proxy
      - default

networks:
  traefik_proxy:
    external:
      name: traefik_proxy

volumes:
  static:
```

### Dockerfile
```
# Dockerfile
FROM python:3.10-alpine

RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libffi-dev libc-dev linux-headers postgresql-dev \
      musl-dev zlib zlib-dev

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

# This is not installed by default
RUN pip install tzdata

COPY ./django_project /app

WORKDIR /app

COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]
```

### Entrypoint Shell Script
```
# entrypoint.sh
#!/bin/sh

python manage.py migrate --no-input
python manage.py collectstatic --no-input

gunicorn core.wsgi:application --bind 0.0.0.0:8000
```