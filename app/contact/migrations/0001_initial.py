# Generated by Django 4.2.5 on 2023-10-16 18:42

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Kontakt Name')),
                ('phone', models.CharField(blank=True, max_length=50, null=True, verbose_name='Telefon')),
                ('email', models.CharField(blank=True, max_length=50, null=True, verbose_name='Email')),
                ('address', models.CharField(blank=True, max_length=50, null=True, verbose_name='Adresse')),
                ('comment', models.CharField(blank=True, max_length=50, null=True, verbose_name='Bemerkungen')),
            ],
        ),
    ]
