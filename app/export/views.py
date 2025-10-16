import csv
from datetime import date

from bird.models import FallenBird
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .forms import CustomExportForm
from .services import BirdExportService


today = date.today().strftime("%Y-%m-%d")


@login_required(login_url="account_login")
def site_exports(request):
    """Main export page with options for different export types."""
    return render(request, "export/overview.html")


@login_required(login_url="account_login")
def export_birds_all(request):
    """Export all birds with extended fields including new columns."""
    birds = FallenBird.objects.all().select_related('bird', 'status', 'aviary', 'user', 'find_circumstances')
    
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f"attachment; filename=fbf_all_birds_{today}.csv"
    
    # Add BOM for proper UTF-8 encoding in Excel
    response.write('\ufeff')
    
    writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_ALL)
    writer.writerow([
        "Patienten Alias",
        "Vogel",
        "Alter",
        "Geschlecht",
        "Gefunden am",
        "Fundort",
        "Region",
        "Patient angelegt am",
        "Patient aktualisiert am",
        "Fundumstände",
        "Diagnose bei Fund",
        "Benutzer",
        "Status",
        "Voliere",
        "Übermittelt nach",
        "Auswilderungsort",
        "Akte geschlossen am",
    ])
    
    for bird in birds:
        # Use patient_file_close_date if available, otherwise fall back to updated date
        if bird.patient_file_close_date:
            close_date = bird.patient_file_close_date.strftime('%Y-%m-%d')
        else:
            close_date = bird.updated.strftime('%Y-%m-%d') if bird.updated else ''
        
        writer.writerow([
            bird.bird_identifier or '',
            bird.bird.name if bird.bird else '',
            bird.get_age_display() if bird.age else '',
            bird.get_sex_display() if bird.sex else '',
            bird.date_found.strftime('%Y-%m-%d') if bird.date_found else '',
            bird.place or '',
            (bird.region.name if bird.region else ''),
            bird.created.strftime('%Y-%m-%d') if bird.created else '',
            bird.updated.strftime('%Y-%m-%d') if bird.updated else '',
            bird.find_circumstances.description if bird.find_circumstances else '',
            bird.diagnostic_finding or '',
            bird.user.username if bird.user else '',
            bird.status.description if bird.status else '',
            bird.aviary.description if bird.aviary else '',
            bird.sent_to or '',
            bird.release_location or '',
            close_date,
        ])
    
    return response


@login_required(login_url="account_login")
def export_birds_custom(request):
    """Custom bird export with configurable date range, columns and filters."""
    
    if request.method == 'POST':
        form = CustomExportForm(request.POST)
        if form.is_valid():
            # Extract form data
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            
            # Filter configuration
            filter_config = {
                'filter_huntable_species': form.cleaned_data['filter_huntable_species']
            }
            
            # Column configuration
            column_config = {
                key: form.cleaned_data[key] 
                for key in form.cleaned_data.keys() 
                if key.startswith('include_')
            }
            
            # Generate export
            export_service = BirdExportService(
                date_from=date_from,
                date_to=date_to,
                filter_config=filter_config,
                column_config=column_config
            )
            
            # Get summary for user feedback
            summary = export_service.get_export_summary()
            
            # Generate CSV response
            response = export_service.generate_csv_response("fbf_custom_export")
            
            # Add success message (won't be shown due to file download, but logged)
            messages.success(
                request, 
                f"Export erfolgreich erstellt: {summary['total_birds']} Datensätze "
                f"vom {date_from} bis {date_to}"
            )
            
            return response
        else:
            messages.error(request, _("Bitte korrigieren Sie die Fehler im Formular."))
    else:
        form = CustomExportForm()
    
    return render(request, 'export/custom_export.html', {
        'form': form,
        'title': _('Angepasster Datenexport')
    })


# Keep the old export_birds for backward compatibility, but redirect to new function
@login_required(login_url="account_login")
def export_birds(request):
    """Legacy function - redirects to new all birds export."""
    return export_birds_all(request)
