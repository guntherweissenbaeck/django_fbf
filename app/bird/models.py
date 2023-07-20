from datetime import date
from uuid import uuid4

from aviary.models import Aviary
from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from rescuer.models import Rescuer


def costs_default():
    return [{"date": date.today().strftime("%Y-%m-%d"), "cost_entry": "0.00"}]


class FallenBird(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    bird_identifier = models.CharField(max_length=256, verbose_name=_("Kennung"))
    bird = models.ForeignKey(
        "Bird", on_delete=models.CASCADE, verbose_name=_("Patient")
    )
    date_found = models.DateField(verbose_name=_("Datum des Fundes"))
    place = models.CharField(max_length=256, verbose_name=_("Ort des Fundes"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("angelegt am"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("geändert am"))
    find_circumstances = models.ForeignKey(
        "Circumstance", on_delete=models.CASCADE, verbose_name=_("Fundumstände")
    )
    diagnostic_finding = models.CharField(
        max_length=256, verbose_name=_("Diagnose bei Fund")
    )
    rescuer = models.ForeignKey(
        Rescuer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Finder"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Benutzer")
    )
    status = models.ForeignKey("BirdStatus", on_delete=models.CASCADE, default=1)
    aviary = models.ForeignKey(
        Aviary,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Voliere"),
    )
    sent_to = models.CharField(
        max_length=256, null=True, blank=True, verbose_name=_("Übersandt nach")
    )

    class Meta:
        verbose_name = _("Patient")
        verbose_name_plural = _("Patienten")

    def __str__(self):
        return self.bird_identifier


class Bird(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=256, unique=True, verbose_name=_("Bezeichnung"))
    description = RichTextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Vogel")
        verbose_name_plural = _("Vögel")

    def __str__(self):
        return self.name


class BirdStatus(models.Model):
    id = models.BigAutoField(primary_key=True)
    description = models.CharField(
        max_length=256, unique=True, verbose_name=_("Bezeichnung")
    )

    class Meta:
        verbose_name = _("Patientenstatus")
        verbose_name_plural = _("Patientenstatus")

    def __str__(self):
        return self.description


# CHOICE_FIND_CIRCUMSTANCES = [
#     ("Neu", "Neu"),
#     ("Scheibenschlag", "Scheibenschlag"),
#     ("Angriff Hund/Katze", "Angriff Hund/Katze"),
#     ("Entkräftet", "Entkräftet"),
#     ("Verkehrsunfall", "Verkehrsunfall"),
#     ("unbekannt", "unbekannt"),
# ]


class Circumstance(models.Model):
    id = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=256, verbose_name=_("Bezeichnung"))

    class Meta:
        verbose_name = _("Fundumstand")
        verbose_name_plural = _("Fundumstände")

    def __str__(self) -> str:
        return self.description
