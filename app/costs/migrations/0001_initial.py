# Generated by Django 4.2.3 on 2023-07-13 09:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bird', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Costs',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('costs', models.DecimalField(decimal_places=2, default='0.00', max_digits=5, verbose_name='Kosten')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='angelegt am')),
                ('comment', models.CharField(blank=True, max_length=512, null=True, verbose_name='Bemerkungen')),
                ('id_bird', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='bird.fallenbird', verbose_name='Patient')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Benutzer')),
            ],
            options={
                'verbose_name': 'Kosten',
                'verbose_name_plural': 'Kosten',
            },
        ),
    ]