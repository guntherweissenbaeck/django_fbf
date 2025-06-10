# -----------------------------------
# Django-allauth settings
# -----------------------------------
# https://django-allauth.readthedocs.io/en/latest/configuration.html
# https://django-allauth.readthedocs.io/en/latest/views.html


SITE_ID = 1
# Updated settings to replace deprecated options
ACCOUNT_LOGIN_METHODS = {"username", "email"}  # Replaces ACCOUNT_AUTHENTICATION_METHOD
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]  # Replaces ACCOUNT_EMAIL_REQUIRED
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_RATE_LIMITS = {
    "login_failed": "5/15m",  # Replaces ACCOUNT_LOGIN_ATTEMPTS_LIMIT/TIMEOUT (5 attempts per 15 minutes)
}
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_USERNAME_BLACKLIST = ["admin", "god"]
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_UNIQUE_EMAIL = True
LOGIN_REDIRECT_URL = "/bird/all"
