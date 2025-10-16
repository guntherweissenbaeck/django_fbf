"""Views for managing bird patients and notification workflows.

The docstrings follow ``:param`` / ``:returns`` conventions to keep the module
compatible with Doxygen generated documentation.
"""

import logging
from django.utils import timezone

import names
from smtplib import SMTPException

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from django.db.models import Q, Sum
from django.http import HttpRequest, HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect, render

from sendemail.message import messagebody
from sendemail.models import Emailadress

from .forms import BirdAddForm, BirdEditForm, BirdSpeciesForm
from .models import Bird, FallenBird, BirdRegion, GeocodeAttempt, RegionBackfillTask
from stations.geocoding import geocode_address, DEFAULT_USER_AGENT, DEFAULT_ENDPOINT
import requests
import logging
logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


def _collect_notification_recipients(bird: Bird) -> list[str]:
    """Return all deduplicated e-mail receivers for the given bird species.

    :param bird: Bird species that has been selected during patient intake.
    :returns: Iterable of unique e-mail addresses honouring notification flags.
    """

    recipient_filter = Q()
    if bird.melden_an_naturschutzbehoerde:
        recipient_filter |= Q(is_naturschutzbehoerde=True)
    if bird.melden_an_jagdbehoerde:
        recipient_filter |= Q(is_jagdbehoerde=True)
    if bird.melden_an_wildvogelhilfe_team:
        recipient_filter |= Q(is_wildvogelhilfe_team=True)

    if not recipient_filter:
        return []

    return list(
        Emailadress.objects.filter(recipient_filter)
        .values_list("email_address", flat=True)
        .distinct()
    )


@login_required(login_url="account_login")
def bird_create(request: HttpRequest) -> HttpResponse:
    """Create one or multiple ``FallenBird`` instances from the add form.

    :param request: Incoming HTTP request that optionally includes POST data.
    :returns: Redirect to the bird index on success or renders the form.
    """

    form = BirdAddForm(initial={"bird_identifier": names.get_first_name()})

    if request.method == "POST":
        form = BirdAddForm(request.POST or None, request.FILES or None)

        if form.is_valid():
            anzahl_patienten = form.cleaned_data.get("anzahl_patienten", 1)
            base_identifier = form.cleaned_data.get(
                "bird_identifier", names.get_first_name()
            )

            created_patients = []
            selected_bird: Bird = form.cleaned_data.get("bird")
            notification_recipients = list(_collect_notification_recipients(selected_bird))

            patient_payload = form.cleaned_data.copy()
            patient_payload.pop("anzahl_patienten", None)

            for index in range(anzahl_patienten):
                unique_identifier = (
                    base_identifier if anzahl_patienten == 1 else f"{base_identifier}-{index + 1}"
                )
                patient_payload["bird_identifier"] = unique_identifier

                # Region ID wurde als ForeignKey über das Formular übergeben (optional)
                patient = FallenBird(**patient_payload)
                patient.user = request.user
                patient.save()

                created_patients.append(patient)

                if notification_recipients:
                    try:
                        send_mail(
                            subject=f"Wildvogel gefunden! (Patient: {unique_identifier})",
                            message=messagebody(
                                patient.date_found,
                                patient.bird,
                                patient.place,
                                patient.diagnostic_finding,
                                unique_identifier,
                            ),
                            from_email=getattr(
                                settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"
                            ),
                            recipient_list=notification_recipients,
                        )
                    except BadHeaderError:
                        return HttpResponse("Invalid header found.")
                    except SMTPException as exc:
                        # Use messages framework to surface delivery issues without failing the request.
                        messages.warning(
                            request,
                            f"E-Mail konnte nicht versendet werden: {exc}",
                            extra_tags="email-failure",
                            fail_silently=True,
                        )
                        logger.exception("Error sending intake email")

            request.session["rescuer_id"] = None

            if anzahl_patienten == 1:
                messages.success(
                    request,
                    f"Patient '{created_patients[0].bird_identifier}' wurde erfolgreich angelegt.",
                )
            else:
                patient_names = ", ".join(
                    [patient.bird_identifier for patient in created_patients]
                )
                messages.success(
                    request,
                    f"{anzahl_patienten} Patienten wurden erfolgreich angelegt: {patient_names}",
                )

            return redirect("bird_all")

    context = {"form": form}
    return render(request, "bird/bird_create.html", context)


