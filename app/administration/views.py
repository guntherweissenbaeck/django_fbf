from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import BackupRestoreForm, BackupRunForm
from .models import BackupDestination, BackupLog
from .services import BackupError, log_backup_event, restore_database_from_file, run_backup

logger = logging.getLogger(__name__)


@staff_member_required
def backup_dashboard(request):
    backup_form = BackupRunForm(request.POST or None)
    restore_form = BackupRestoreForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if "run_backup" in request.POST:
            if backup_form.is_valid():
                destination = backup_form.cleaned_data["destination"]
                try:
                    file_name = run_backup(destination)
                    log_backup_event(destination, BackupLog.ACTION_BACKUP, BackupLog.STATUS_SUCCESS, "Backup erfolgreich erstellt.", file_name)
                    messages.success(request, _(f"Backup wurde erfolgreich erstellt und an {destination} übertragen."))
                except BackupError as exc:
                    log_backup_event(destination, BackupLog.ACTION_BACKUP, BackupLog.STATUS_FAILURE, str(exc))
                    logger.exception("Backup fehlgeschlagen")
                    messages.error(request, _(f"Backup fehlgeschlagen: {exc}"))
                except Exception as exc:  # pragma: no cover
                    log_backup_event(destination, BackupLog.ACTION_BACKUP, BackupLog.STATUS_FAILURE, str(exc))
                    logger.exception("Backup fehlgeschlagen")
                    messages.error(request, _(f"Unbekannter Fehler beim Backup: {exc}"))
                return redirect("administration:backup_dashboard")
        elif "restore_backup" in request.POST:
            if restore_form.is_valid():
                uploaded = restore_form.cleaned_data["backup_file"]
                try:
                    restore_database_from_file(uploaded)
                    log_backup_event(None, BackupLog.ACTION_RESTORE, BackupLog.STATUS_SUCCESS, "Backup erfolgreich eingespielt.", uploaded.name)
                    messages.success(request, _(f"Backup '{uploaded.name}' wurde erfolgreich eingespielt."))
                except BackupError as exc:
                    log_backup_event(None, BackupLog.ACTION_RESTORE, BackupLog.STATUS_FAILURE, str(exc), uploaded.name)
                    logger.exception("Restore fehlgeschlagen")
                    messages.error(request, _(f"Restore fehlgeschlagen: {exc}"))
                except Exception as exc:  # pragma: no cover
                    log_backup_event(None, BackupLog.ACTION_RESTORE, BackupLog.STATUS_FAILURE, str(exc), uploaded.name)
                    logger.exception("Restore fehlgeschlagen")
                    messages.error(request, _(f"Unbekannter Fehler beim Restore: {exc}"))
                return redirect("administration:backup_dashboard")
            else:
                backup_form = BackupRunForm()

    destinations = BackupDestination.objects.all()
    logs = BackupLog.objects.select_related("destination").all()[:10]

    context = {
        "backup_form": backup_form,
        "restore_form": restore_form,
        "destinations": destinations,
        "logs": logs,
    }
    return render(request, "administration/backup.html", context)
