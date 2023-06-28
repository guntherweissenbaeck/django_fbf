from uuid import uuid4
from django.db import models


class Aviary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    description = models.CharField(max_length=256)
    condition = models.CharField(max_length=256)
    last_ward_round = models.DateField()

    def __str__(self):
        return self.description
