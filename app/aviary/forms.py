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
            "description",
            "condition",
            "last_ward_round",
            "comment",
        ]
        labels = {
            "description": _("Beschreibung"),
            "condition": _("Zustand"),
            "last_ward_round": _("Letzte Visite"),
            "comment": _("Bemerkungen"),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        self.fields['description'].required = True
        self.fields['condition'].required = True
        self.fields['last_ward_round'].required = True
        
        # Set today as default for last_ward_round
        if not self.instance.pk and 'last_ward_round' in self.fields:
            self.fields['last_ward_round'].initial = date.today
    
    def clean(self):
        """Custom validation for the form."""
        cleaned_data = super().clean()
        return cleaned_data
