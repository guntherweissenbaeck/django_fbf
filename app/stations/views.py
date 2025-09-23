"""! @brief Public views serving the Wildvogelhilfe station map."""

from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
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
    """! @brief Return the station dataset as JSON for the front-end map."""

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        """! @brief Serialize approved stations and expose them as JSON.

        :returns: JSON response containing all map marker payloads.
        """

        stations = (
            WildbirdHelpStation.objects.filter(approved_for_publication=True)
            .order_by("country", "state", "name")
        )
        payload = [station.to_map_payload() for station in stations]
        return JsonResponse(payload, safe=False)


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
