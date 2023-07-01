from django.urls import path

from .views import (
    aviary_all
)

urlpatterns = [
    path("all/", aviary_all, name="aviary_all"),
]
