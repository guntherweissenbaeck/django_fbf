from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from aviary.models import Aviary

from sendemail.models import Emailadress

from .models import Bird, BirdStatus, Circumstance, FallenBird
from .views import _collect_notification_recipients
from django.urls import reverse
from unittest import mock

import json


class BirdTestCase(TestCase):
    def setUp(self):
        self.aviary = Aviary.objects.create(
            description="Voliere 1",
            condition="Offen",
            last_ward_round="2021-01-01",
            comment="Test",
        )
        self.bird = Bird.objects.create(
            name="Vogel 1",
            species="Art 1",
            aviary=self.aviary,
            found_date="2020-01-01",
        )

    def test_bird_creation(self):
        """Test that a bird can be created successfully."""
        self.assertEqual(self.bird.name, "Vogel 1")
        self.assertEqual(self.bird.species, "Art 1")
        self.assertEqual(self.bird.aviary, self.aviary)


class CollectNotificationRecipientsTests(TestCase):
    """Tests for the helper that resolves notification recipients."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="recipient-owner",
            email="owner@example.com",
            password="dummy-pass",
        )
        self.status = BirdStatus.objects.create(description="In Behandlung")
        self.bird = Bird.objects.create(
            name="Turmfalke",
            species="Falco tinnunculus",
            status=self.status,
            melden_an_naturschutzbehoerde=True,
            melden_an_jagdbehoerde=True,
            melden_an_wildvogelhilfe_team=False,
        )

        # Matching recipients for different categories (with an intentional duplicate address).
        Emailadress.objects.create(
            email_address="naturschutz@example.com",
            user=self.user,
            is_naturschutzbehoerde=True,
            is_jagdbehoerde=False,
        )
        Emailadress.objects.create(
            email_address="jagd@example.com",
            user=self.user,
            is_naturschutzbehoerde=False,
            is_jagdbehoerde=True,
        )
        Emailadress.objects.create(
            email_address="naturschutz@example.com",
            user=self.user,
            is_naturschutzbehoerde=True,
            is_jagdbehoerde=False,
        )

    def test_recipients_are_deduplicated(self):
        recipients = _collect_notification_recipients(self.bird)
        self.assertCountEqual(
            recipients,
            ["naturschutz@example.com", "jagd@example.com"],
        )

    def test_no_recipients_when_flags_disabled(self):
        self.bird.melden_an_naturschutzbehoerde = False
        self.bird.melden_an_jagdbehoerde = False
        self.bird.save(update_fields=[
            "melden_an_naturschutzbehoerde",
            "melden_an_jagdbehoerde",
        ])

        self.assertEqual(_collect_notification_recipients(self.bird), [])


class BirdCreateViewTests(TestCase):
    """Integration tests for the bird intake view."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="intake-user",
            email="intake@example.com",
            password="strong-pass",
        )
        self.client.force_login(self.user)

        self.status_closed = BirdStatus.objects.create(description="Verstorben")
        self.circumstance = Circumstance.objects.create(
            name="Fensterkollision",
            description="Kollision mit einer Scheibe",
        )
        self.bird = Bird.objects.create(
            name="Mauersegler",
            species="Apus apus",
            status=self.status_closed,
            melden_an_naturschutzbehoerde=True,
            melden_an_jagdbehoerde=False,
            melden_an_wildvogelhilfe_team=True,
        )

        Emailadress.objects.create(
            email_address="behorde@example.com",
            user=self.user,
            is_naturschutzbehoerde=True,
            is_wildvogelhilfe_team=False,
        )
        Emailadress.objects.create(
            email_address="team@example.com",
            user=self.user,
            is_naturschutzbehoerde=False,
            is_wildvogelhilfe_team=True,
        )

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_creating_multiple_patients_sends_notifications(self):
        date_found = timezone.now().date().strftime("%Y-%m-%d")
        response = self.client.post(
            reverse("bird_create"),
            data={
                "bird_identifier": "Patient",
                "bird": self.bird.id,
                "age": "Adult",
                "sex": "Weiblich",
                "date_found": date_found,
                "place": "Jena",
                "find_circumstances": self.circumstance.id,
                "diagnostic_finding": "Flügelbruch",
                "finder": "Finder Informationen",
                "comment": "Beobachtungsnotiz",
                "anzahl_patienten": 2,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        created = FallenBird.objects.filter(bird=self.bird).order_by("bird_identifier")
        self.assertEqual(created.count(), 2)
        self.assertEqual(created[0].bird_identifier, "Patient-1")
        self.assertEqual(created[1].bird_identifier, "Patient-2")

        # Ensure two notification e-mails were queued with deduplicated recipients.
        self.assertEqual(len(mail.outbox), 2)
        recipients = sorted(mail.outbox[0].to)
        self.assertEqual(recipients, ["behorde@example.com", "team@example.com"])

    def test_invalid_submission_renders_form_again(self):
        response = self.client.post(reverse("bird_create"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bird/bird_create.html")
        form = response.context.get("form")
        self.assertIsNotNone(form)
        self.assertFalse(form.is_valid())
        self.assertEqual(FallenBird.objects.count(), 0)


class GeocodeFoundLocationTests(TestCase):
    """Tests for the geocode_found_location endpoint.

    We mock the Nominatim response to avoid rate limits / network flakiness.
    The view performs a single pass currently; these tests capture expected
    extraction logic for city/county/state and region auto-creation.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="geo-user", email="geo@example.com", password="pw"
        )
        self.client.force_login(self.user)

    def _mock_nominatim(self, payload_list, status=200):
        """Helper to patch requests.get returning provided JSON list."""
        class DummyResp:
            def __init__(self, data, status_code):
                self._data = data
                self.status_code = status_code
                self.headers = {"Content-Type": "application/json"}

            def json(self):
                return self._data

        return mock.patch("bird.views.requests.get", return_value=DummyResp(payload_list, status))

    def test_city_extraction_prefers_city_field(self):
        query = "Erfurt, Alte Synagoge"
        mocked = [
            {
                "address": {
                    "city": "Erfurt",
                    "county": "Erfurt",
                    "state": "Thüringen",
                    "country": "Deutschland",
                }
            }
        ]
        with self._mock_nominatim(mocked):
            resp = self.client.get(reverse("bird_geocode_found_location"), {"q": query})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])  # success flag
        self.assertEqual(data["city"], "Erfurt")
        self.assertEqual(data["region_name"], "Erfurt")  # region uses city
        self.assertTrue(data["region_id"])  # created

    def test_fallback_to_county_when_no_city(self):
        query = "Kirche Kahla"
        mocked = [
            {
                "address": {
                    # no city/town/village fields, only county/state
                    "county": "Saale-Holzland-Kreis",
                    "state": "Thüringen",
                    "country": "Deutschland",
                }
            }
        ]
        with self._mock_nominatim(mocked):
            resp = self.client.get(reverse("bird_geocode_found_location"), {"q": query})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["city"], "")
        self.assertEqual(data["county"], "Saale-Holzland-Kreis")
        self.assertEqual(data["region_name"], "Saale-Holzland-Kreis")

    def test_fallback_to_state_when_no_city_or_county(self):
        query = "Lutherstraße 3, Jena"
        mocked = [
            {
                "address": {
                    # Simulate odd response missing city & county
                    "state": "Thüringen",
                    "country": "Deutschland",
                }
            }
        ]
        with self._mock_nominatim(mocked):
            resp = self.client.get(reverse("bird_geocode_found_location"), {"q": query})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["city"], "")
        self.assertEqual(data["county"], "")
        self.assertEqual(data["state"], "Thüringen")
        self.assertEqual(data["region_name"], "Thüringen")

    def test_error_when_no_results(self):
        query = "Universitätsklinikum Jena"
        mocked = []  # empty list -> no results
        with self._mock_nominatim(mocked):
            resp = self.client.get(reverse("bird_geocode_found_location"), {"q": query})
        self.assertEqual(resp.status_code, 404)
        data = resp.json()
        self.assertFalse(data["success"])  # failure
        self.assertIn("Keine Geocoding-Ergebnisse", data["error"])

    def test_institution_word_stripping_fallback(self):
        """Simuliert, dass Haupt-Query fehlschlägt und erst die letzte Token-Heuristik greift."""
        query = "Universitätsklinikum Jena"
        # Sequence of responses for attempts: 1-5 empty, 6 returns city Jena
        # We patch requests.get to return empty list until attempt_no==6 based on called params['q'] pattern.
        class DummyResp:
            def __init__(self, data):
                self._data = data
                self.status_code = 200
                self.headers = {"Content-Type": "application/json"}
            def json(self):
                return self._data

        def side_effect(url, params, headers, timeout):
            q = params.get('q')
            if q == 'Jena, Deutschland':  # last token heuristic (attempt 6)
                return DummyResp([
                    {"address": {"city": "Jena", "state": "Thüringen", "country": "Deutschland"}}
                ])
            return DummyResp([])

        with mock.patch('bird.views.requests.get', side_effect=side_effect):
            resp = self.client.get(reverse("bird_geocode_found_location"), {"q": query})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["city"], "Jena")
        self.assertEqual(data["region_name"], "Jena")
