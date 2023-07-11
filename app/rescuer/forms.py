from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Rescuer


class DateInput(forms.DateInput):
    input_type = "date"


class RescuerForm(forms.ModelForm):
    class Meta:
        model = Rescuer
        fields = [
            "first_name",
            "last_name",
            "street",
            "street_number",
            "zip_code",
            "city",
            "phone",
        ]
        labels = {
            "first_name": _("Vorname"),
            "last_name": _("Nachname"),
            "street": _("Straße"),
            "street_number": _("Hausnummer"),
            "zip_code": _("Postleitzahl"),
            "city": _("Stadt"),
            "phone": _("Telefon"),
        }
