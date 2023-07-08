# Generated by Django 4.2.2 on 2023-07-08 20:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("rescuer", "0001_initial"),
        ("aviary", "0002_alter_aviary_condition"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Bird",
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
                ("name", models.CharField(max_length=256, unique=True)),
                (
                    "description",
                    models.CharField(max_length=4096, verbose_name="Hilfetext"),
                ),
            ],
            options={
                "verbose_name": "Vogel",
                "verbose_name_plural": "Vögel",
            },
        ),
        migrations.CreateModel(
            name="BirdStatus",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("description", models.CharField(max_length=256, unique=True)),
            ],
            options={
                "verbose_name": "Patientenstatus",
                "verbose_name_plural": "Patientenstatus",
            },
        ),
        migrations.CreateModel(
            name="FallenBird",
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
                    "bird_identifier",
                    models.CharField(max_length=256, verbose_name="Kennung"),
                ),
                ("date_found", models.DateField(verbose_name="Datum des Fundes")),
                (
                    "place",
                    models.CharField(max_length=256, verbose_name="Ort des Fundes"),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="angelegt am"),
                ),
                (
                    "updated",
                    models.DateTimeField(auto_now=True, verbose_name="geändert am"),
                ),
                ("diagnostic_finding", models.CharField(max_length=256)),
                (
                    "cost_sum",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
                ),
                (
                    "aviary",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="aviary.aviary",
                    ),
                ),
                (
                    "bird",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bird.bird",
                        verbose_name="Patient",
                    ),
                ),
                (
                    "rescuer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="rescuer.rescuer",
                    ),
                ),
                (
                    "status",
                    models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bird.birdstatus",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Patient",
                "verbose_name_plural": "Patienten",
            },
        ),
    ]
