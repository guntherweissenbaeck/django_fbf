from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from datetime import date, timedelta
from .models import AutomaticReport, ReportLog
from .services import ReportGenerator


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
    actions = ['send_report_now']
    
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
    
    def send_report_now(self, request, queryset):
        """Send selected reports immediately."""
        sent_count = 0
        error_count = 0
        skipped_count = 0
        
        for report in queryset:
            if not report.is_active:
                messages.warning(
                    request, 
                    f"Report '{report.name}' ist deaktiviert und wurde übersprungen."
                )
                skipped_count += 1
                continue
                
            if not report.email_addresses.exists():
                messages.warning(
                    request, 
                    f"Report '{report.name}' hat keine E-Mail-Adressen und wurde übersprungen."
                )
                skipped_count += 1
                continue
            
            # Get email addresses
            email_addresses = [addr.email_address for addr in report.email_addresses.all()]
            
            # Calculate date range based on frequency
            today = date.today()
            if report.frequency == 'weekly':
                date_from = today - timedelta(days=7)
                range_description = "letzte 7 Tage"
            elif report.frequency == 'monthly':
                # Go back one month
                if today.month == 1:
                    date_from = today.replace(year=today.year-1, month=12, day=1)
                else:
                    date_from = today.replace(month=today.month-1, day=1)
                range_description = "letzter Monat"
            elif report.frequency == 'quarterly':
                # Go back three months
                if today.month <= 3:
                    date_from = today.replace(year=today.year-1, month=today.month+9, day=1)
                else:
                    date_from = today.replace(month=today.month-3, day=1)
                range_description = "letztes Quartal"
            else:
                date_from = today - timedelta(days=30)  # Default to 30 days
                range_description = "letzte 30 Tage"
            
            # Generate and send report
            try:
                generator = ReportGenerator(
                    date_from=date_from,
                    date_to=today,
                    include_naturschutzbehoerde=report.include_naturschutzbehoerde,
                    include_jagdbehoerde=report.include_jagdbehoerde
                )
                
                report_log, success, error_msg = generator.send_email_report(
                    email_addresses=email_addresses,
                    automatic_report=report
                )
                
                if success:
                    # Update last_sent timestamp
                    report.last_sent = today
                    report.save(update_fields=['last_sent'])
                    sent_count += 1
                    
                    # Success message with details
                    messages.success(
                        request, 
                        f"Report '{report.name}' erfolgreich gesendet "
                        f"({range_description}, {report_log.patient_count} Patienten, "
                        f"{len(email_addresses)} Empfänger)."
                    )
                else:
                    error_count += 1
                    messages.error(
                        request, 
                        f"Fehler beim Senden von '{report.name}': {error_msg}"
                    )
                    
            except Exception as e:
                error_count += 1
                messages.error(
                    request, 
                    f"Unerwarteter Fehler bei '{report.name}': {str(e)}"
                )
        
        # Show summary message
        if sent_count > 0:
            messages.success(
                request, 
                f"Zusammenfassung: {sent_count} Report(s) erfolgreich gesendet"
                + (f", {skipped_count} übersprungen" if skipped_count > 0 else "")
                + (f", {error_count} Fehler" if error_count > 0 else "") + "."
            )
        elif skipped_count > 0 and error_count == 0:
            messages.info(
                request, 
                f"Alle {skipped_count} ausgewählten Reports wurden übersprungen (deaktiviert oder keine E-Mail-Adressen)."
            )
        elif error_count > 0 and sent_count == 0:
            messages.error(
                request, 
                f"Alle {error_count} Reports konnten nicht gesendet werden."
            )
    
    send_report_now.short_description = _("Ausgewählte Reports sofort senden")


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
