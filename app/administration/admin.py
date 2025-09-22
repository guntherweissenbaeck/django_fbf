from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html

from .forms import SMTPConfigurationAdminForm
from .models import BackupDestination, BackupLog, SMTPConfiguration


@admin.register(BackupDestination)
class BackupDestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "destination_type", "get_display_endpoint", "remote_path", "updated_at")
    list_filter = ("destination_type", "use_ssl", "verify_ssl")
    search_fields = ("name", "endpoint", "remote_path")
    fieldsets = (
        (None, {"fields": ("name", "destination_type", "endpoint", "port", "remote_path")} ),
        ("Anmeldung", {"fields": ("username", "password")}),
        ("Sicherheit", {"fields": ("use_ssl", "verify_ssl")}),
    )


@admin.register(BackupLog)
class BackupLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "status", "destination", "file_name", "short_message")
    list_filter = ("action", "status", "destination")
    search_fields = ("message", "file_name", "destination__name")
    readonly_fields = ("created_at", "destination", "action", "status", "message", "file_name")

    def has_add_permission(self, request):  # pragma: no cover
        return False

    def has_change_permission(self, request, obj=None):  # pragma: no cover
        return False

    def short_message(self, obj):
        return format_html("{}", obj.message[:80] + ("…" if len(obj.message) > 80 else ""))


@admin.register(SMTPConfiguration)
class SMTPConfigurationAdmin(admin.ModelAdmin):
    form = SMTPConfigurationAdminForm
    change_list_template = "admin/administration/smtpconfiguration/change_list.html"
    list_display = ("name", "host", "port", "username", "is_active", "updated_at")
    list_filter = ("is_active", )
    search_fields = ("name", "host", "username")
    readonly_fields = ("is_active", "updated_at", "created_at")
    fieldsets = (
        (None, {"fields": ("name",)}),
        ("Server", {"fields": ("email_backend", "host", "port", "timeout")} ),
        ("Anmeldung", {"fields": ("username", "password")}),
        ("E-Mail", {"fields": ("default_from_email", "use_tls", "use_ssl")}),
        ("Status", {"fields": ("is_active", "created_at", "updated_at")}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields.pop("is_active", None)
        return form

    def changelist_view(self, request, extra_context=None):
        if request.method == "POST" and request.user.is_staff:
            target_id = request.POST.get("activate")
            if target_id:
                activated = SMTPConfiguration.set_active(target_id)
                if activated:
                    messages.success(
                        request,
                        f"SMTP-Konfiguration '{activated.name}' wurde als Standard aktiviert.",
                    )
                else:
                    messages.error(request, "Ausgewählte SMTP-Konfiguration konnte nicht gefunden werden.")
            return redirect(request.path)

        extra_context = extra_context or {}
        extra_context.update(
            {
                "smtp_configurations": SMTPConfiguration.objects.all(),
                "active_configuration": SMTPConfiguration.get_active(),
                "settings_configuration": {
                    "EMAIL_HOST": settings.EMAIL_HOST,
                    "EMAIL_PORT": getattr(settings, "EMAIL_PORT", None),
                    "EMAIL_HOST_USER": getattr(settings, "EMAIL_HOST_USER", ""),
                    "EMAIL_USE_TLS": getattr(settings, "EMAIL_USE_TLS", False),
                    "EMAIL_USE_SSL": getattr(settings, "EMAIL_USE_SSL", False),
                    "DEFAULT_FROM_EMAIL": getattr(settings, "DEFAULT_FROM_EMAIL", ""),
                },
            }
        )
        return super().changelist_view(request, extra_context=extra_context)
