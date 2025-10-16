"""! @brief Data models powering the public Wildvogelhilfe station map."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class WildbirdHelpStation(models.Model):
    """! @brief Contact and location details for a wild bird rescue station."""

    officially_authorised = models.BooleanField(
        _("Amtlich anerkannt"),
        default=False,
        help_text=_("Markiert Stationen mit amtlicher Anerkennung."),
    )
    notes = models.TextField(
        _("Interne Notiz"),
        blank=True,
        help_text=_("Administratives Feld; wird nicht öffentlich angezeigt."),
    )
    checked_until = models.DateField(
        _("Geprüft bis"),
        blank=True,
        null=True,
        help_text=_("Datum der letzten Überprüfung der Stationsdaten."),
    )
    approved_for_publication = models.BooleanField(
        _("Für Karte freigeben"),
        default=True,
        help_text=_("Nur freigegebene Stationen erscheinen auf der öffentlichen Karte."),
    )
    name = models.CharField(_("Name"), max_length=255)
    specialization = models.TextField(
        _("Spezialisierung"),
        blank=True,
        help_text=_("Ausführliche Beschreibung der aufgenommenen Tierarten."),
    )
    address = models.TextField(
        _("Anfahrtsinformationen"),
        blank=True,
        help_text=_("Freitext für Wegbeschreibungen oder zusätzliche Hinweise."),
    )
    phone = models.CharField(_("Telefon"), max_length=64, blank=True)
    phone_secondary = models.CharField(
        _("Telefon (alternativ)"), max_length=64, blank=True, help_text=_("Optional."),
    )
    contact = models.CharField(_("Ansprechperson"), max_length=128, blank=True)
    postal_code = models.CharField(_("Postleitzahl"), max_length=20, blank=True)
    postal_code_prefix = models.CharField(_("PLZ-Region"), max_length=32, blank=True)
    city = models.CharField(_("Ort"), max_length=128, blank=True)
    street = models.CharField(_("Straße"), max_length=255, blank=True)
    region = models.CharField(_("Region"), max_length=128, blank=True)
    state = models.CharField(_("Bundesland/Kanton"), max_length=128, blank=True)
    country = models.CharField(_("Land"), max_length=128, blank=True, default="Deutschland")
    latitude = models.DecimalField(
        _("Breitengrad"), max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        _("Längengrad"), max_digits=9, decimal_places=6, blank=True, null=True
    )
    note = models.TextField(
        _("Öffentliche Hinweise"),
        blank=True,
        help_text=_("Freitext-Hinweise, die im Karten-Popup angezeigt werden."),
    )
    website = models.URLField(_("Website"), blank=True)
    email = models.EmailField(_("E-Mail"), blank=True)
    status = models.CharField(
        _("Status"),
        max_length=32,
        blank=True,
        default="aktiv",
        help_text=_("Z. B. aktiv, inaktiv oder NABU."),
    )

    created_at = models.DateTimeField(_("Erstellt am"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Aktualisiert am"), auto_now=True)

    class Meta:
        """! @brief Configure admin metadata and ordering for stations."""

        verbose_name = _("Wildvogelhilfe-Station")
        verbose_name_plural = _("Wildvogelhilfe-Stationen")
        ordering = ("name",)
        unique_together = (("name", "city", "country"),)

    def __str__(self) -> str:
        """! @brief Provide a readable representation for admin drop-downs."""

        location = ", ".join(part for part in [self.city, self.country] if part)
        return f"{self.name} ({location})" if location else self.name

    def to_map_payload(self) -> dict[str, Any]:
        """! @brief Convert this instance into a serialisable map payload.

        :returns: Dictionary consumed by the Leaflet frontend to render markers.
        """

        return {
            "name": self.name,
            "specialization": self.specialization,
            "address": self.address or self._compose_address(),
            "phone": self.phone,
            "phone2": self.phone_secondary,
            "contact": self.contact,
            "plz": self.postal_code,
            "plz_prefix": self.postal_code_prefix,
            "city": self.city,
            "street": self.street,
            "region": self.region,
            "state": self.state,
            "country": self.country,
            "latitude": self._decimal_to_float(self.latitude),
            "longitude": self._decimal_to_float(self.longitude),
            "note": self.note,
            "website": self.website,
            "email": self.email,
            "status": self.status or "aktiv",
            "officially_authorised": self.officially_authorised,
            "notes": self.notes,
            "checked": self.checked_until.isoformat() if self.checked_until else "",
            "approved_for_publication": self.approved_for_publication,
        }

    def _compose_address(self) -> str:
        """! @brief Build a display address from discrete address fields."""

        parts = [self.street, self.postal_code, self.city]
        return ", ".join(part for part in parts if part)

    @staticmethod
    def _decimal_to_float(value: Decimal | None) -> float | None:
        """! @brief Cast Decimal coordinates to floats for JSON serialisation."""

        if value is None:
            return None
        return float(value)


class StationReport(models.Model):
    """! @brief Volunteer submitted proposals for new or updated stations."""

    class Status(models.TextChoices):
        """! @brief Workflow states used to track review progress."""

        PENDING = "pending", _("Offen")
        APPROVED = "approved", _("Übernommen")
        REJECTED = "rejected", _("Abgelehnt")

    name = models.CharField(_("Stationsname"), max_length=255)
    specialization = models.TextField(_("Spezialisierung"), blank=True)
    description = models.TextField(
        _("Beschreibung"), blank=True, help_text=_("Freitext für zusätzliche Hinweise."),
    )
    address = models.TextField(_("Anfahrtsinformationen"), blank=True)
    postal_code = models.CharField(_("Postleitzahl"), max_length=20, blank=True)
    city = models.CharField(_("Ort"), max_length=128, blank=True)
    state = models.CharField(_("Bundesland/Kanton"), max_length=128, blank=True)
    country = models.CharField(
        _("Land"), max_length=128, blank=True, default="Deutschland"
    )
    latitude = models.DecimalField(
        _("Breitengrad"), max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        _("Längengrad"), max_digits=9, decimal_places=6, blank=True, null=True
    )
    website = models.URLField(_("Website"), blank=True)
    email = models.EmailField(_("E-Mail"), blank=True)
    phone = models.CharField(_("Telefon"), max_length=64, blank=True)
    note = models.TextField(_("Öffentliche Hinweise"), blank=True)
    reporter_name = models.CharField(_("Kontaktname"), max_length=128, blank=True)
    reporter_email = models.EmailField(_("Kontakt E-Mail"), blank=True)
    reporter_phone = models.CharField(_("Kontakt Telefon"), max_length=64, blank=True)

    status = models.CharField(
        _("Status"),
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    processed_at = models.DateTimeField(_("Bearbeitet am"), blank=True, null=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Bearbeitet von"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="station_reports",
    )
    related_station = models.ForeignKey(
        "stations.WildbirdHelpStation",
        verbose_name=_("Verknüpfte Station"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text=_("Wird gesetzt, wenn der Vorschlag übernommen wurde."),
    )

    created_at = models.DateTimeField(_("Eingereicht am"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Aktualisiert am"), auto_now=True)

    class Meta:
        """! @brief Metadata for sorting and admin naming."""

        verbose_name = _("Stationsvorschlag")
        verbose_name_plural = _("Stationsvorschläge")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        """! @brief Human readable representation for admin listings."""

        return f"{self.name} ({self.get_status_display()})"

    def to_station_payload(self) -> dict[str, Any]:
        """! @brief Map this report into a ``WildbirdHelpStation`` kwargs dict."""

        return {
            "name": self.name,
            "specialization": self.specialization,
            "address": self.address,
            "postal_code": self.postal_code,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "website": self.website,
            "email": self.email,
            "phone": self.phone,
            "note": self.note or self.description,
        }


class StationReportSettings(models.Model):
    """! @brief Configuration container for station report notifications."""

    notification_email = models.EmailField(
        _("Benachrichtigungsadresse"),
        blank=True,
        help_text=_("Optional: erhält E-Mails, wenn neue Vorschläge eingehen."),
    )
    updated_at = models.DateTimeField(_("Aktualisiert am"), auto_now=True)

    class Meta:
        """! @brief Limit to a single configuration row."""

        verbose_name = _("Stationsvorschlag-Einstellungen")
        verbose_name_plural = _("Stationsvorschlag-Einstellungen")

    def __str__(self) -> str:
        """! @brief Show the configured notification address in admin lists."""

        return self.notification_email or _("Keine E-Mail hinterlegt")


class StationMapSettings(models.Model):
    """! @brief Konfiguration für Hinweisblöcke der öffentlichen Stationskarte.

    Ermöglicht das (De-)Aktivieren sowie die freie Textpflege zweier Hinweisbereiche:
    1. Kopfbereich unterhalb des Seitentitels
    2. Informationspanel unterhalb der Karte

    Die Felder sind optional; leere Texte werden bei aktivierten Flags nicht angezeigt.
    """

    show_header_note = models.BooleanField(
        _("Hinweis im Kopf anzeigen"),
        default=True,
        help_text=_("Schaltet den gelben Hinweisblock direkt unter der Überschrift ein."),
    )
    header_note_text = models.TextField(
        _("Text Kopf-Hinweis"),
        blank=True,
        help_text=_("Inhalt für den oberen Hinweisblock. Unterstützt einfachen Text/HTML."),
    )
    show_info_note = models.BooleanField(
        _("Hinweis im Infopanel anzeigen"),
        default=True,
        help_text=_("Steuert den Hinweisblock im Informationsbereich unter der Karte."),
    )
    info_note_text = models.TextField(
        _("Text Infopanel-Hinweis"),
        blank=True,
        help_text=_("Inhalt für den Hinweisblock im Infopanel. Unterstützt einfachen Text/HTML."),
    )
    page_title = models.CharField(
        _("Seitentitel"),
        max_length=120,
        blank=True,
        help_text=_("Überschrift der Karten-Seite. Leer = Standard '🦅 Wildvogelhilfen – Interaktive Karte'."),
    )
    updated_at = models.DateTimeField(_("Aktualisiert am"), auto_now=True)

    class Meta:
        verbose_name = _("Stations Einstellungen")
        verbose_name_plural = _("Stations Einstellungen")

    def __str__(self) -> str:  # pragma: no cover - trivial
        # Rückgabe muss ein echter String sein, nicht der Lazy Proxy
        return str(_("Stations Karten Einstellungen"))

