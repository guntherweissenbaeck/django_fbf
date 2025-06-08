# -----------------------------------
# DJANGO Content Security Policy
# -----------------------------------

CSP_DEFAULT_SRC = (
    "'self'",
    "https://cdn.datatables.net",
    "https://cdn.ckeditor.com",
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://bootswatch.com",
    "https://cdn.datatables.net",
    "https://cdnjs.cloudflare.com",
    "https://fonts.googleapis.com",
)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://cdn.datatables.net",
    "https://cdn.jsdelivr.net",
    "https://code.jquery.com",
)
CSP_INCLUDE_NONCE_IN = ["script-src"]
CSP_IMG_SRC = ("'self'", "data:")
CSP_FONT_SRC = (
    "'self'",
    "https://fonts.gstatic.com",
    "https://cdnjs.cloudflare.com",
)
