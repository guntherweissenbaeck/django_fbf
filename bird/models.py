from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from aviary.models import Aviary
from rescuer.models import Rescuer


class FallenBird(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    bird = models.ForeignKey(
        "Bird",
        on_delete=models.CASCADE,
        verbose_name=_("Patient"))
    date_found = models.DateField(verbose_name=_("Datum des Fundes"))
    place = models.CharField(max_length=256, verbose_name=_("Ort des Fundes"))
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("angelegt am"))
    updated = models.DateTimeField(
        auto_now=True, verbose_name=_("geändert am"))
    diagnostic_finding = models.CharField(max_length=256)
    cost_sum = models.DecimalField(max_digits=4, decimal_places=2)
    rescuer = models.ForeignKey(
        Rescuer, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.ForeignKey(
        "BirdStatus", on_delete=models.SET_NULL, blank=True, null=True)
    aviary = models.ForeignKey(
        Aviary, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = _("Patient")
        verbose_name_plural = _("Patienten")

    def __str__(self):
        return self.place


class Bird(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=256)

    class Meta:
        verbose_name = _("Vogel")
        verbose_name_plural = _("Vögel")

    def __str__(self):
        return self.name


class BirdStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    description = models.CharField(max_length=256)

    class Meta:
        verbose_name = _("Patientenstatus")
        verbose_name_plural = _("Patientenstatus")

    def __str__(self):
        return self.description
