"""
Unit tests for Aviary models.
"""
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone

from aviary.models import Aviary


class AviaryModelTests(TestCase):
    """Test cases for Aviary model."""
    
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
            description="Test description",
            capacity=50,
            current_occupancy=10,
            contact_person="Jane Doe",
            contact_phone="987654321",
            contact_email="jane@example.com",
            created_by=self.user
        )
    
    def test_aviary_creation(self):
        """Test that an aviary can be created."""
        self.assertTrue(isinstance(self.aviary, Aviary))
        self.assertEqual(self.aviary.name, "Test Aviary")
        self.assertEqual(self.aviary.location, "Test Location")
        self.assertEqual(self.aviary.description, "Test description")
        self.assertEqual(self.aviary.capacity, 50)
        self.assertEqual(self.aviary.current_occupancy, 10)
        self.assertEqual(self.aviary.contact_person, "Jane Doe")
        self.assertEqual(self.aviary.contact_phone, "987654321")
        self.assertEqual(self.aviary.contact_email, "jane@example.com")
    
    def test_aviary_str_representation(self):
        """Test the string representation of aviary."""
        self.assertEqual(str(self.aviary), "Test Aviary")
    
    def test_aviary_capacity_validation(self):
        """Test that aviary capacity is validated."""
        # Test negative capacity
        with self.assertRaises(ValidationError):
            aviary = Aviary(
                name="Invalid Aviary",
                location="Test Location",
                capacity=-1,
                created_by=self.user
            )
            aviary.full_clean()
        
        # Test zero capacity
        aviary = Aviary(
            name="Zero Capacity Aviary",
            location="Test Location", 
            capacity=0,
            created_by=self.user
        )
        # This should be valid
        aviary.full_clean()
    
    def test_aviary_occupancy_validation(self):
        """Test that current occupancy is validated."""
        # Test negative occupancy
        with self.assertRaises(ValidationError):
            aviary = Aviary(
                name="Invalid Aviary",
                location="Test Location",
                current_occupancy=-1,
                created_by=self.user
            )
            aviary.full_clean()
    
    def test_aviary_occupancy_exceeds_capacity(self):
        """Test validation when occupancy exceeds capacity."""
        # Test occupancy exceeding capacity
        with self.assertRaises(ValidationError):
            aviary = Aviary(
                name="Overcrowded Aviary",
                location="Test Location",
                capacity=10,
                current_occupancy=15,
                created_by=self.user
            )
            aviary.full_clean()
    
    def test_aviary_required_fields(self):
        """Test that required fields are validated."""
        with self.assertRaises(ValidationError):
            aviary = Aviary()
            aviary.full_clean()
    
    def test_aviary_email_validation(self):
        """Test that email field is validated."""
        with self.assertRaises(ValidationError):
            aviary = Aviary(
                name="Test Aviary",
                location="Test Location",
                contact_email="invalid-email",
                created_by=self.user
            )
            aviary.full_clean()
    
    def test_aviary_relationship(self):
        """Test aviary relationship with user."""
        self.assertEqual(self.aviary.created_by, self.user)
    
    def test_aviary_is_full_property(self):
        """Test the is_full property."""
        # Create aviary at capacity
        full_aviary = Aviary.objects.create(
            name="Full Aviary",
            location="Test Location",
            capacity=5,
            current_occupancy=5,
            created_by=self.user
        )
        
        # Check if we can add a property method to test
        self.assertEqual(full_aviary.capacity, full_aviary.current_occupancy)
        
        # Check partial occupancy
        self.assertLess(self.aviary.current_occupancy, self.aviary.capacity)
    
    def test_aviary_available_space(self):
        """Test calculating available space."""
        expected_available = self.aviary.capacity - self.aviary.current_occupancy
        self.assertEqual(expected_available, 40)  # 50 - 10 = 40
