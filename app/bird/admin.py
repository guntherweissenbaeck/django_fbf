from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Q
from datetime import date

from .models import Bird, FallenBird, BirdStatus, Circumstance


@admin.register(FallenBird)
class FallenBirdAdmin(admin.ModelAdmin):
    """Comprehensive admin interface for all bird patients (including closed cases)."""
    
    list_display = [
        'bird_identifier_display',
        'bird_species',
        'age_sex_display', 
        'date_found',
        'status_display',
        'location_display',
        'days_in_care',
        'close_date_display',
        'user_display',
        'edit_link'
    ]
    
    list_filter = [
        'status',
        'bird__melden_an_jagdbehoerde',
        'bird__melden_an_naturschutzbehoerde', 
        'age',
        'sex',
        'date_found',
        'patient_file_close_date',
        'created',
        'user',
        'aviary'
    ]
    
    search_fields = [
        'bird_identifier',
        'bird__name',
        'place',
        'finder',
        'diagnostic_finding',
        'comment',
        'sent_to',
        'release_location'
    ]
    
    readonly_fields = [
        'created',
        'updated',
        'days_in_care_calculation'
    ]
    
    fieldsets = (
        (_('Patientenidentifikation'), {
            'fields': ('bird_identifier', 'bird', 'age', 'sex')
        }),
        (_('Fundinformationen'), {
            'fields': ('date_found', 'place', 'find_circumstances', 'diagnostic_finding', 'finder')
        }),
        (_('Aktueller Status'), {
            'fields': ('status', 'aviary', 'user')
        }),
        (_('Statusspezifische Felder'), {
            'fields': ('sent_to', 'release_location'),
            'description': _('Diese Felder werden je nach Status automatisch ein-/ausgeblendet.')
        }),
        (_('Aktenschließung'), {
            'fields': ('patient_file_close_date',),
            'description': _('Wird automatisch gesetzt bei Status "Ausgewildert", "Übermittelt" oder "Verstorben".')
        }),
        (_('Zusätzliche Informationen'), {
            'fields': ('comment',),
            'classes': ('collapse',)
        }),
        (_('Metadaten'), {
            'fields': ('created', 'updated', 'days_in_care_calculation'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'date_found'
    ordering = ['-date_found', '-created']
    list_per_page = 50
    
    def bird_identifier_display(self, obj):
        """Display patient identifier with link to regular edit page."""
        if obj.bird_identifier:
            url = reverse('bird_single', args=[obj.id])
            return format_html(
                '<a href="{}" target="_blank"><strong>{}</strong></a>',
                url, obj.bird_identifier
            )
        return '-'
    bird_identifier_display.short_description = _('Patient ID')
    bird_identifier_display.admin_order_field = 'bird_identifier'
    
    def bird_species(self, obj):
        """Display bird species with hunting status indicators."""
        if obj.bird:
            parts = [obj.bird.name]
            
            if obj.bird.melden_an_jagdbehoerde:
                parts.append('<span style="color: #dc3545;" title="Jagdbare Art">🎯</span>')
            if obj.bird.melden_an_naturschutzbehoerde:
                parts.append('<span style="color: #28a745;" title="Naturschutz">🌿</span>')
            
            return format_html(' '.join(parts))
        return '-'
    bird_species.short_description = _('Vogelart')
    bird_species.admin_order_field = 'bird__name'
    
    def age_sex_display(self, obj):
        """Combined age and sex display."""
        parts = []
        if obj.age:
            parts.append(obj.get_age_display())
        if obj.sex:
            parts.append(obj.get_sex_display())
        return ' | '.join(parts) if parts else '-'
    age_sex_display.short_description = _('Alter | Geschlecht')
    
    def status_display(self, obj):
        """Status with color coding."""
        if obj.status:
            colors = {
                'In Behandlung': '#17a2b8',
                'In Auswilderung': '#ffc107', 
                'Ausgewildert': '#28a745',
                'Übermittelt': '#6f42c1',
                'Verstorben': '#dc3545'
            }
            color = colors.get(obj.status.description, '#6c757d')
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, obj.status.description
            )
        return '-'
    status_display.short_description = _('Status')
    status_display.admin_order_field = 'status__description'
    
    def location_display(self, obj):
        """Display location with truncation."""
        if obj.place:
            if len(obj.place) > 30:
                return f"{obj.place[:27]}..."
            return obj.place
        return '-'
    location_display.short_description = _('Fundort')
    location_display.admin_order_field = 'place'
    
    def days_in_care(self, obj):
        """Calculate days in care."""
        if obj.date_found:
            end_date = obj.patient_file_close_date or date.today()
            days = (end_date - obj.date_found).days
            
            if obj.patient_file_close_date:
                # Case closed
                return format_html(
                    '<span style="color: #6c757d;">{} Tage</span>',
                    days
                )
            else:
                # Still in care
                color = '#dc3545' if days > 365 else '#ffc107' if days > 90 else '#28a745'
                return format_html(
                    '<span style="color: {}; font-weight: bold;">{} Tage</span>',
                    color, days
                )
        return '-'
    days_in_care.short_description = _('aktuelle Verweildauer')
    
    def close_date_display(self, obj):
        """Display close date with status."""
        if obj.patient_file_close_date:
            return format_html(
                '<span style="color: #6c757d;">{}</span>',
                obj.patient_file_close_date.strftime('%d.%m.%Y')
            )
        elif obj.status and obj.status.description in ['Ausgewildert', 'Übermittelt', 'Verstorben']:
            return format_html(
                '<span style="color: #ffc107;">⚠️ Fehlt</span>'
            )
        return format_html('<span style="color: #28a745;">Offen</span>')
    close_date_display.short_description = _('Akte geschlossen')
    close_date_display.admin_order_field = 'patient_file_close_date'
    
    def user_display(self, obj):
        """Display assigned user."""
        if obj.user:
            return obj.user.username
        return format_html('<span style="color: #ffc107;">Nicht zugewiesen</span>')
    user_display.short_description = _('Bearbeiter')
    user_display.admin_order_field = 'user__username'
    
    def edit_link(self, obj):
        """Link to regular edit page."""
        url = reverse('bird_single', args=[obj.id])
        return format_html(
            '<a href="{}" class="button" target="_blank">Bearbeiten</a>',
            url
        )
    edit_link.short_description = _('Aktionen')
    
    def days_in_care_calculation(self, obj):
        """Detailed calculation display for readonly field."""
        if obj.date_found:
            end_date = obj.patient_file_close_date or date.today()
            days = (end_date - obj.date_found).days
            
            status = "geschlossen" if obj.patient_file_close_date else "offen"
            end_date_str = end_date.strftime('%d.%m.%Y')
            found_date_str = obj.date_found.strftime('%d.%m.%Y')
            
            return f"{days} Tage (von {found_date_str} bis {end_date_str}, Akte {status})"
        return "Kein Funddatum vorhanden"
    days_in_care_calculation.short_description = _('Verweildauer (Detail)')
    
    def get_queryset(self, request):
        """Include all birds, regardless of status (including closed cases)."""
        return super().get_queryset(request).select_related(
            'bird', 'status', 'aviary', 'user', 'find_circumstances'
        )
    
    def save_model(self, request, obj, form, change):
        """Set user if not already set."""
        if not change and not obj.user:  # Creating new object without user
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Bird)
class BirdAdmin(admin.ModelAdmin):
    list_display = ["name", "species_indicators", "notification_settings"]
    list_filter = ["melden_an_naturschutzbehoerde", "melden_an_jagdbehoerde", "melden_an_wildvogelhilfe_team"]
    search_fields = ["name", "species"]
    fields = ('name', 'description', 'species', 'melden_an_naturschutzbehoerde', 'melden_an_jagdbehoerde', 'melden_an_wildvogelhilfe_team')
    ordering = ['name']
    
    def species_indicators(self, obj):
        """Display species with visual indicators."""
        indicators = []
        if obj.melden_an_jagdbehoerde:
            indicators.append('<span style="color: #dc3545;" title="Jagdbare Art">🎯 Jagdbar</span>')
        if obj.melden_an_naturschutzbehoerde:
            indicators.append('<span style="color: #28a745;" title="Naturschutz">🌿 Naturschutz</span>')
        
        return format_html(' | '.join(indicators)) if indicators else '-'
    species_indicators.short_description = _('Kategorien')
    
    def notification_settings(self, obj):
        """Display notification settings."""
        settings = []
        if obj.melden_an_naturschutzbehoerde:
            settings.append("Naturschutz")
        if obj.melden_an_jagdbehoerde:
            settings.append("Jagd")
        if obj.melden_an_wildvogelhilfe_team:
            settings.append("Team")
        
        return ', '.join(settings) if settings else 'Keine'
    notification_settings.short_description = _('Benachrichtigungen')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by when creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BirdStatus)
class BirdStatusAdmin(admin.ModelAdmin):
    list_display = ["id", "description", "usage_count"]
    ordering = ["id"]
    
    def usage_count(self, obj):
        """Show how many birds have this status."""
        count = FallenBird.objects.filter(status=obj).count()
        return f"{count} Patienten"
    usage_count.short_description = _('Verwendung')


@admin.register(Circumstance)
class CircumstanceAdmin(admin.ModelAdmin):
    list_display = ["description", "usage_count"]
    ordering = ["description"]
    
    def usage_count(self, obj):
        """Show how many birds have this circumstance."""
        count = FallenBird.objects.filter(find_circumstances=obj).count()
        return f"{count} Patienten"
    usage_count.short_description = _('Verwendung')
