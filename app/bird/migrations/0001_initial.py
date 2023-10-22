# Generated by Django 4.2.6 on 2023-10-22 09:59

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('aviary', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bird',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, unique=True, verbose_name='Bezeichnung')),
                ('description', ckeditor.fields.RichTextField(verbose_name='Erläuterungen')),
            ],
            options={
                'verbose_name': 'Vogel',
                'verbose_name_plural': 'Vögel',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='BirdStatus',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=256, unique=True, verbose_name='Bezeichnung')),
            ],
            options={
                'verbose_name': 'Patientenstatus',
                'verbose_name_plural': 'Patientenstatus',
            },
        ),
        migrations.CreateModel(
            name='Circumstance',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=256, verbose_name='Bezeichnung')),
            ],
            options={
                'verbose_name': 'Fundumstand',
                'verbose_name_plural': 'Fundumstände',
            },
        ),
        migrations.CreateModel(
            name='FallenBird',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('bird_identifier', models.CharField(max_length=256, verbose_name='Patienten Alias')),
                ('age', models.CharField(choices=[('unbekannt', 'unbekannt'), ('Ei', 'Ei'), ('Nestling', 'Nestling'), ('Ästling', 'Ästling'), ('Juvenil', 'Juvenil'), ('Adult', 'Adult')], max_length=15, verbose_name='Alter')),
                ('sex', models.CharField(choices=[('Weiblich', 'Weiblich'), ('Männlich', 'Männlich'), ('Unbekannt', 'Unbekannt')], max_length=15, verbose_name='Geschlecht')),
                ('date_found', models.DateField(verbose_name='Datum des Fundes')),
                ('place', models.CharField(max_length=256, verbose_name='Ort des Fundes')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='angelegt am')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='geändert am')),
                ('diagnostic_finding', models.CharField(max_length=256, verbose_name='Diagnose bei Fund')),
                ('sent_to', models.CharField(blank=True, max_length=256, null=True, verbose_name='Übersandt nach')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Bemerkung')),
                ('finder', models.TextField(blank=True, default='Vorname: \nNachname: \nStraße: \nHausnummer: \nStadt: \nPLZ: \nTelefonnummer: ', null=True, verbose_name='Finder')),
                ('aviary', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='aviary.aviary', verbose_name='Voliere')),
                ('bird', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bird.bird', verbose_name='Vogel')),
                ('find_circumstances', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bird.circumstance', verbose_name='Fundumstände')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='bird.birdstatus')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Benutzer')),
            ],
            options={
                'verbose_name': 'Patient',
                'verbose_name_plural': 'Patienten',
            },
        ),
    ]
