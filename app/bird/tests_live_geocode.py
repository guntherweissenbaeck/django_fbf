import os
import time
import requests
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

LIVE_FLAG = os.getenv('RUN_LIVE_GEOCODE') == '1'

class LiveNominatimGeocodeTests(TestCase):
    """Optional Live-Tests gegen Nominatim. Werden nur ausgeführt wenn RUN_LIVE_GEOCODE=1.

    WARNUNG: Unterliegt Rate Limits. Nicht im Standard-CI aktivieren.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='live-user', password='pw')

    def setUp(self):
        self.client.force_login(self.user)

    def _skip_if_disabled(self):
        if not LIVE_FLAG:
            self.skipTest('Live Geocode Tests deaktiviert (RUN_LIVE_GEOCODE != 1)')

    def test_live_erfurt(self):
        self._skip_if_disabled()
        resp = self.client.get(reverse('bird_geocode_found_location'), {'q': 'Erfurt, Alte Synagoge'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertIn(data['city'], ['Erfurt'])

    def test_live_uniklinikum_jena(self):
        self._skip_if_disabled()
        resp = self.client.get(reverse('bird_geocode_found_location'), {'q': 'Universitätsklinikum Jena'})
        # Kann 200 oder 404 sein, abhängig von tagesaktuellen Daten
        self.assertIn(resp.status_code, [200, 404])
        if resp.status_code == 200:
            data = resp.json()
            self.assertTrue(data['success'])
            self.assertIn(data['region_name'], ['Jena', 'Thüringen'])

    def test_live_kirche_kahla(self):
        self._skip_if_disabled()
        resp = self.client.get(reverse('bird_geocode_found_location'), {'q': 'Kirche Kahla'})
        # Heuristik kann zu Stadt oder Landkreis führen
        self.assertIn(resp.status_code, [200, 404])
        if resp.status_code == 200:
            data = resp.json()
            self.assertTrue(data['success'])
            self.assertTrue(data['region_name'])

    def test_live_lutherstrasse(self):
        self._skip_if_disabled()
        resp = self.client.get(reverse('bird_geocode_found_location'), {'q': 'Lutherstraße3, Jena'})
        self.assertIn(resp.status_code, [200, 404])
        if resp.status_code == 200:
            data = resp.json()
            self.assertTrue(data['success'])
            self.assertTrue(data['region_name'])
