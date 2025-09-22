"""Helper utilities for assembling the statistics dashboard context.

The functions and classes in this module are structured to minimise database
queries and provide clear extension points. Docstrings follow the
``:param``/``:returns`` convention to stay compatible with Doxygen.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from django.db.models import Count, Min
from django.utils import timezone

from bird.models import Bird, FallenBird

from .models import (
    StatisticConfiguration,
    StatisticIndividual,
    StatisticTotalGroup,
    StatisticYearGroup,
)


@dataclass(slots=True)
class YearContext:
    """Encapsulate the time window used to build the statistics view."""

    current_year: int
    selected_year: int
    earliest_year: int

    @property
    def can_go_previous(self) -> bool:
        """Return ``True`` if a previous year is available."""

        return self.selected_year > self.earliest_year

    @property
    def can_go_next(self) -> bool:
        """Return ``True`` if a next (newer) year exists."""

        return self.selected_year < self.current_year

    @property
    def previous_year(self) -> int | None:
        """Return the previous year or ``None`` when not available."""

        return self.selected_year - 1 if self.can_go_previous else None

    @property
    def next_year(self) -> int | None:
        """Return the next year or ``None`` when not available."""

        return self.selected_year + 1 if self.can_go_next else None


class StatisticsBuilder:
    """Aggregate statistics for the dashboard in a reusable fashion."""

    def __init__(self, requested_year: str | None):
        self.requested_year = requested_year
        self.current_year = timezone.now().year
        self.year_context = self._determine_year_context()
        self.config = self._resolve_active_configuration()

        # Prefetch the group definitions once to avoid repeated queries later on.
        self.year_groups = list(
            StatisticYearGroup.objects.filter(is_active=True)
            .prefetch_related("status_list")
            .order_by("order")
        )
        self.total_groups = list(
            StatisticTotalGroup.objects.filter(is_active=True)
            .prefetch_related("status_list")
            .order_by("order")
        )
        self.individual_groups = list(
            StatisticIndividual.objects.filter(is_active=True)
            .prefetch_related("status_list")
            .order_by("order")
        )

        self.year_group_status_map = {
            group.id: [status.id for status in group.status_list.all()]
            for group in self.year_groups
        }
        self.total_group_status_map = {
            group.id: [status.id for status in group.status_list.all()]
            for group in self.total_groups
        }
        self.individual_group_status_map = {
            group.id: [status.id for status in group.status_list.all()]
            for group in self.individual_groups
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def build_context(self) -> dict:
        """Build a dictionary with all context variables used by the view."""

        context = {
            "config": self.config,
            "current_year": self.year_context.current_year,
            "selected_year": self.year_context.selected_year,
            "earliest_year": self.year_context.earliest_year,
            "can_go_previous": self.year_context.can_go_previous,
            "can_go_next": self.year_context.can_go_next,
            "previous_year": self.year_context.previous_year,
            "next_year": self.year_context.next_year,
            "year_summary": [],
            "total_summary": [],
            "statistic_individuals": self.individual_groups,
        }

        if self.config.show_year_total_patients:
            patients_this_year, year_summary = self._build_year_statistics()
            context["patients_this_year"] = patients_this_year
            context["year_summary"] = year_summary
        else:
            context["patients_this_year"] = 0

        if self.config.show_total_patients:
            total_patients, total_summary = self._build_total_statistics()
            context["total_patients"] = total_patients
            context["total_summary"] = total_summary

        context["bird_stats"] = self._build_bird_statistics()
        (
            context["circumstances_this_year"],
            context["circumstances_this_year_total"],
            context["circumstances_all_time"],
            context["circumstances_all_time_total"],
        ) = self._build_circumstances()

        return context

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _determine_year_context(self) -> YearContext:
        """Resolve the selected, current and earliest years from the data."""

        earliest_year = (
            FallenBird.objects.aggregate(earliest=Min("date_found__year"))["earliest"]
            or self.current_year
        )

        try:
            requested = int(self.requested_year) if self.requested_year else self.current_year
        except (TypeError, ValueError):
            requested = self.current_year

        selected_year = max(min(requested, self.current_year), earliest_year)
        return YearContext(
            current_year=self.current_year,
            selected_year=selected_year,
            earliest_year=earliest_year,
        )

    def _resolve_active_configuration(self) -> StatisticConfiguration:
        """Return the active configuration, creating a default when missing."""

        config = StatisticConfiguration.objects.filter(is_active=True).first()
        if config:
            return config
        return StatisticConfiguration.objects.create(
            is_active=True,
            show_year_total_patients=True,
            show_total_patients=True,
            show_percentages=True,
            show_absolute_numbers=True,
        )

    def _status_counts(self, queryset) -> dict[int | None, int]:
        """Return a mapping of ``status_id`` to patient counts."""

        return {
            row["status"]: row["count"]
            for row in queryset.values("status").annotate(count=Count("id"))
        }

    def _build_group_summary(
        self,
        status_counts: dict[int | None, int],
        total_patients: int,
        groups: Iterable,
        status_map: dict[int, list[int]],
    ) -> list[dict]:
        """Create the summary data structure for the supplied group list."""

        summary = []
        for group in groups:
            status_ids = status_map.get(group.id, [])
            group_count = sum(status_counts.get(status_id, 0) for status_id in status_ids)
            group_percentage = (group_count / total_patients * 100) if total_patients else 0
            summary.append(
                {
                    "name": group.name,
                    "count": group_count,
                    "percentage": round(group_percentage, 1),
                    "color": group.color,
                    "order": group.order,
                }
            )
        return summary

    def _build_year_statistics(self) -> tuple[int, list[dict]]:
        year_qs = FallenBird.objects.filter(
            date_found__year=self.year_context.selected_year
        )
        status_counts = self._status_counts(year_qs)
        total_patients = sum(status_counts.values())
        summary = self._build_group_summary(
            status_counts,
            total_patients,
            self.year_groups,
            self.year_group_status_map,
        )
        return total_patients, summary

    def _build_total_statistics(self) -> tuple[int, list[dict]]:
        total_qs = FallenBird.objects.all()
        status_counts = self._status_counts(total_qs)
        total_patients = sum(status_counts.values())
        summary = self._build_group_summary(
            status_counts,
            total_patients,
            self.total_groups,
            self.total_group_status_map,
        )
        return total_patients, summary

    def _build_bird_statistics(self) -> list[dict]:
        if not self.individual_groups:
            return []

        per_bird_status_counts = (
            FallenBird.objects.values("bird_id", "status")
            .annotate(count=Count("id"))
            .order_by()
        )

        aggregates: dict[int, dict] = {}
        for row in per_bird_status_counts:
            bird_id = row["bird_id"]
            status_id = row["status"]
            count = row["count"]
            bird_entry = aggregates.setdefault(
                bird_id, {"total": 0, "statuses": defaultdict(int)}
            )
            bird_entry["total"] += count
            bird_entry["statuses"][status_id] += count

        if not aggregates:
            return []

        bird_metadata = {
            bird.id: {
                "name": bird.name,
                "species": bird.species or "Unbekannt",
            }
            for bird in Bird.objects.filter(id__in=aggregates.keys())
        }

        statistics = []
        for bird_id, aggregate in aggregates.items():
            bird_info = bird_metadata.get(bird_id)
            if not bird_info or aggregate["total"] == 0:
                continue

            entry = {
                "name": bird_info["name"],
                "species": bird_info["species"],
                "total": aggregate["total"],
                "groups": [],
            }

            for group in self.individual_groups:
                status_ids = self.individual_group_status_map.get(group.id, [])
                group_count = sum(
                    aggregate["statuses"].get(status_id, 0)
                    for status_id in status_ids
                )
                group_percentage = (
                    (group_count / aggregate["total"]) * 100
                    if aggregate["total"]
                    else 0
                )
                entry["groups"].append(
                    {
                        "name": group.name,
                        "color": group.color,
                        "count": group_count,
                        "percentage": round(group_percentage, 1),
                        "order": group.order,
                    }
                )

            statistics.append(entry)

        statistics.sort(key=lambda item: item["total"], reverse=True)

        if statistics:
            max_total = statistics[0]["total"]
            for bird_entry in statistics:
                total_bar_width = (bird_entry["total"] / max_total * 100) if max_total else 0
                bird_entry["total_bar_width"] = f"{total_bar_width:.1f}".replace(",", ".")
                for group_data in bird_entry["groups"]:
                    absolute_width = (group_data["percentage"] / 100) * total_bar_width
                    group_data["absolute_width"] = f"{absolute_width:.1f}".replace(",", ".")

        return statistics

    def _build_circumstances(self):
        colors = [
            "#FF6384",
            "#36A2EB",
            "#FFCE56",
            "#4BC0C0",
            "#9966FF",
            "#FF9F40",
            "#FF6384",
            "#C9CBCF",
            "#4BC0C0",
            "#FF6384",
        ]

        def format_circumstances(queryset):
            circumstances = list(
                queryset.values(
                    "find_circumstances__name",
                    "find_circumstances__description",
                )
                .annotate(count=Count("id"))
                .order_by("-count")
            )
            total = sum(item["count"] for item in circumstances)
            formatted = []
            for index, item in enumerate(circumstances):
                name = item["find_circumstances__name"] or item["find_circumstances__description"]
                percentage = (item["count"] / total * 100) if total else 0
                formatted.append(
                    {
                        "name": name,
                        "count": item["count"],
                        "percentage": round(percentage, 1),
                        "color": colors[index % len(colors)],
                    }
                )
            return formatted, total

        current_year_qs = FallenBird.objects.filter(
            date_found__year=self.year_context.selected_year,
            find_circumstances__isnull=False,
        )
        all_time_qs = FallenBird.objects.filter(
            find_circumstances__isnull=False,
        )

        current_formatted, current_total = format_circumstances(current_year_qs)
        all_formatted, all_total = format_circumstances(all_time_qs)

        return current_formatted, current_total, all_formatted, all_total

