from datetime import date

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import FallenBird


class DateInput(forms.DateInput):
    input_type = "date"


class BirdAddForm(forms.ModelForm):

    class Meta:
        widgets = {
            "date_found": DateInput(
                format="%Y-%m-%d",
                attrs={
                    "value": date.today})}
        model = FallenBird
        fields = [
            "bird_identifier",
            "bird",
            "date_found",
            "place",
            "find_circumstances",
            "diagnostic_finding",
        ]
        labels = {
            "bird_identifier": _("Kennung"),
            "bird": _("Vogel"),
            "date_found": _("Datum des Fundes"),
            "place": _("Fundort"),
            "find_circumstances": _("Fundumstände"),
            "diagnostic_finding": _("Diagnose bei Fund"),
        }


class BirdEditForm(forms.ModelForm):
    class Meta:
        widgets = {"date_found": DateInput(format="%Y-%m-%d")}
        model = FallenBird
        fields = [
            "bird_identifier",
            "bird",
            "date_found",
            "place",
            "status",
            "aviary",
            "sent_to",
            "find_circumstances",
            "diagnostic_finding",
        ]
        labels = {
            "bird": _("Vogel"),
            "date_found": _("Datum des Fundes"),
            "place": _("Fundort"),
            "status": _("Status"),
            "aviary": _("Voliere"),
            "sent_to": _("Übermittelt nach"),
            "find_circumstances": _("Fundumstände"),
            "diagnostic_finding": _("Diagnose bei Fund"),
        }
