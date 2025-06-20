# Generated by Django 5.2.2 on 2025-06-07 13:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0002_contacttag_contact_tag_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'ordering': ['last_name', 'first_name'], 'verbose_name': 'Kontakt', 'verbose_name_plural': 'Kontakte'},
        ),
        migrations.AddField(
            model_name='contact',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Stadt'),
        ),
        migrations.AddField(
            model_name='contact',
            name='country',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Land'),
        ),
        migrations.AddField(
            model_name='contact',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Erstellt von'),
        ),
        migrations.AddField(
            model_name='contact',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Vorname'),
        ),
        migrations.AddField(
            model_name='contact',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Aktiv'),
        ),
        migrations.AddField(
            model_name='contact',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Nachname'),
        ),
        migrations.AddField(
            model_name='contact',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='Notizen'),
        ),
        migrations.AddField(
            model_name='contact',
            name='postal_code',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Postleitzahl'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='address',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Adresse'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(blank=True, max_length=50, null=True, verbose_name='Email'),
        ),
    ]
