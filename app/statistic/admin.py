from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import StatisticIndividual, StatisticYearGroup, StatisticTotalGroup, StatisticConfiguration


@admin.register(StatisticIndividual)
class StatisticIndividualAdmin(admin.ModelAdmin):
    """
    Admin-Interface für die Verwaltung von Statistik-Individuen (Vogelarten-Balkendiagramme).
    """
    list_display = [
        'name', 
        'color_display', 
        'order', 
        'status_count', 
        'is_active',
        'updated'
    ]
    list_filter = ['is_active', 'created', 'updated']
    search_fields = ['name']
    ordering = ['order', 'name']
    
    fieldsets = (
        (_("Grundeinstellungen"), {
            'fields': ('name', 'color', 'order', 'is_active')
        }),
        (_("Status-Zuordnung"), {
            'fields': ('status_list',),
            'description': _("Wählen Sie die BirdStatus aus, die zu dieser Gruppe gehören sollen.")
        }),
    )
    
    filter_horizontal = ('status_list',)
    
    def color_display(self, obj):
        """Zeigt die Farbe als farbigen Block an."""
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.color
        )
    color_display.short_description = _("Farbe")
    
    def status_count(self, obj):
        """Zeigt die Anzahl der zugeordneten Status an."""
        count = obj.status_list.count()
        return f"{count} Status"
    status_count.short_description = _("Anzahl Status")
    
    def get_form(self, request, obj=None, **kwargs):
        """Bereite das Form für erweiterte Farbauswahl vor."""
        # Get the form class first
        form = super().get_form(request, obj, **kwargs)
        # Set default color for new objects
        if obj is None and 'color' in form.base_fields:
            form.base_fields['color'].initial = '#28a745'
        return form
    
    class Media:
        css = {
            'all': (
                'admin/css/widgets.css',
                'admin/css/statistic_admin.css',
            )
        }
        js = (
            'admin/js/admin/RelatedObjectLookups.js',
            'admin/js/statistic_color_picker.js',
        )


@admin.register(StatisticYearGroup)
class StatisticYearGroupAdmin(admin.ModelAdmin):
    """
    Admin-Interface für die Verwaltung von Jahres-Statistik-Gruppen.
    """
    list_display = [
        'name', 
        'color_display', 
        'order', 
        'status_count', 
        'is_active',
        'updated'
    ]
    list_filter = ['is_active', 'created', 'updated']
    search_fields = ['name']
    ordering = ['order', 'name']
    
    fieldsets = (
        (_("Grundeinstellungen"), {
            'fields': ('name', 'color', 'order', 'is_active'),
            'description': _("Konfiguration für die Jahresstatistik-Karten")
        }),
        (_("Status-Zuordnung"), {
            'fields': ('status_list',),
            'description': _("Welche BirdStatus sollen in dieser Jahresgruppe zusammengefasst werden?")
        }),
    )
    
    filter_horizontal = ('status_list',)
    
    def color_display(self, obj):
        """Zeigt die Farbe als farbigen Block an."""
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.color
        )
    color_display.short_description = _("Farbe")
    
    def status_count(self, obj):
        """Zeigt die Anzahl der zugeordneten Status an."""
        count = obj.status_list.count()
        return f"{count} Status"
    status_count.short_description = _("Anzahl Status")
    
    def get_form(self, request, obj=None, **kwargs):
        """Bereite das Form für erweiterte Farbauswahl vor."""
        # Get the form class first
        form = super().get_form(request, obj, **kwargs)
        # Set default color for new objects
        if obj is None and 'color' in form.base_fields:
            form.base_fields['color'].initial = '#007bff'
        return form
    
    class Media:
        css = {
            'all': (
                'admin/css/widgets.css',
                'admin/css/statistic_admin.css',
            )
        }
        js = (
            'admin/js/admin/RelatedObjectLookups.js',
            'admin/js/statistic_color_picker.js',
        )


@admin.register(StatisticTotalGroup)
class StatisticTotalGroupAdmin(admin.ModelAdmin):
    """
    Admin-Interface für die Verwaltung von Gesamt-Statistik-Gruppen.
    """
    list_display = [
        'name', 
        'color_display', 
        'order', 
        'status_count', 
        'is_active',
        'updated'
    ]
    list_filter = ['is_active', 'created', 'updated']
    search_fields = ['name']
    ordering = ['order', 'name']
    
    fieldsets = (
        (_("Grundeinstellungen"), {
            'fields': ('name', 'color', 'order', 'is_active'),
            'description': _("Konfiguration für die Gesamtstatistik-Karten")
        }),
        (_("Status-Zuordnung"), {
            'fields': ('status_list',),
            'description': _("Welche BirdStatus sollen in dieser Gesamtgruppe zusammengefasst werden?")
        }),
    )
    
    filter_horizontal = ('status_list',)
    
    def color_display(self, obj):
        """Zeigt die Farbe als farbigen Block an."""
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.color
        )
    color_display.short_description = _("Farbe")
    
    def status_count(self, obj):
        """Zeigt die Anzahl der zugeordneten Status an."""
        count = obj.status_list.count()
        return f"{count} Status"
    status_count.short_description = _("Anzahl Status")
    
    def get_form(self, request, obj=None, **kwargs):
        """Bereite das Form für erweiterte Farbauswahl vor."""
        # Get the form class first
        form = super().get_form(request, obj, **kwargs)
        # Set default color for new objects
        if obj is None and 'color' in form.base_fields:
            form.base_fields['color'].initial = '#28a745'
        return form
    
    class Media:
        css = {
            'all': (
                'admin/css/widgets.css',
                'admin/css/statistic_admin.css',
            )
        }
        js = (
            'admin/js/admin/RelatedObjectLookups.js',
            'admin/js/statistic_color_picker.js',
        )


@admin.register(StatisticConfiguration)
class StatisticConfigurationAdmin(admin.ModelAdmin):
    """
    Admin-Interface für die Verwaltung der Statistik-Konfiguration.
    """
    list_display = [
        'get_name',
        'show_year_total_patients', 
        'show_total_patients',
        'show_percentages', 
        'show_absolute_numbers',
        'is_active',
        'updated'
    ]
    list_filter = ['is_active', 'show_percentages', 'show_absolute_numbers', 'show_year_total_patients', 'show_total_patients']
    
    fieldsets = (
        (_("Jahresstatistik"), {
            'fields': ('show_year_total_patients',),
            'description': _("Konfiguration für die Anzeige der aktuellen Jahresstatistik")
        }),
        (_("Gesamtstatistik"), {
            'fields': ('show_total_patients',),
            'description': _("Konfiguration für die Anzeige der Gesamtstatistik")
        }),
        (_("Anzeige-Optionen"), {
            'fields': ('show_percentages', 'show_absolute_numbers'),
            'description': _("Allgemeine Anzeige-Optionen für Balkendiagramme")
        }),
        (_("System"), {
            'fields': ('is_active',),
            'description': _("Systemeinstellungen")
        }),
    )
    
    def get_name(self, obj):
        return "Statistik Konfiguration"
    get_name.short_description = _("Konfiguration")
    
    def has_add_permission(self, request):
        """Erlaube nur eine Konfiguration."""
        return StatisticConfiguration.objects.count() == 0
    
    def has_delete_permission(self, request, obj=None):
        """Verhindert das Löschen der Konfiguration."""
        return False
