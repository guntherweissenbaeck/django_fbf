from uuid import uuid4

from django.conf import settings
from django.db import models

from aviary.models import Aviary
from rescuer.models import Rescuer


#  STATUS = [
#  ("In Behandlung", "In Behandlung"),
#  ("In Auswilderung", "In Auswilderung"),
#  ("Ausgewildert", "Ausgewildert"),
#  ("Verstorben", "Verstorben"),
#  ]


class FallenBird(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    bird = models.ForeignKey("Bird", on_delete=models.CASCADE)
    date_found = models.DateField()
    place = models.CharField(max_length=256)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    diagnostic_finding = models.CharField(max_length=256)
    cost_sum = models.DecimalField(max_digits=4, decimal_places=2)
    rescuer = models.ForeignKey(
        Rescuer, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    aviary = models.ForeignKey(
        Aviary, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.ForeignKey(
        "BirdStatus", on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.place


class Bird(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class BirdStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    description = models.CharField(max_length=256)

    def __str__(self):
        return self.description
