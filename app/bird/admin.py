from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Q
from django.http import JsonResponse
from datetime import date

from .models import Bird, FallenBird, BirdStatus, Circumstance, BirdRegion, GeocodeAttempt, WildvogelhilfeCenter
from .geocode_utils import geocode_place_to_region


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
        'region',
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
        'region__name',
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
            'fields': ('date_found', 'place', 'region', 'find_circumstances', 'diagnostic_finding', 'finder'),
            'description': _('Region wird automatisch vorgeschlagen oder kann aus der Liste gewählt werden.')
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

    actions = ['backfill_regions']

    def backfill_regions(self, request, queryset):
        """Admin-Aktion: Fehlende Regionen per Geocoding nachtragen.

        Für jeden ausgewählten Patienten ohne gesetzte Region wird versucht,
        aus dem Feld `place` eine Region zu bestimmen. Erfolgreiche Zuordnungen
        werden gesetzt und gezählt; Fehler werden gesammelt und am Ende als
        Hinweis angezeigt.
        """
        success_count = 0
        error_items = []
        for fb in queryset:
            if fb.region_id:  # bereits vorhanden
                continue
            if not fb.place:
                error_items.append((fb.bird_identifier or fb.id, 'kein Fundort'))
                continue
            region_obj, attempts, err = geocode_place_to_region(fb.place)
            if region_obj and not err:
                fb.region = region_obj
                fb.save(update_fields=['region'])
                success_count += 1
            else:
                error_items.append((fb.bird_identifier or fb.id, err or 'unbekannter Fehler'))
        msg = f"Regionen nachgetragen: {success_count}."
        if error_items:
            details = ', '.join(f"{ident}:{reason}" for ident, reason in error_items[:10])
            if len(error_items) > 10:
                details += f" (+{len(error_items)-10} weitere)"
            msg += f" Fehler bei {len(error_items)} Patienten: {details}";
        self.message_user(request, msg)
    backfill_regions.short_description = _("Regionen nachtragen (Geocoding)")

    # ===== Helper display methods required by list_display / readonly_fields =====
    def bird_identifier_display(self, obj):
        return obj.bird_identifier or '-'
    bird_identifier_display.short_description = _('Patient ID')
    bird_identifier_display.admin_order_field = 'bird_identifier'

    def bird_species(self, obj):
        if obj.bird:
            return obj.bird.name
        return '-'
    bird_species.short_description = _('Vogelart')
    bird_species.admin_order_field = 'bird__name'

    def age_sex_display(self, obj):
        parts = []
        if obj.age:
            parts.append(obj.get_age_display())
        if obj.sex:
            parts.append(obj.get_sex_display())
        return ' | '.join(parts) if parts else '-'
    age_sex_display.short_description = _('Alter | Geschlecht')

    def status_display(self, obj):
        if obj.status:
            return obj.status.description
        return '-'
    status_display.short_description = _('Status')
    status_display.admin_order_field = 'status__description'

    def location_display(self, obj):
        if obj.place:
            return obj.place if len(obj.place) < 40 else obj.place[:37] + '…'
        return '-'
    location_display.short_description = _('Fundort')
    location_display.admin_order_field = 'place'

    def days_in_care(self, obj):
        if obj.date_found:
            end_date = obj.patient_file_close_date or date.today()
            return (end_date - obj.date_found).days
        return 0
    days_in_care.short_description = _('Tage in Pflege')

    def close_date_display(self, obj):
        if obj.patient_file_close_date:
            return obj.patient_file_close_date.strftime('%d.%m.%Y')
        return '-'
    close_date_display.short_description = _('Akte geschlossen am')
    close_date_display.admin_order_field = 'patient_file_close_date'

    def user_display(self, obj):
        if obj.user:
            return obj.user.username
        return '-'
    user_display.short_description = _('Bearbeiter')
    user_display.admin_order_field = 'user__username'

    def edit_link(self, obj):  # pragma: no cover - UI helper
        url = reverse('bird_single', args=[obj.id])
        return format_html('<a href="{}" class="button">Bearbeiten</a>', url)
    edit_link.short_description = _('Aktion')

    def days_in_care_calculation(self, obj):
        if obj.date_found:
            end_date = obj.patient_file_close_date or date.today()
            days = (end_date - obj.date_found).days
            return f"{days} Tage (von {obj.date_found.strftime('%d.%m.%Y')} bis {end_date.strftime('%d.%m.%Y')})"
        return '—'
    days_in_care_calculation.short_description = _('Verweildauer (Detail)')

