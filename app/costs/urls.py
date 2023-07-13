from django.urls import path

from .views import (
    costs_all,
    costs_create,
    costs_edit,
    costs_delete,
)

urlpatterns = [
    path("all/", costs_all, name="costs_all"),
    path("create/", costs_create, name="costs_create"),
    path("edit/<id>", costs_edit, name="costs_edit"),
    path("delete/<id>", costs_delete, name="costs_delete"),
]
