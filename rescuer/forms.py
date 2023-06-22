from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Rescuer


class DateInput(forms.DateInput):
    input_type = "date"


class RescuerForm(forms.ModelForm):
    class Meta:
        widgets = {"date_of_birth": DateInput()}
        model = Rescuer
        fields = [
            "gender",
            "first_name",
            "last_name",
            "street",
            "street_number",
            "zip_code",
            "city",
            "state",
            "date_of_birth",
            "email",
        ]
        labels = {
            "gender": _("Geschlecht"),
            "first_name": _("Vorname"),
            "last_name": _("Nachname"),
            "date_of_birth": _("Geburtstag"),
            "street": _("Straße"),
            "street_number": _("Hausnummer"),
            "zip_code": _("Postleitzahl"),
            "city": _("Stadt"),
            "state": _("Land"),
            "email": _("Email"),
        }
