from django import forms
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta


class DateInput(forms.DateInput):
    input_type = "date"


class CustomExportForm(forms.Form):
    """Form for custom bird data export with configurable columns and filters."""
    
    # Date range
    date_from = forms.DateField(
        label=_("Von Datum"),
        widget=DateInput(),
        initial=lambda: date.today() - timedelta(days=365),
        help_text=_("Startdatum für den Export (Funddatum der Vögel)")
    )
    
    date_to = forms.DateField(
        label=_("Bis Datum"),
        widget=DateInput(),
        initial=date.today,
        help_text=_("Enddatum für den Export (Funddatum der Vögel)")
    )
    
    # Filter options
    filter_huntable_species = forms.ChoiceField(
        label=_("Arten-Filter"),
        choices=[
            ('all', _('Alle Arten exportieren')),
            ('huntable_only', _('Nur jagdbare Arten exportieren')),
            ('non_huntable_only', _('Nur nicht-jagdbare Arten exportieren')),
        ],
        initial='all',
        widget=forms.RadioSelect,
        help_text=_("Welche Arten sollen exportiert werden?")
    )
    
    # Column selection
    include_date_found = forms.BooleanField(
        label=_("Funddatum"),
        initial=True,
        required=False,
        help_text=_("Datum des Vogelfunds")
    )
    
    include_bird_species = forms.BooleanField(
        label=_("Vogelart"),
        initial=True,
        required=False,
        help_text=_("Name der Vogelart")
    )
    
    include_bird_details = forms.BooleanField(
        label=_("Vogel-Details"),
        initial=True,
        required=False,
        help_text=_("Alter und Geschlecht des Vogels")
    )
    
    include_bird_status = forms.BooleanField(
        label=_("Status"),
        initial=True,
        required=False,
        help_text=_("Aktueller Status des Vogels")
    )
    
    include_location = forms.BooleanField(
        label=_("Fundort"),
        initial=True,
        required=False,
        help_text=_("Ort des Funds")
    )
    
    include_circumstances = forms.BooleanField(
        label=_("Fundumstände"),
        initial=True,
        required=False,
        help_text=_("Umstände des Funds")
    )
    
    include_diagnosis = forms.BooleanField(
        label=_("Diagnose bei Fund"),
        initial=True,
        required=False,
        help_text=_("Erste Diagnose bei Fund")
    )
    
    include_finder_info = forms.BooleanField(
        label=_("Finder-Informationen"),
        initial=False,
        required=False,
        help_text=_("Informationen zum Finder")
    )
    
    include_aviary = forms.BooleanField(
        label=_("Voliere"),
        initial=False,
        required=False,
        help_text=_("Zugewiesene Voliere")
    )
    
    include_sent_to = forms.BooleanField(
        label=_("Übermittelt nach"),
        initial=False,
        required=False,
        help_text=_("Information über Übermittlung")
    )
    
    include_release_location = forms.BooleanField(
        label=_("Auswilderungsort"),
        initial=False,
        required=False,
        help_text=_("Ort der Auswilderung")
    )
    
    include_close_date = forms.BooleanField(
        label=_("Schließungsdatum"),
        initial=False,
        required=False,
        help_text=_("Datum der Aktenschließung")
    )
    
    include_notes = forms.BooleanField(
        label=_("Bemerkungen"),
        initial=False,
        required=False,
        help_text=_("Zusätzliche Bemerkungen")
    )
    
    include_timestamps = forms.BooleanField(
        label=_("Zeitstempel"),
        initial=False,
        required=False,
        help_text=_("Erstellungs- und Änderungsdatum")
    )
    
    include_user_info = forms.BooleanField(
        label=_("Benutzer-Information"),
        initial=False,
        required=False,
        help_text=_("Benutzer der den Datensatz angelegt/bearbeitet hat")
    )

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to:
            if date_from > date_to:
                raise forms.ValidationError(_("Das Startdatum muss vor dem Enddatum liegen."))
                
            # Warnung bei sehr großen Datumsbereichen
            days_diff = (date_to - date_from).days
            if days_diff > 1095:  # 3 Jahre
                self.add_error('date_to', _("Der gewählte Zeitraum ist sehr groß. Dies kann zu langen Ladezeiten führen."))
        
        # Mindestens eine Spalte muss ausgewählt sein
        column_fields = [
            'include_date_found', 'include_bird_species', 'include_bird_details',
            'include_bird_status', 'include_location', 'include_circumstances',
            'include_diagnosis', 'include_finder_info', 'include_aviary',
            'include_sent_to', 'include_release_location', 'include_close_date',
            'include_notes', 'include_timestamps', 'include_user_info'
        ]
        
        if not any(cleaned_data.get(field, False) for field in column_fields):
            raise forms.ValidationError(_("Mindestens eine Spalte muss für den Export ausgewählt werden."))
        
        return cleaned_data
