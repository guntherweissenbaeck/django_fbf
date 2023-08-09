import csv

from bird.models import FallenBird
from costs.models import Costs
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


@login_required(login_url="account_login")
def site_exports(request):
    return render(request, "export/overview.html")


@login_required(login_url="account_login")
def export_costs(request):
    costs = Costs.objects.all().values_list(
        "id_bird__bird_identifier", "costs", "created", "comment", "user__username"
    )
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment, filename=fbf_costs.csv"
    writer = csv.writer(response)
    writer.writerow(
        ["Vogel", "Betrag in Euro", "Gebucht am", "Kommentar", "Gebucht von"]
    )
    for single_costs in costs:
        writer.writerow(single_costs)
    return response


@login_required(login_url="account_login")
def export_birds(request):
    birds = FallenBird.objects.all().values_list(
        "bird_identifier",
        "bird__name",
        "age",
        "sex",
        "date_found",
        "place",
        "created",
        "updated",
        "find_circumstances__description",
        "diagnostic_finding",
        "rescuer__last_name",
        "user__username",
        "status__description",
        "aviary__description",
        "sent_to",
    )
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment, filename=fbf_birds.csv"
    writer = csv.writer(response)
    writer.writerow(
        [
            "Vogel",
            "Patienten Alias",
            "Alter",
            "Geschlecht",
            "gefunden am",
            "Fundort",
            "Pateient angelegt am",
            "Pateient aktualisiert am",
            "Fundumstände",
            "Diagnose bei Fund",
            "Finder (Nachname)",
            "Benutzer",
            "Status",
            "Voliere",
            "Übersandt",
        ]
    )
    for bird in birds:
        writer.writerow(bird)
    return response
