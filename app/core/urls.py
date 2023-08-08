from django.contrib import admin
from django.urls import path, include
from bird import views

urlpatterns = [
    # Dynamic sites
    path("", views.bird_all, name="index"),
    path("aviary/", include("aviary.urls")),
    path("bird/", include("bird.urls")),
    path("costs/", include("costs.urls")),
    path("export/", include("export.urls")),
    path("rescuer/", include("rescuer.urls")),
    # Admin
    path("admin/", admin.site.urls),
    # Allauth
    path("accounts/", include("allauth.urls")),
    # Static sites
    # path("", include("sites.urls")),
]
