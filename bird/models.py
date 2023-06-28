from uuid import uuid4

from django.conf import settings
from django.db import models

from rescuer.models import Rescuer
from aviary.models import Aviary


class FallenBird(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    bird = models.ForeignKey("Bird", on_delete=models.CASCADE)
    date_found = models.DateField()
    place = models.CharField(max_length=256)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    rescuer = models.ForeignKey(Rescuer, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    aviary = models.ForeignKey(Aviary, on_delete=models.CASCADE)

    def __str__(self):
        return self.place


class Bird(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name
