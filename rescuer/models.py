from datetime import date
from uuid import uuid4

from django.conf import settings
from django.db import models

STATE_CHOICES = [
    ("Deutschland", "Deutschland"),
]

GENDER_CHOICES = [("Frau", "Frau"), ("Herr", "Herr"), ("Divers", "Divers")]


class Rescuer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    street = models.CharField(max_length=200)
    street_number = models.CharField(max_length=20)
    city = models.CharField(max_length=200)
    zip_code = models.CharField(max_length=200)
    state = models.CharField(max_length=200, choices=STATE_CHOICES)
    date_of_birth = models.DateField()
    email = models.EmailField(max_length=200)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.first_name + " " + self.last_name
