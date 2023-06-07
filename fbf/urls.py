from django.urls import path

from .views import (
    bird_create,
    bird_all,
    bird_single,
    bird_delete,
    bird_recover,
    bird_recover_all,
)

urlpatterns = [
    path("create/", bird_create, name="bird_create"),
    path("delete/<id>", bird_delete, name="bird_delete"),
    path("recover/all", bird_recover_all, name="bird_recover_all"),
    path("recover/<id>", bird_recover, name="bird_recover"),
    path("all/", bird_all, name="bird_all"),
    path("<id>/", bird_single, name="bird_single"),
]
