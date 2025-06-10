from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Emailadress


class EmailaddressForm(forms.ModelForm):
    """Form for editing email addresses with notification categories."""
    class Meta:
        model = Emailadress
        fields = [
            "email_address",
            "is_naturschutzbehoerde",
            "is_jagdbehoerde", 
            "is_wildvogelhilfe_team",
        ]
        labels = {
            "email_address": _("E-Mail-Adresse"),
            "is_naturschutzbehoerde": _("Naturschutzbehörde"),
            "is_jagdbehoerde": _("Jagdbehörde"),
            "is_wildvogelhilfe_team": _("Wildvogelhilfe-Team"),
        }
        help_texts = {
            "is_naturschutzbehoerde": _("Diese Adresse für Naturschutzbehörden-Benachrichtigungen verwenden"),
            "is_jagdbehoerde": _("Diese Adresse für Jagdbehörden-Benachrichtigungen verwenden"),
            "is_wildvogelhilfe_team": _("Diese Adresse für Wildvogelhilfe-Team-Benachrichtigungen verwenden"),
        }
        widgets = {
            "email_address": forms.EmailInput(attrs={"class": "form-control"}),
        }
