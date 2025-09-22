"""Unit tests for the current AviaryEditForm implementation."""
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from aviary.forms import AviaryEditForm
from aviary.models import Aviary


class AviaryEditFormTests(TestCase):
    """Ensure the form mirrors the simplified aviary editing workflow."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.valid_form_data = {
            "description": "Pflegestation Nord",
            "condition": "Offen",
            "last_ward_round": date.today().isoformat(),
            "comment": "Alles im grünen Bereich",
        }

    def test_form_accepts_valid_payload(self):
        form = AviaryEditForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_form_persists_changes(self):
        form = AviaryEditForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid(), msg=form.errors)

        aviary = form.save(commit=False)
        aviary.created_by = self.user
        aviary.save()

        self.assertEqual(aviary.description, "Pflegestation Nord")
        self.assertEqual(aviary.condition, "Offen")
        self.assertEqual(aviary.comment, "Alles im grünen Bereich")
        self.assertEqual(aviary.last_ward_round, date.fromisoformat(self.valid_form_data["last_ward_round"]))

    def test_required_fields_enforced(self):
        form = AviaryEditForm(data={"comment": "Nur Kommentar"})
        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)
        self.assertIn("condition", form.errors)
        self.assertIn("last_ward_round", form.errors)

    def test_condition_must_match_choice(self):
        invalid_data = self.valid_form_data | {"condition": "Ungültig"}
        form = AviaryEditForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("condition", form.errors)

    def test_last_ward_round_requires_valid_date(self):
        invalid_data = self.valid_form_data | {"last_ward_round": "31-12-2024"}
        form = AviaryEditForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("last_ward_round", form.errors)

    def test_initial_last_ward_round_default(self):
        form = AviaryEditForm()
        widget_value = form.fields["last_ward_round"].widget.attrs.get("value")
        # Meta widgets configure a callable default; fall back to the field initial when present.
        if widget_value is None:
            initial = form.fields["last_ward_round"].initial
            widget_value = initial

        self.assertIsNotNone(widget_value)
        resolved = widget_value() if callable(widget_value) else widget_value
        self.assertEqual(resolved, date.today())

    def test_comment_is_optional(self):
        data = self.valid_form_data.copy()
        data.pop("comment")
        form = AviaryEditForm(data=data)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_existing_instance_updates(self):
        aviary = Aviary.objects.create(
            description="Altbestand",
            condition="Geschlossen",
            last_ward_round=date.today() - timedelta(days=7),
            created_by=self.user,
        )
        form = AviaryEditForm(data=self.valid_form_data, instance=aviary)
        self.assertTrue(form.is_valid(), msg=form.errors)
        updated = form.save()
        self.assertEqual(updated.description, "Pflegestation Nord")
        self.assertEqual(updated.condition, "Offen")
