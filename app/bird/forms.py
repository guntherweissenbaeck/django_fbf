from datetime import date

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import FallenBird, Bird


class DateInput(forms.DateInput):
    input_type = "date"


class BirdAddForm(forms.ModelForm):
    class Meta:
        widgets = {
            "date_found": DateInput(
                format="%Y-%m-%d", attrs={"value": date.today}
            )
        }
        model = FallenBird
        fields = [
            "bird_identifier",
            "bird",
            "age",
            "sex",
            "date_found",
            "place",
            "find_circumstances",
            "diagnostic_finding",
            "finder",
            "comment",
        ]
        labels = {
            "bird_identifier": _("Kennung"),
            "bird": _("Vogel"),
            "age": _("Alter"),
            "sex": _("Geschlecht"),
            "date_found": _("Datum des Fundes"),
            "place": _("Fundort"),
            "find_circumstances": _("Fundumstände"),
            "diagnostic_finding": _("Diagnose bei Fund"),
            "comment": _("Bermerkung"),
            "finder": _("Finder"),
        }


class BirdEditForm(forms.ModelForm):
    class Meta:
        widgets = {"date_found": DateInput(format="%Y-%m-%d")}
        model = FallenBird
        fields = [
            "bird_identifier",
            "bird",
            "sex",
            "date_found",
            "place",
            "status",
            "aviary",
            "sent_to",
            "find_circumstances",
            "diagnostic_finding",
            "finder",
            "comment",
        ]
        labels = {
            "bird": _("Vogel"),
            "sex": _("Geschlecht"),
            "date_found": _("Datum des Fundes"),
            "place": _("Fundort"),
            "status": _("Status"),
            "aviary": _("Voliere"),
            "sent_to": _("Übermittelt nach"),
            "find_circumstances": _("Fundumstände"),
            "diagnostic_finding": _("Diagnose bei Fund"),
            "finder": _("Finder"),
            "comment": _("Bermerkung"),
        }


class BirdSpeciesForm(forms.ModelForm):
    """Form for editing Bird species with notification settings."""
    class Meta:
        model = Bird
        fields = [
            "name",
            "description",
            "species",
            "melden_an_naturschutzbehoerde",
            "melden_an_jagdbehoerde",
            "melden_an_wildvogelhilfe_team",
        ]
        labels = {
            "name": _("Bezeichnung"),
            "description": _("Erläuterungen"),
            "species": _("Art"),
            "melden_an_naturschutzbehoerde": _("Melden an Naturschutzbehörde"),
            "melden_an_jagdbehoerde": _("Melden an Jagdbehörde"),
            "melden_an_wildvogelhilfe_team": _("Melden an Wildvogelhilfe-Team"),
        }
        help_texts = {
            "melden_an_naturschutzbehoerde": _("Automatische E-Mail-Benachrichtigung an Naturschutzbehörde senden"),
            "melden_an_jagdbehoerde": _("Automatische E-Mail-Benachrichtigung an Jagdbehörde senden"),
            "melden_an_wildvogelhilfe_team": _("Automatische E-Mail-Benachrichtigung an Wildvogelhilfe-Team senden"),
        }
