from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'costs'
    verbose_name = _("Kosten")
