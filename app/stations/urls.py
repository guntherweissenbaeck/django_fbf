"""! @brief URL configuration for the wild bird station map."""

from __future__ import annotations

from django.urls import path

from .views import StationDataView, StationMapView, StationReportView

app_name = "stations"

urlpatterns = [
    path("", StationMapView.as_view(), name="map"),
    path("daten/", StationDataView.as_view(), name="data"),
    path("report/", StationReportView.as_view(), name="report"),
]
