from django.test import TestCase


class AviaryTestCase(TestCase):
    def setUp(self):
        Aviary.objects.create(
            description="Voliere 1",
            condition="Offen",
            last_ward_round="2021-01-01",
            comment="Test",
        )

    def test_aviary_description(self):
        aviary = Aviary.objects.get(description="Voliere 1")
        self.assertEqual(aviary.description, "Voliere 1")

    def test_aviary_condition(self):
        aviary = Aviary.objects.get(description="Voliere 1")
        self.assertEqual(aviary.condition, "Offen")

    def test_aviary_last_ward_round(self):
        aviary = Aviary.objects.get(description="Voliere 1")
        self.assertEqual(aviary.last_ward_round, "2021-01-01")

    def test_aviary_comment(self):
        aviary = Aviary.objects.get(description="Voliere 1")
        self.assertEqual(aviary.comment, "Test")
