from django.core.management.base import BaseCommand
from django.db import transaction
from bird.models import FallenBird
from datetime import date


class Command(BaseCommand):
    help = 'Update patient_file_close_date for birds that should be closed based on their status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Status-IDs die eine Schließung bedeuten
        closing_status_ids = [3, 4, 5]  # Ausgewildert, Übermittelt, Verstorben
        
        # Finde Vögel mit schließenden Status aber ohne Schließungsdatum
        birds_to_update = FallenBird.objects.filter(
            status_id__in=closing_status_ids,
            patient_file_close_date__isnull=True
        ).select_related('status')
        
        count = birds_to_update.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would update {count} birds:')
            )
            for bird in birds_to_update[:10]:  # Zeige nur erste 10
                self.stdout.write(
                    f'  - {bird.bird_identifier or "No ID"} ({bird.status.description})'
                )
            if count > 10:
                self.stdout.write(f'  ... and {count - 10} more')
        else:
            self.stdout.write(f'Updating {count} birds...')
            
            with transaction.atomic():
                updated = 0
                for bird in birds_to_update:
                    # Verwende das Datum der letzten Statusänderung oder heute
                    close_date = bird.date_found or date.today()
                    
                    # Wenn es ein späteres Datum gibt (z.B. release_date), verwende das
                    if hasattr(bird, 'date_released') and bird.date_released:
                        close_date = max(close_date, bird.date_released)
                    
                    bird.patient_file_close_date = close_date
                    bird.save(update_fields=['patient_file_close_date'])
                    updated += 1
                    
                    if updated % 100 == 0:
                        self.stdout.write(f'  Updated {updated}/{count}...')
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated {updated} birds')
                )
