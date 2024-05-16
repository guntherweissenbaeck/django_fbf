# Generated by Django 4.2.6 on 2023-10-22 10:14

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactTag',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tag', models.CharField(blank=True, max_length=50, null=True, verbose_name='Tag')),
            ],
            options={
                'verbose_name': 'Kontakt Tag',
                'verbose_name_plural': 'Kontakt Tags',
            },
        ),
        migrations.AddField(
            model_name='contact',
            name='tag_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contact.contacttag', verbose_name='Tag'),
        ),
    ]