@login_required(login_url="account_login")
def bird_help(request: HttpRequest) -> HttpResponse:
    """Render a help view containing all ``Bird`` species.

    :param request: Incoming request instance.
    :returns: Rendered help template with the ``Bird`` queryset.
    """

    birds = Bird.objects.all().order_by("name")
    context = {"birds": birds}
    return render(request, "bird/bird_help.html", context)


@login_required(login_url="account_login")
def bird_help_single(request: HttpRequest, id: int) -> HttpResponse:
    """Show help information for a single ``Bird`` species.

    :param request: Incoming request instance.
    :param id: Primary key of the ``Bird`` entry.
    :returns: Rendered template for the selected bird.
    """

    bird = Bird.objects.get(id=id)
    context = {"bird": bird}
    return render(request, "bird/bird_help_single.html", context)


@login_required(login_url="account_login")
def bird_all(request: HttpRequest) -> HttpResponse:
    """List active ``FallenBird`` patients along with aggregated costs.

    :param request: Incoming request instance.
    :returns: Rendered template containing all active patients.
    """

    birds = (
        FallenBird.objects.filter(Q(status="1") | Q(status="2"))
        .annotate(total_costs=Sum("costs__costs"))
        .order_by("date_found")
    )
    context = {"birds": birds}
    return render(request, "bird/bird_all.html", context)


@login_required(login_url="account_login")
def bird_inactive(request: HttpRequest) -> HttpResponse:
    """List inactive ``FallenBird`` patients with aggregated costs.

    :param request: Incoming request instance.
    :returns: Rendered template containing all inactive patients.
    """

    birds = (
        FallenBird.objects.filter(~Q(status="1") & ~Q(status="2"))
        .annotate(total_costs=Sum("costs__costs"))
        .order_by("date_found")
    )
    context = {"birds": birds}
    return render(request, "bird/bird_inactive.html", context)


@login_required(login_url="account_login")
def bird_single(request: HttpRequest, id: str) -> HttpResponse:
    """Edit a single ``FallenBird`` instance via the edit form.

    :param request: Incoming request instance populated with POST data (optional).
    :param id: Primary key of the ``FallenBird`` record to edit.
    :returns: Rendered edit template or redirect after successful save.
    """

    bird = FallenBird.objects.get(id=id)
    form = BirdEditForm(
        request.POST or None,
        request.FILES or None,
        instance=bird)
    if request.method == "POST":
        if form.is_valid():
            fs = form.save(commit=False)
            if fs.status.description != "In Auswilderung":
                fs.aviary = None
            fs.save()
            return redirect("bird_all")
    context = {"form": form, "bird": bird}
    return render(request, "bird/bird_single.html", context)


@login_required(login_url="account_login")
def bird_delete(request: HttpRequest, id: str) -> HttpResponse:
    """Confirm and delete a ``FallenBird`` instance.

    :param request: Request instance used to confirm deletion.
    :param id: Primary key for the ``FallenBird`` record slated for removal.
    :returns: Rendered confirmation template or redirect after deletion.
    """

    bird = FallenBird.objects.get(id=id)
    if request.method == "POST":
        bird.delete()
        return redirect("bird_all")
    context = {"bird": bird}
    return render(request, "bird/bird_delete.html", context)


@login_required(login_url="account_login")
def bird_species_list(request: HttpRequest) -> HttpResponse:
    """List all bird species with their notification settings.

    :param request: Incoming request instance.
    :returns: Rendered species list template.
    """

    birds = Bird.objects.all().order_by("name")
    context = {"birds": birds}
    return render(request, "bird/bird_species_list.html", context)


@login_required(login_url="account_login")
def bird_species_edit(request: HttpRequest, id: int) -> HttpResponse:
    """Edit bird species notification settings.

    :param request: Request instance containing form data.
    :param id: Primary key of the ``Bird`` record being edited.
    :returns: Rendered edit form or redirect after saving.
    """

    bird_species = Bird.objects.get(id=id)
    form = BirdSpeciesForm(request.POST or None, instance=bird_species)
    
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("bird_species_list")
    
    context = {"form": form, "bird_species": bird_species}
    return render(request, "bird/bird_species_edit.html", context)


