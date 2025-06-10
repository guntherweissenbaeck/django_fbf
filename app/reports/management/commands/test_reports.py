from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from reports.services import ReportGenerator
from reports.models import AutomaticReport


class Command(BaseCommand):
    help = 'Test the report generation system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-manual',
            action='store_true',
            help='Test manual report generation',
        )
        parser.add_argument(
            '--test-email',
            action='store_true',
            help='Test email sending (requires SMTP configuration)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Report System'))
        
        # Simple test first
        self.stdout.write('Reports app is working!')
        
        # Test basic report generation
        if options.get('test_manual'):
            self.test_manual_report()
        
        if options.get('test_email'):
            self.test_email_report()
        
        self.test_basic_functionality()
        
    def test_basic_functionality(self):
        self.stdout.write('Testing basic report functionality...')
        
        # Create test date range (last 30 days)
        date_to = date.today()
        date_from = date_to - timedelta(days=30)
        
        generator = ReportGenerator(
            date_from=date_from,
            date_to=date_to,
            include_naturschutzbehoerde=True,
            include_jagdbehoerde=False
        )
        
        # Test CSV generation
        try:
            csv_content, bird_count = generator.generate_csv()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ CSV generation successful: {bird_count} birds found'
                )
            )
            
            # Test summary
            summary = generator.get_summary()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Summary generation successful: {summary["total_birds"]} total birds'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ CSV generation failed: {e}')
            )
    
    def test_manual_report(self):
        self.stdout.write('Testing manual report creation...')
        
        date_to = date.today()
        date_from = date_to - timedelta(days=7)  # Last week
        
        generator = ReportGenerator(
            date_from=date_from,
            date_to=date_to,
            include_naturschutzbehoerde=True,
            include_jagdbehoerde=True
        )
        
        try:
            # Create download log
            log = generator.create_download_log()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Manual report log created: {log.id} with {log.patient_count} patients'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Manual report creation failed: {e}')
            )
    
    def test_email_report(self):
        self.stdout.write('Testing email report (dry run)...')
        
        # This would test email functionality if SMTP is configured
        # For now, just test the email template rendering
        from django.template.loader import render_to_string
        
        context = {
            'date_from': '01.01.2024',
            'date_to': '31.01.2024',
            'patient_count': 42,
            'filter_naturschutzbehörde': True,
            'filter_jagdbehörde': False,
            'automatic_report': None,
            'created_at': '01.02.2024',
        }
        
        try:
            subject = render_to_string('reports/email/report_subject.txt', context).strip()
            message = render_to_string('reports/email/report_message.txt', context)
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Email template rendering successful')
            )
            self.stdout.write(f'Subject: {subject}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Email template rendering failed: {e}')
            )
