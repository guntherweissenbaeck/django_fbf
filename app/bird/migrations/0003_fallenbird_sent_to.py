# Generated by Django 4.2.3 on 2023-07-12 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bird', '0002_alter_fallenbird_costs'),
    ]

    operations = [
        migrations.AddField(
            model_name='fallenbird',
            name='sent_to',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Übersandt nach'),
        ),
    ]
