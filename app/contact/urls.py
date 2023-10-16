from django.urls import path

from .views import contact_all

urlpatterns = [
    path("", contact_all, name="contact_all"),
]
