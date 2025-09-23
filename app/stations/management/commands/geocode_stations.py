"""! @brief Batch geocode Wildvogelhilfe stations via CLI."""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandParser
from django.db.models import Q

from stations.models import WildbirdHelpStation
from stations.services import batch_update_coordinates


class Command(BaseCommand):
    """! @brief Management command that resolves missing coordinates."""

    help = "Koordinaten für Wildvogelhilfe-Stationen automatisch bestimmen."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--ids",
            nargs="+",
            type=int,
            help="Optionale Liste von Stations-IDs, die verarbeitet werden sollen.",
        )
        parser.add_argument(
            "--missing",
            action="store_true",
            help="Nur Stationen ohne Koordinaten berücksichtigen.",
        )

    def handle(self, *args, **options):
        queryset = WildbirdHelpStation.objects.all()

        if options.get("ids"):
            queryset = queryset.filter(pk__in=options["ids"])
        if options.get("missing"):
            queryset = queryset.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True))

        stations = list(queryset.distinct())
        total = len(stations)
        if not total:
            self.stdout.write(self.style.WARNING("Keine passenden Stationen gefunden."))
            return

        successes, errors = batch_update_coordinates(stations)

        self.stdout.write(
            self.style.SUCCESS(
                f"Koordinaten erfolgreich ermittelt für {successes} von {total} Station(en)."
            )
        )

        if errors:
            for line in errors:
                self.stdout.write(self.style.WARNING(line))
