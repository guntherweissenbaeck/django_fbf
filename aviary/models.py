from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


class Aviary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    description = models.CharField(
        max_length=256, verbose_name=_("Beschreibung"))
    condition = models.CharField(max_length=256, verbose_name=_("Zustand"))
    last_ward_round = models.DateField(verbose_name=_("letzte Visite"))

    class Meta:
        verbose_name = _("Voliere")
        verbose_name_plural = _("Volieren")

    def __str__(self):
        return self.description
