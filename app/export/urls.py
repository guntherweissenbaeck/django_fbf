from django.urls import path

from .views import (
    export_birds,
    export_birds_all, 
    export_birds_custom,
    site_exports,
)

urlpatterns = [
    path("", site_exports, name="site_exports"),
    path("birds/", export_birds, name="export_birds"),  # Legacy compatibility
    path("birds/all/", export_birds_all, name="export_birds_all"),
    path("birds/custom/", export_birds_custom, name="export_birds_custom"),
]
