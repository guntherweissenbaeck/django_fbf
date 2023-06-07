from django.urls import path

from .views import bird_create, bird_all, bird_single

urlpatterns = [
    path("create/", bird_create, name="bird_create"),
    path("all/", bird_all, name="bird_all"),
    path("<id>/", bird_single, name="bird_single"),
]
