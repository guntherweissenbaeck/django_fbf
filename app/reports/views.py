import csv
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models import Q

from bird.models import FallenBird
from .forms import ManualReportForm, AutomaticReportForm
from .models import AutomaticReport, ReportLog
from .services import ReportGenerator


@staff_member_required
def reports_dashboard(request):
    """Main reports dashboard."""
    context = {
        'title': 'Reports Dashboard',
    }
    return render(request, 'admin/reports/dashboard.html', context)


@staff_member_required
def manual_report(request):
    """Create and send/download manual reports."""
    if request.method == 'POST':
        form = ManualReportForm(request.POST)
        if form.is_valid():
            # Handle form submission based on action
            action = request.POST.get('action')
            
            if action == 'download':
                # Generate CSV and return as download
                generator = ReportGenerator(
                    date_from=form.cleaned_data['date_from'],
                    date_to=form.cleaned_data['date_to'],
                    include_naturschutzbehoerde=form.cleaned_data['include_naturschutzbehörde'],
                    include_jagdbehoerde=form.cleaned_data['include_jagdbehörde']
                )
                
                csv_content, bird_count = generator.generate_csv()
                filename = generator.get_filename()
                
                # Create download log
                generator.create_download_log()
                
                response = HttpResponse(csv_content, content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                
                messages.success(request, f'Report mit {bird_count} Patienten wurde heruntergeladen.')
                return response
                
            elif action == 'email':
                # Send via email
                email_addresses = form.cleaned_data['email_addresses']
                email_list = [email.email for email in email_addresses]
                
                # Add custom email if provided
                if form.cleaned_data.get('custom_email'):
                    email_list.append(form.cleaned_data['custom_email'])
                
                if not email_list:
                    messages.error(request, 'Bitte wählen Sie mindestens eine E-Mail-Adresse aus.')
                    return render(request, 'admin/reports/manual_report.html', {'form': form, 'title': 'Manuellen Report erstellen'})
                
                generator = ReportGenerator(
                    date_from=form.cleaned_data['date_from'],
                    date_to=form.cleaned_data['date_to'],
                    include_naturschutzbehoerde=form.cleaned_data['include_naturschutzbehörde'],
                    include_jagdbehoerde=form.cleaned_data['include_jagdbehörde']
                )
                
                report_log, success, error = generator.send_email_report(email_list)
                
                if success:
                    messages.success(
                        request, 
                        f'Report wurde erfolgreich an {len(email_list)} E-Mail-Adresse(n) gesendet.'
                    )
                    return redirect('reports:dashboard')
                else:
                    messages.error(request, f'Fehler beim Senden des Reports: {error}')
    else:
        form = ManualReportForm()
    
    context = {
        'form': form,
        'title': 'Manuellen Report erstellen',
    }
    return render(request, 'admin/reports/manual_report.html', context)


@staff_member_required
def automatic_reports(request):
    """List and manage automatic reports."""
    reports = AutomaticReport.objects.all()
    context = {
        'reports': reports,
        'title': 'Automatische Reports',
    }
    return render(request, 'admin/reports/automatic_reports.html', context)


@staff_member_required
def create_automatic_report(request):
    """Create new automatic report."""
    if request.method == 'POST':
        form = AutomaticReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Automatischer Report wurde erfolgreich erstellt.')
            return redirect('reports:automatic_reports')
    else:
        form = AutomaticReportForm()
    
    context = {
        'form': form,
        'title': 'Automatischen Report erstellen',
    }
    return render(request, 'admin/reports/automatic_report_form.html', context)


@staff_member_required
def edit_automatic_report(request, report_id):
    """Edit automatic report."""
    report = get_object_or_404(AutomaticReport, id=report_id)
    
    if request.method == 'POST':
        form = AutomaticReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, 'Automatischer Report wurde erfolgreich aktualisiert.')
            return redirect('reports:automatic_reports')
    else:
        form = AutomaticReportForm(instance=report)
    
    context = {
        'form': form,
        'report': report,
        'title': f'Report bearbeiten: {report.name}',
    }
    return render(request, 'admin/reports/automatic_report_form.html', context)


@staff_member_required
def delete_automatic_report(request, report_id):
    """Delete automatic report."""
    report = get_object_or_404(AutomaticReport, id=report_id)
    
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Automatischer Report wurde erfolgreich gelöscht.')
        return redirect('reports:automatic_reports')
    
    context = {
        'report': report,
        'title': f'Report löschen: {report.name}',
    }
    return render(request, 'admin/reports/automatic_report_confirm_delete.html', context)


@staff_member_required
def report_logs(request):
    """View report logs."""
    logs = ReportLog.objects.all().order_by('-created_at')[:100]  # Show last 100 logs
    context = {
        'report_logs': logs,
        'title': 'Report-Protokoll',
    }
    return render(request, 'admin/reports/report_logs.html', context)
