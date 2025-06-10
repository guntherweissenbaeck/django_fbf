from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import models
from datetime import date, timedelta
from bird.models import Bird, FallenBird, BirdStatus
from sendemail.models import Emailadress
from reports.models import AutomaticReport


class Command(BaseCommand):
    help = 'Create test data for the reports system'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data for reports system...')
        
        # Create test email addresses
        email1, created = Emailadress.objects.get_or_create(
            email_address='test1@example.com',
            defaults={'user_id': 1}
        )
        if created:
            self.stdout.write(f'✓ Created email: {email1.email_address}')
        
        email2, created = Emailadress.objects.get_or_create(
            email_address='test2@example.com',
            defaults={'user_id': 1}
        )
        if created:
            self.stdout.write(f'✓ Created email: {email2.email_address}')
        
        # Create a test automatic report
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            auto_report, created = AutomaticReport.objects.get_or_create(
                name='Test Weekly Report',
                defaults={
                    'description': 'Automatic weekly report for testing',
                    'frequency': 'weekly',
                    'include_naturschutzbehoerde': True,
                    'include_jagdbehoerde': False,
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            if created:
                auto_report.email_addresses.add(email1, email2)
                self.stdout.write(f'✓ Created automatic report: {auto_report.name}')
        
        # Check existing bird data
        bird_count = FallenBird.objects.count()
        self.stdout.write(f'✓ Found {bird_count} existing birds in database')
        
        # Check birds with notification settings
        notification_birds = Bird.objects.filter(
            models.Q(melden_an_naturschutzbehoerde=True) | 
            models.Q(melden_an_jagdbehoerde=True)
        ).count()
        self.stdout.write(f'✓ Found {notification_birds} birds with notification settings')
        
        self.stdout.write(
            self.style.SUCCESS('✓ Test data creation completed successfully!')
        )
