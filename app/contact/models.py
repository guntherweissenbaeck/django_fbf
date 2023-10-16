from django.db import models
from uuid import uuid4

from django.utils.translation import gettext_lazy as _


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Kontakt Name")
    )
    phone = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Telefon")
    )
    email = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Email")
    )
    address = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Adresse")
    )
    comment = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Bemerkungen")
    )


    class Meta:
        verbose_name = _("Kontakt")
        verbose_name_plural = _("Kontakte")
