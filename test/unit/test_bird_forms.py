"""Current unit tests for BirdAddForm and BirdEditForm."""
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from aviary.models import Aviary
from bird.forms import BirdAddForm, BirdEditForm
from bird.models import Bird, BirdStatus, Circumstance, FallenBird


class BirdAddFormTests(TestCase):
    """Validate the simplified bulk-intake form for new patients."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="form-user",
            email="user@example.com",
            password="secret",
        )
        self.aviary = Aviary.objects.create(
            name="Pflegestation",
            location="Jena",
            created_by=self.user,
        )
        self.status = BirdStatus.objects.create(description="In Behandlung")
        self.circumstance = Circumstance.objects.create(name="Fensterkollision", description="Fund am Fenster")
        self.bird = Bird.objects.create(
            name="Mauersegler",
            species="Apus apus",
            status=self.status,
            aviary=self.aviary,
            created_by=self.user,
        )
        self.valid_payload = {
            "bird_identifier": "MS-001",
            "bird": self.bird.id,
            "age": "Adult",
            "sex": "Unbekannt",
            "date_found": date.today().isoformat(),
            "place": "Jena",
            "find_circumstances": self.circumstance.id,
            "diagnostic_finding": "Schwäche",
            "finder": "Finder Name\nStraße 1\nJena",
            "comment": "Erstaufnahme",
            "anzahl_patienten": 1,
        }

    def test_valid_payload_passes(self):
        form = BirdAddForm(data=self.valid_payload)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_save_creates_patient(self):
        form = BirdAddForm(data=self.valid_payload)
        self.assertTrue(form.is_valid(), msg=form.errors)
        patient = form.save(commit=False)
        patient.user = self.user
        patient.save()
        self.assertEqual(patient.bird, self.bird)
        self.assertEqual(patient.bird_identifier, "MS-001")

    def test_missing_required_fields(self):
        form = BirdAddForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("bird", form.errors)
        self.assertIn("anzahl_patienten", form.errors)

    def test_patient_count_bounds(self):
        too_low = self.valid_payload | {"anzahl_patienten": 0}
        form = BirdAddForm(data=too_low)
        self.assertFalse(form.is_valid())
        self.assertIn("anzahl_patienten", form.errors)

        too_high = self.valid_payload | {"anzahl_patienten": 100}
        form = BirdAddForm(data=too_high)
        self.assertFalse(form.is_valid())
        self.assertIn("anzahl_patienten", form.errors)

    def test_invalid_choice_values(self):
        payload = self.valid_payload | {"age": "falsch"}
        form = BirdAddForm(data=payload)
        self.assertFalse(form.is_valid())
        self.assertIn("age", form.errors)

        payload = self.valid_payload | {"sex": "falsch"}
        form = BirdAddForm(data=payload)
        self.assertFalse(form.is_valid())
        self.assertIn("sex", form.errors)


class BirdEditFormTests(TestCase):
    """Ensure editing an existing patient honours current business rules."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="edit-user",
            email="edit@example.com",
            password="secret",
        )
        self.aviary = Aviary.objects.create(
            name="Innenvoliere",
            location="Jena",
            created_by=self.user,
        )
        self.status = BirdStatus.objects.create(description="Verletzter Patient")
        self.circumstance = Circumstance.objects.create(name="Katze", description="Von Katze gebracht")
        self.bird = Bird.objects.create(
            name="Turmfalke",
            species="Falco tinnunculus",
            status=self.status,
            aviary=self.aviary,
            created_by=self.user,
        )
        self.patient = FallenBird.objects.create(
            bird=self.bird,
            date_found=date.today(),
            place="Jena",
            status=self.status,
            find_circumstances=self.circumstance,
            user=self.user,
        )
        self.valid_update = {
            "bird_identifier": "TF-2025",
            "bird": self.bird.id,
            "sex": "Weiblich",
            "date_found": date.today().isoformat(),
            "place": "Pflegestation",
            "status": self.status.id,
            "aviary": self.aviary.id,
            "find_circumstances": self.circumstance.id,
            "diagnostic_finding": "Flügelbruch",
            "finder": "Finder Team",
            "comment": "Stabil",
        }

    def test_update_payload_valid(self):
        form = BirdEditForm(data=self.valid_update, instance=self.patient)
        self.assertTrue(form.is_valid(), msg=form.errors)
        updated = form.save()
        self.assertEqual(updated.bird_identifier, "TF-2025")
        self.assertEqual(updated.place, "Pflegestation")

    def test_missing_bird_reference_invalid(self):
        payload = self.valid_update.copy()
        payload.pop("bird")
        form = BirdEditForm(data=payload, instance=self.patient)
        self.assertFalse(form.is_valid())
        self.assertIn("bird", form.errors)

    def test_optional_fields_can_be_cleared(self):
        payload = self.valid_update | {"comment": "", "diagnostic_finding": ""}
        form = BirdEditForm(data=payload, instance=self.patient)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_invalid_status_choice(self):
        payload = self.valid_update | {"status": 9999}
        form = BirdEditForm(data=payload, instance=self.patient)
        self.assertFalse(form.is_valid())
        self.assertIn("status", form.errors)
