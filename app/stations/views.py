"""! @brief Public views serving the Wildvogelhilfe station map."""

from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.http import (
    HttpRequest,
    HttpResponseRedirect,
    JsonResponse,
    HttpResponse,
)
from django.utils.http import http_date
import hashlib
from django.db.models import Max
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, View
from django.views.generic.edit import CreateView

from .forms import StationReportForm
from .models import WildbirdHelpStation
from .services import notify_new_station_report


class StationMapView(TemplateView):
    """! @brief Render the Leaflet based station overview."""

    template_name = "stations/map.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """! @brief Provide template context including station metrics.

        :returns: Base context enriched with the total count of visible stations.
        """

        context = super().get_context_data(**kwargs)
        queryset = WildbirdHelpStation.objects.filter(approved_for_publication=True)
        context.update(
            {
                "station_count": queryset.count(),
                "data_url": reverse("stations:data"),
            }
        )
        return context


class StationDataView(View):
    """! @brief Liefert Stationsdaten mit Conditional GET Unterstützung.

    Strategie:
    - ETag basiert auf (max(updated_at), Anzahl) für schnelle Ungleichheitsprüfung.
    - Cache-Control erlaubt Revalidation (kein Blind-Caching alter Daten).
    - 304 Responses enthalten konsistente Header.
    """

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        qs = (
            WildbirdHelpStation.objects.filter(approved_for_publication=True)
            .order_by("country", "state", "name")
        )

        agg = qs.aggregate(last=Max("updated_at"))
        last_modified = agg.get("last")
        etag_source = f"{last_modified.isoformat() if last_modified else 'no-ts'}:{qs.count()}".encode("utf-8")
        try:
            etag = hashlib.md5(etag_source, usedforsecurity=False).hexdigest()  # type: ignore[arg-type]
        except TypeError:
            etag = hashlib.md5(etag_source).hexdigest()

        inm = request.headers.get("If-None-Match")
        if inm and inm.strip('"') == etag:
            resp_304 = HttpResponse(status=304)
            resp_304["ETag"] = f'"{etag}"'
            resp_304["Cache-Control"] = "public, max-age=0, must-revalidate"
            if last_modified:
                resp_304["Last-Modified"] = http_date(last_modified.timestamp())
            return resp_304

        payload = [obj.to_map_payload() for obj in qs]
        resp = JsonResponse(payload, safe=False)
        resp["Cache-Control"] = "public, max-age=0, must-revalidate"
        resp["ETag"] = f'"{etag}"'
        if last_modified:
            resp["Last-Modified"] = http_date(last_modified.timestamp())
        return resp


class StationReportView(CreateView):
    """! @brief Public form endpoint for proposing new stations."""

    template_name = "stations/report_form.html"
    form_class = StationReportForm
    success_url = reverse_lazy("stations:report")

    def form_valid(self, form: StationReportForm) -> HttpResponseRedirect:
        """! @brief Persist the suggestion and send optional notifications."""

        self.object = form.save()
        notify_new_station_report(self.object)
        messages.success(
            self.request,
            _("Vielen Dank! Wir prüfen den Vorschlag zeitnah."),
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self) -> dict[str, Any]:
        """! @brief Provide sensible defaults for the form."""

        initial = super().get_initial()
        initial.setdefault("country", "Deutschland")
        return initial
