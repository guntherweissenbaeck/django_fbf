"""Core views for auxiliary endpoints such as PWA assets and static pages."""

from __future__ import annotations

import json
from typing import Any

from django.http import HttpResponse
from django.templatetags.static import static
from django.urls import reverse
from django.views.generic import TemplateView


class ManifestView(TemplateView):
    """Serve the web app manifest from the application root."""

    template_name = "pwa/manifest.webmanifest"
    content_type = "application/manifest+json"

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        response = super().render_to_response(context, **response_kwargs)
        response["Cache-Control"] = "no-cache"
        return response


class ServiceWorkerView(TemplateView):
    """Serve a templated service worker with the correct asset URLs."""

    template_name = "pwa/service-worker.js"
    content_type = "application/javascript"

    cache_name = "fbf-pwa-v1"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        precache_urls = [
            reverse("account_login"),
            reverse("pwa_offline"),
            static("css/style.css"),
            static("css/login.css"),
            static("img/logo/wvh.svg"),
            static("img/appicon/appiconfbf.png"),
            "https://bootswatch.com/5/cosmo/bootstrap.min.css",
        ]

        context.update(
            {
                "cache_name": self.cache_name,
                "offline_url": reverse("pwa_offline"),
                "precache_urls": json.dumps(sorted(set(precache_urls))),
            }
        )
        return context

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        response = super().render_to_response(context, **response_kwargs)
        response["Cache-Control"] = "no-cache"
        response["Service-Worker-Allowed"] = "/"
        return response


class PWAInstallView(TemplateView):
    """Static documentation page explaining how to install the PWA."""

    template_name = "pwa/install.html"


class PWAOfflineView(TemplateView):
    """Fallback page displayed when the application is offline."""

    template_name = "pwa/offline.html"


class PingView(TemplateView):
    """Lightweight connectivity probe returning 200 and JSON body.

    Service Worker kann diesen Endpoint regelmäßig abrufen um echte Offline-Situationen
    von Cache- oder Netzwerkfehlern zu unterscheiden.
    """
    def get(self, request, *args, **kwargs):  # pragma: no cover - trivial
        return HttpResponse('{"ok": true}', content_type='application/json')
