"""Views for managing bird patients and notification workflows.

The docstrings follow ``:param`` / ``:returns`` conventions to keep the module
compatible with Doxygen generated documentation.
"""

import logging

import names
from smtplib import SMTPException

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from django.db.models import Q, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from sendemail.message import messagebody
from sendemail.models import Emailadress

from .forms import BirdAddForm, BirdEditForm, BirdSpeciesForm
from .models import Bird, FallenBird

logger = logging.getLogger(__name__)


def _collect_notification_recipients(bird: Bird) -> list[str]:
    """Return all deduplicated e-mail receivers for the given bird species.

    :param bird: Bird species that has been selected during patient intake.
    :returns: Iterable of unique e-mail addresses honouring notification flags.
    """

    recipient_filter = Q()
    if bird.melden_an_naturschutzbehoerde:
        recipient_filter |= Q(is_naturschutzbehoerde=True)
    if bird.melden_an_jagdbehoerde:
        recipient_filter |= Q(is_jagdbehoerde=True)
    if bird.melden_an_wildvogelhilfe_team:
        recipient_filter |= Q(is_wildvogelhilfe_team=True)

    if not recipient_filter:
        return []

    return list(
        Emailadress.objects.filter(recipient_filter)
        .values_list("email_address", flat=True)
        .distinct()
    )


@login_required(login_url="account_login")
def bird_create(request: HttpRequest) -> HttpResponse:
    """Create one or multiple ``FallenBird`` instances from the add form.

    :param request: Incoming HTTP request that optionally includes POST data.
    :returns: Redirect to the bird index on success or renders the form.
    """

    form = BirdAddForm(initial={"bird_identifier": names.get_first_name()})

    if request.method == "POST":
        form = BirdAddForm(request.POST or None, request.FILES or None)

        if form.is_valid():
            anzahl_patienten = form.cleaned_data.get("anzahl_patienten", 1)
            base_identifier = form.cleaned_data.get(
                "bird_identifier", names.get_first_name()
            )

            created_patients = []
            selected_bird: Bird = form.cleaned_data.get("bird")
            notification_recipients = list(_collect_notification_recipients(selected_bird))

            patient_payload = form.cleaned_data.copy()
            patient_payload.pop("anzahl_patienten", None)

            for index in range(anzahl_patienten):
                unique_identifier = (
                    base_identifier if anzahl_patienten == 1 else f"{base_identifier}-{index + 1}"
                )
                patient_payload["bird_identifier"] = unique_identifier

                patient = FallenBird(**patient_payload)
                patient.user = request.user
                patient.save()

                created_patients.append(patient)

                if notification_recipients:
                    try:
                        send_mail(
                            subject=f"Wildvogel gefunden! (Patient: {unique_identifier})",
                            message=messagebody(
                                patient.date_found,
                                patient.bird,
                                patient.place,
                                patient.diagnostic_finding,
                                unique_identifier,
                            ),
                            from_email=getattr(
                                settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"
                            ),
                            recipient_list=notification_recipients,
                        )
                    except BadHeaderError:
                        return HttpResponse("Invalid header found.")
                    except SMTPException as exc:
                        # Use messages framework to surface delivery issues without failing the request.
                        messages.warning(
                            request,
                            f"E-Mail konnte nicht versendet werden: {exc}",
                            extra_tags="email-failure",
                            fail_silently=True,
                        )
                        logger.exception("Error sending intake email")

            request.session["rescuer_id"] = None

            if anzahl_patienten == 1:
                messages.success(
                    request,
                    f"Patient '{created_patients[0].bird_identifier}' wurde erfolgreich angelegt.",
                )
            else:
                patient_names = ", ".join(
                    [patient.bird_identifier for patient in created_patients]
                )
                messages.success(
                    request,
                    f"{anzahl_patienten} Patienten wurden erfolgreich angelegt: {patient_names}",
                )

            return redirect("bird_all")

    context = {"form": form}
    return render(request, "bird/bird_create.html", context)


