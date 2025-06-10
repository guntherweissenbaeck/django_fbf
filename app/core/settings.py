import os
from pathlib import Path

import environ

env = environ.Env()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# -----------------------------------
# SECURITY WARNING: keep the secret key used in production secret!
# -----------------------------------
SECRET_KEY = env("SECRET_KEY")

# -----------------------------------
# SECURITY WARNING: don't run with debug turned on in production!
# -----------------------------------
DEBUG = env.bool("DEBUG")

# -----------------------------------
# CSRF Stuff
# -----------------------------------
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ["https://fbf.nabu-jena.de"]

# -----------------------------------
# Cookies
# -----------------------------------
SESSION_COOKIE_SECURE = True

# -----------------------------------
# HTTPS
# -----------------------------------
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# -----------------------------------
# Allowed Hosts
# -----------------------------------
ALLOWED_HOSTS = [env("ALLOWED_HOSTS")]

# -----------------------------------
# Application definition
# -----------------------------------
INSTALLED_APPS = [
    # -----------------------------------
    # Jazzmin
    # -----------------------------------
    "jazzmin",
    # -----------------------------------
    # Django default
    # -----------------------------------
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # -----------------------------------
    # All auth
    # -----------------------------------
    "allauth",
    "allauth.account",
    # -----------------------------------
    # Crispy forms, modals and bootstrap5
    # -----------------------------------
    "bootstrap_modal_forms",
    "crispy_bootstrap5",
    "crispy_forms",
    # -----------------------------------
    # CKEditor 5
    # -----------------------------------
    "django_ckeditor_5",
    # -----------------------------------
    # My Apps
    # -----------------------------------
    "aviary",
    "bird",
    "contact",
    "costs",
    "export",
    "sendemail",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
]

# -----------------------------------
# DJANGO Content Security Policy
# -----------------------------------
try:
    from .csp import (
        CSP_DEFAULT_SRC,
        CSP_FONT_SRC,
        CSP_IMG_SRC,
        CSP_SCRIPT_SRC,
        CSP_STYLE_SRC,
        CSP_INCLUDE_NONCE_IN,
    )
except ImportError:
    print("No CSP Settings found!")

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # Allauth specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

WSGI_APPLICATION = "core.wsgi.application"


# -----------------------------------
# Database
# -----------------------------------
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env("DB_HOST"),
        "NAME": env("DB_NAME"),
        "PASSWORD": env("DB_PASSWORD"),
        "PORT": env("DB_PORT"),
        "USER": env("DB_USER"),
    }
}


# -----------------------------------
# Password validation
# -----------------------------------
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# -----------------------------------
# Internationalization
# -----------------------------------
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "de-de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

# -----------------------------------
# Default primary key field type
# -----------------------------------
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# -----------------------------------
# Allauth
# -----------------------------------
try:
    from .allauth import (
        ACCOUNT_LOGIN_METHODS,
        ACCOUNT_SIGNUP_FIELDS,
        ACCOUNT_EMAIL_VERIFICATION,
        ACCOUNT_RATE_LIMITS,
        ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION,
        ACCOUNT_LOGOUT_REDIRECT_URL,
        ACCOUNT_LOGOUT_ON_GET,
        ACCOUNT_SESSION_REMEMBER,
        ACCOUNT_USERNAME_BLACKLIST,
        ACCOUNT_USERNAME_MIN_LENGTH,
        ACCOUNT_UNIQUE_EMAIL,
        LOGIN_REDIRECT_URL,
        SITE_ID,
    )
except ImportError:
    print("No AllAuth Settings found!")


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# -----------------------------------
# Media files (User uploaded content)
# -----------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -----------------------------------
# Email
# -----------------------------------

# Console Backend for Development Usage.
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# SMTP Backup for Production Usage.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":
    DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
    EMAIL_HOST_USER = env("EMAIL_HOST_USER")
    EMAIL_HOST = env("EMAIL_HOST")
    EMAIL_PORT = env("EMAIL_PORT")
    EMAIL_USE_TLS = True

# -----------------------------------
# Additional App Settings
# -----------------------------------
# Jazzmin
try:
    from .jazzmin import JAZZMIN_SETTINGS
except ImportError:
    print("No Jazzmin Settings found!")

# CKEditor 5
try:
    from .ckeditor import CKEDITOR_5_CONFIGS
except ImportError:
    print("No CKEditor Settings found!")
