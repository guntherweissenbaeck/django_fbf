"""Targeted tests for the statistics aggregation helpers."""
from datetime import date

import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from bird.models import Bird, BirdStatus, Circumstance, FallenBird
from statistic.models import (
    StatisticConfiguration,
    StatisticIndividual,
    StatisticTotalGroup,
    StatisticYearGroup,
)
from statistic.services import StatisticsBuilder


class StatisticsBuilderTests(TestCase):
    """Exercise the high-level builder to improve coverage."""

    def setUp(self):
        self.current_year = timezone.now().year
        self.previous_year = self.current_year - 1

        self.user = User.objects.create_user(
            username="stats-user",
            email="stats@example.com",
            password="stats-pass",
        )

        self.status_released = BirdStatus.objects.create(description="Ausgewildert")
        self.status_dead = BirdStatus.objects.create(description="Verstorben")

        self.year_group_released = StatisticYearGroup.objects.create(
            name="Ausgewildert",
            color="#00ff00",
            order=1,
        )
        self.year_group_released.status_list.add(self.status_released)

        self.year_group_dead = StatisticYearGroup.objects.create(
            name="Verstorben",
            color="#ff0000",
            order=2,
        )
        self.year_group_dead.status_list.add(self.status_dead)

        self.total_group_released = StatisticTotalGroup.objects.create(
            name="Ausgewildert",
            color="#00ff00",
            order=1,
        )
        self.total_group_released.status_list.add(self.status_released)

        self.total_group_dead = StatisticTotalGroup.objects.create(
            name="Verstorben",
            color="#ff0000",
            order=2,
        )
        self.total_group_dead.status_list.add(self.status_dead)

        self.individual_group_released = StatisticIndividual.objects.create(
            name="Ausgewildert",
            color="#00ff00",
            order=1,
        )
        self.individual_group_released.status_list.add(self.status_released)

        self.individual_group_dead = StatisticIndividual.objects.create(
            name="Verstorben",
            color="#ff0000",
            order=2,
        )
        self.individual_group_dead.status_list.add(self.status_dead)

        self.circumstance_window = Circumstance.objects.create(
            name="Fenster",
            description="Fensterfund",
        )
        self.circumstance_cat = Circumstance.objects.create(
            name="Katze",
            description="Katze brachte den Vogel",
        )

        self.bird_swift = Bird.objects.create(
            name="Mauersegler",
            species="Apus apus",
            status=self.status_released,
            melden_an_naturschutzbehoerde=True,
        )
        self.bird_owl = Bird.objects.create(
            name="Waldkauz",
            species="Strix aluco",
            status=self.status_dead,
        )

        FallenBird.objects.create(
            bird=self.bird_swift,
            status=self.status_released,
            date_found=date(self.current_year, 5, 10),
            find_circumstances=self.circumstance_window,
            user=self.user,
        )
        FallenBird.objects.create(
            bird=self.bird_swift,
            status=self.status_dead,
            date_found=date(self.current_year, 6, 5),
            find_circumstances=self.circumstance_cat,
            user=self.user,
        )
        FallenBird.objects.create(
            bird=self.bird_owl,
            status=self.status_dead,
            date_found=date(self.previous_year, 7, 15),
            find_circumstances=self.circumstance_cat,
            user=self.user,
        )

    def test_builder_creates_default_configuration_and_aggregates(self):
        builder = StatisticsBuilder(str(self.current_year))
        context = builder.build_context()

        # Default configuration is created on-the-fly when none exists.
        self.assertEqual(StatisticConfiguration.objects.count(), 1)
        config = context["config"]
        self.assertTrue(config.show_year_total_patients)

        self.assertEqual(context["patients_this_year"], 2)
        self.assertEqual(context["total_patients"], 3)
        self.assertTrue(context["can_go_previous"])
        self.assertTrue(context["can_go_next"] is False)
        self.assertEqual(context["previous_year"], self.previous_year)
        self.assertIsNone(context["next_year"])

        year_summary = {item["name"]: item for item in context["year_summary"]}
        self.assertEqual(year_summary["Ausgewildert"]["count"], 1)
        self.assertEqual(year_summary["Verstorben"]["count"], 1)

        total_summary = {item["name"]: item for item in context["total_summary"]}
        self.assertEqual(total_summary["Verstorben"]["count"], 2)

        bird_stats = context["bird_stats"]
        leading = bird_stats[0]
        self.assertEqual(leading["name"], "Mauersegler")
        self.assertIn("total_bar_width", leading)
        self.assertGreater(float(leading["total_bar_width"]), 0.0)
        first_group = leading["groups"][0]
        self.assertIn("absolute_width", first_group)

        circ_this_year = {item["name"]: item for item in context["circumstances_this_year"]}
        self.assertEqual(circ_this_year["Fenster"]["count"], 1)
        self.assertEqual(context["circumstances_this_year_total"], 2)

    def test_year_selection_clamped_to_current(self):
        # Configuration now exists, exercise the returning branch.
        builder = StatisticsBuilder(str(self.current_year + 5))
        context = builder.build_context()
        self.assertEqual(context["selected_year"], self.current_year)
        self.assertFalse(context["can_go_next"])
        self.assertGreaterEqual(context["earliest_year"], self.previous_year)
