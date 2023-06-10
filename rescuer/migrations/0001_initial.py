# Generated by Django 4.2.2 on 2023-06-08 15:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Rescuer",
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
                    "gender",
                    models.CharField(
                        choices=[
                            ("Frau", "Frau"),
                            ("Herr", "Herr"),
                            ("Divers", "Divers"),
                        ],
                        max_length=10,
                    ),
                ),
                ("first_name", models.CharField(max_length=200)),
                ("last_name", models.CharField(max_length=200)),
                ("street", models.CharField(max_length=200)),
                ("street_number", models.CharField(max_length=20)),
                ("city", models.CharField(max_length=200)),
                ("zip_code", models.CharField(max_length=200)),
                (
                    "state",
                    models.CharField(
                        choices=[("Deutschland", "Deutschland")], max_length=200
                    ),
                ),
                ("date_of_birth", models.DateField()),
                ("email", models.EmailField(max_length=200)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]