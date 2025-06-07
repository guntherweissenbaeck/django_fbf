from datetime import date
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Costs


class DateInput(forms.DateInput):
    input_type = "date"


class CostsForm(forms.ModelForm):
    class Meta:
        model = Costs
        fields = ["id_bird", "costs", "comment"]
        labels = {
            "id_bird": _("Patient"),
            "costs": _("Betrag [€]"),
            "comment": _("Bemerkung"),
        }