@login_required(login_url="account_login")
def geocode_found_location(request: HttpRequest) -> JsonResponse:
    """Geocode the free-text found location and return city/region info.

    Mehrstufige Logik für robustere Treffer:
    1. Original-Query
    2. Falls keine Kommata vorhanden: ", Deutschland" anhängen
    3. Straßennummer trennen ("Lutherstraße3" -> "Lutherstraße 3") und erneut versuchen
    4. Heuristik für Muster "Kirche <Ort>" (Reihung drehen: "<Ort> Kirche")

    Beste gefundene Adresse wird genutzt. Jede Stufe loggt ihren Versuch.
    """

    raw_query = (request.GET.get("q") or "").strip()
    if not raw_query:
        return JsonResponse({"success": False, "error": "Kein Fundort übergeben."}, status=400)

    attempts = []  # (query, params, response_list)

    # Einfaches Cache-Layer (Key = normalisierte Originaleingabe). TTL 30 Minuten.
    from django.core.cache import cache
    cache_key = f"geocode:{raw_query.lower()}"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse(cached)

    def perform(query: str, attempt_no: int):
        # Hole mehrere Kandidaten damit wir später den nächsten zum Center wählen können.
        params = {
            'q': query,
            'format': 'json',
            'limit': 7,  # mehrere Kandidaten für Distanz-Berechnung
            'addressdetails': 1,
        }
        try:
            # Exponential Backoff für 429: bis zu 3 Versuche mit wachsender Wartezeit.
            delay = 0.5
            for retry in range(3):
                resp = requests.get(
                    DEFAULT_ENDPOINT,
                    params=params,
                    headers={'User-Agent': DEFAULT_USER_AGENT},
                    timeout=10,
                )
                if resp.status_code != 429:
                    break
                time.sleep(delay)
                delay *= 2
        except requests.RequestException as exc:
            logger.error('Geocoding Netzwerkfehler bei Query=%s: %s', query, exc)
            return params, None, 'network'
        if resp.status_code == 429:
            logger.warning('Geocoding rate limit (429) bei Query=%s', query)
            return params, None, 'rate_limited'
        if resp.status_code != 200:
            logger.warning('Geocoding HTTP %s für Query=%s', resp.status_code, query)
        data = resp.json() if resp.headers.get('Content-Type','').startswith('application/json') else []
        return params, data, 'ok'

    # 1. Original
    import time  # lokal halten
    params, data, status_flag = perform(raw_query, 1)
    attempts.append((raw_query, params, data, status_flag))

    # Früher exit bei Rate Limit / Netzwerk: alternativen nicht versuchen
    if status_flag == 'rate_limited':
        return JsonResponse({"success": False, "rate_limited": True, "error": "Geocoding gedrosselt (429)."}, status=429)
    if status_flag == 'network':
        return JsonResponse({"success": False, "error": "Netzwerkfehler bei Geocoding."}, status=502)

    def has_result(d):
        return isinstance(d, list) and len(d) > 0

    # 2. Deutschland anhängen falls kein Komma vorhanden & kein Treffer bisher
    if not has_result(data) and ',' not in raw_query:
        alt_query = f"{raw_query}, Deutschland"
        params, data_alt, status_flag_alt = perform(alt_query, 2)
        attempts.append((alt_query, params, data_alt, status_flag_alt))
        if status_flag_alt in ('rate_limited','network'):
            # Diese Fehler behandeln wie oben (vorherige Stufe war leer, also relevante Antwort)
            if status_flag_alt == 'rate_limited':
                return JsonResponse({"success": False, "rate_limited": True, "error": "Geocoding gedrosselt (429)."}, status=429)
            return JsonResponse({"success": False, "error": "Netzwerkfehler bei Geocoding."}, status=502)
        if has_result(data_alt):
            data = data_alt

    # 3. Straßennummer trennen (Regex: Wort gefolgt von Zahl ohne Leerzeichen)
    if not has_result(data):
        import re
        m = re.search(r"([A-Za-zÄÖÜäöüß]+)(\d+)", raw_query)
        if m:
            spaced = raw_query.replace(m.group(0), f"{m.group(1)} {m.group(2)}")
            params, data_alt2, status_flag_alt2 = perform(spaced, 3)
            attempts.append((spaced, params, data_alt2, status_flag_alt2))
            if status_flag_alt2 in ('rate_limited','network'):
                if status_flag_alt2 == 'rate_limited':
                    return JsonResponse({"success": False, "rate_limited": True, "error": "Geocoding gedrosselt (429)."}, status=429)
                return JsonResponse({"success": False, "error": "Netzwerkfehler bei Geocoding."}, status=502)
            if has_result(data_alt2):
                data = data_alt2

    # 4. Heuristik "Kirche <Ort>" -> "<Ort> Kirche"
    if not has_result(data) and raw_query.lower().startswith("kirche "):
        parts = raw_query.split(maxsplit=1)
        if len(parts) == 2:
            flipped = f"{parts[1]} Kirche"
            params, data_alt3, status_flag_alt3 = perform(flipped, 4)
            attempts.append((flipped, params, data_alt3, status_flag_alt3))
            if status_flag_alt3 in ('rate_limited','network'):
                if status_flag_alt3 == 'rate_limited':
                    return JsonResponse({"success": False, "rate_limited": True, "error": "Geocoding gedrosselt (429)."}, status=429)
                return JsonResponse({"success": False, "error": "Netzwerkfehler bei Geocoding."}, status=502)
            if has_result(data_alt3):
                data = data_alt3

    # 5. Institution-Wörter entfernen (Universitätsklinikum, Klinikum, Krankenhaus) und erneut versuchen
    if not has_result(data):
        lower = raw_query.lower()
        institution_words = ["universitätsklinikum", "klinikum", "krankenhaus"]
        stripped_query = raw_query
        for w in institution_words:
            stripped_query = " ".join(part for part in stripped_query.split() if part.lower() != w)
        stripped_query = stripped_query.strip()
        if stripped_query and stripped_query != raw_query:
            alt5 = stripped_query if ',' in stripped_query else f"{stripped_query}, Deutschland"
            params, data_alt5, status_flag_alt5 = perform(alt5, 5)
            attempts.append((alt5, params, data_alt5, status_flag_alt5))
            if status_flag_alt5 in ('rate_limited','network'):
                if status_flag_alt5 == 'rate_limited':
                    return JsonResponse({"success": False, "rate_limited": True, "error": "Geocoding gedrosselt (429)."}, status=429)
                return JsonResponse({"success": False, "error": "Netzwerkfehler bei Geocoding."}, status=502)
            if has_result(data_alt5):
                data = data_alt5

    # 6. Letztes Token als Stadt interpretieren (z.B. "Universitätsklinikum Jena" -> "Jena, Deutschland")
    if not has_result(data):
        parts = raw_query.split()
        if len(parts) >= 2:
            last_token = parts[-1]
            alt6 = f"{last_token}, Deutschland"
            params, data_alt6, status_flag_alt6 = perform(alt6, 6)
            attempts.append((alt6, params, data_alt6, status_flag_alt6))
            if status_flag_alt6 in ('rate_limited','network'):
                if status_flag_alt6 == 'rate_limited':
                    return JsonResponse({"success": False, "rate_limited": True, "error": "Geocoding gedrosselt (429)."}, status=429)
                return JsonResponse({"success": False, "error": "Netzwerkfehler bei Geocoding."}, status=502)
            if has_result(data_alt6):
                data = data_alt6

    # Ergebnis extrahieren – falls Center vorhanden, wähle den nächsten Kandidaten.
    from .models import WildvogelhilfeCenter
    center = WildvogelhilfeCenter.get_active()

    def extract_region_name(address: dict) -> str:
        if not isinstance(address, dict):
            return ''
        city = address.get("city") or address.get("town") or address.get("village") or ""
        county = address.get("county") or address.get("district") or ""
        state = address.get("state") or ""
        return city or county or state

    def haversine(lat1, lon1, lat2, lon2):
        """Berechne Distanz in km zwischen zwei Koordinaten (Haversine)."""
        from math import radians, sin, cos, asin, sqrt
        R = 6371.0
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return R * c

    chosen = None
    chosen_distance = None
    if center and has_result(data):
        try:
            c_lat, c_lon = float(center.latitude), float(center.longitude)
            for candidate in data:
                try:
                    lat = float(candidate.get('lat'))
                    lon = float(candidate.get('lon'))
                except (TypeError, ValueError):
                    continue
                address = candidate.get('address', {})
                region_name = extract_region_name(address)
                if not region_name:
                    continue  # nur Kandidaten mit verwertbarer Region
                dist = haversine(c_lat, c_lon, lat, lon)
                if chosen is None or dist < chosen_distance:
                    chosen = candidate
                    chosen_distance = dist
        except Exception as exc:  # sicherheitshalber keine harte Exception
            logger.warning('Distanzberechnung fehlgeschlagen: %s', exc)
    # Fallback: nimm ersten Treffer wenn kein Center / keine geeigneten Kandidaten
    result_data = chosen or (data[0] if has_result(data) else None)
    if not result_data:
        logger.info('Geocoding keine Treffer für Query=%s Versuche=%s', raw_query, [a[0] for a in attempts])
        attempted_queries = [q for q, p, d, s in attempts]
        GeocodeAttempt.objects.create(
            query=raw_query,
            attempted_queries=attempted_queries,
            success=False,
            status_code=None,
            error="Keine Geocoding-Ergebnisse.",
        )
        return JsonResponse({"success": False, "error": "Keine Geocoding-Ergebnisse."}, status=404)

    address = result_data.get('address', {}) if isinstance(result_data, dict) else {}

    city = address.get("city") or address.get("town") or address.get("village") or ""
    county = address.get("county") or address.get("district") or ""
    state = address.get("state") or ""

    # Auswahlregion bestimmen (Bevorzugung Stadt, dann Landkreis, dann Staat)
    region_name_candidate = city or county or state
    region_id = None
    if region_name_candidate:
        try:
            region_obj, created = BirdRegion.objects.get_or_create(name=region_name_candidate)
            region_id = str(region_obj.id)
            if created:
                logger.debug('Region automatisch angelegt: %s', region_name_candidate)
        except Exception as exc:
            logger.error('Region create failed für %s: %s', region_name_candidate, exc)
            region_id = None

    display = region_name_candidate

    payload = {
        "success": True,
        "city": city,
        "county": county,
        "state": state,
        "display": display,
        "region_name": region_name_candidate,
        "region_id": region_id,
        "region_created": bool(region_id and region_name_candidate),
    }
    if request.GET.get("debug") == "1":
        payload["raw"] = {k: address.get(k) for k in ["city", "town", "village", "county", "district", "state", "country"]}
        payload["_attempts"] = [
            {"query": q, "status": s, "result_count": (len(d) if isinstance(d, list) else None)}
            for q, p, d, s in attempts
        ]
        if chosen_distance is not None:
            payload["chosen_distance_km"] = round(chosen_distance, 3)
            payload["candidate_count"] = len(data) if isinstance(data, list) else None
    # Persist attempt record
    attempted_queries = [q for q, p, d, s in attempts]
    try:
        GeocodeAttempt.objects.create(
            query=raw_query,
            attempted_queries=attempted_queries,
            success=True,
            status_code=200,
            city=city,
            county=county,
            state=state,
        )
    except Exception as exc:
        logger.error('Persist GeocodeAttempt fehlgeschlagen: %s', exc)

    cache.set(cache_key, payload, timeout=60 * 30)  # 30 Minuten Cache
    return JsonResponse(payload)


