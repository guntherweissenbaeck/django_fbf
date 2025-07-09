from django.db import models
from django.utils.translation import gettext_lazy as _
from bird.models import BirdStatus


class StatisticIndividual(models.Model):
    """
    Definiert Gruppierungen von BirdStatus für die Statistik-Anzeige der Vogelarten.
    Ermöglicht die flexible Konfiguration der Balkendiagramm-Kategorien.
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("Gruppenname"),
        help_text=_("Name der Gruppe (z.B. 'Gerettet', 'Verstorben')")
    )
    
    color = models.CharField(
        max_length=7,
        default="#28a745",
        verbose_name=_("Farbe"),
        help_text=_("Hex-Farbcode (z.B. #28a745 für Grün)")
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Reihenfolge"),
        help_text=_("Bestimmt die Reihenfolge der Gruppen in den Balkendiagrammen")
    )
    
    status_list = models.ManyToManyField(
        BirdStatus,
        verbose_name=_("Status"),
        help_text=_("Welche Status gehören zu dieser Gruppe?")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Aktiv"),
        help_text=_("Soll diese Gruppe in der Statistik angezeigt werden?")
    )
    
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Erstellt am"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Geändert am"))

    class Meta:
        verbose_name = _("Statistik-Individuum")
        verbose_name_plural = _("Statistik-Individuen")
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_status_names()})"
    
    def get_status_names(self):
        """Gibt eine kommaseparierte Liste der Status-Namen zurück."""
        return ", ".join(self.status_list.values_list('description', flat=True))
    
    def get_css_color(self):
        """Gibt die CSS-Farbe für die Anzeige zurück."""
        return self.color


class StatisticYearGroup(models.Model):
    """
    Definiert Gruppierungen von BirdStatus für die Jahres-Übersichtskarten.
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("Gruppenname"),
        help_text=_("Name der Gruppe für die Jahresstatistik")
    )
    
    color = models.CharField(
        max_length=7,
        default="#007bff",
        verbose_name=_("Farbe"),
        help_text=_("Hex-Farbcode für die Anzeige")
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Reihenfolge"),
        help_text=_("Bestimmt die Reihenfolge der Karten in der Jahresübersicht")
    )
    
    status_list = models.ManyToManyField(
        BirdStatus,
        verbose_name=_("Status"),
        help_text=_("Welche Status gehören zu dieser Jahresgruppe?")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Aktiv"),
        help_text=_("Soll diese Gruppe in der Jahresstatistik angezeigt werden?")
    )
    
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Erstellt am"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Geändert am"))

    class Meta:
        verbose_name = _("Statistik-Jahr Gruppe")
        verbose_name_plural = _("Statistik-Jahr")
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_status_names()})"
    
    def get_status_names(self):
        """Gibt eine kommaseparierte Liste der Status-Namen zurück."""
        return ", ".join(self.status_list.values_list('description', flat=True))


class StatisticTotalGroup(models.Model):
    """
    Definiert Gruppierungen von BirdStatus für die Gesamt-Übersichtskarten.
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("Gruppenname"),
        help_text=_("Name der Gruppe für die Gesamtstatistik")
    )
    
    color = models.CharField(
        max_length=7,
        default="#28a745",
        verbose_name=_("Farbe"),
        help_text=_("Hex-Farbcode für die Anzeige")
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Reihenfolge"),
        help_text=_("Bestimmt die Reihenfolge der Karten in der Gesamtübersicht")
    )
    
    status_list = models.ManyToManyField(
        BirdStatus,
        verbose_name=_("Status"),
        help_text=_("Welche Status gehören zu dieser Gesamtgruppe?")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Aktiv"),
        help_text=_("Soll diese Gruppe in der Gesamtstatistik angezeigt werden?")
    )
    
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Erstellt am"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Geändert am"))

    class Meta:
        verbose_name = _("Statistik-Insgesamt Gruppe")
        verbose_name_plural = _("Statistik-Insgesamt")
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_status_names()})"
    
    def get_status_names(self):
        """Gibt eine kommaseparierte Liste der Status-Namen zurück."""
        return ", ".join(self.status_list.values_list('description', flat=True))


class StatisticConfiguration(models.Model):
    """
    Globale Konfiguration für die Statistik-Anzeige.
    """
    # Jahresstatistik Einstellungen
    show_year_total_patients = models.BooleanField(
        default=True,
        verbose_name=_("Gesamtanzahl Patienten dieses Jahr anzeigen"),
        help_text=_("Zeigt die Gesamtanzahl aller aufgenommenen Patienten des aktuellen Jahres")
    )
    
    # Gesamtstatistik Einstellungen  
    show_total_patients = models.BooleanField(
        default=True,
        verbose_name=_("Gesamtanzahl aller Patienten anzeigen"),
        help_text=_("Zeigt die Gesamtanzahl aller Patienten seit Beginn der Aufzeichnungen")
    )
    
    # Weitere Anzeige-Optionen
    show_percentages = models.BooleanField(
        default=True,
        verbose_name=_("Prozentangaben anzeigen"),
        help_text=_("Sollen Prozentangaben in den Balkendiagrammen angezeigt werden?")
    )
    
    show_absolute_numbers = models.BooleanField(
        default=True,
        verbose_name=_("Absolute Zahlen anzeigen"),
        help_text=_("Sollen absolute Zahlen in den Balkendiagrammen angezeigt werden?")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Aktive Konfiguration"),
        help_text=_("Nur eine Konfiguration kann gleichzeitig aktiv sein")
    )
    
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Erstellt am"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Geändert am"))

    class Meta:
        verbose_name = _("Statistik-Konfiguration")
        verbose_name_plural = _("Statistik-Konfiguration")

    def __str__(self):
        return "Statistik Konfiguration"
    
    def save(self, *args, **kwargs):
        # Stelle sicher, dass nur eine Konfiguration aktiv ist
        if self.is_active:
            StatisticConfiguration.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


# Backward Compatibility Alias (temporär für Migration)
StatisticGroup = StatisticIndividual
