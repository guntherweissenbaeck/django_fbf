from __future__ import annotations

from typing import Optional
import warnings

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone


class BackupDestination(models.Model):
    WEB_DAV = "webdav"
    SFTP = "sftp"

    DESTINATION_CHOICES = [
        (WEB_DAV, "WebDAV"),
        (SFTP, "SFTP"),
    ]

    name = models.CharField(max_length=150, unique=True)
    destination_type = models.CharField(max_length=10, choices=DESTINATION_CHOICES)
    endpoint = models.CharField(
        max_length=255,
        help_text="Für WebDAV die Basis-URL (z. B. https://example.org/webdav/), für SFTP den Hostnamen (z. B. backup.example.org).",
    )
    port = models.PositiveIntegerField(
        default=0,
        help_text="Port des Ziels. WebDAV verwendet Standard 443/80, SFTP Standard 22. Belassen Sie 0 für Standardports.",
    )
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    remote_path = models.CharField(
        max_length=255,
        blank=True,
        help_text="Zielpfad oder Verzeichnis auf dem Server.",
    )
    use_ssl = models.BooleanField(default=True, help_text="Nur für WebDAV relevant.")
    verify_ssl = models.BooleanField(default=True, help_text="SSL-Zertifikate prüfen (WebDAV).")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Backup-Ziel"
        verbose_name_plural = "Backup-Ziele"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.get_destination_type_display()} – {self.name}"

    def get_display_endpoint(self) -> str:
        if self.destination_type == self.SFTP and self.port:
            return f"{self.endpoint}:{self.port}"
        return self.endpoint


class BackupLog(models.Model):
    ACTION_BACKUP = "backup"
    ACTION_RESTORE = "restore"
    STATUS_SUCCESS = "success"
    STATUS_FAILURE = "failure"

    ACTION_CHOICES = [
        (ACTION_BACKUP, "Backup"),
        (ACTION_RESTORE, "Restore"),
    ]
    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Erfolgreich"),
        (STATUS_FAILURE, "Fehlgeschlagen"),
    ]

    destination = models.ForeignKey(
        BackupDestination,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    message = models.TextField(blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Backup-Protokoll"
        verbose_name_plural = "Backup-Protokolle"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_action_display()} – {self.get_status_display()} – {timezone.localtime(self.created_at):%d.%m.%Y %H:%M}"


class SMTPConfiguration(models.Model):
    name = models.CharField(max_length=150, unique=True)
    email_backend = models.CharField(
        max_length=255,
        default="django.core.mail.backends.smtp.EmailBackend",
        help_text="Python-Importpfad des E-Mail-Backends.",
    )
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=587)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    default_from_email = models.EmailField(blank=True)
    timeout = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Timeout in Sekunden.",
    )
    is_active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "SMTP-Konfiguration"
        verbose_name_plural = "SMTP-Konfigurationen"
        ordering = ["-is_active", "name"]

    def __str__(self) -> str:
        marker = " (aktiv)" if self.is_active else ""
        return f"{self.name}{marker}"

    def clean(self):
        super().clean()
        if self.use_tls and self.use_ssl:
            raise ValidationError("TLS und SSL können nicht gleichzeitig aktiviert werden.")

    def save(self, *args, **kwargs):
        if not self.password and self.pk:
            existing = SMTPConfiguration.objects.filter(pk=self.pk).first()
            if existing:
                self.password = existing.password

        super().save(*args, **kwargs)

        if self.is_active:
            SMTPConfiguration.objects.exclude(pk=self.pk).update(is_active=False)
        elif not SMTPConfiguration.objects.exclude(pk=self.pk).filter(is_active=True).exists():
            SMTPConfiguration.objects.filter(pk=self.pk).update(is_active=True)
            self.is_active = True

        if self.is_active:
            self.apply_to_settings()

    def apply_to_settings(self):
        settings.EMAIL_BACKEND = self.email_backend
        settings.EMAIL_HOST = self.host
        settings.EMAIL_PORT = self.port
        settings.EMAIL_HOST_USER = self.username
        settings.EMAIL_HOST_PASSWORD = self.password
        settings.EMAIL_USE_TLS = self.use_tls
        settings.EMAIL_USE_SSL = self.use_ssl
        if self.timeout is not None:
            settings.EMAIL_TIMEOUT = self.timeout
        if self.default_from_email:
            settings.DEFAULT_FROM_EMAIL = self.default_from_email
        elif self.username:
            settings.DEFAULT_FROM_EMAIL = self.username

    @classmethod
    def apply_active_configuration(cls):
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    category=RuntimeWarning,
                    message="Accessing the database during app initialization is discouraged.",
                )
                active: Optional[SMTPConfiguration] = cls.objects.filter(is_active=True).first()
        except (OperationalError, ProgrammingError):  # Database table not ready yet
            return
        if active:
            active.apply_to_settings()

    @classmethod
    def get_active(cls) -> Optional[SMTPConfiguration]:
        return cls.objects.filter(is_active=True).first()
