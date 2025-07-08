from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from bird import views

urlpatterns = [
    # Dynamic sites
    path("", views.bird_all, name="index"),
    path("aviary/", include("aviary.urls")),
    path("bird/", include("bird.urls")),
    path("contacts/", include("contact.urls")),
    path("costs/", include("costs.urls")),
    path("statistics/", include("statistic.urls")),
    path("export/", include("export.urls")),
    path("notizen/", include("notizen.urls")),
    # Admin
    path("admin/", admin.site.urls),
    path("admin/reports/", include("reports.urls", namespace="reports")),
    # Allauth
    path("accounts/", include("allauth.urls")),
    # CKEditor 5
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    # Static sites
    # path("", include("sites.urls")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
