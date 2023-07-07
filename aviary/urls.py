from django.urls import path

from .views import (
    aviary_all,
    aviary_single
)

urlpatterns = [
    path("all/", aviary_all, name="aviary_all"),
    path("<id>", aviary_single, name="aviary_single"),
]
