from django.urls import path

from .views import bird_create, bird_all, bird_single

urlpatterns = [
    path("create/", bird_create, name="fallen_bird_create"),
    path("all/", bird_all, name="fallen_bird_all"),
    path("<id>/", bird_single, name="fallen_bird_single"),
]
