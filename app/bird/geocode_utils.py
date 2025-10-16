"""Hilfsfunktionen für Geocoding außerhalb der View (z.B. Admin-Aktionen).

Die Funktion kapselt Fallback-Heuristiken in vereinfachter Form (keine Cache-/Backoff-Logik),
da Admin-Bulk-Aktionen meist selten ausgeführt werden. Für hohe Datenmengen könnte
das wiederverwendet oder erweitert werden.
"""

from typing import Tuple, Optional, List
import re
import requests
from math import radians, sin, cos, asin, sqrt
from .models import BirdRegion, WildvogelhilfeCenter
from .views import DEFAULT_ENDPOINT, DEFAULT_USER_AGENT


def _attempt(query: str) -> List[dict]:
    """Führe eine Geocoding-Abfrage aus und liefere eine Liste von Kandidaten (ggf. leer)."""
    try:
        resp = requests.get(
            DEFAULT_ENDPOINT,
            params={'q': query, 'format': 'json', 'limit': 7, 'addressdetails': 1},
            headers={'User-Agent': DEFAULT_USER_AGENT},
            timeout=10,
        )
        if resp.status_code != 200:
            return []
        data = resp.json()
        if isinstance(data, list):
            return data
    except requests.RequestException:
        return []
    return []


def geocode_place_to_region(place: str) -> Tuple[Optional[BirdRegion], List[str], str]:
    """Versucht einen Fundort grob zu einer Region (Stadt/County/State) aufzulösen.

    Rückgabe: (region_obj oder None, versuchte_queries, error_string oder '').
    """
    place = (place or '').strip()
    if not place:
        return None, [], 'leer'

    attempts: List[str] = []
    chosen: Optional[dict] = None
    chosen_distance: Optional[float] = None

    def extract_region_name(address: dict) -> str:
        if not isinstance(address, dict):
            return ''
        city = address.get("city") or address.get("town") or address.get("village") or ""
        county = address.get("county") or address.get("district") or ""
        state = address.get("state") or ""
        return city or county or state

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return R * c

    center = WildvogelhilfeCenter.get_active()
    center_lat = center.longitude if center else None  # bug? ensure proper variable names
    if center:
        center_lat = center.latitude
        center_lon = center.longitude
    else:
        center_lat = center_lon = None

    def consider_candidates(candidates: List[dict]):
        nonlocal chosen, chosen_distance
        for cand in candidates:
            address = cand.get('address', {})
            region_name = extract_region_name(address)
            if not region_name:
                continue
            # Distanz berechnen falls Center vorhanden sonst erste passende Wahl
            if center_lat is not None and center_lon is not None:
                try:
                    lat = float(cand.get('lat'))
                    lon = float(cand.get('lon'))
                except (TypeError, ValueError):
                    continue
                dist = haversine(center_lat, center_lon, lat, lon)
                if chosen is None or dist < chosen_distance:
                    chosen = cand
                    chosen_distance = dist
            else:
                if chosen is None:
                    chosen = cand

    def add(query: str):
        attempts.append(query)
        # Falls schon gewählt und Center existiert, trotzdem weitere Queries erlauben falls noch nichts gewählt?
        if chosen is None:
            cand_list = _attempt(query)
            if cand_list:
                consider_candidates(cand_list)

    # Basis
    add(place)
    if not chosen and ',' not in place:
        add(f"{place}, Deutschland")
    if not chosen:
        m = re.search(r"([A-Za-zÄÖÜäöüß]+)(\d+)", place)
        if m:
            add(place.replace(m.group(0), f"{m.group(1)} {m.group(2)}"))
    if not chosen and place.lower().startswith('kirche '):
        parts = place.split(maxsplit=1)
        if len(parts) == 2:
            add(f"{parts[1]} Kirche")
    if not chosen:
        lower = place.lower()
        inst_words = ["universitätsklinikum", "klinikum", "krankenhaus"]
        stripped = ' '.join(p for p in place.split() if p.lower() not in inst_words)
        stripped = stripped.strip()
        if stripped and stripped != place:
            add(stripped if ',' in stripped else f"{stripped}, Deutschland")
    if not chosen:
        parts = place.split()
        if len(parts) >= 2:
            add(f"{parts[-1]}, Deutschland")

    if not chosen:
        return None, attempts, 'keine Treffer'

    address = chosen.get('address', {})
    city = address.get("city") or address.get("town") or address.get("village") or ""
    county = address.get("county") or address.get("district") or ""
    state = address.get("state") or ""
    region_name = city or county or state
    if not region_name:
        return None, attempts, 'unvollständige Adresse'
    region_obj, _ = BirdRegion.objects.get_or_create(name=region_name)
    return region_obj, attempts, ''
