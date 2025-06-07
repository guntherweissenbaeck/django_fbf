from datetime import date
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Aviary


class DateInput(forms.DateInput):
    input_type = "date"


class AviaryEditForm(forms.ModelForm):
    class Meta:
        widgets = {
            "last_ward_round": DateInput(
                format="%Y-%m-%d", attrs={"value": date.today}
            )
        }
        model = Aviary
        fields = [
            "name",
            "location", 
            "description",
            "capacity",
            "current_occupancy",
            "contact_person",
            "contact_phone",
            "contact_email",
            "notes",
            "condition",
            "last_ward_round",
            "comment",
        ]
        labels = {
            "name": _("Name"),
            "location": _("Standort"),
            "description": _("Bezeichnung"),
            "capacity": _("Kapazität"),
            "current_occupancy": _("Aktuelle Belegung"),
            "contact_person": _("Ansprechpartner"),
            "contact_phone": _("Telefon"),
            "contact_email": _("E-Mail"),
            "notes": _("Notizen"),
            "condition": _("Zustand"),
            "last_ward_round": _("Letzte Inspektion"),
            "comment": _("Bemerkungen"),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set help text for key fields
        if 'capacity' in self.fields:
            self.fields['capacity'].help_text = str(_("Maximum number of birds this aviary can hold"))
        if 'current_occupancy' in self.fields:
            self.fields['current_occupancy'].help_text = str(_("Current number of birds in this aviary"))
    
    def clean(self):
        """Custom validation for the form."""
        cleaned_data = super().clean()
        capacity = cleaned_data.get('capacity')
        current_occupancy = cleaned_data.get('current_occupancy')
        
        # Validate that occupancy doesn't exceed capacity
        if capacity is not None and current_occupancy is not None:
            if current_occupancy > capacity:
                raise forms.ValidationError({
                    'current_occupancy': _('Current occupancy cannot exceed capacity.')
                })
        
        return cleaned_data
