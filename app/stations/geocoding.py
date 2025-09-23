"""! @brief Utility helpers to geocode Wildvogelhilfe stations."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = getattr(
    settings, "STATIONS_GEOCODER_ENDPOINT", "https://nominatim.openstreetmap.org/search"
)
DEFAULT_USER_AGENT = getattr(
    settings,
    "STATIONS_GEOCODER_USER_AGENT",
    "FBF Stations Geocoder/1.0 (+https://fallenbirdyform.example)",
)

COUNTRY_CODE_MAP = {
    "de": "de",
    "deutschland": "de",
    "germany": "de",
    "österreich": "at",
    "austria": "at",
    "schweiz": "ch",
    "switzerland": "ch",
    "italien": "it",
    "italy": "it",
}


@dataclass(slots=True)
class GeocodingResult:
    """! @brief Successful geocoding outcome."""

    latitude: Decimal
    longitude: Decimal
    raw: dict[str, Any]


def _normalise_country(country: str | None) -> str | None:
    if not country:
        return None
    slug = country.strip().lower()
    return COUNTRY_CODE_MAP.get(slug, None)


def _request(params: dict[str, Any]) -> dict[str, Any] | None:
    try:
        response = requests.get(
            DEFAULT_ENDPOINT,
            params=params,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - network interaction
        logger.warning("Geocoding request failed: %s", exc)
        return None

    data = response.json()
    if not isinstance(data, list) or not data:
        return None
    return data[0]


def geocode_address(
    *,
    street: str | None,
    postal_code: str | None,
    city: str | None,
    state: str | None,
    country: str | None,
    fallback_query: str | None = None,
) -> GeocodingResult | None:
    """! @brief Resolve an address to coordinates using Nominatim."""

    country_code = _normalise_country(country)

    params: dict[str, Any] = {
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }

    query_parts = [
        part.strip()
        for part in [street, city, state, postal_code, country]
        if part and part.strip()
    ]

    if query_parts:
        params["q"] = ", ".join(query_parts)
    elif fallback_query:
        params["q"] = fallback_query

    if not params.get("q") and postal_code:
        params["postalcode"] = postal_code

    if country_code:
        params["countrycodes"] = country_code

    raw = _request(params)
    if not raw:
        return None

    try:
        lat = Decimal(str(raw.get("lat")))
        lon = Decimal(str(raw.get("lon")))
    except (TypeError, ArithmeticError, ValueError):
        return None

    return GeocodingResult(latitude=lat, longitude=lon, raw=raw)


def geocode_station(station) -> GeocodingResult | None:
    """! @brief Convenience wrapper for a ``WildbirdHelpStation`` instance."""

    fallback = None
    if station.address:
        fallback = station.address

    return geocode_address(
        street=getattr(station, "street", None),
        postal_code=getattr(station, "postal_code", None),
        city=getattr(station, "city", None),
        state=getattr(station, "state", None),
        country=getattr(station, "country", None),
        fallback_query=fallback,
    )
