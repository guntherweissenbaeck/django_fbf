"""Tests für die Stationsdaten JSON View bzgl. Cache-Verhalten."""

from __future__ import annotations

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from stations.models import WildbirdHelpStation


class StationDataViewCacheTests(TestCase):
    def setUp(self) -> None:  # noqa: D401
        # Eine Beispielstation anlegen
        WildbirdHelpStation.objects.create(
            name="Test Station",
            city="Jena",
            country="Deutschland",
            approved_for_publication=True,
            latitude=50.9271,
            longitude=11.5892,
            updated_at=timezone.now(),
        )

    def test_no_cache_headers_and_etag(self):
        client = Client()
        url = reverse("stations:data")
        response = client.get(url)

        # Basis: JSON OK
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), list))

        # Cache-Control Header prüfen
        cache_control = response["Cache-Control"]
        self.assertIn("must-revalidate", cache_control)
        self.assertIn("max-age=0", cache_control)

        # ETag vorhanden
        etag = response.get("ETag")
        self.assertIsNotNone(etag)
        self.assertTrue(etag.startswith("\""))  # Anführungszeichen gemäß Spec

        # Conditional Abruf mit If-None-Match sollte 304 liefern
        response_304 = client.get(url, HTTP_IF_NONE_MATCH=etag)
        self.assertEqual(response_304.status_code, 304)
        self.assertEqual(response_304.get("ETag"), etag)
