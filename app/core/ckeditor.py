# -----------------------------------
# CKEDITOR CONFIGURATION
# -----------------------------------

CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"
CKEDITOR_UPLOAD_PATH = "media"

CKEDITOR_CONFIGS = {
    "default": {
        "removePlugins": "exportpdf",
        "height": 300,
        "width": "100%",
        "allowedContent": True,
    }
}
