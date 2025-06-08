"""
Unit tests for Bird models.
"""
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

from bird.models import Bird, FallenBird, BirdStatus, Circumstance
from aviary.models import Aviary


class BirdStatusModelTests(TestCase):
    """Test cases for BirdStatus model."""
    
    def setUp(self):
        """Set up test data."""
        self.bird_status = BirdStatus.objects.create(
            description="Test Status"
        )
    
    def test_bird_status_creation(self):
        """Test that a bird status can be created."""
        self.assertTrue(isinstance(self.bird_status, BirdStatus))
        self.assertEqual(self.bird_status.description, "Test Status")
    
    def test_bird_status_str_representation(self):
        """Test the string representation of bird status."""
        self.assertEqual(str(self.bird_status), "Test Status")
    
    def test_bird_status_description_max_length(self):
        """Test that bird status description has maximum length validation."""
        long_description = "x" * 257  # Assuming max_length is 256
        with self.assertRaises(ValidationError):
            status = BirdStatus(description=long_description)
            status.full_clean()


class CircumstanceModelTests(TestCase):
    """Test cases for Circumstance model."""
    
    def setUp(self):
        """Set up test data."""
        self.circumstance = Circumstance.objects.create(
            description="Test Circumstance"
        )
    
    def test_circumstance_creation(self):
        """Test that a circumstance can be created."""
        self.assertTrue(isinstance(self.circumstance, Circumstance))
        self.assertEqual(self.circumstance.description, "Test Circumstance")
    
    def test_circumstance_str_representation(self):
        """Test the string representation of circumstance."""
        self.assertEqual(str(self.circumstance), "Test Circumstance")


class BirdModelTests(TestCase):
    """Test cases for Bird model."""
    
    def setUp(self):
        """Set up test data."""
        self.bird = Bird.objects.create(
            name="Test Bird",
            description="Test bird description"
        )
    
    def test_bird_creation(self):
        """Test that a bird can be created."""
        self.assertTrue(isinstance(self.bird, Bird))
        self.assertEqual(self.bird.name, "Test Bird")
        self.assertEqual(self.bird.description, "Test bird description")
    
    def test_bird_str_representation(self):
        """Test the string representation of bird."""
        self.assertEqual(str(self.bird), "Test Bird")
    
    def test_bird_name_unique(self):
        """Test that bird name must be unique."""
        with self.assertRaises(ValidationError):
            duplicate_bird = Bird(name="Test Bird", description="Another description")
            duplicate_bird.full_clean()
    
    def test_bird_required_fields(self):
        """Test that required fields are validated."""
        with self.assertRaises(ValidationError):
            bird = Bird()
            bird.full_clean()


class FallenBirdModelTests(TestCase):
    """Test cases for FallenBird model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.aviary = Aviary.objects.create(
            name="Test Aviary",
            location="Test Location",
            created_by=self.user
        )
        
        self.bird_status = BirdStatus.objects.create(
            name="Verstorben",
            description="Deceased bird"
        )
        
        self.circumstance = Circumstance.objects.create(
            name="Gefunden",
            description="Found bird"
        )
        
        self.bird = Bird.objects.create(
            name="Test Bird",
            species="Test Species",
            aviary=self.aviary,
            status=self.bird_status,
            circumstance=self.circumstance,
            created_by=self.user
        )
        
        self.fallen_bird = FallenBird.objects.create(
            bird=self.bird,
            death_date=timezone.now().date(),
            cause_of_death="Natural causes",
            notes="Test notes",
            created_by=self.user
        )
    
    def test_fallen_bird_creation(self):
        """Test that a fallen bird can be created."""
        self.assertTrue(isinstance(self.fallen_bird, FallenBird))
        self.assertEqual(self.fallen_bird.bird, self.bird)
        self.assertEqual(self.fallen_bird.cause_of_death, "Natural causes")
        self.assertEqual(self.fallen_bird.notes, "Test notes")
    
    def test_fallen_bird_str_representation(self):
        """Test the string representation of fallen bird."""
        expected = f"Gefallener Vogel: {self.bird.name}"
        self.assertEqual(str(self.fallen_bird), expected)
    
    def test_fallen_bird_relationship(self):
        """Test fallen bird relationship with bird."""
        self.assertEqual(self.fallen_bird.bird, self.bird)
        self.assertEqual(self.fallen_bird.created_by, self.user)
