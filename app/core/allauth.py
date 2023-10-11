# -----------------------------------
# Django-allauth settings
# -----------------------------------
# https://django-allauth.readthedocs.io/en/latest/configuration.html
# https://django-allauth.readthedocs.io/en/latest/views.html


SITE_ID = 1
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 900  # 15 Minutes
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_USERNAME_BLACKLIST = ["admin", "god"]
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_UNIQUE_EMAIL = True
LOGIN_REDIRECT_URL = "/bird/all"