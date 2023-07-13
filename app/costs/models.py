from datetime import date
from uuid import uuid4

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from bird.models import FallenBird


class Costs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    id_bird = models.ForeignKey(
        FallenBird,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Patient"),
    )
    costs = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default="0.00",
        verbose_name=_("Betrag"))
    created = models.DateField(
        verbose_name=_("Gebucht am"))
    comment = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        verbose_name=_("Bemerkungen"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Benutzer"))

    class Meta:
        verbose_name = _("Kosten")
        verbose_name_plural = _("Kosten")
