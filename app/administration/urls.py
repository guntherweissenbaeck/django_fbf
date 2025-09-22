from django.urls import path

from . import views

app_name = "administration"

urlpatterns = [
    path("backup/", views.backup_dashboard, name="backup_dashboard"),
]
