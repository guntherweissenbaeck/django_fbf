import csv
from io import StringIO
from datetime import date
from django.db.models import Q
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.core.files.base import ContentFile
from bird.models import FallenBird


class ReportGenerator:
    """Service class for generating bird reports."""
    
    def __init__(self, date_from, date_to, include_naturschutzbehoerde=True, include_jagdbehoerde=False):
        self.date_from = date_from
        self.date_to = date_to
        self.include_naturschutzbehoerde = include_naturschutzbehoerde
        self.include_jagdbehoerde = include_jagdbehoerde
    
    def get_birds_queryset(self):
        """Get queryset of birds based on filters."""
        # Date filter
        queryset = FallenBird.objects.filter(
            date_found__gte=self.date_from,
            date_found__lte=self.date_to
        )
        
        # Bird type filter based on notification settings
        bird_filter = Q()
        
        if self.include_naturschutzbehoerde:
            bird_filter |= Q(bird__melden_an_naturschutzbehoerde=True)
        
        if self.include_jagdbehoerde:
            bird_filter |= Q(bird__melden_an_jagdbehoerde=True)
        
        if bird_filter:
            queryset = queryset.filter(bird_filter)
        
        return queryset.select_related('bird', 'status', 'aviary', 'user').order_by('date_found')
    
    def generate_csv(self):
        """Generate CSV content and return as string with bird count."""
        birds = self.get_birds_queryset()
        bird_count = birds.count()
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_ALL)
        
        # Header row
        headers = [
            'Vogel',
            'Alter',
            'Geschlecht',
            'Gefunden am',
            'Fundort',
            'Fundumstände',
            'Diagnose bei Fund',
            'Status'
        ]
        writer.writerow(headers)
        
        # Data rows
        for bird in birds:
            row = [
                bird.bird.name if bird.bird else '',
                bird.get_age_display() if bird.age else '',
                bird.get_sex_display() if bird.sex else '',
                bird.date_found.strftime('%d.%m.%Y') if bird.date_found else '',
                bird.place or '',
                bird.find_circumstances or '',
                bird.diagnostic_finding or '',
                bird.status.description if bird.status else '',
            ]
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content, bird_count
    
    def get_filename(self):
        """Generate filename for the report."""
        return f"wildvogelhilfe_report_{self.date_from}_{self.date_to}.csv"
    
    def get_summary(self):
        """Get summary statistics for the report."""
        birds = self.get_birds_queryset()
        
        summary = {
            'total_birds': birds.count(),
            'naturschutz_birds': birds.filter(bird__melden_an_naturschutzbehoerde=True).count() if self.include_naturschutzbehoerde else 0,
            'jagd_birds': birds.filter(bird__melden_an_jagdbehoerde=True).count() if self.include_jagdbehoerde else 0,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        
        return summary
    
    def send_email_report(self, email_addresses, automatic_report=None):
        """Send the report via email to specified addresses."""
        from .models import ReportLog
        
        csv_content, bird_count = self.generate_csv()
        filename = self.get_filename()
        
        # Prepare email context
        context = {
            'date_from': self.date_from.strftime('%d.%m.%Y'),
            'date_to': self.date_to.strftime('%d.%m.%Y'),
            'patient_count': bird_count,
            'filter_naturschutzbehörde': self.include_naturschutzbehoerde,
            'filter_jagdbehörde': self.include_jagdbehoerde,
            'automatic_report': automatic_report,
            'created_at': date.today().strftime('%d.%m.%Y'),
        }
        
        # Render email templates
        subject = render_to_string('reports/email/report_subject.txt', context).strip()
        message = render_to_string('reports/email/report_message.txt', context)
        
        # Create email
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@wildvogelhilfe-jena.de'),
            to=email_addresses,
        )
        
        # Attach CSV file
        email.attach(filename, csv_content, 'text/csv')
        
        try:
            # Send email
            email.send()
            
            # Create log entry
            report_log = ReportLog.objects.create(
                automatic_report=automatic_report,
                date_from=self.date_from,
                date_to=self.date_to,
                patient_count=bird_count,
                include_naturschutzbehörde=self.include_naturschutzbehoerde,
                include_jagdbehörde=self.include_jagdbehoerde,
                email_sent_to=email_addresses,
            )
            
            # Save CSV file to the log
            report_log.csv_file.save(
                filename,
                ContentFile(csv_content.encode('utf-8')),
                save=True
            )
            
            return report_log, True, None
            
        except Exception as e:
            return None, False, str(e)
    
    def create_download_log(self, automatic_report=None):
        """Create a log entry for downloaded reports."""
        from .models import ReportLog
        
        csv_content, bird_count = self.generate_csv()
        filename = self.get_filename()
        
        # Create log entry
        report_log = ReportLog.objects.create(
            automatic_report=automatic_report,
            date_from=self.date_from,
            date_to=self.date_to,
            patient_count=bird_count,
            include_naturschutzbehörde=self.include_naturschutzbehoerde,
            include_jagdbehörde=self.include_jagdbehoerde,
            email_sent_to=[],  # Empty list indicates download
        )
        
        # Save CSV file to the log
        report_log.csv_file.save(
            filename,
            ContentFile(csv_content.encode('utf-8')),
            save=True
        )
        
        return report_log
