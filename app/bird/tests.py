from django.test import TestCase
from .models import Bird
from aviary.models import Aviary


class BirdTestCase(TestCase):
    def setUp(self):
        self.aviary = Aviary.objects.create(
            description="Voliere 1",
            condition="Offen",
            last_ward_round="2021-01-01",
            comment="Test",
        )
        self.bird = Bird.objects.create(
            name="Vogel 1",
            species="Art 1",
            aviary=self.aviary,
            found_date="2020-01-01",
        )

    def test_bird_creation(self):
        """Test that a bird can be created successfully."""
        self.assertEqual(self.bird.name, "Vogel 1")
        self.assertEqual(self.bird.species, "Art 1")
        self.assertEqual(self.bird.aviary, self.aviary)
