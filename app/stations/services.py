"""! @brief Service helpers for importing and exporting station data."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from io import StringIO
from typing import Any, BinaryIO

from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .geocoding import geocode_station
from .models import (
    StationReport,
    StationReportSettings,
    StationMapSettings,
    WildbirdHelpStation,
)


@dataclass(slots=True)
class StationImportResult:
    """! @brief Outcome summary for a CSV import run."""

    created: int = 0
    updated: int = 0
    errors: list[str] = field(default_factory=list)

    def as_message(self) -> str:
        """! @brief Format the result for Django admin feedback messages."""

        status = _("{created} neu, {updated} aktualisiert").format(
            created=self.created,
            updated=self.updated,
        )
        if not self.errors:
            return status
        return f"{status} — {len(self.errors)} {_('Fehler')}"


class StationCSVImporter:
    """! @brief Parse and persist wild bird stations from CSV uploads."""

    delimiter = ";"

    TRUE_VALUES = {"1", "true", "ja", "yes", "y", "wahr"}

    DATE_FORMATS = ("%Y.%m.%d", "%d.%m.%Y", "%Y-%m-%d")

    FIELD_MAP = {
        "officially_authorised": "officially_authorised",
        "notes": "notes",
        "checked": "checked_until",
        "approved_for_publication": "approved_for_publication",
        "name": "name",
        "specialization": "specialization",
        "address": "address",
        "phone": "phone",
        "phone2": "phone_secondary",
        "contact": "contact",
        "plz": "postal_code",
        "plz_prefix": "postal_code_prefix",
        "city": "city",
        "street": "street",
        "region": "region",
        "state": "state",
        "country": "country",
        "latitude": "latitude",
        "longitude": "longitude",
        "note": "note",
        "website": "website",
        "email": "email",
        "status": "status",
    }

    @classmethod
    def import_file(cls, file_obj: BinaryIO, update_existing: bool = True) -> StationImportResult:
        """! @brief Import CSV content into ``WildbirdHelpStation`` records.

        :param file_obj: Raw file-like object from the Django upload handler.
        :param update_existing: Update stations that already exist in the database.
        :returns: Summary of created and updated records.
        """

        csv_bytes = file_obj.read()
        try:
            file_obj.seek(0)
        except (AttributeError, OSError):  # pragma: no cover - optional
            pass
        decoded = csv_bytes.decode("utf-8-sig")
        stream = StringIO(decoded)
        reader = csv.DictReader(stream, delimiter=cls.delimiter)

        result = StationImportResult()

        with transaction.atomic():
            for index, row in enumerate(reader, start=2):
                if not any(row.values()):
                    continue
                normalised = cls._normalise_keys(row)
                try:
                    payload = cls._map_fields(normalised)
                except ValueError as exc:
                    result.errors.append(f"Zeile {index}: {exc}")
                    continue

                unique_filter = {
                    "name": payload.pop("name"),
                    "city": payload.get("city") or "",
                    "country": payload.get("country") or "Deutschland",
                }

                if not update_existing and WildbirdHelpStation.objects.filter(**unique_filter).exists():
                    continue

                defaults = payload
                defaults.setdefault("country", "Deutschland")
                defaults["address"] = defaults.get("address") or cls._build_address(defaults)

                try:
                    station, created = WildbirdHelpStation.objects.update_or_create(
                        defaults=defaults,
                        **unique_filter,
                    )
                except Exception as exc:  # pragma: no cover - safety net for edge cases
                    result.errors.append(f"Zeile {index}: {exc}")
                    continue

                if created:
                    result.created += 1
                else:
                    result.updated += 1

        return result

    @classmethod
    def _normalise_keys(cls, row: dict[str, Any]) -> dict[str, Any]:
        """! @brief Prepare CSV keys for easier lookups."""

        return {str(key).strip().lower(): (value.strip() if isinstance(value, str) else value)
                for key, value in row.items()}

    @classmethod
    def _map_fields(cls, row: dict[str, Any]) -> dict[str, Any]:
        """! @brief Convert CSV columns into Django model fields."""

        payload: dict[str, Any] = {}
        for csv_field, model_field in cls.FIELD_MAP.items():
            value = row.get(csv_field)
            if value in (None, ""):
                continue
            if isinstance(value, str):
                value = value.strip()
            if model_field in {"latitude", "longitude"}:
                payload[model_field] = cls._parse_decimal(value)
                continue
            if model_field == "checked_until":
                payload[model_field] = cls._parse_date(value)
                continue
            if model_field in {"officially_authorised", "approved_for_publication"}:
                payload[model_field] = cls._parse_bool(value)
                continue
            if model_field == "postal_code_prefix" and isinstance(value, str):
                payload[model_field] = value[:32]
                continue
            payload[model_field] = value

        if "name" not in payload or not payload["name"]:
            raise ValueError("Stationsname fehlt")

        return payload

    @staticmethod
    def _parse_bool(value: str) -> bool:
        """! @brief Interpret common CSV boolean representations."""

        return value.strip().lower() in StationCSVImporter.TRUE_VALUES

    @staticmethod
    def _parse_decimal(value: str) -> Decimal | None:
        """! @brief Convert coordinate strings into Decimal values."""

        value = value.strip().replace(",", ".")
        if not value:
            return None
        try:
            return Decimal(value)
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(_("Ungültige Zahl: %s") % value) from exc

    @classmethod
    def _parse_date(cls, value: str) -> date | None:
        """! @brief Parse multiple date formats used in the data export."""

        clean = value.strip().rstrip(".")
        for fmt in cls.DATE_FORMATS:
            try:
                return datetime.strptime(clean, fmt).date()
            except ValueError:
                continue
        raise ValueError(_("Ungültiges Datum: %s") % value)

    @staticmethod
    def _build_address(payload: dict[str, Any]) -> str:
        """! @brief Compose a fallback address string."""

        parts = [payload.get("street"), payload.get("postal_code"), payload.get("city")]
        return ", ".join(part for part in parts if part)


def get_report_settings() -> StationReportSettings:
    """! @brief Ensure a settings row exists and return it."""

    settings_obj, _ = StationReportSettings.objects.get_or_create(pk=1)
    return settings_obj


def get_map_settings() -> StationMapSettings:
    """! @brief Ensure a map settings row exists and return it.

    Verwendet eine fixe Primärschlüssel-ID, um nur einen Datensatz zuzulassen.
    """

    obj, _ = StationMapSettings.objects.get_or_create(pk=1)
    return obj


def notify_new_station_report(report: StationReport) -> None:
    """! @brief Send an optional notification for a freshly filed report."""

    settings_obj = get_report_settings()
    if not settings_obj.notification_email:
        return

    subject = _("Neuer Wildvogelhilfe-Vorschlag: %(name)s") % {"name": report.name}
    admin_path = reverse("admin:stations_stationreport_change", args=[report.pk])

    reporter_lines = []
    if report.reporter_name:
        reporter_lines.append(f"Name: {report.reporter_name}")
    if report.reporter_email:
        reporter_lines.append(f"E-Mail: {report.reporter_email}")
    if report.reporter_phone:
        reporter_lines.append(f"Telefon: {report.reporter_phone}")

    reporter_block = "\n".join(reporter_lines) if reporter_lines else _("Keine Kontaktdaten angegeben.")

    message = "\n".join(
        [
            _("Es wurde ein neuer Vorschlag für die Wildvogelhilfen-Karte eingereicht."),
            "",
            f"Station: {report.name}",
            f"Ort: {report.city or '-'}",
            f"Land: {report.country or '-'}",
            "",
            _("Kontaktdaten der meldenden Person:"),
            reporter_block,
            "",
            _("Bearbeitung im Admin:"),
            admin_path,
        ]
    )

    from_email = getattr(django_settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")
    send_mail(
        subject,
        message,
        from_email,
        [settings_obj.notification_email],
        fail_silently=True,
    )


def mark_reports(
    queryset: list[StationReport],
    *,
    status: StationReport.Status,
    user=None,
    station: WildbirdHelpStation | None = None,
) -> None:
    """! @brief Update report workflow fields in a consistent manner."""

    now = timezone.now()
    for report in queryset:
        report.status = status
        if status == StationReport.Status.PENDING:
            report.processed_at = None
            report.processed_by = None
            report.related_station = None
        else:
            report.processed_at = now
            report.processed_by = user
            if station is not None:
                report.related_station = station
        report.save()


def update_station_coordinates(
    station: WildbirdHelpStation,
) -> tuple[bool, str | None]:
    """! @brief Resolve and persist coordinates for a single station.

    :returns: Tuple ``(success, message)`` for user feedback.
    """

    if not station.postal_code and not station.address and not station.city:
        return False, _("Keine ausreichend genaue Adresse vorhanden.")

    result = geocode_station(station)
    if not result:
        return False, _("Geocoding war nicht erfolgreich.")

    station.latitude = result.latitude
    station.longitude = result.longitude
    station.save(update_fields=["latitude", "longitude", "updated_at"])
    return True, None


def batch_update_coordinates(
    queryset: list[WildbirdHelpStation],
) -> tuple[int, list[str]]:
    """! @brief Apply coordinate lookups for multiple stations."""

    successes = 0
    errors: list[str] = []

    for station in queryset:
        ok, message = update_station_coordinates(station)
        if ok:
            successes += 1
        elif message:
            errors.append(f"{station.name}: {message}")

    return successes, errors