@login_required(login_url="account_login")
def region_backfill_progress(request: HttpRequest) -> JsonResponse:
    """Return JSON status of latest running RegionBackfillTask (or finished last)."""
    # Erst laufenden Task, sonst zuletzt erstellten
    task = RegionBackfillTask.objects.filter(is_running=True).order_by('-created_at').first()
    if not task:
        task = RegionBackfillTask.objects.order_by('-created_at').first()
    if not task:
        return JsonResponse({"active": False})
    # Stale-Detection: Falls Task läuft, aber keinerlei Fortschritt nach bestimmter Zeit
    # (z.B. Thread abgestorben), markieren wir ihn als finished, damit ein Neustart möglich ist.
    if task and task.is_running and task.processed_patients == 0 and task.started_at:
        age = (timezone.now() - task.started_at).total_seconds()
        if age > 120:  # 2 Minuten ohne Fortschritt -> stale
            task.is_running = False
            task.finished_at = timezone.now()
            task.errors.append({"id": None, "reason": "stale_no_progress"})
            task.save(update_fields=['is_running','finished_at','errors'])
            stale = True
        else:
            stale = False
    else:
        stale = False
    # ETA & Rate berechnen
    rate = None
    eta_seconds = None
    # ETA erst ab 5 verarbeiteten Patienten berechnen (stabilere Rate)
    if task.started_at and task.processed_patients > 5 and task.total_patients:
        elapsed = (timezone.now() - task.started_at).total_seconds()
        if elapsed > 0:
            rate = task.processed_patients / elapsed  # Patienten pro Sekunde
            remaining = max(task.total_patients - task.processed_patients, 0)
            if rate > 0:
                eta_seconds = remaining / rate
    aborted = False
    if task.finished_at and not stale and task.total_patients:
        # Aborted wenn beendet und nicht alle verarbeitet (processed < total)
        if task.processed_patients < task.total_patients:
            aborted = True
    return JsonResponse({
        "active": task.is_running,
        "task_id": task.id,
        "processed": task.processed_patients,
        "total": task.total_patients,
        "success": task.success_count,
        "errors": task.error_count,
        "percent": task.progress_percent(),
        "finished": bool(task.finished_at),
        "stale": stale,
        "rate_per_second": rate,
        "eta_seconds": eta_seconds,
        "aborted": aborted,
    })


