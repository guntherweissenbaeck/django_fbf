from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bird', '0012_birdregion_fallenbird_region'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeocodeAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query', models.CharField(max_length=256, verbose_name='Originaleingabe')),
                ('attempted_queries', models.JSONField(verbose_name='Versuchs-Queries')),
                ('success', models.BooleanField(default=False, verbose_name='Erfolg')),
                ('status_code', models.PositiveIntegerField(blank=True, null=True, verbose_name='HTTP Status')),
                ('city', models.CharField(blank=True, max_length=128, verbose_name='Stadt')),
                ('county', models.CharField(blank=True, max_length=128, verbose_name='Landkreis')),
                ('state', models.CharField(blank=True, max_length=128, verbose_name='Bundesland')),
                ('error', models.CharField(blank=True, max_length=256, verbose_name='Fehlertext')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Zeitpunkt')),
            ],
            options={
                'verbose_name': 'Geocoding-Versuch',
                'verbose_name_plural': 'Geocoding-Versuche',
                'ordering': ('-created_at',),
            },
        ),
    ]
