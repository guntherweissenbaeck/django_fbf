# Generated manually for notification settings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bird', '0006_alter_fallenbird_options_alter_fallenbird_age_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bird',
            name='melden_an_naturschutzbehoerde',
            field=models.BooleanField(default=True, verbose_name='Melden an Naturschutzbehörde'),
        ),
        migrations.AddField(
            model_name='bird',
            name='melden_an_jagdbehoerde',
            field=models.BooleanField(default=False, verbose_name='Melden an Jagdbehörde'),
        ),
        migrations.AddField(
            model_name='bird',
            name='melden_an_wildvogelhilfe_team',
            field=models.BooleanField(default=True, verbose_name='Melden an Wildvogelhilfe-Team'),
        ),
    ]
