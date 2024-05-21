from django.test import TestCase


class BirdTestCase(TestCase):
    def setUp(self):
        Bird.objects.create(
            name="Vogel 1",
            species="Art 1",
            aviary=Aviary.objects.create(
                description="Voliere 1",
                condition="Offen",
                last_ward_round="2021-01-01",
                comment="Test",
            ),
            date_of_birth="2020-01-01