@login_required(login_url="account_login")
def bird_help(request: HttpRequest) -> HttpResponse:
    """Render a help view containing all ``Bird`` species.

    :param request: Incoming request instance.
    :returns: Rendered help template with the ``Bird`` queryset.
    """

    birds = Bird.objects.all().order_by("name")
    context = {"birds": birds}
    return render(request, "bird/bird_help.html", context)


@login_required(login_url="account_login")
def bird_help_single(request: HttpRequest, id: int) -> HttpResponse:
    """Show help information for a single ``Bird`` species.

    :param request: Incoming request instance.
    :param id: Primary key of the ``Bird`` entry.
    :returns: Rendered template for the selected bird.
    """

    bird = Bird.objects.get(id=id)
    context = {"bird": bird}
    return render(request, "bird/bird_help_single.html", context)


@login_required(login_url="account_login")
def bird_all(request: HttpRequest) -> HttpResponse:
    """List active ``FallenBird`` patients along with aggregated costs.

    :param request: Incoming request instance.
    :returns: Rendered template containing all active patients.
    """

    birds = (
        FallenBird.objects.filter(Q(status="1") | Q(status="2"))
        .annotate(total_costs=Sum("costs__costs"))
        .order_by("date_found")
    )
    context = {"birds": birds}
    return render(request, "bird/bird_all.html", context)


@login_required(login_url="account_login")
def bird_inactive(request: HttpRequest) -> HttpResponse:
    """List inactive ``FallenBird`` patients with aggregated costs.

    :param request: Incoming request instance.
    :returns: Rendered template containing all inactive patients.
    """

    birds = (
        FallenBird.objects.filter(~Q(status="1") & ~Q(status="2"))
        .annotate(total_costs=Sum("costs__costs"))
        .order_by("date_found")
    )
    context = {"birds": birds}
    return render(request, "bird/bird_inactive.html", context)


@login_required(login_url="account_login")
def bird_single(request: HttpRequest, id: str) -> HttpResponse:
    """Edit a single ``FallenBird`` instance via the edit form.

    :param request: Incoming request instance populated with POST data (optional).
    :param id: Primary key of the ``FallenBird`` record to edit.
    :returns: Rendered edit template or redirect after successful save.
    """

    bird = FallenBird.objects.get(id=id)
    form = BirdEditForm(
        request.POST or None,
        request.FILES or None,
        instance=bird)
    if request.method == "POST":
        if form.is_valid():
            fs = form.save(commit=False)
            if fs.status.description != "In Auswilderung":
                fs.aviary = None
            fs.save()
            return redirect("bird_all")
    context = {"form": form, "bird": bird}
    return render(request, "bird/bird_single.html", context)


@login_required(login_url="account_login")
def bird_delete(request: HttpRequest, id: str) -> HttpResponse:
    """Confirm and delete a ``FallenBird`` instance.

    :param request: Request instance used to confirm deletion.
    :param id: Primary key for the ``FallenBird`` record slated for removal.
    :returns: Rendered confirmation template or redirect after deletion.
    """

    bird = FallenBird.objects.get(id=id)
    if request.method == "POST":
        bird.delete()
        return redirect("bird_all")
    context = {"bird": bird}
    return render(request, "bird/bird_delete.html", context)


@login_required(login_url="account_login")
def bird_species_list(request: HttpRequest) -> HttpResponse:
    """List all bird species with their notification settings.

    :param request: Incoming request instance.
    :returns: Rendered species list template.
    """

    birds = Bird.objects.all().order_by("name")
    context = {"birds": birds}
    return render(request, "bird/bird_species_list.html", context)


@login_required(login_url="account_login")
def bird_species_edit(request: HttpRequest, id: int) -> HttpResponse:
    """Edit bird species notification settings.

    :param request: Request instance containing form data.
    :param id: Primary key of the ``Bird`` record being edited.
    :returns: Rendered edit form or redirect after saving.
    """

    bird_species = Bird.objects.get(id=id)
    form = BirdSpeciesForm(request.POST or None, instance=bird_species)
    
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("bird_species_list")
    
    context = {"form": form, "bird_species": bird_species}
    return render(request, "bird/bird_species_edit.html", context)
