from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from .models import AutomaticReport, ReportLog


@admin.register(AutomaticReport)
class AutomaticReportAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'frequency', 
        'is_active', 
        'last_sent', 
        'created_by', 
        'created_at',
        'email_count'
    ]
    list_filter = ['frequency', 'is_active', 'created_at', 'include_naturschutzbehoerde', 'include_jagdbehoerde']
    search_fields = ['name', 'description']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        (_('E-Mail-Einstellungen'), {
            'fields': ('email_addresses',)
        }),
        (_('Filter-Einstellungen'), {
            'fields': ('include_naturschutzbehoerde', 'include_jagdbehoerde')
        }),
        (_('Zeitplan'), {
            'fields': ('frequency',)
        }),
        (_('Metadaten'), {
            'fields': ('created_by', 'created_at', 'updated_at', 'last_sent'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def email_count(self, obj):
        """Show number of email addresses."""
        count = obj.email_addresses.count()
        return f"{count} E-Mail-Adresse(n)"
    email_count.short_description = _("E-Mail-Adressen")


@admin.register(ReportLog)
class ReportLogAdmin(admin.ModelAdmin):
    list_display = [
        'created_at',
        'get_report_type',
        'date_range',
        'patient_count',
        'has_email_recipients',
        'filters_used'
    ]
    list_filter = [
        'automatic_report', 
        'include_naturschutzbehörde', 
        'include_jagdbehörde',
        'created_at'
    ]
    search_fields = ['automatic_report__name']
    readonly_fields = [
        'automatic_report', 'date_from', 'date_to', 'include_naturschutzbehörde',
        'include_jagdbehörde', 'patient_count', 'email_sent_to',
        'created_at', 'csv_file'
    ]
    
    def get_report_type(self, obj):
        """Show report type."""
        if obj.automatic_report:
            return format_html(
                '<span style="color: #007bff;"><i class="fas fa-clock"></i> Automatisch</span>'
            )
        return format_html(
            '<span style="color: #6c757d;"><i class="fas fa-hand-paper"></i> Manuell</span>'
        )
    get_report_type.short_description = _("Typ")
    
    def date_range(self, obj):
        """Show date range."""
        return f"{obj.date_from} - {obj.date_to}"
    date_range.short_description = _("Zeitraum")
    
    def has_email_recipients(self, obj):
        """Show if email was sent."""
        if obj.email_sent_to:
            return format_html(
                '<span style="color: #28a745;"><i class="fas fa-envelope"></i> {} Empfänger</span>',
                len(obj.email_sent_to)
            )
        return format_html(
            '<span style="color: #17a2b8;"><i class="fas fa-download"></i> Download</span>'
        )
    has_email_recipients.short_description = _("Versendung")
    
    def filters_used(self, obj):
        """Show which filters were used."""
        filters = []
        if obj.include_naturschutzbehörde:
            filters.append("Naturschutzbehörde")
        if obj.include_jagdbehörde:
            filters.append("Jagdbehörde")
        return ", ".join(filters) if filters else _("Keine Filter")
    filters_used.short_description = _("Filter")
    
    def has_add_permission(self, request):
        """Disable manual creation of logs."""
        return False


# Custom admin site configuration
admin.site.site_header = "Django FBF Administration"
admin.site.site_title = "Django FBF Admin"
admin.site.index_title = "Willkommen zur Django FBF Administration"
