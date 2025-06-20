# Generated by Django 5.2.2 on 2025-06-10 09:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sendemail', '0004_delete_birdemail'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AutomaticReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Beschreibung')),
                ('include_naturschutzbehoerde', models.BooleanField(default=True, help_text='Vögel einschließen, die an Naturschutzbehörde gemeldet werden', verbose_name='Naturschutzbehörde einschließen')),
                ('include_jagdbehoerde', models.BooleanField(default=False, help_text='Vögel einschließen, die an Jagdbehörde gemeldet werden', verbose_name='Jagdbehörde einschließen')),
                ('frequency', models.CharField(choices=[('weekly', 'Wöchentlich'), ('monthly', 'Monatlich'), ('quarterly', 'Vierteljährlich')], default='monthly', max_length=20, verbose_name='Häufigkeit')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktiv')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Aktualisiert am')),
                ('last_sent', models.DateTimeField(blank=True, null=True, verbose_name='Zuletzt gesendet')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Erstellt von')),
                ('email_addresses', models.ManyToManyField(help_text='E-Mail-Adressen, an die der Report gesendet wird', to='sendemail.emailadress', verbose_name='E-Mail-Adressen')),
            ],
            options={
                'verbose_name': 'Automatischer Report',
                'verbose_name_plural': 'Automatische Reports',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ReportLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(choices=[('manual', 'Manuell erstellt'), ('automatic', 'Automatisch erstellt')], max_length=20, verbose_name='Report-Typ')),
                ('date_from', models.DateField(verbose_name='Von')),
                ('date_to', models.DateField(verbose_name='Bis')),
                ('included_naturschutzbehoerde', models.BooleanField(verbose_name='Naturschutzbehörde eingeschlossen')),
                ('included_jagdbehoerde', models.BooleanField(verbose_name='Jagdbehörde eingeschlossen')),
                ('bird_count', models.IntegerField(verbose_name='Anzahl Vögel')),
                ('email_sent', models.BooleanField(default=False, verbose_name='E-Mail gesendet')),
                ('recipients', models.TextField(blank=True, verbose_name='Empfänger')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')),
                ('automatic_report', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reports.automaticreport', verbose_name='Automatischer Report')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Erstellt von')),
            ],
            options={
                'verbose_name': 'Report-Log',
                'verbose_name_plural': 'Report-Logs',
                'ordering': ['-created_at'],
            },
        ),
    ]