@admin.register(BirdRegion)
class BirdRegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'referenzierte_patienten', 'created_at', 'updated_at')
    search_fields = ('name', 'slug')
    ordering = ('name',)
    readonly_fields = ('slug', 'created_at', 'updated_at')
    fields = ('name', 'slug', 'created_at', 'updated_at')

    def get_urls(self):  # fügt Korrektur-URL hinzu
        from django.urls import path
        urls = super().get_urls()
        custom = [
            path('korrektur/', self.admin_site.admin_view(self.correct_regions_view), name='birdregion_correct_regions'),
            path('korrektur/save/', self.admin_site.admin_view(self.correct_region_ajax), name='birdregion_correct_region_ajax'),
        ]
        return custom + urls

    def correct_regions_view(self, request):
        """Zeigt eine Tabelle mit Patienten (Fundort vs aktuelle Region) zur schnellen manuellen Korrektur.

        POST verarbeitet ein Formular mit mehreren Zeilen: Keys pattern row-<index>-patient, row-<index>-region.
        """
        from django.shortcuts import render, redirect
        from django.contrib import messages
        # Patienten-Sample (Begrenzung auf 300 neueste für schnelle Bearbeitung)
        # Filter
        filter_mode = request.GET.get('filter', 'all')  # all | no_region | short_place
        base_qs = FallenBird.objects.select_related('region', 'bird').order_by('-created')
        if filter_mode == 'no_region':
            base_qs = base_qs.filter(region__isnull=True)
        # Für short_place später Python-Filter
        items = list(base_qs[:2000])  # Obergrenze vor Python-Filter
        if filter_mode == 'short_place':
            items = [fb for fb in items if fb.place and len(fb.place.strip()) < 15]
        # Pagination
        from django.core.paginator import Paginator
        page_number = request.GET.get('page', '1')
        # Page size aus Parameter (Fallback 50)
        try:
            page_size = int(request.GET.get('page_size', '50'))
        except ValueError:
            page_size = 50
        if page_size not in [10,25,50,100,200]:
            page_size = 50
        paginator = Paginator(items, page_size)
        page_obj = paginator.get_page(page_number)
        qs = page_obj.object_list
        rows = []
        for fb in qs:
            rows.append({
                'id': str(fb.id),
                'identifier': fb.bird_identifier or '',
                'bird': fb.bird.name if fb.bird else '',
                'place': fb.place or '',
                'region': fb.region.name if fb.region else '',
            })
        if request.method == 'POST':
            changed = 0
            for idx in range(len(rows)):
                patient_id = request.POST.get(f'row-{idx}-patient')
                new_region = (request.POST.get(f'row-{idx}-region') or '').strip()
                if not patient_id:
                    continue
                try:
                    fb = FallenBird.objects.get(id=patient_id)
                except FallenBird.DoesNotExist:
                    continue
                current_name = fb.region.name if fb.region else ''
                if new_region == current_name:
                    continue
                if not new_region:  # Region entfernen
                    fb.region = None
                    fb.save(update_fields=['region'])
                    changed += 1
                else:
                    # Falls bereits eine Region mit diesem Namen existiert, nutze sie direkt.
                    existing = BirdRegion.objects.filter(name=new_region).first()
                    if existing:
                        region_obj = existing
                    else:
                        region_obj = BirdRegion.objects.create(name=new_region)
                    fb.region = region_obj
                    fb.save(update_fields=['region'])
                    changed += 1
            msg_txt = f'Regionen aktualisiert: {changed} Änderungen gespeichert.'
            self.message_user(request, msg_txt, level='success')
            return redirect('admin:birdregion_correct_regions')
        context = {
            **self.admin_site.each_context(request),
            'title': _('Regionen korrigieren'),
            'rows': rows,
            'filter_mode': filter_mode,
            'page_obj': page_obj,
            'paginator': paginator,
            'existing_regions': list(BirdRegion.objects.values_list('name', flat=True)),
            'page_size': page_size,
            'page_sizes': [10, 25, 50, 100, 200],
            'opts': self.model._meta,
        }
        return render(request, 'admin/bird/birdregion/correct_regions.html', context)

    def correct_region_ajax(self, request):
        if request.method != 'POST':
            return JsonResponse({'error':'POST required'}, status=405)
        patient_id = request.POST.get('patient_id')
        new_region = (request.POST.get('region') or '').strip()
        try:
            fb = FallenBird.objects.get(id=patient_id)
        except FallenBird.DoesNotExist:
            return JsonResponse({'error':'patient not found'}, status=404)
        old_region = fb.region.name if fb.region else ''
        if new_region == old_region:
            return JsonResponse({'changed': False, 'region': old_region})
        if not new_region:
            fb.region = None
            fb.save(update_fields=['region'])
            return JsonResponse({'changed': True, 'region': ''})
        existing = BirdRegion.objects.filter(name=new_region).first()
        if existing:
            fb.region = existing
            fb.save(update_fields=['region'])
            return JsonResponse({'changed': True, 'region': existing.name, 'existing': True})
        region_obj = BirdRegion.objects.create(name=new_region)
        fb.region = region_obj
        fb.save(update_fields=['region'])
        return JsonResponse({'changed': True, 'region': region_obj.name, 'created': True})

    def referenzierte_patienten(self, obj):
        return obj.fallen_birds.count()
    referenzierte_patienten.short_description = _('# Patienten')

    def changelist_view(self, request, extra_context=None):
        center = WildvogelhilfeCenter.get_active()
        if request.method == 'POST' and 'center_latitude' in request.POST:
            lat = request.POST.get('center_latitude')
            lon = request.POST.get('center_longitude')
            address = request.POST.get('center_address','')
            try:
                lat_f = float(lat)
                lon_f = float(lon)
                if center:
                    center.latitude = lat_f
                    center.longitude = lon_f
                    center.address = address
                    center.save(update_fields=['latitude','longitude','address','updated_at'])
                else:
                    center = WildvogelhilfeCenter.objects.create(latitude=lat_f, longitude=lon_f, address=address)
                self.message_user(request, _('Standort der Wildvogelhilfe aktualisiert.'))
            except (TypeError, ValueError):
                self.message_user(request, _('Ungültige Koordinaten.'), level='error')
        extra_context = extra_context or {}
        extra_context['wildvogelhilfe_center'] = center
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(GeocodeAttempt)
class GeocodeAttemptAdmin(admin.ModelAdmin):
    list_display = ("query", "success", "status_code", "city", "county", "state", "created_at")
    list_filter = ("success", "status_code", "city", "county", "state")
    search_fields = ("query", "city", "county", "state", "error")
    readonly_fields = ("query", "attempted_queries", "success", "status_code", "city", "county", "state", "error", "created_at")
    ordering = ("-created_at",)
    
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
    
    # Kein erweitertes get_queryset notwendig; Model hat keine FK für select_related.


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
        super().save_model(request, obj, form, change)

@admin.register(WildvogelhilfeCenter)
class WildvogelhilfeCenterAdmin(admin.ModelAdmin):
    list_display = ('address','latitude','longitude','created_at','updated_at')
    readonly_fields = ('created_at','updated_at')
    fields = ('address','latitude','longitude','created_at','updated_at')


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
