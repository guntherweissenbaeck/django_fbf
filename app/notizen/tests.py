from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notizen.models import Notiz


class PublicNotizTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="note-owner",
            email="owner@example.com",
            password="secret-pass",
        )
        self.client.force_login(self.user)
        self.notiz = Notiz.objects.create(
            name="Test Notiz",
            inhalt="<p>Inhalt</p>",
            erstellt_von=self.user,
        )

    def test_enable_public_access_and_fetch_without_login(self):
        response = self.client.post(
            reverse("notizen:edit", args=[self.notiz.pk]),
            data={
                "name": "Test Notiz",
                "inhalt": "<p>Inhalt</p>",
                "is_public": "on",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.notiz.refresh_from_db()
        self.assertTrue(self.notiz.is_public)

        public_url = reverse("notizen:public_edit", kwargs={"token": self.notiz.public_token})
        self.client.logout()
        public_response = self.client.get(public_url)
        self.assertContains(public_response, "Test Notiz")
        self.assertEqual(public_response.status_code, 200)

    def test_public_edit_updates_content(self):
        self.notiz.is_public = True
        self.notiz.save(update_fields=["is_public"])

        public_url = reverse("notizen:public_edit", kwargs={"token": self.notiz.public_token})
        response = self.client.post(
            public_url,
            data={
                "name": "Neue Überschrift",
                "inhalt": "<p>Geänderter Inhalt</p>",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.notiz.refresh_from_db()
        self.assertIn("Geänderter Inhalt", self.notiz.inhalt)
        self.assertEqual(self.notiz.name, "Test Notiz")

    def test_non_public_request_returns_404(self):
        url = reverse("notizen:public_edit", kwargs={"token": self.notiz.public_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
