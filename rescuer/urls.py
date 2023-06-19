from django.urls import path

from .views import rescuer_all, rescuer_create, rescuer_single

urlpatterns = [
    path("all", rescuer_all, name="rescuer_all"),
    path("create", rescuer_create, name="rescuer_create"),
    path("<id>", rescuer_single, name="rescuer_single"),
]
