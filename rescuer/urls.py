from django.urls import path

from .views import rescuer_single

urlpatterns = [path("<id>", rescuer_single, name="rescuer_single")]
