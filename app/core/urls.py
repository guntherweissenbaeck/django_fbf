from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from bird import views
from core import views as core_views

urlpatterns = [
    # Dynamic sites
    path("", views.bird_all, name="index"),
    path("aviary/", include("aviary.urls")),
    path("bird/", include("bird.urls")),
    path("contacts/", include("contact.urls")),
    path("costs/", include("costs.urls")),
    path("stationen/", include("stations.urls", namespace="stations")),
    path("statistics/", include("statistic.urls")),
    path("export/", include("export.urls")),
    path("notizen/", include("notizen.urls")),
    # PWA support
    path("manifest.webmanifest", core_views.ManifestView.as_view(), name="pwa_manifest"),
    path("service-worker.js", core_views.ServiceWorkerView.as_view(), name="pwa_service_worker"),
    path("pwa/offline/", core_views.PWAOfflineView.as_view(), name="pwa_offline"),
    path("pwa/install/", core_views.PWAInstallView.as_view(), name="pwa_install"),
    path("ping/", core_views.PingView.as_view(), name="ping"),
    # Admin
    path("admin/administration/", include("administration.urls")),
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
