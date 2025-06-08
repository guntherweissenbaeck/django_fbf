"""
Unit tests for Costs models.
"""
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from decimal import Decimal

from costs.models import Costs
from bird.models import Bird, BirdStatus, Circumstance
from aviary.models import Aviary


class CostsModelTests(TestCase):
    """Test cases for Costs model."""
    
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
            name="Gesund",
            description="Healthy bird"
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
        
        self.costs = Costs.objects.create(
            bird=self.bird,
            description="Veterinary treatment",
            amount=Decimal('150.75'),
            cost_date=timezone.now().date(),
            category="medical",
            invoice_number="INV-001",
            vendor="Test Veterinary Clinic",
            notes="Routine checkup and treatment",
            user=self.user,
            created_by=self.user
        )
    
    def test_costs_creation(self):
        """Test that a cost entry can be created."""
        self.assertTrue(isinstance(self.costs, Costs))
        self.assertEqual(self.costs.bird, self.bird)
        self.assertEqual(self.costs.description, "Veterinary treatment")
        self.assertEqual(self.costs.amount, Decimal('150.75'))
        self.assertEqual(self.costs.category, "medical")
        self.assertEqual(self.costs.invoice_number, "INV-001")
        self.assertEqual(self.costs.vendor, "Test Veterinary Clinic")
        self.assertEqual(self.costs.notes, "Routine checkup and treatment")
    
    def test_costs_str_representation(self):
        """Test the string representation of costs."""
        expected = f"{self.costs.description} - €{self.costs.amount}"
        self.assertEqual(str(self.costs), expected)
    
    def test_costs_amount_validation(self):
        """Test that cost amount is validated."""
        # Test negative amount
        with self.assertRaises(ValidationError):
            costs = Costs(
                bird=self.bird,
                description="Invalid cost",
                amount=Decimal('-10.00'),
                cost_date=timezone.now().date(),
                user=self.user,
                created_by=self.user
            )
            costs.full_clean()
        
        # Test zero amount (should be valid)
        costs = Costs(
            bird=self.bird,
            description="Zero cost",
            amount=Decimal('0.00'),
            cost_date=timezone.now().date(),
            user=self.user,
            created_by=self.user
        )
        costs.full_clean()  # Should not raise validation error
    
    def test_costs_category_choices(self):
        """Test that cost category has valid choices."""
        valid_categories = ['medical', 'food', 'equipment', 'transport', 'other']
        self.assertIn(self.costs.category, valid_categories)
        
        # Test invalid category
        with self.assertRaises(ValidationError):
            costs = Costs(
                bird=self.bird,
                description="Invalid category",
                amount=Decimal('10.00'),
                category="invalid_category",
                cost_date=timezone.now().date(),
                user=self.user,
                created_by=self.user
            )
            costs.full_clean()
    
    def test_costs_required_fields(self):
        """Test that required fields are validated."""
        with self.assertRaises(ValidationError):
            costs = Costs()
            costs.full_clean()
    
    def test_costs_relationship(self):
        """Test costs relationships."""
        self.assertEqual(self.costs.bird, self.bird)
        self.assertEqual(self.costs.created_by, self.user)
    
    def test_costs_date_validation(self):
        """Test that cost date is validated."""
        # Test future date (should be valid unless restricted)
        future_date = timezone.now().date() + timezone.timedelta(days=30)
        costs = Costs(
            bird=self.bird,
            description="Future cost",
            amount=Decimal('50.00'),
            cost_date=future_date,
            user=self.user,
            created_by=self.user
        )
        costs.full_clean()  # Should not raise validation error
    
    def test_costs_decimal_precision(self):
        """Test decimal precision for amounts."""
        # Test 2 decimal place amount (model allows max 2 decimal places)
        precise_amount = Decimal('123.45')
        costs = Costs(
            bird=self.bird,
            description="Precise amount",
            amount=precise_amount,
            cost_date=timezone.now().date(),
            user=self.user,
            created_by=self.user
        )
        costs.full_clean()
        costs.save()
        
        # Reload from database and check precision
        costs.refresh_from_db()
        # Model supports 2 decimal places, should match exactly
        self.assertEqual(costs.amount, precise_amount)
        
        # Test that amounts with more than 2 decimal places are rejected
        with self.assertRaises(ValidationError):
            invalid_costs = Costs(
                bird=self.bird,
                description="Too precise amount",
                amount=Decimal('123.456'),  # More than 2 decimal places
                cost_date=timezone.now().date(),
                user=self.user,
                created_by=self.user
            )
            invalid_costs.full_clean()
    
    def test_costs_filtering_by_category(self):
        """Test filtering costs by category."""
        # Create costs in different categories
        Costs.objects.create(
            bird=self.bird,
            description="Food cost",
            amount=Decimal('25.00'),
            category="food",
            cost_date=timezone.now().date(),
            user=self.user,
            created_by=self.user
        )
        
        Costs.objects.create(
            bird=self.bird,
            description="Equipment cost",
            amount=Decimal('75.00'),
            category="equipment",
            cost_date=timezone.now().date(),
            user=self.user,
            created_by=self.user
        )
        
        # Filter by category
        medical_costs = Costs.objects.filter(category="medical")
        food_costs = Costs.objects.filter(category="food")
        equipment_costs = Costs.objects.filter(category="equipment")
        
        self.assertEqual(medical_costs.count(), 1)
        self.assertEqual(food_costs.count(), 1)
        self.assertEqual(equipment_costs.count(), 1)
        
        self.assertIn(self.costs, medical_costs)
    
    def test_costs_total_for_bird(self):
        """Test calculating total costs for a bird."""
        # Create additional costs for the same bird
        Costs.objects.create(
            bird=self.bird,
            description="Additional cost 1",
            amount=Decimal('50.00'),
            cost_date=timezone.now().date(),
            user=self.user,
            created_by=self.user
        )
        
        Costs.objects.create(
            bird=self.bird,
            description="Additional cost 2",
            amount=Decimal('25.25'),
            cost_date=timezone.now().date(),
            user=self.user,
            created_by=self.user
        )
        
        # Calculate total costs for the bird
        total_costs = Costs.objects.filter(bird=self.bird).aggregate(
            total=models.Sum('amount')
        )['total']
        
        expected_total = Decimal('150.75') + Decimal('50.00') + Decimal('25.25')
        self.assertEqual(total_costs, expected_total)
    
    def test_costs_invoice_number_uniqueness(self):
        """Test invoice number uniqueness if enforced."""
        # Try to create another cost with the same invoice number
        try:
            duplicate_costs = Costs(
                bird=self.bird,
                description="Duplicate invoice",
                amount=Decimal('10.00'),
                invoice_number="INV-001",  # Same as self.costs
                cost_date=timezone.now().date(),
                user=self.user,
                created_by=self.user
            )
            duplicate_costs.full_clean()
            # If unique constraint exists, this should fail
        except ValidationError:
            # Expected if invoice_number has unique constraint
            pass
