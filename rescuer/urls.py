from django.urls import path

from .views import rescuer_single, rescuer_all

urlpatterns = [
    path("all", rescuer_all, name="rescuer_all"),
    path("<id>", rescuer_single, name="rescuer_single"),
]
