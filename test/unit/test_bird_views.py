"""High-value coverage tests for `bird.views`."""
from datetime import date
from smtplib import SMTPException

import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core import mail
from django.core.mail import BadHeaderError
from django.test import override_settings
from django.urls import reverse

from aviary.models import Aviary
from bird.models import Bird, BirdStatus, Circumstance, FallenBird
from sendemail.models import Emailadress


@pytest.fixture
@pytest.mark.django_db
def bird_test_data():
    """Provision shared objects for view tests."""
    user = User.objects.create_user(
        username="view-user",
        email="view@example.com",
        password="super-secret",
    )
    aviary = Aviary.objects.create(
        description="Innenvoliere Ost",
        condition="Offen",
        last_ward_round=date.today(),
        created_by=user,
    )
    status_active = BirdStatus.objects.create(description="Aktiv")
    status_secondary = BirdStatus.objects.create(description="In Pflege")
    status_inactive = BirdStatus.objects.create(description="Verstorben")

    circumstance_window = Circumstance.objects.create(name="Fenster", description="Fund am Fenster")
    circumstance_cat = Circumstance.objects.create(name="Katze", description="Durch Katze gebracht")

    bird = Bird.objects.create(
        name="Turmfalke",
        species="Falco tinnunculus",
        status=status_active,
        melden_an_naturschutzbehoerde=True,
        melden_an_jagdbehoerde=False,
        melden_an_wildvogelhilfe_team=True,
    )

    # Active patients (status ids 1 & 2 are considered active by the view filters)
    FallenBird.objects.create(
        bird=bird,
        status=status_active,
        date_found=date.today(),
        place="Jena",
        find_circumstances=circumstance_window,
    )
    FallenBird.objects.create(
        bird=bird,
        status=status_secondary,
        date_found=date.today(),
        place="Jena",
        find_circumstances=circumstance_cat,
    )
    # Inactive patient (status id != 1 or 2)
    FallenBird.objects.create(
        bird=bird,
        status=status_inactive,
        date_found=date.today(),
        place="Jena",
        find_circumstances=circumstance_cat,
    )

    return {
        "user": user,
        "aviary": aviary,
        "bird": bird,
        "status_active": status_active,
        "status_secondary": status_secondary,
        "status_inactive": status_inactive,
        "circumstance_window": circumstance_window,
        "circumstance_cat": circumstance_cat,
    }


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", DEFAULT_FROM_EMAIL="alerts@example.com")
def test_bird_create_multiple_patients_send_signal(client, bird_test_data):
    """Happy-path submission creates patients and dispatches notifications."""
    user = bird_test_data["user"]
    bird = bird_test_data["bird"]
    circumstance = bird_test_data["circumstance_window"]

    Emailadress.objects.create(
        email_address="naturschutz@example.com",
        user=user,
        is_naturschutzbehoerde=True,
    )
    Emailadress.objects.create(
        email_address="team@example.com",
        user=user,
        is_wildvogelhilfe_team=True,
    )

    client.force_login(user)
    payload = {
        "bird_identifier": "TF",
        "bird": bird.id,
        "age": "Adult",
        "sex": "Unbekannt",
        "date_found": date.today().isoformat(),
        "place": "Jena",
        "find_circumstances": circumstance.id,
        "diagnostic_finding": "Flügelbruch",
        "finder": "Finder Team\nStraße 1\nJena",
        "comment": "Erstaufnahme",
        "anzahl_patienten": 2,
    }

    response = client.post(reverse("bird_create"), data=payload)
    assert response.status_code == 302

    patients = list(FallenBird.objects.filter(bird=bird).order_by("bird_identifier"))
    assert len(patients) >= 5  # includes seeded entries from fixture plus new two
    assert patients[-2].bird_identifier == "TF-1"
    assert patients[-1].bird_identifier == "TF-2"

    assert len(mail.outbox) == 2
    for message in mail.outbox:
        assert message.from_email == "alerts@example.com"
        assert set(message.to) == {"naturschutz@example.com", "team@example.com"}


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_bird_create_handles_bad_header(client, monkeypatch, bird_test_data):
    """A BadHeaderError aborts with an explanatory response."""
    user = bird_test_data["user"]
    bird = bird_test_data["bird"]
    circumstance = bird_test_data["circumstance_window"]
    client.force_login(user)

    def boom(*args, **kwargs):
        raise BadHeaderError("bad header")

    monkeypatch.setattr("bird.views.send_mail", boom)

    Emailadress.objects.create(
        email_address="behorde@example.com",
        user=user,
        is_naturschutzbehoerde=True,
    )

    payload = {
        "bird_identifier": "BH-1",
        "bird": bird.id,
        "find_circumstances": circumstance.id,
        "date_found": date.today().isoformat(),
        "finder": "Finder",
        "comment": "",
        "anzahl_patienten": 1,
    }

    response = client.post(reverse("bird_create"), data=payload)
    assert response.status_code == 200
    assert "Invalid header found" in response.content.decode()


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_bird_create_logs_smtp_exception(client, monkeypatch, bird_test_data, caplog):
    """SMTP exceptions surface as warnings but do not abort the intake."""
    user = bird_test_data["user"]
    bird = bird_test_data["bird"]
    circumstance = bird_test_data["circumstance_cat"]

    Emailadress.objects.create(
        email_address="team@example.com",
        user=user,
        is_wildvogelhilfe_team=True,
    )

    client.force_login(user)

    def boom(*args, **kwargs):
        raise SMTPException("mailbox down")

    monkeypatch.setattr("bird.views.send_mail", boom)

    payload = {
        "bird_identifier": "SMTP",
        "bird": bird.id,
        "date_found": date.today().isoformat(),
        "find_circumstances": circumstance.id,
        "anzahl_patienten": 1,
    }

    response = client.post(reverse("bird_create"), data=payload, follow=True)
    assert response.status_code == 200

    messages = list(get_messages(response.wsgi_request))
    assert any("E-Mail konnte nicht versendet werden" in msg.message for msg in messages)
    assert any("Error sending intake email" in record.message for record in caplog.records)


@pytest.mark.django_db
def test_list_and_delete_views_authenticated(client, bird_test_data):
    """Smoke test list/detail/delete flows for both active and inactive patients."""
    user = bird_test_data["user"]
    bird = bird_test_data["bird"]

    client.force_login(user)

    response = client.get(reverse("bird_all"))
    assert response.status_code == 200
    assert "Turmfalke" in response.content.decode()

    response = client.get(reverse("bird_inactive"))
    assert response.status_code == 200

    detail_response = client.get(reverse("bird_single", args=[bird.fallenbird_set.first().id]))
    assert detail_response.status_code == 200

    # Exercise delete view
    target_id = bird.fallenbird_set.first().id
    response = client.post(reverse("bird_delete", args=[target_id]), follow=True)
    assert response.status_code == 200
    assert not FallenBird.objects.filter(id=target_id).exists()


@pytest.mark.django_db
def test_help_views_render_species_listing(client, bird_test_data):
    """Ensure the help pages render with the expected context."""
    user = bird_test_data["user"]
    client.force_login(user)

    response = client.get(reverse("bird_help"))
    assert response.status_code == 200

    bird = bird_test_data["bird"]
    response = client.get(reverse("bird_help_single", args=[bird.id]))
    assert response.status_code == 200
