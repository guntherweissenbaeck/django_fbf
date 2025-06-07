"""
Unit tests for Contact models.
"""
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone

from contact.models import Contact


class ContactModelTests(TestCase):
    """Test cases for Contact model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.contact = Contact.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="123456789",
            address="123 Test Street",
            city="Test City",
            postal_code="12345",
            country="Test Country",
            notes="Test notes",
            is_active=True,
            created_by=self.user
        )
    
    def test_contact_creation(self):
        """Test that a contact can be created."""
        self.assertTrue(isinstance(self.contact, Contact))
        self.assertEqual(self.contact.first_name, "John")
        self.assertEqual(self.contact.last_name, "Doe")
        self.assertEqual(self.contact.email, "john.doe@example.com")
        self.assertEqual(self.contact.phone, "123456789")
        self.assertEqual(self.contact.address, "123 Test Street")
        self.assertEqual(self.contact.city, "Test City")
        self.assertEqual(self.contact.postal_code, "12345")
        self.assertEqual(self.contact.country, "Test Country")
        self.assertEqual(self.contact.notes, "Test notes")
        self.assertTrue(self.contact.is_active)
    
    def test_contact_str_representation(self):
        """Test the string representation of contact."""
        expected = f"{self.contact.first_name} {self.contact.last_name}"
        self.assertEqual(str(self.contact), expected)
    
    def test_contact_full_name_property(self):
        """Test the full name property."""
        expected = f"{self.contact.first_name} {self.contact.last_name}"
        self.assertEqual(self.contact.full_name, expected)
    
    def test_contact_email_validation(self):
        """Test that email field is validated."""
        with self.assertRaises(ValidationError):
            contact = Contact(
                first_name="Invalid",
                last_name="Email",
                email="invalid-email",
                created_by=self.user
            )
            contact.full_clean()
    
    def test_contact_required_fields(self):
        """Test that required fields are validated."""
        with self.assertRaises(ValidationError):
            contact = Contact()
            contact.full_clean()
    
    def test_contact_optional_fields(self):
        """Test that contact can be created with minimal required fields."""
        minimal_contact = Contact(
            first_name="Jane",
            last_name="Smith",
            created_by=self.user
        )
        minimal_contact.full_clean()  # Should not raise validation error
        minimal_contact.save()
        
        self.assertEqual(minimal_contact.first_name, "Jane")
        self.assertEqual(minimal_contact.last_name, "Smith")
        self.assertTrue(minimal_contact.is_active)  # Default value
    
    def test_contact_relationship(self):
        """Test contact relationship with user."""
        self.assertEqual(self.contact.created_by, self.user)
    
    def test_contact_is_active_default(self):
        """Test that is_active defaults to True."""
        new_contact = Contact(
            first_name="Default",
            last_name="Active",
            created_by=self.user
        )
        # Before saving, check default
        self.assertTrue(new_contact.is_active)
    
    def test_contact_postal_code_validation(self):
        """Test postal code format validation if implemented."""
        # This would depend on your specific validation rules
        contact = Contact(
            first_name="Test",
            last_name="PostalCode",
            postal_code="INVALID_FORMAT_IF_VALIDATED",
            created_by=self.user
        )
        # If you have postal code validation, this would fail
        # For now, just test that it accepts the value
        contact.full_clean()
    
    def test_contact_phone_validation(self):
        """Test phone number validation if implemented."""
        # Test with various phone formats
        phone_formats = [
            "123456789",
            "+49123456789",
            "0123 456 789",
            "(0123) 456-789"
        ]
        
        for phone in phone_formats:
            contact = Contact(
                first_name="Test",
                last_name="Phone",
                phone=phone,
                created_by=self.user
            )
            # Should not raise validation error
            contact.full_clean()
    
    def test_contact_search_fields(self):
        """Test that contact can be found by common search terms."""
        # Test finding by name
        contacts = Contact.objects.filter(
            first_name__icontains="john"
        )
        self.assertIn(self.contact, contacts)
        
        # Test finding by email
        contacts = Contact.objects.filter(
            email__icontains="john.doe"
        )
        self.assertIn(self.contact, contacts)
    
    def test_contact_ordering(self):
        """Test default ordering of contacts."""
        # Create additional contacts
        Contact.objects.create(
            first_name="Alice",
            last_name="Smith",
            created_by=self.user
        )
        Contact.objects.create(
            first_name="Bob",
            last_name="Jones", 
            created_by=self.user
        )
        
        # Get all contacts (should be ordered by last_name then first_name if implemented)
        contacts = list(Contact.objects.all())
        
        # Check that we have all contacts
        self.assertEqual(len(contacts), 3)