def _run_region_backfill(task_id: int):  # Hintergrundthread ohne Request
    import threading, time
    from django.utils import timezone
    from .geocode_utils import geocode_place_to_region
    task = RegionBackfillTask.objects.get(id=task_id)
    task.started_at = timezone.now()
    task.is_running = True
    task.save(update_fields=['started_at','is_running'])
    # Patientenset bestimmen
    qs = FallenBird.objects.filter(region__isnull=True).order_by('created')
    total = qs.count()
    task.total_patients = total
    task.save(update_fields=['total_patients'])
    batch_size = task.batch_size
    last_flush = time.time()
    for offset in range(0, total, batch_size):
        # Prüfen ob Abbruch angefordert (is_running False gesetzt durch Abort-Endpoint)
        task.refresh_from_db(fields=['is_running'])
        if not task.is_running:
            # Abbruch markieren
            task.finished_at = timezone.now()
            task.errors.append({"id": None, "reason": "aborted_by_user"})
            task.save(update_fields=['finished_at','errors'])
            return
        batch = list(qs[offset:offset+batch_size])
        for fb in batch:
            try:
                logger.debug('RegionBackfill Task %s: verarbeite Patient %s (processed=%s)', task.id, fb.id, task.processed_patients)
                if fb.region_id:
                    continue
                if not fb.place:
                    task.error_count += 1
                    task.errors.append({"id": str(fb.id), "reason": "kein Fundort"})
                    task.processed_patients += 1
                    # Sofort flush alle paar Sekunden oder nach jedem 10. Patient
                    if task.processed_patients % 10 == 0 or (time.time() - last_flush) > 2:
                        task.save(update_fields=['processed_patients','success_count','error_count','errors'])
                        last_flush = time.time()
                    continue
                region_obj, attempts, err = geocode_place_to_region(fb.place)
                if region_obj and not err:
                    fb.region = region_obj
                    fb.save(update_fields=['region'])
                    task.success_count += 1
                else:
                    task.error_count += 1
                    task.errors.append({"id": str(fb.id), "reason": err or 'keine Zuordnung'})
                task.processed_patients += 1
                if task.processed_patients % 10 == 0 or (time.time() - last_flush) > 2:
                    task.save(update_fields=['processed_patients','success_count','error_count','errors'])
                    last_flush = time.time()
            except Exception as exc:
                task.error_count += 1
                task.errors.append({"id": str(fb.id), "reason": f'exception: {exc}'})
                task.processed_patients += 1
                task.save(update_fields=['processed_patients','success_count','error_count','errors'])
                last_flush = time.time()
        # Batch-Ende Flush falls noch nicht geschehen
        task.save(update_fields=['processed_patients','success_count','error_count','errors'])
        last_flush = time.time()
        time.sleep(0.2)  # kleine Pause zwischen Batches
    task.finished_at = timezone.now()
    task.is_running = False
    task.save(update_fields=['finished_at','is_running'])


@login_required(login_url="account_login")
def region_backfill_start(request: HttpRequest) -> JsonResponse:
    """Start a background region backfill task if none running."""
    active = RegionBackfillTask.objects.filter(is_running=True).exists()
    if active:
        task = RegionBackfillTask.objects.filter(is_running=True).order_by('-created_at').first()
        return JsonResponse({"started": False, "reason": "läuft bereits", "task_id": task.id})
    task = RegionBackfillTask.objects.create()
    import threading
    threading.Thread(target=_run_region_backfill, args=(task.id,), daemon=True).start()
    return JsonResponse({"started": True, "task_id": task.id})


@login_required(login_url="account_login")
def region_backfill_abort(request: HttpRequest) -> JsonResponse:
    """Abort a running region backfill task by setting is_running False."""
    task = RegionBackfillTask.objects.filter(is_running=True).order_by('-created_at').first()
    if not task:
        return JsonResponse({"aborted": False, "reason": "kein laufender Task"}, status=404)
    task.is_running = False
    task.save(update_fields=['is_running'])
    return JsonResponse({"aborted": True, "task_id": task.id})
