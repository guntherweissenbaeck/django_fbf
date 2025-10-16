from django.urls import path

from .views import (
    bird_all,
    bird_create,
    bird_delete,
    bird_help,
    bird_help_single,
    bird_inactive,
    bird_single,
    bird_species_list,
    bird_species_edit,
    geocode_found_location,
    region_backfill_start,
    region_backfill_progress,
    region_backfill_abort,
)

urlpatterns = [
    path("all/", bird_all, name="bird_all"),
    path("inactive/", bird_inactive, name="bird_inactive"),
    path("create/", bird_create, name="bird_create"),
    path("delete/<id>", bird_delete, name="bird_delete"),
    path("help/", bird_help, name="bird_help"),
    path("help/<id>", bird_help_single, name="bird_help_single"),
    path("species/", bird_species_list, name="bird_species_list"),
    path("species/<id>/edit/", bird_species_edit, name="bird_species_edit"),
    # Geocode endpoint muss vor den generischen PK-Patterns stehen, sonst fängt UUID Pattern ggf. den String ab.
    path("geocode-found-location/", geocode_found_location, name="bird_geocode_found_location"),
    path("region-backfill/start/", region_backfill_start, name="bird_region_backfill_start"),
    path("region-backfill/progress/", region_backfill_progress, name="bird_region_backfill_progress"),
    path("region-backfill/abort/", region_backfill_abort, name="region_backfill_abort"),
    # UUID Patienten (aktuelle DB nutzt UUID Primary Key)
    path("<uuid:id>/", bird_single, name="bird_single"),
    # Fallback für ältere int IDs (falls historisch vorhanden)
    path("<int:id>/", bird_single, name="bird_single_int"),
]
