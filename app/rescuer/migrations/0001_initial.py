# Generated by Django 4.2.3 on 2023-07-13 09:34

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
            name='Rescuer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=200, verbose_name='Vorname')),
                ('last_name', models.CharField(max_length=200, verbose_name='Nachname')),
                ('street', models.CharField(max_length=200, verbose_name='Straße')),
                ('street_number', models.CharField(max_length=20, verbose_name='Nummer')),
                ('city', models.CharField(max_length=200, verbose_name='Stadt')),
                ('zip_code', models.CharField(max_length=200, verbose_name='PLZ')),
                ('phone', models.CharField(max_length=200, verbose_name='Telefon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Finder',
                'verbose_name_plural': 'Finder',
            },
        ),
    ]
