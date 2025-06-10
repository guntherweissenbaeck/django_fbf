# Data migration to set defaults for existing Bird records

from django.db import migrations


def set_default_notification_settings(apps, schema_editor):
    """Set default notification settings for all existing Bird records."""
    Bird = apps.get_model('bird', 'Bird')
    
    # Update all existing birds to have the default notification settings
    Bird.objects.all().update(
        melden_an_naturschutzbehoerde=True,
        melden_an_wildvogelhilfe_team=True,
        melden_an_jagdbehoerde=False
    )


def reverse_default_notification_settings(apps, schema_editor):
    """Reverse the default settings if needed."""
    Bird = apps.get_model('bird', 'Bird')
    
    # Reset all notification settings to False
    Bird.objects.all().update(
        melden_an_naturschutzbehoerde=False,
        melden_an_wildvogelhilfe_team=False,
        melden_an_jagdbehoerde=False
    )


class Migration(migrations.Migration):

    dependencies = [
        ('bird', '0007_add_notification_settings'),
    ]

    operations = [
        migrations.RunPython(
            set_default_notification_settings,
            reverse_default_notification_settings
        ),
    ]
