from .views import index, privacy, impress
from django.urls import path


urlpatterns = [
    path("", index, name="index"),
    path("privacy/", privacy, name="privacy"),
    path("impress/", impress, name="impress"),
]
