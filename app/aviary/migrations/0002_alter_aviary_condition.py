# Generated by Django 4.2.2 on 2023-07-08 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aviary", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="aviary",
            name="condition",
            field=models.CharField(
                choices=[
                    ("Offen", "Offen"),
                    ("Geschlossen", "Geschlossen"),
                    ("Gesperrt", "Geshlossem"),
                ],
                max_length=256,
                verbose_name="Zustand",
            ),
        ),
    ]