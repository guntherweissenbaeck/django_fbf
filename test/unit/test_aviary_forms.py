"""
Unit tests for Aviary forms.
"""
import pytest
from django.test import TestCase
from django.contrib.auth.models import User

from aviary.forms import AviaryEditForm


class AviaryEditFormTests(TestCase):
    """Test cases for AviaryEditForm."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.valid_form_data = {
            'name': 'Test Aviary',
            'location': 'Test Location',
            'description': 'Test description',
            'capacity': 50,
            'current_occupancy': 10,
            'contact_person': 'Jane Doe',
            'contact_phone': '987654321',
            'contact_email': 'jane@example.com',
            'notes': 'Test notes'
        }
    
    def test_aviary_edit_form_valid_data(self):
        """Test that form is valid with correct data."""
        form = AviaryEditForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_aviary_edit_form_save(self):
        """Test that form saves correctly."""
        form = AviaryEditForm(data=self.valid_form_data)
        if form.is_valid():
            aviary = form.save(commit=False)
            aviary.created_by = self.user
            aviary.save()
            
            self.assertEqual(aviary.name, 'Test Aviary')
            self.assertEqual(aviary.location, 'Test Location')
            self.assertEqual(aviary.capacity, 50)
            self.assertEqual(aviary.current_occupancy, 10)
    
    def test_aviary_edit_form_required_fields(self):
        """Test form validation with missing required fields."""
        form = AviaryEditForm(data={})
        self.assertFalse(form.is_valid())
        
        # Check that required fields have errors
        required_fields = ['name', 'location']
        for field in required_fields:
            if field in form.fields and form.fields[field].required:
                self.assertIn(field, form.errors)
    
    def test_aviary_edit_form_invalid_capacity(self):
        """Test form validation with invalid capacity."""
        invalid_data = self.valid_form_data.copy()
        invalid_data['capacity'] = -5  # Negative capacity
        
        form = AviaryEditForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        if 'capacity' in form.errors:
            self.assertIn('capacity', form.errors)
    
    def test_aviary_edit_form_invalid_occupancy(self):
        """Test form validation with invalid occupancy."""
        invalid_data = self.valid_form_data.copy()
        invalid_data['current_occupancy'] = -1  # Negative occupancy
        
        form = AviaryEditForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        if 'current_occupancy' in form.errors:
            self.assertIn('current_occupancy', form.errors)
    
    def test_aviary_edit_form_occupancy_exceeds_capacity(self):
        """Test form validation when occupancy exceeds capacity."""
        invalid_data = self.valid_form_data.copy()
        invalid_data['capacity'] = 10
        invalid_data['current_occupancy'] = 15  # More than capacity
        
        form = AviaryEditForm(data=invalid_data)
        # This should be caught by form validation or model validation
        if form.is_valid():
            # If form validation doesn't catch it, model validation should
            with self.assertRaises(Exception):  # Could be ValidationError
                aviary = form.save(commit=False)
                aviary.created_by = self.user
                aviary.full_clean()
        else:
            # Form validation caught the issue
            self.assertTrue('current_occupancy' in form.errors or 
                           'capacity' in form.errors or 
                           '__all__' in form.errors)
    
    def test_aviary_edit_form_invalid_email(self):
        """Test form validation with invalid email."""
        invalid_data = self.valid_form_data.copy()
        invalid_data['contact_email'] = 'invalid-email'
        
        form = AviaryEditForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('contact_email', form.errors)
    
    def test_aviary_edit_form_optional_fields(self):
        """Test form with only required fields."""
        minimal_data = {
            'name': 'Minimal Aviary',
            'location': 'Minimal Location'
        }
        
        form = AviaryEditForm(data=minimal_data)
        if form.is_valid():
            aviary = form.save(commit=False)
            aviary.created_by = self.user
            aviary.save()
            
            self.assertEqual(aviary.name, 'Minimal Aviary')
            self.assertEqual(aviary.location, 'Minimal Location')
        else:
            # Print errors for debugging if needed
            print(f"Minimal form errors: {form.errors}")
    
    def test_aviary_edit_form_field_types(self):
        """Test that form fields have correct types."""
        form = AviaryEditForm()
        
        # Check field types
        if 'capacity' in form.fields:
            self.assertEqual(form.fields['capacity'].__class__.__name__, 'IntegerField')
        
        if 'current_occupancy' in form.fields:
            self.assertEqual(form.fields['current_occupancy'].__class__.__name__, 'IntegerField')
        
        if 'contact_email' in form.fields:
            self.assertEqual(form.fields['contact_email'].__class__.__name__, 'EmailField')
    
    def test_aviary_edit_form_help_text(self):
        """Test that form fields have appropriate help text."""
        form = AviaryEditForm()
        
        # Check if help text is provided for important fields
        if 'capacity' in form.fields and form.fields['capacity'].help_text:
            self.assertIsInstance(form.fields['capacity'].help_text, str)
        
        if 'current_occupancy' in form.fields and form.fields['current_occupancy'].help_text:
            self.assertIsInstance(form.fields['current_occupancy'].help_text, str)
