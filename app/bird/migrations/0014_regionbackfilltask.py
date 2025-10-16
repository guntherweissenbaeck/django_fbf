from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bird', '0013_geocodeattempt'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegionBackfillTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('total_patients', models.PositiveIntegerField(default=0)),
                ('processed_patients', models.PositiveIntegerField(default=0)),
                ('success_count', models.PositiveIntegerField(default=0)),
                ('error_count', models.PositiveIntegerField(default=0)),
                ('errors', models.JSONField(blank=True, default=list)),
                ('is_running', models.BooleanField(default=False)),
                ('batch_size', models.PositiveIntegerField(default=50)),
            ],
        ),
    ]
