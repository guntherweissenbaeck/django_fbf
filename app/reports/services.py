"""Utility services for generating and distributing CSV-based bird reports.

This module centralises the logic used by the reports application to build CSV
exports, send them via e-mail and persist metadata in the database. The
docstrings intentionally use ``:param`` / ``:returns`` style so that they can be
parsed by Doxygen when generating the project documentation.
"""

import csv
from datetime import date
from io import StringIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.db.models import Q
from django.template.loader import render_to_string

from bird.models import FallenBird


class ReportGenerator:
    """Build and distribute CSV exports based on configurable filters.

    :param date_from: Inclusive start date for the report window.
    :param date_to: Inclusive end date for the report window.
    :param include_naturschutzbehoerde: If ``True`` include birds requiring
        notifications to the nature conservation authority.
    :param include_jagdbehoerde: If ``True`` include birds requiring
        notifications to the hunting authority.
    :param column_config: Either an ``AutomaticReport`` instance or a ``dict``
        with boolean flags that control which columns are rendered.
    """

    def __init__(
        self,
        date_from,
        date_to,
        include_naturschutzbehoerde=True,
        include_jagdbehoerde=False,
        column_config=None,
    ):
        self.date_from = date_from
        self.date_to = date_to
        self.include_naturschutzbehoerde = include_naturschutzbehoerde
        self.include_jagdbehoerde = include_jagdbehoerde

        # Column configuration (AutomaticReport instance or dict with column settings)
        self.column_config = column_config or {
            "include_date_found": True,
            "include_bird_species": True,
            "include_bird_status": True,
            "include_finder_info": False,
            "include_aviary": False,
            "include_circumstances": True,
            "include_location": True,
            "include_notes": False,  # This refers to "Bemerkungen" (comment field)
            "include_sent_to": False,
            "include_release_location": False,
            "include_close_date": False,
        }
    
    def get_birds_queryset(self):
        """Return the filtered ``FallenBird`` queryset for the requested span.

        :returns: A queryset with the relevant ``select_related`` joins applied.
        """
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
        """Generate the configured CSV export.

        :returns: Tuple of ``(csv_content, bird_count)`` where ``csv_content`` is
            the semi-colon delimited CSV string and ``bird_count`` represents the
            amount of patients included in the export.
        """
        birds = self.get_birds_queryset()
        bird_count = birds.count()
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_ALL)
        
        # Build dynamic header row based on configuration
        headers = []
        if self._get_column_setting('include_date_found'):
            headers.append('Gefunden am')
        if self._get_column_setting('include_bird_species'):
            headers.extend(['Vogelart', 'Alter', 'Geschlecht'])
        if self._get_column_setting('include_bird_status'):
            headers.extend(['Status', 'Diagnose bei Fund'])
        if self._get_column_setting('include_location'):
            headers.append('Fundort')
        if self._get_column_setting('include_circumstances'):
            headers.append('Fundumstände')
        if self._get_column_setting('include_finder_info'):
            headers.extend(['Finder Name', 'Finder Telefon', 'Finder Email'])
        if self._get_column_setting('include_aviary'):
            headers.append('Voliere')
        if self._get_column_setting('include_notes'):
            headers.append('Bemerkungen')
        if self._get_column_setting('include_sent_to'):
            headers.append('Übermittelt nach')
        if self._get_column_setting('include_release_location'):
            headers.append('Auswilderungsort')
        if self._get_column_setting('include_close_date'):
            headers.append('Akte geschlossen am')
            
        writer.writerow(headers)
        
        # Data rows
        for bird in birds:
            row = []
            
            if self._get_column_setting('include_date_found'):
                row.append(bird.date_found.strftime('%d.%m.%Y') if bird.date_found else '')
                
            if self._get_column_setting('include_bird_species'):
                row.extend([
                    bird.bird.name if bird.bird else '',
                    bird.get_age_display() if bird.age else '',
                    bird.get_sex_display() if bird.sex else '',
                ])
                
            if self._get_column_setting('include_bird_status'):
                row.extend([
                    bird.status.description if bird.status else '',
                    bird.diagnostic_finding or '',
                ])
                
            if self._get_column_setting('include_location'):
                row.append(bird.place or '')
                
            if self._get_column_setting('include_circumstances'):
                row.append(bird.find_circumstances or '')
                
            if self._get_column_setting('include_finder_info'):
                row.extend([
                    f"{bird.finder_first_name or ''} {bird.finder_last_name or ''}".strip(),
                    bird.finder_phone or '',
                    bird.finder_email or '',
                ])
                
            if self._get_column_setting('include_aviary'):
                row.append(bird.aviary.description if bird.aviary else '')
                
            if self._get_column_setting('include_notes'):
                # Use the comment field (Bemerkung) from FallenBird
                row.append(bird.comment or '')
                
            if self._get_column_setting('include_sent_to'):
                row.append(bird.sent_to or '')
                
            if self._get_column_setting('include_release_location'):
                row.append(bird.release_location or '')
                
            if self._get_column_setting('include_close_date'):
                # Use patient_file_close_date if available, otherwise fall back to updated date
                close_date = bird.patient_file_close_date or bird.updated.date()
                row.append(close_date.strftime('%d.%m.%Y') if close_date else '')
                
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content, bird_count
    
    def _get_column_setting(self, setting_name):
        """Resolve the column flag for the given setting name.

        :param setting_name: Name of the column attribute to fetch.
        :returns: Boolean indicating whether the column should be rendered.
        """
        if hasattr(self.column_config, setting_name):
            # AutomaticReport instance
            return getattr(self.column_config, setting_name)
        elif isinstance(self.column_config, dict):
            # Dictionary config
            return self.column_config.get(setting_name, False)
        return False
    
    def get_filename(self):
        """Build a slugified filename for the generated CSV export."""
        return f"wildvogelhilfe_report_{self.date_from}_{self.date_to}.csv"
    
    def get_summary(self):
        """Return a dict with basic statistics for the planned export."""
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
        """Render and dispatch the report via e-mail.

        :param email_addresses: Iterable of recipient addresses.
        :param automatic_report: Optional ``AutomaticReport`` instance that
            triggered the send.
        :returns: Tuple ``(ReportLog|None, success, error_message)`` where
            ``success`` is a boolean flag and ``error_message`` contains the
            caught exception message when sending fails.
        """
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
        """Persist metadata and CSV content when a report is downloaded.

        :param automatic_report: Optional schedule definition for the report.
        :returns: The newly created ``ReportLog`` instance.
        """
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
    
    @classmethod
    def generate_csv_report(cls, date_from, date_to, automatic_report=None):
        """Convenience wrapper used by scheduled report generation.

        :param date_from: Inclusive start date for the export window.
        :param date_to: Inclusive end date for the export window.
        :param automatic_report: Optional schedule definition with column flags.
        :returns: Raw CSV content as string.
        """
        generator = cls(
            date_from=date_from,
            date_to=date_to,
            include_naturschutzbehoerde=getattr(automatic_report, 'include_naturschutzbehörde', True),
            include_jagdbehoerde=getattr(automatic_report, 'include_jagdbehörde', False),
            column_config=automatic_report
        )
        csv_content, bird_count = generator.generate_csv()
        return csv_content
