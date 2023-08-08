from django.urls import path

from .views import (
    export_birds,
    export_costs,
    site_exports,
)

urlpatterns = [
    path("", site_exports, name="site_exports"),
    path("birds/", export_birds, name="export_birds"),
    path("costs/", export_costs, name="export_costs"),
]
