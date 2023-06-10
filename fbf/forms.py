from datetime import date

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import FallenBird


class DateInput(forms.DateInput):
    input_type = "date"


class BirdForm(forms.ModelForm):
    class Meta:
        widgets = {"date_found": DateInput()}
        model = FallenBird
        fields = [
            "bird",
            "date_found",
            "place",
            "rescuer",
        ]
        labels = {
            "bird": _("Vogel"),
            "date_found": _("Datum des Fundes"),
            "place": _("Fundort"),
            "rescuer": _("Finder"),
        }
