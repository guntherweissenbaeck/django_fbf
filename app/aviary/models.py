from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


CHOICE_AVIARY = [
    ("Offen", "Offen"),
    ("Geschlossen", "Geschlossen"),
    ("Gesperrt", "Gesperrt"),
]


class Aviary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    description = models.CharField(
        max_length=256, verbose_name=_("Beschreibung"), unique=True
    )
    condition = models.CharField(
        max_length=256, choices=CHOICE_AVIARY, verbose_name=_("Zustand")
    )
    last_ward_round = models.DateField(verbose_name=_("letzte Visite"))
    comment = models.CharField(
        max_length=512, blank=True, null=True, verbose_name=_("Bemerkungen")
    )

    class Meta:
        verbose_name = _("Voliere")
        verbose_name_plural = _("Volieren")

    def __str__(self):
        return self.description
