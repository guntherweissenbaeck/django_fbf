from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _



class RescuerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rescuer"
    verbose_name = _("Finder")

