"""! @brief Application configuration for the public station map app."""

from django.apps import AppConfig


class StationsConfig(AppConfig):
    """! @brief Register configuration metadata for the ``stations`` Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "stations"
