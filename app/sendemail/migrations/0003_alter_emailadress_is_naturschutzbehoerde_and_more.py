# Generated by Django 5.2.2 on 2025-06-10 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sendemail', '0002_add_notification_categories'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailadress',
            name='is_naturschutzbehoerde',
            field=models.BooleanField(default=True, verbose_name='Naturschutzbehörde'),
        ),
        migrations.AlterField(
            model_name='emailadress',
            name='is_wildvogelhilfe_team',
            field=models.BooleanField(default=True, verbose_name='Wildvogelhilfe-Team'),
        ),
    ]
