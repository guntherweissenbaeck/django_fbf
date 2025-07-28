from datetime import date
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_ckeditor_5.fields import CKEditor5Field

from aviary.models import Aviary


CHOICE_AGE = [
    ("unbekannt", "unbekannt"),
    ("Ei", "Ei"),
    ("Nestling", "Nestling"),
    ("Ästling", "Ästling"),
    ("Juvenil", "Juvenil"),
    ("Adult", "Adult"),
]

CHOICE_SEX = [
    ("Weiblich", "Weiblich"),
    ("Männlich", "Männlich"),
    ("Unbekannt", "Unbekannt"),
]


def costs_default():
    return [{"date": date.today().strftime("%Y-%m-%d"), "cost_entry": "0.00"}]


class FallenBird(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    bird_identifier = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_("Patienten Alias")
    )
    bird = models.ForeignKey(
        "Bird", on_delete=models.CASCADE, verbose_name=_("Vogel")
    )
    age = models.CharField(
        max_length=15, choices=CHOICE_AGE, blank=True, null=True, verbose_name=_("Alter")
    )
    sex = models.CharField(
        max_length=15, choices=CHOICE_SEX, blank=True, null=True, verbose_name=_("Geschlecht")
    )
    date_found = models.DateField(blank=True, null=True, verbose_name=_("Datum des Fundes"))
    place = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("Ort des Fundes"))
    # Fields expected by tests for deceased birds
    death_date = models.DateField(blank=True, null=True, verbose_name=_("Todesdatum"))
    cause_of_death = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_("Todesursache")
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notizen"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Erstellt von"),
        related_name="fallen_birds_created"
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("angelegt am")
    )
    updated = models.DateTimeField(
        auto_now=True, verbose_name=_("geändert am")
    )
    find_circumstances = models.ForeignKey(
        "Circumstance",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Fundumstände"),
    )
    diagnostic_finding = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_("Diagnose bei Fund")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Benutzer"),
        related_name="fallen_birds_handled"
    )
    status = models.ForeignKey(
        "BirdStatus", 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        default=1,
        verbose_name=_("Status")
    )
    aviary = models.ForeignKey(
        Aviary,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Voliere"),
    )
    sent_to = models.CharField(
        max_length=256, null=True, blank=True, verbose_name=_("Übermittelt nach")
    )
    release_location = models.CharField(
        max_length=256, null=True, blank=True, verbose_name=_("Auswilderungsort")
    )
    patient_file_close_date = models.DateField(
        null=True, blank=True, verbose_name=_("Patientenakte geschlossen am")
    )
    comment = models.TextField(
        blank=True, null=True, verbose_name=_("Bemerkung")
    )
    finder = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Finder"),
        default="Vorname: \nNachname: \nStraße: \nHausnummer: \nStadt: \nPLZ: \nTelefonnummer: ",
    )

    class Meta:
        verbose_name = _("Gefallener Vogel")
        verbose_name_plural = _("Gefallene Vögel")

    def save(self, *args, **kwargs):
        """Override save to automatically set patient_file_close_date when status changes to closed states."""
        # Define status IDs that should close the patient file
        CLOSED_STATUS_IDS = [3, 4, 5]  # Ausgewildert, Übermittelt, Verstorben
        
        # Check if this is an update (not a new instance)
        if self.pk:
            try:
                # Get the old instance from database
                old_instance = FallenBird.objects.get(pk=self.pk)
                
                # Check if status changed to a closed status and file_close_date is not set
                if (self.status_id in CLOSED_STATUS_IDS and 
                    old_instance.status_id != self.status_id and 
                    not self.patient_file_close_date):
                    
                    self.patient_file_close_date = date.today()
                    
            except FallenBird.DoesNotExist:
                # This shouldn't happen in normal circumstances, but handle gracefully
                pass
        
        super().save(*args, **kwargs)

    def __str__(self):
        bird_name = str(self.bird) if self.bird else "Unbekannt"
        return f"Patient: {bird_name}"


class Bird(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(
        max_length=256, unique=True, verbose_name=_("Bezeichnung")
    )
    description = CKEditor5Field(verbose_name=_("Erläuterungen"), blank=True, null=True)
    species = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_("Art")
    )
    age_group = models.CharField(
        max_length=15, choices=CHOICE_AGE, blank=True, null=True, verbose_name=_("Alter")
    )
    gender = models.CharField(
        max_length=15, choices=CHOICE_SEX, blank=True, null=True, verbose_name=_("Geschlecht")
    )
    weight = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True, verbose_name=_("Gewicht")
    )
    wing_span = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True, verbose_name=_("Flügelspannweite")
    )
    found_date = models.DateField(
        blank=True, null=True, verbose_name=_("Datum des Fundes")
    )
    found_location = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_("Fundort")
    )
    finder_name = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_("Finder Name")
    )
    finder_phone = models.CharField(
        max_length=50, blank=True, null=True, verbose_name=_("Finder Telefon")
    )
    finder_email = models.EmailField(
        blank=True, null=True, verbose_name=_("Finder Email")
    )
    aviary = models.ForeignKey(
        Aviary,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Voliere"),
    )
    status = models.ForeignKey(
        "BirdStatus", 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        verbose_name=_("Status")
    )
    circumstance = models.ForeignKey(
        "Circumstance",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Fundumstände"),
    )
    notes = models.TextField(
        blank=True, null=True, verbose_name=_("Notizen")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Erstellt von"),
    )
    created = models.DateTimeField(
        auto_now_add=True, blank=True, null=True, verbose_name=_("Erstellt am")
    )
    updated = models.DateTimeField(
        auto_now=True, verbose_name=_("Geändert am")
    )
    
    # New notification settings fields - "Melden an" section
    melden_an_naturschutzbehoerde = models.BooleanField(
        default=True,
        verbose_name=_("Melden an Naturschutzbehörde")
    )
    melden_an_jagdbehoerde = models.BooleanField(
        default=False,
        verbose_name=_("Melden an Jagdbehörde")
    )
    melden_an_wildvogelhilfe_team = models.BooleanField(
        default=True,
        verbose_name=_("Melden an Wildvogelhilfe-Team")
    )

    class Meta:
        verbose_name = _("Vogel")
        verbose_name_plural = _("Vögel")
        ordering = ["name"]

    def __str__(self):
        return self.name or f"Bird {self.id}"


class BirdStatus(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(
        max_length=256, null=True, blank=True, verbose_name=_("Name")
    )
    description = models.CharField(
        max_length=256, unique=True, verbose_name=_("Bezeichnung")
    )

    class Meta:
        verbose_name = _("Patientenstatus")
        verbose_name_plural = _("Patientenstatus")

    def __str__(self):
        return self.name or self.description or f"BirdStatus {self.id}"


class Circumstance(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(
        max_length=256, null=True, blank=True, verbose_name=_("Name")
    )
    description = models.CharField(
        max_length=256, verbose_name=_("Bezeichnung")
    )

    class Meta:
        verbose_name = _("Fundumstand")
        verbose_name_plural = _("Fundumstände")

    def __str__(self) -> str:
        return self.name or self.description or f"Circumstance {self.id}"
