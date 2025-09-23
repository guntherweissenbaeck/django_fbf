"""! @brief Django admin integration for Wildvogelhilfe stations."""

from __future__ import annotations

import csv
from datetime import datetime
from typing import Any

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .forms import StationCSVImportForm, StationReportSettingsForm
from .models import StationReport, WildbirdHelpStation
from .services import (
    StationCSVImporter,
    batch_update_coordinates,
    get_report_settings,
    mark_reports,
    update_station_coordinates,
)


@admin.register(WildbirdHelpStation)
class WildbirdHelpStationAdmin(admin.ModelAdmin):
    """! @brief Configure list display, import and export for stations."""

    change_list_template = "admin/stations/wildbirdhelpstation/change_list.html"
    change_form_template = "admin/stations/wildbirdhelpstation/change_form.html"

    list_display = (
        "name",
        "city",
        "state",
        "country",
        "status",
        "approved_for_publication",
        "officially_authorised",
    )
    list_filter = (
        "country",
        "state",
        "approved_for_publication",
        "officially_authorised",
        "status",
    )
    search_fields = ("name", "city", "postal_code", "contact", "phone", "email")
    ordering = ("country", "state", "name")
    actions = ("export_as_csv", "geocode_coordinates")

    def get_urls(self) -> list[Any]:
        """! @brief Add a custom URL for the CSV import view."""

        urls = super().get_urls()
        custom_urls = [
            path(
                "import-csv/",
                self.admin_site.admin_view(self.import_csv_view),
                name="stations_wildbirdhelpstation_import",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request: HttpRequest, extra_context: dict[str, Any] | None = None) -> HttpResponse:
        """! @brief Inject CSV import form into the change list template."""

        extra_context = extra_context or {}
        extra_context.setdefault("import_form", StationCSVImportForm())
        extra_context.setdefault(
            "import_action",
            reverse("admin:stations_wildbirdhelpstation_import"),
        )
        return super().changelist_view(request, extra_context=extra_context)

    def import_csv_view(self, request: HttpRequest) -> HttpResponse:
        """! @brief Handle CSV uploads and provide user feedback."""

        if request.method == "POST":
            form = StationCSVImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data["csv_file"]
                update_existing = form.cleaned_data["update_existing"]
                result = StationCSVImporter.import_file(
                    csv_file,
                    update_existing=update_existing,
                )

                if result.errors:
                    for error in result.errors:
                        messages.warning(request, error)

                messages.success(request, result.as_message())
                changelist_url = reverse("admin:stations_wildbirdhelpstation_changelist")
                return redirect(changelist_url)
        else:
            form = StationCSVImportForm()

        context = {
            "form": form,
            "title": _("Wildvogelhilfen per CSV importieren"),
            "opts": self.model._meta,
            "original": None,
        }
        return TemplateResponse(
            request,
            "admin/stations/wildbirdhelpstation/import_form.html",
            context,
        )

    @admin.action(description=_("Auswahl als CSV exportieren"))
    def export_as_csv(self, request: HttpRequest, queryset: QuerySet[WildbirdHelpStation]) -> HttpResponse:
        """! @brief Export the selected stations as semicolon-separated CSV."""

        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        filename = f"wildvogelhilfen-{timestamp}.csv"
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={filename}"

        writer = csv.writer(response, delimiter=";")

        header = [
            "officially_authorised",
            "notes",
            "checked",
            "approved_for_publication",
            "name",
            "specialization",
            "address",
            "phone",
            "phone2",
            "contact",
            "plz",
            "plz_prefix",
            "city",
            "street",
            "region",
            "state",
            "country",
            "latitude",
            "longitude",
            "note",
            "website",
            "email",
            "status",
        ]
        writer.writerow(header)

        for station in queryset.order_by("country", "state", "name"):
            writer.writerow(
                [
                    "yes" if station.officially_authorised else "no",
                    station.notes,
                    station.checked_until.isoformat() if station.checked_until else "",
                    "ja" if station.approved_for_publication else "nein",
                    station.name,
                    station.specialization,
                    station.address,
                    station.phone,
                    station.phone_secondary,
                    station.contact,
                    station.postal_code,
                    station.postal_code_prefix,
                    station.city,
                    station.street,
                    station.region,
                    station.state,
                    station.country,
                    f"{station.latitude}" if station.latitude is not None else "",
                    f"{station.longitude}" if station.longitude is not None else "",
                    station.note,
                    station.website,
                    station.email,
                    station.status,
                ]
            )

        return response

    @admin.action(description=_("Koordinaten automatisch ermitteln"))
    def geocode_coordinates(self, request: HttpRequest, queryset: QuerySet[WildbirdHelpStation]) -> None:
        """! @brief Batch geocode selected stations."""

        successes, errors = batch_update_coordinates(list(queryset))

        if successes:
            messages.success(
                request,
                _("Koordinaten aktualisiert für %(count)s Station(en).")
                % {"count": successes},
            )

        for error in errors:
            messages.warning(request, error)

    def response_change(self, request: HttpRequest, obj: WildbirdHelpStation) -> HttpResponse:
        """! @brief Handle geocoding button on the change form."""

        if "_geocode" in request.POST:
            success, message = update_station_coordinates(obj)
            if success:
                self.message_user(
                    request,
                    _("Koordinaten erfolgreich aktualisiert."),
                    messages.SUCCESS,
                )
            else:
                self.message_user(
                    request,
                    message or _("Koordinaten konnten nicht ermittelt werden."),
                    messages.WARNING,
                )
            return redirect(
                "admin:stations_wildbirdhelpstation_change",
                obj.pk,
            )

        return super().response_change(request, obj)


@admin.register(StationReport)
class StationReportAdmin(admin.ModelAdmin):
    """! @brief Manage submitted station proposals and notifications."""

    change_list_template = "admin/stations/reports/change_list.html"

    list_display = (
        "name",
        "city",
        "country",
        "status",
        "created_at",
        "processed_at",
        "related_station_display",
    )
    list_filter = ("status", "country", "state", "created_at")
    search_fields = (
        "name",
        "city",
        "state",
        "reporter_name",
        "reporter_email",
    )
    ordering = ("-created_at",)
    actions = ("accept_reports", "reject_reports", "reset_reports")
    readonly_fields = (
        "status",
        "processed_at",
        "processed_by",
        "related_station",
        "created_at",
        "updated_at",
    )

    def get_queryset(self, request: HttpRequest):
        """! @brief Optimize admin list queries."""

        return super().get_queryset(request).select_related("related_station", "processed_by")

    def related_station_display(self, obj: StationReport) -> str:
        """! @brief Render the associated station in the list display."""

        return str(obj.related_station) if obj.related_station else "-"

    related_station_display.short_description = _("Verknüpfte Station")

    def changelist_view(self, request: HttpRequest, extra_context: dict[str, Any] | None = None) -> HttpResponse:
        """! @brief Inject notification settings management into the list view."""

        extra_context = extra_context or {}
        settings_obj = get_report_settings()

        if request.method == "GET" and "status__exact" not in request.GET:
            mutable = request.GET._mutable
            request.GET._mutable = True
            request.GET["status__exact"] = StationReport.Status.PENDING
            request.GET._mutable = mutable
            request.META["QUERY_STRING"] = request.GET.urlencode()

        if request.method == "POST" and request.POST.get("settings_submit"):
            form = StationReportSettingsForm(request.POST, instance=settings_obj)
            if form.is_valid():
                form.save()
                messages.success(request, _("Benachrichtigungsadresse gespeichert."))
                return redirect(request.path)
            extra_context["settings_form"] = form
        else:
            extra_context.setdefault(
                "settings_form",
                StationReportSettingsForm(instance=settings_obj),
            )

        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description=_("Ausgewählte Vorschläge übernehmen"))
    def accept_reports(self, request: HttpRequest, queryset: QuerySet[StationReport]) -> None:
        """! @brief Create or update stations from the selected reports."""

        created_total = 0
        updated_total = 0

        for report in queryset:
            payload = report.to_station_payload()
            if not payload.get("name"):
                continue

            defaults = {k: v for k, v in payload.items() if k not in {"name", "city", "country"}}
            defaults.setdefault("country", report.country or "Deutschland")
            defaults.setdefault("approved_for_publication", True)
            defaults.setdefault("status", "aktiv")
            if report.reporter_name and not defaults.get("contact"):
                defaults["contact"] = report.reporter_name

            station, created = WildbirdHelpStation.objects.update_or_create(
                name=payload.get("name"),
                city=payload.get("city") or "",
                country=payload.get("country") or "Deutschland",
                defaults=defaults,
            )

            if created:
                created_total += 1
            else:
                updated_total += 1

            mark_reports(
                [report],
                status=StationReport.Status.APPROVED,
                user=request.user,
                station=station,
            )

        if created_total or updated_total:
            messages.success(
                request,
                _("Vorschläge übernommen: %(new)s neu, %(updated)s aktualisiert.")
                % {"new": created_total, "updated": updated_total},
            )
        else:
            messages.info(request, _("Es wurden keine neuen Stationen angelegt."))

    @admin.action(description=_("Ausgewählte Vorschläge ablehnen"))
    def reject_reports(self, request: HttpRequest, queryset: QuerySet[StationReport]) -> None:
        """! @brief Mark the selected reports as rejected."""

        mark_reports(list(queryset), status=StationReport.Status.REJECTED, user=request.user)
        messages.info(request, _("Vorschläge wurden als abgelehnt markiert."))

    @admin.action(description=_("Status auf offen zurücksetzen"))
    def reset_reports(self, request: HttpRequest, queryset: QuerySet[StationReport]) -> None:
        """! @brief Reopen previously processed reports for further review."""

        mark_reports(list(queryset), status=StationReport.Status.PENDING)
        messages.success(request, _("Vorschläge wurden erneut auf offen gesetzt."))
