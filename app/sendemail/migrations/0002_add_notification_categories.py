# Generated manually for notification categories

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sendemail', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailadress',
            name='is_naturschutzbehoerde',
            field=models.BooleanField(default=False, verbose_name='Naturschutzbehörde'),
        ),
        migrations.AddField(
            model_name='emailadress',
            name='is_jagdbehoerde',
            field=models.BooleanField(default=False, verbose_name='Jagdbehörde'),
        ),
        migrations.AddField(
            model_name='emailadress',
            name='is_wildvogelhilfe_team',
            field=models.BooleanField(default=False, verbose_name='Wildvogelhilfe-Team'),
        ),
    ]
