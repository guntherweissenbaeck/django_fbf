from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from sendemail.models import Emailadress
from .models import AutomaticReport


class DateInput(forms.DateInput):
    input_type = "date"


class ManualReportForm(forms.Form):
    """Form for creating manual reports."""
    
    # Email selection
    email_addresses = forms.ModelMultipleChoiceField(
        queryset=Emailadress.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label=_("E-Mail-Adressen"),
        help_text=_("Wählen Sie E-Mail-Adressen aus oder lassen Sie das Feld leer für nur Download")
    )
    
    custom_email = forms.EmailField(
        required=False,
        label=_("Zusätzliche E-Mail-Adresse"),
        help_text=_("Optional: Geben Sie eine zusätzliche E-Mail-Adresse ein")
    )
    
    # Date range
    date_from = forms.DateField(
        widget=DateInput(format="%Y-%m-%d"),
        label=_("Von"),
        initial=lambda: date.today() - timedelta(days=90),  # 3 months ago
        help_text=_("Startdatum für den Report")
    )
    
    date_to = forms.DateField(
        widget=DateInput(format="%Y-%m-%d"),
        label=_("Bis"),
        initial=date.today,
        help_text=_("Enddatum für den Report")
    )
    
    # Filter options
    include_naturschutzbehoerde = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Naturschutzbehörde"),
        help_text=_("Vögel einschließen, die an Naturschutzbehörde gemeldet werden")
    )
    
    include_jagdbehoerde = forms.BooleanField(
        required=False,
        initial=False,
        label=_("Jagdbehörde"),
        help_text=_("Vögel einschließen, die an Jagdbehörde gemeldet werden")
    )
    
    # Action choice
    action_choices = [
        ('download', _('Nur herunterladen')),
        ('email', _('Per E-Mail senden')),
        ('both', _('Herunterladen und per E-Mail senden')),
    ]
    
    action = forms.ChoiceField(
        choices=action_choices,
        widget=forms.RadioSelect,
        initial='download',
        label=_("Aktion")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default date_from to 3 months ago
        if not self.initial.get('date_from'):
            self.fields['date_from'].initial = date.today() - timedelta(days=90)

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        action = cleaned_data.get('action')
        email_addresses = cleaned_data.get('email_addresses')
        custom_email = cleaned_data.get('custom_email')

        # Validate date range
        if date_from and date_to:
            if date_from > date_to:
                raise ValidationError(
                    _("Das 'Von'-Datum darf nicht nach dem 'Bis'-Datum liegen.")
                )

        # Validate email requirements for email actions
        if action in ['email', 'both']:
            if not email_addresses and not custom_email:
                raise ValidationError(
                    _("Für E-Mail-Versendung müssen E-Mail-Adressen ausgewählt oder eingegeben werden.")
                )
        
        # Validate at least one filter is selected
        include_naturschutz = cleaned_data.get('include_naturschutzbehoerde')
        include_jagd = cleaned_data.get('include_jagdbehoerde')
        
        if not include_naturschutz and not include_jagd:
            raise ValidationError(
                _("Mindestens eine Kategorie (Naturschutzbehörde oder Jagdbehörde) muss ausgewählt werden.")
            )

        return cleaned_data


class AutomaticReportForm(forms.ModelForm):
    """Form for creating/editing automatic reports."""
    
    class Meta:
        model = AutomaticReport
        fields = [
            'name',
            'description',
            'email_addresses',
            'include_naturschutzbehoerde',
            'include_jagdbehoerde',
            'frequency',
            'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'email_addresses': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_addresses'].queryset = Emailadress.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        
        # Validate at least one filter is selected
        include_naturschutz = cleaned_data.get('include_naturschutzbehoerde')
        include_jagd = cleaned_data.get('include_jagdbehoerde')
        
        if not include_naturschutz and not include_jagd:
            raise ValidationError(
                _("Mindestens eine Kategorie (Naturschutzbehörde oder Jagdbehörde) muss ausgewählt werden.")
            )
        
        # Validate email addresses are selected
        email_addresses = cleaned_data.get('email_addresses')
        if not email_addresses:
            raise ValidationError(
                _("Für automatische Reports müssen E-Mail-Adressen ausgewählt werden.")
            )

        return cleaned_data
