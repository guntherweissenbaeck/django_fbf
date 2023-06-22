from django import forms
from django.utils.translation import gettext_lazy as _

from .models import FallenBird


class DateInput(forms.DateInput):
    input_type = "date"


class BirdAddForm(forms.ModelForm):
    class Meta:
        widgets = {
            "date_found": DateInput()}
        model = FallenBird
        fields = ["bird", "date_found", "place", ]
        labels = {"bird": _("Vogel"), "date_found": _(
            "Datum des Fundes"), "place": _("Fundort")}


class BirdEditForm(forms.ModelForm):
    class Meta:
        widgets = {"date_found": DateInput(format="%Y-%m-%d")}
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
            "rescuer": _("Retter"),
        }
