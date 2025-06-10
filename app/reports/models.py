from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from sendemail.models import Emailadress


class AutomaticReport(models.Model):
    """Model for automatic report configuration."""
    name = models.CharField(
        max_length=255, 
        verbose_name=_("Name")
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_("Beschreibung")
    )
    
    # Email recipients
    email_addresses = models.ManyToManyField(
        Emailadress,
        verbose_name=_("E-Mail-Adressen"),
        help_text=_("E-Mail-Adressen, an die der Report gesendet wird")
    )
    
    # Report filters
    include_naturschutzbehoerde = models.BooleanField(
        default=True,
        verbose_name=_("Naturschutzbehörde einschließen"),
        help_text=_("Vögel einschließen, die an Naturschutzbehörde gemeldet werden")
    )
    include_jagdbehoerde = models.BooleanField(
        default=False,
        verbose_name=_("Jagdbehörde einschließen"),
        help_text=_("Vögel einschließen, die an Jagdbehörde gemeldet werden")
    )
    
    # Schedule settings
    frequency_choices = [
        ('weekly', _('Wöchentlich')),
        ('monthly', _('Monatlich')),
        ('quarterly', _('Vierteljährlich')),
    ]
    frequency = models.CharField(
        max_length=20,
        choices=frequency_choices,
        default='monthly',
        verbose_name=_("Häufigkeit")
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Aktiv")
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Erstellt von")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Erstellt am")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Aktualisiert am")
    )
    last_sent = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Zuletzt gesendet")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Automatischer Report")
        verbose_name_plural = _("Automatische Reports")
        ordering = ['-created_at']


class ReportLog(models.Model):
    """Log for generated reports."""
    
    # Link to automatic report if applicable
    automatic_report = models.ForeignKey(
        AutomaticReport,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Automatischer Report")
    )
    
    # Date range
    date_from = models.DateField(verbose_name=_("Von"))
    date_to = models.DateField(verbose_name=_("Bis"))
    
    # Filters used
    include_naturschutzbehörde = models.BooleanField(
        verbose_name=_("Naturschutzbehörde eingeschlossen")
    )
    include_jagdbehörde = models.BooleanField(
        verbose_name=_("Jagdbehörde eingeschlossen")
    )
    
    # Results
    patient_count = models.IntegerField(
        default=0,
        verbose_name=_("Anzahl Patienten")
    )
    
    # Email info - stores list of email addresses as JSON
    email_sent_to = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("E-Mail gesendet an"),
        help_text=_("Liste der E-Mail-Adressen, an die der Report gesendet wurde")
    )
    
    # CSV file storage
    csv_file = models.FileField(
        upload_to='reports/csv/',
        null=True,
        blank=True,
        verbose_name=_("CSV-Datei")
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Erstellt am")
    )

    def __str__(self):
        if self.automatic_report:
            return f"Report {self.date_from} - {self.date_to} ({self.automatic_report.name})"
        return f"Report {self.date_from} - {self.date_to} (Manuell)"

    class Meta:
        verbose_name = _("Report-Log")
        verbose_name_plural = _("Report-Logs")
        ordering = ['-created_at']
