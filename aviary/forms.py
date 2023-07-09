from datetime import date
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Aviary


class DateInput(forms.DateInput):
    input_type = "date"


class AviaryEditForm(forms.ModelForm):
    class Meta:
        widgets = {
            "last_ward_round": DateInput(format="%Y-%m-%d", attrs={"value": date.today})
        }
        model = Aviary
        fields = [
            "description",
            "condition",
            "last_ward_round",
        ]
        labels = {
            "description": _("Bezeichnung"),
            "condition": _("Zustand"),
            "last_ward_round": _("Letzte Inspektion"),
        }
