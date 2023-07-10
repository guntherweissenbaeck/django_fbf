from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AviaryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aviary"
    verbose_name = _("Volieren")
