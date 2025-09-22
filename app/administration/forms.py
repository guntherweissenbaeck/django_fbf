from __future__ import annotations

from django import forms

from .models import BackupDestination, SMTPConfiguration


class BackupRunForm(forms.Form):
    destination = forms.ModelChoiceField(
        queryset=BackupDestination.objects.all(),
        label="Backup-Ziel",
        help_text="Wählen Sie das Ziel, auf das das Backup hochgeladen werden soll.",
    )


class BackupRestoreForm(forms.Form):
    backup_file = forms.FileField(
        label="Backup-Datei",
        help_text="PostgreSQL Dump (.sql oder .dump)."
    )

    def clean_backup_file(self):
        uploaded = self.cleaned_data["backup_file"]
        if uploaded.size == 0:
            raise forms.ValidationError("Die Datei ist leer.")
        if not uploaded.name.endswith((".sql", ".dump", ".bak")):
            raise forms.ValidationError("Nur SQL-/Dump-Dateien werden unterstützt.")
        return uploaded


class SMTPConfigurationAdminForm(forms.ModelForm):
    password = forms.CharField(
        label="Passwort",
        required=False,
        widget=forms.PasswordInput(render_value=False),
    )

    class Meta:
        model = SMTPConfiguration
        fields = [
            "name",
            "email_backend",
            "host",
            "port",
            "username",
            "password",
            "use_tls",
            "use_ssl",
            "default_from_email",
            "timeout",
        ]

    def clean(self):
        cleaned = super().clean()
        use_tls = cleaned.get("use_tls")
        use_ssl = cleaned.get("use_ssl")
        if use_tls and use_ssl:
            raise forms.ValidationError("TLS und SSL können nicht gleichzeitig aktiv sein.")
        return cleaned
