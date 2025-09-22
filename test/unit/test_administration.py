from unittest import mock

import pytest
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from administration.forms import BackupRestoreForm, BackupRunForm
from administration.models import BackupDestination, BackupLog, SMTPConfiguration


class BackupFormsTests(TestCase):
    def setUp(self):
        self.destination = BackupDestination.objects.create(
            name="Test SFTP",
            destination_type=BackupDestination.SFTP,
            endpoint="example.org",
        )

    def test_backup_run_form_valid(self):
        form = BackupRunForm(data={"destination": self.destination.pk})
        assert form.is_valid()

    def test_backup_restore_requires_file(self):
        form = BackupRestoreForm(data={})
        assert not form.is_valid()
        upload = SimpleUploadedFile("backup.sql", b"-- test backup --")
        form = BackupRestoreForm(files={"backup_file": upload})
        assert form.is_valid()


@pytest.mark.django_db
def test_backup_dashboard_run(monkeypatch):
    destination = BackupDestination.objects.create(
        name="WebDAV",
        destination_type=BackupDestination.WEB_DAV,
        endpoint="https://example.com/webdav/",
    )
    user = User.objects.create_superuser("admin", "admin@example.com", "pass")
    client = Client()
    client.force_login(user)

    mocked_run = mock.Mock(return_value="fbf_backup_20230914.sql")
    monkeypatch.setattr("administration.views.run_backup", mocked_run)

    response = client.post(
        reverse("administration:backup_dashboard"),
        {"destination": destination.pk, "run_backup": "1"},
        follow=True,
    )
    mocked_run.assert_called_once_with(destination)
    assert response.status_code == 200
    assert BackupLog.objects.filter(action=BackupLog.ACTION_BACKUP).exists()


@pytest.mark.django_db
def test_backup_dashboard_restore(monkeypatch):
    user = User.objects.create_superuser("admin", "admin@example.com", "pass")
    client = Client()
    client.force_login(user)

    mocked_restore = mock.Mock()
    monkeypatch.setattr("administration.views.restore_database_from_file", mocked_restore)

    uploaded = SimpleUploadedFile("restore.sql", b"-- test --")

    response = client.post(
        reverse("administration:backup_dashboard"),
        {"backup_file": uploaded, "restore_backup": "1"},
        follow=True,
    )
    assert response.status_code == 200
    mocked_restore.assert_called_once()
    assert BackupLog.objects.filter(action=BackupLog.ACTION_RESTORE).exists()


@pytest.mark.django_db
def test_smtp_configuration_applies_settings(settings):
    settings.EMAIL_HOST = "oldhost"
    config = SMTPConfiguration.objects.create(
        name="Mail",
        host="smtp.example.com",
        port=465,
        username="mailer",
        password="secret",
        use_tls=False,
        use_ssl=True,
        default_from_email="mailer@example.com",
        is_active=True,
    )
    config.refresh_from_db()
    assert SMTPConfiguration.get_active() == config
    assert settings.EMAIL_HOST == "smtp.example.com"
    assert settings.EMAIL_USE_SSL is True
    assert settings.DEFAULT_FROM_EMAIL == "mailer@example.com"
