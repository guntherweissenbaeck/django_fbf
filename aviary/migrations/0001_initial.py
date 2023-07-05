# Generated by Django 4.2.2 on 2023-07-04 16:19

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Aviary",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        max_length=256, unique=True, verbose_name="Beschreibung"
                    ),
                ),
                ("condition", models.CharField(max_length=256, verbose_name="Zustand")),
                ("last_ward_round", models.DateField(verbose_name="letzte Visite")),
            ],
            options={
                "verbose_name": "Voliere",
                "verbose_name_plural": "Volieren",
            },
        ),
    ]
