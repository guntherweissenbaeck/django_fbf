# Generated by Django 5.2.2 on 2025-06-10 07:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sendemail', '0003_alter_emailadress_is_naturschutzbehoerde_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BirdEmail',
        ),
    ]
