from django.apps import AppConfig


class AdministrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "administration"
    verbose_name = "Administration"

    def ready(self):
        from .models import SMTPConfiguration
        SMTPConfiguration.apply_active_configuration()
