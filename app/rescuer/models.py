from datetime import date
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Rescuer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    first_name = models.CharField(max_length=200,  verbose_name=_("Vorname"))
    last_name = models.CharField(max_length=200,  verbose_name=_("Nachname"))
    street = models.CharField(max_length=200, verbose_name=_("Straße"))
    street_number = models.CharField(max_length=20, verbose_name=_("Nummer"))
    city = models.CharField(max_length=200, verbose_name=_("Stadt"))
    zip_code = models.CharField(max_length=200,  verbose_name=_("PLZ"))
    phone = models.CharField(max_length=200,  verbose_name=_("Telefon"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Finder")
        verbose_name_plural = _("Finder")

    def __str__(self) -> str:
        return self.first_name + " " + self.last_name
