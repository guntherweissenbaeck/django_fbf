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
    path("<id>/", bird_single, name="bird_single"),
]
