# Generated by Django 5.2.2 on 2025-06-07 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bird', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='birdstatus',
            name='name',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='circumstance',
            name='name',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Name'),
        ),
    ]
