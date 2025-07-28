import csv
from io import StringIO
from django.db.models import Q
from django.http import HttpResponse
from bird.models import FallenBird


class BirdExportService:
    """Service class for exporting bird data with configurable columns and filters."""
    
    def __init__(self, date_from, date_to, filter_config, column_config):
        self.date_from = date_from
        self.date_to = date_to
        self.filter_config = filter_config
        self.column_config = column_config

    def get_birds_queryset(self):
        """Get queryset of birds based on date range and filters."""
        # Date filter - based on date_found
        queryset = FallenBird.objects.filter(
            date_found__gte=self.date_from,
            date_found__lte=self.date_to
        )
        
        # Species filter
        filter_huntable = self.filter_config.get('filter_huntable_species', 'all')
        
        if filter_huntable == 'huntable_only':
            # Only birds that should be reported to hunting authorities
            queryset = queryset.filter(bird__melden_an_jagdbehoerde=True)
        elif filter_huntable == 'non_huntable_only':
            # Only birds that should NOT be reported to hunting authorities
            queryset = queryset.filter(bird__melden_an_jagdbehoerde=False)
        # 'all' means no additional filter
        
        return queryset.select_related('bird', 'status', 'aviary', 'user', 'find_circumstances').order_by('date_found')

    def generate_csv_response(self, filename_prefix="fbf_export"):
        """Generate CSV response for download."""
        birds = self.get_birds_queryset()
        
        # Create response
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        filename = f"{filename_prefix}_{self.date_from}_{self.date_to}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Write BOM for proper UTF-8 encoding in Excel
        response.write('\ufeff')
        
        writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_ALL)
        
        # Build dynamic header row
        headers = self._build_headers()
        writer.writerow(headers)
        
        # Write data rows
        for bird in birds:
            row = self._build_row(bird)
            writer.writerow(row)
        
        return response

    def _build_headers(self):
        """Build CSV header row based on column configuration."""
        headers = []
        
        if self.column_config.get('include_date_found', False):
            headers.append('Funddatum')
            
        if self.column_config.get('include_bird_species', False):
            headers.append('Vogelart')
            
        if self.column_config.get('include_bird_details', False):
            headers.extend(['Alter', 'Geschlecht'])
            
        if self.column_config.get('include_bird_status', False):
            headers.append('Status')
            
        if self.column_config.get('include_location', False):
            headers.append('Fundort')
            
        if self.column_config.get('include_circumstances', False):
            headers.append('Fundumstände')
            
        if self.column_config.get('include_diagnosis', False):
            headers.append('Diagnose bei Fund')
            
        if self.column_config.get('include_finder_info', False):
            headers.extend(['Finder Name', 'Finder Telefon', 'Finder Email'])
            
        if self.column_config.get('include_aviary', False):
            headers.append('Voliere')
            
        if self.column_config.get('include_sent_to', False):
            headers.append('Übermittelt nach')
            
        if self.column_config.get('include_release_location', False):
            headers.append('Auswilderungsort')
            
        if self.column_config.get('include_close_date', False):
            headers.append('Akte geschlossen am')
            
        if self.column_config.get('include_notes', False):
            headers.append('Bemerkungen')
            
        if self.column_config.get('include_timestamps', False):
            headers.extend(['Erstellt am', 'Aktualisiert am'])
            
        if self.column_config.get('include_user_info', False):
            headers.append('Bearbeitet von')
        
        return headers

    def _build_row(self, bird):
        """Build CSV data row for a single bird."""
        row = []
        
        if self.column_config.get('include_date_found', False):
            row.append(bird.date_found.strftime('%Y-%m-%d') if bird.date_found else '')
            
        if self.column_config.get('include_bird_species', False):
            row.append(bird.bird.name if bird.bird else '')
            
        if self.column_config.get('include_bird_details', False):
            row.extend([
                bird.get_age_display() if bird.age else '',
                bird.get_sex_display() if bird.sex else '',
            ])
            
        if self.column_config.get('include_bird_status', False):
            row.append(bird.status.description if bird.status else '')
            
        if self.column_config.get('include_location', False):
            row.append(bird.place or '')
            
        if self.column_config.get('include_circumstances', False):
            row.append(bird.find_circumstances.description if bird.find_circumstances else '')
            
        if self.column_config.get('include_diagnosis', False):
            row.append(bird.diagnostic_finding or '')
            
        if self.column_config.get('include_finder_info', False):
            # Parse finder information from the text field
            finder_lines = bird.finder.split('\n') if bird.finder else []
            finder_name = ''
            finder_phone = ''
            finder_email = ''
            
            for line in finder_lines:
                line = line.strip()
                if line.startswith('Vorname:') or line.startswith('Nachname:'):
                    name_part = line.split(':', 1)[1].strip()
                    if name_part:
                        finder_name += f" {name_part}".strip()
                elif line.startswith('Telefonnummer:'):
                    finder_phone = line.split(':', 1)[1].strip()
                elif '@' in line and not line.startswith('E-Mail:'):
                    finder_email = line.strip()
                elif line.startswith('E-Mail:'):
                    finder_email = line.split(':', 1)[1].strip()
            
            row.extend([finder_name.strip(), finder_phone, finder_email])
            
        if self.column_config.get('include_aviary', False):
            row.append(bird.aviary.description if bird.aviary else '')
            
        if self.column_config.get('include_sent_to', False):
            row.append(bird.sent_to or '')
            
        if self.column_config.get('include_release_location', False):
            row.append(bird.release_location or '')
            
        if self.column_config.get('include_close_date', False):
            # Use patient_file_close_date if available, otherwise fall back to updated date
            if bird.patient_file_close_date:
                close_date = bird.patient_file_close_date
            else:
                close_date = bird.updated.date() if bird.updated else None
            row.append(close_date.strftime('%Y-%m-%d') if close_date else '')
            
        if self.column_config.get('include_notes', False):
            row.append(bird.comment or '')
            
        if self.column_config.get('include_timestamps', False):
            row.extend([
                bird.created.strftime('%Y-%m-%d %H:%M:%S') if bird.created else '',
                bird.updated.strftime('%Y-%m-%d %H:%M:%S') if bird.updated else '',
            ])
            
        if self.column_config.get('include_user_info', False):
            row.append(bird.user.username if bird.user else '')
        
        return row

    def get_export_summary(self):
        """Get summary information about the export."""
        birds = self.get_birds_queryset()
        
        summary = {
            'total_birds': birds.count(),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'filter_huntable': self.filter_config.get('filter_huntable_species', 'all'),
            'selected_columns': len([k for k, v in self.column_config.items() if v and k.startswith('include_')])
        }
        
        return summary
