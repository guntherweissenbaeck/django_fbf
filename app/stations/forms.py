"""! @brief Forms related to the Wildvogelhilfe station administration."""

from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import StationReport, StationReportSettings

class StationCSVImportForm(forms.Form):
    """! @brief Upload form that feeds the CSV importer service."""

    csv_file = forms.FileField(
        label=_("CSV-Datei"),
        help_text=_("Erwartet UTF-8-kodierte Dateien mit Semikolon als Trennzeichen."),
    )
    update_existing = forms.BooleanField(
        label=_("Vorhandene Einträge aktualisieren"),
        required=False,
        initial=True,
        help_text=_("Aktualisiert vorhandene Stationen anhand von Name, Ort und Land."),
    )


class StationReportForm(forms.ModelForm):
    """! @brief Public form backing the station suggestion page."""

    privacy_confirmed = forms.BooleanField(
        label=_("Ich habe die Hinweise zur Datenverarbeitung gelesen."),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["postal_code"].required = True
        self.fields["reporter_email"].required = True

    class Meta:
        model = StationReport
        fields = [
            "name",
            "specialization",
            "description",
            "address",
            "postal_code",
            "city",
            "state",
            "country",
            "latitude",
            "longitude",
            "website",
            "email",
            "phone",
            "note",
            "reporter_name",
            "reporter_email",
            "reporter_phone",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "note": forms.Textarea(attrs={"rows": 3}),
            "specialization": forms.Textarea(attrs={"rows": 3}),
            "address": forms.Textarea(attrs={"rows": 2}),
        }

    def clean(self):
        """! @brief Remove helper fields that are not part of the model."""

        cleaned = super().clean()
        cleaned.pop("privacy_confirmed", None)

        postal_code = cleaned.get("postal_code")
        reporter_email = cleaned.get("reporter_email")

        if not postal_code:
            self.add_error("postal_code", _("Bitte eine Postleitzahl angeben."))

        if not reporter_email:
            self.add_error("reporter_email", _("Bitte eine E-Mail-Adresse angeben."))

        return cleaned


class StationReportSettingsForm(forms.ModelForm):
    """! @brief Simple form to edit report notification preferences."""

    class Meta:
        model = StationReportSettings
        fields = ["notification_email"]
        widgets = {
            "notification_email": forms.EmailInput(attrs={"placeholder": "alerts@example.org"}),
        }
