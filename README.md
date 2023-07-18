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

## How to use this project?

### Development

Build the images and spin up the containers:

```sh
$ docker-compose up -d --build
```

Test it out:

1. [http://django.localhost:8008/](http://django.localhost:8008/)
1. [http://django.localhost:8081/](http://django.localhost:8081/)

### Production

Update the domain in *docker-compose.prod.yml*, and add your email to *traefik.prod.toml*.

Build the images and run the containers:

```sh
$ docker-compose -f docker-compose.prod.yml up -d --build
```

https://testdriven.io/blog/django-docker-traefik/

