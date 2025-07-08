from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime
from bird.models import FallenBird, Bird, BirdStatus, Circumstance
from .models import StatisticIndividual, StatisticYearGroup, StatisticTotalGroup, StatisticConfiguration


class StatisticView(TemplateView):
    template_name = 'statistic/overview.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Aktuelles Jahr
        current_year = timezone.now().year
        
        # Lade aktive Konfiguration
        try:
            config = StatisticConfiguration.objects.get(is_active=True)
        except StatisticConfiguration.DoesNotExist:
            # Fallback: Erstelle Standard-Konfiguration wenn keine vorhanden
            config = StatisticConfiguration.objects.create(
                is_active=True,
                show_year_total_patients=True,
                show_total_patients=True,
                show_percentages=True,
                show_absolute_numbers=True
            )
        
        context['config'] = config
        context['current_year'] = current_year
        
        # 1. Jahresstatistik
        if config.show_year_total_patients:
            patients_this_year = FallenBird.objects.filter(
                date_found__year=current_year
            ).count()
            context['patients_this_year'] = patients_this_year
        
        # Lade aktive Jahres-Gruppen und berechne Statistiken
        year_groups = StatisticYearGroup.objects.filter(is_active=True).order_by('order')
        year_summary = []
        
        for group in year_groups:
            status_ids = list(group.status_list.values_list('id', flat=True))
            year_count = FallenBird.objects.filter(
                date_found__year=current_year,
                status__id__in=status_ids
            ).count()
            
            # Berechne Prozentanteil
            year_percentage = (year_count / patients_this_year * 100) if patients_this_year > 0 else 0
            
            year_summary.append({
                'name': group.name,
                'count': year_count,
                'percentage': round(year_percentage, 1),
                'color': group.color,
                'order': group.order
            })
        
        context['year_summary'] = year_summary
        
        # 2. Gesamtstatistik
        if config.show_total_patients:
            total_patients = FallenBird.objects.count()
            context['total_patients'] = total_patients
        
        # Lade aktive Gesamt-Gruppen und berechne Statistiken
        total_groups = StatisticTotalGroup.objects.filter(is_active=True).order_by('order')
        total_summary = []
        
        for group in total_groups:
            status_ids = list(group.status_list.values_list('id', flat=True))
            total_count = FallenBird.objects.filter(
                status__id__in=status_ids
            ).count()
            
            # Berechne Prozentanteil
            total_percentage = (total_count / total_patients * 100) if total_patients > 0 else 0
            
            total_summary.append({
                'name': group.name,
                'count': total_count,
                'percentage': round(total_percentage, 1),
                'color': group.color,
                'order': group.order
            })
        
        context['total_summary'] = total_summary
        
        # 3. Statistik pro Vogelart (Individuen - dynamisch basierend auf Konfiguration)
        individual_groups = StatisticIndividual.objects.filter(is_active=True).order_by('order')
        context['statistic_individuals'] = individual_groups
        
        bird_stats = []
        for bird in Bird.objects.all():
            fallen_birds = FallenBird.objects.filter(bird=bird)
            total_count = fallen_birds.count()
            
            if total_count > 0:  # Nur Vögel anzeigen, die auch Patienten haben
                bird_data = {
                    'name': bird.name,
                    'species': bird.species or 'Unbekannt',
                    'total': total_count,
                    'groups': []
                }
                
                # Berechne Statistiken für jede konfigurierte Individuen-Gruppe
                for group in individual_groups:
                    status_ids = list(group.status_list.values_list('id', flat=True))
                    group_count = fallen_birds.filter(status__id__in=status_ids).count()
                    group_percentage = (group_count / total_count) * 100 if total_count > 0 else 0
                    
                    bird_data['groups'].append({
                        'name': group.name,
                        'color': group.color,
                        'count': group_count,
                        'percentage': round(group_percentage, 1),
                        'order': group.order
                    })
                
                bird_stats.append(bird_data)
        
        # Sortiere nach Gesamtanzahl (absteigend)
        bird_stats.sort(key=lambda x: x['total'], reverse=True)
        
        # Berechne Balkenbreiten basierend auf der höchsten Vogelart für bessere Visualisierung
        if bird_stats:
            max_count = bird_stats[0]['total']  # Höchste Anzahl (wird 100% der Balkenbreite)
            
            for bird in bird_stats:
                # Berechne Balkenbreite für Gesamtanzahl
                total_bar_width = (bird['total'] / max_count) * 100 if max_count > 0 else 0
                bird['total_bar_width'] = f"{total_bar_width:.1f}".replace(',', '.')
                
                # Berechne Balkenbreiten für jede Gruppe
                for group_data in bird['groups']:
                    group_bar_width = (group_data['count'] / max_count) * 100 if max_count > 0 else 0
                    group_data['bar_width'] = f"{group_bar_width:.1f}".replace(',', '.')
        
        context['bird_stats'] = bird_stats
        
        # 4. Fundumstände-Statistiken (unverändert)
        # Fundumstände für aktuelles Jahr
        circumstances_this_year = FallenBird.objects.filter(
            date_found__year=current_year,
            find_circumstances__isnull=False
        ).values('find_circumstances__name', 'find_circumstances__description').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Fundumstände für alle Jahre
        circumstances_all_time = FallenBird.objects.filter(
            find_circumstances__isnull=False
        ).values('find_circumstances__name', 'find_circumstances__description').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Formatiere Daten für Tortendiagramme
        def format_circumstances_data(circumstances_data):
            total = sum(item['count'] for item in circumstances_data)
            formatted_data = []
            colors = [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
            ]
            
            for i, item in enumerate(circumstances_data):
                name = item['find_circumstances__name'] or item['find_circumstances__description']
                percentage = round((item['count'] / total) * 100, 1) if total > 0 else 0
                formatted_data.append({
                    'name': name,
                    'count': item['count'],
                    'percentage': percentage,
                    'color': colors[i % len(colors)]
                })
            return formatted_data, total
        
        context['circumstances_this_year'], context['circumstances_this_year_total'] = format_circumstances_data(circumstances_this_year)
        context['circumstances_all_time'], context['circumstances_all_time_total'] = format_circumstances_data(circumstances_all_time)
        
        return context
