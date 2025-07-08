from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime
from bird.models import FallenBird, Bird, BirdStatus


class StatistikView(TemplateView):
    template_name = 'statistik/overview.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Aktuelles Jahr
        current_year = timezone.now().year
        
        # 1. Übersicht über das aktuelle Jahr
        context['current_year'] = current_year
        
        # Patienten dieses Jahr aufgenommen
        patients_this_year = FallenBird.objects.filter(
            date_found__year=current_year
        ).count()
        context['patients_this_year'] = patients_this_year
        
        # Aktuell in Behandlung oder Auswilderung
        in_treatment_or_release = FallenBird.objects.filter(
            date_found__year=current_year,
            status__id__in=[1, 2]  # In Behandlung, In Auswilderung
        ).count()
        context['in_treatment_or_release'] = in_treatment_or_release
        
        # Ausgewildert + Übermittelt dieses Jahr
        rescued_this_year = FallenBird.objects.filter(
            date_found__year=current_year,
            status__id__in=[3, 4]  # Ausgewildert, Übermittelt
        ).count()
        context['rescued_this_year'] = rescued_this_year
        
        # 2. Übersicht über alle Jahre
        total_patients = FallenBird.objects.count()
        context['total_patients'] = total_patients
        
        total_rescued = FallenBird.objects.filter(
            status__id__in=[3, 4]  # Ausgewildert, Übermittelt
        ).count()
        context['total_rescued'] = total_rescued
        
        # 3. Statistik pro Vogelart
        bird_stats = []
        for bird in Bird.objects.all():
            fallen_birds = FallenBird.objects.filter(bird=bird)
            
            total_count = fallen_birds.count()
            rescued_count = fallen_birds.filter(status__id__in=[3, 4]).count()
            deceased_count = fallen_birds.filter(status__id=5).count()
            
            if total_count > 0:  # Nur Vögel anzeigen, die auch Patienten haben
                bird_stats.append({
                    'name': bird.name,
                    'species': bird.species or 'Unbekannt',
                    'total': total_count,
                    'rescued': rescued_count,
                    'deceased': deceased_count,
                    'rescued_percentage': round((rescued_count / total_count) * 100, 1) if total_count > 0 else 0,
                    'deceased_percentage': round((deceased_count / total_count) * 100, 1) if total_count > 0 else 0
                })
        
        # Sortiere nach Gesamtanzahl (absteigend)
        bird_stats.sort(key=lambda x: x['total'], reverse=True)
        context['bird_stats'] = bird_stats
        
        # Status-Namen für das Template
        try:
            context['status_names'] = {
                1: BirdStatus.objects.get(id=1).description,
                2: BirdStatus.objects.get(id=2).description,
                3: BirdStatus.objects.get(id=3).description,
                4: BirdStatus.objects.get(id=4).description,
                5: BirdStatus.objects.get(id=5).description,
            }
        except BirdStatus.DoesNotExist:
            context['status_names'] = {}
        
        return context
