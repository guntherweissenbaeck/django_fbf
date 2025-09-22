from django.contrib import admin
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
    list_display = ("name", "host", "port", "username", "is_active", "updated_at")
    list_filter = ("is_active", )
    search_fields = ("name", "host", "username")
    fieldsets = (
        (None, {"fields": ("name", "is_active")}),
        ("Server", {"fields": ("email_backend", "host", "port", "timeout")} ),
        ("Anmeldung", {"fields": ("username", "password")}),
        ("E-Mail", {"fields": ("default_from_email", "use_tls", "use_ssl")}),
    )
