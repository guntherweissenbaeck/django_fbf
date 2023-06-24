from django.urls import path

from .views import (
    rescuer_all,
    rescuer_create,
    rescuer_single,
    rescuer_delete,
    rescuer_edit,
)

urlpatterns = [
    path("all", rescuer_all, name="rescuer_all"),
    path("create", rescuer_create, name="rescuer_create"),
    path("edit/<id>", rescuer_edit, name="rescuer_edit"),
    path("delete/<id>", rescuer_delete, name="rescuer_delete"),
    path("<id>", rescuer_single, name="rescuer_single"),
]
