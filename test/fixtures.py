"""
Test fixtures and utilities for Django FBF tests.
"""
import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

from bird.models import Bird, BirdStatus, Circumstance
from aviary.models import Aviary
from costs.models import Costs
from contact.models import Contact


class TestDataMixin:
    """Mixin class providing common test data setup."""
    
    def create_test_user(self, username='testuser', email='test@example.com', is_staff=False):
        """Create a test user."""
        return User.objects.create_user(
            username=username,
            email=email,
            password='testpass123',
            is_staff=is_staff
        )
    
    def create_test_aviary(self, user, name='Test Aviary'):
        """Create a test aviary."""
        return Aviary.objects.create(
            name=name,
            location='Test Location',
            description='Test description',
            capacity=20,
            current_occupancy=5,
            contact_person='Test Contact',
            contact_phone='123456789',
            contact_email='contact@example.com',
            created_by=user
        )
    
    def create_test_bird_status(self, name='Gesund'):
        """Create a test bird status."""
        return BirdStatus.objects.create(
            name=name,
            description=f'{name} bird status'
        )
    
    def create_test_circumstance(self, name='Gefunden'):
        """Create a test circumstance."""
        return Circumstance.objects.create(
            name=name,
            description=f'{name} circumstance'
        )
    
    def create_test_bird(self, user, aviary, status, circumstance, name='Test Bird'):
        """Create a test bird."""
        return Bird.objects.create(
            name=name,
            species='Test Species',
            age_group='adult',
            gender='unknown',
            weight=Decimal('100.50'),
            wing_span=Decimal('25.00'),
            found_date=timezone.now().date(),
            found_location='Test Location',
            finder_name='Test Finder',
            finder_phone='123456789',
            finder_email='finder@example.com',
            aviary=aviary,
            status=status,
            circumstance=circumstance,
            notes='Test notes',
            created_by=user
        )
    
    def create_test_contact(self, user, first_name='John', last_name='Doe'):
        """Create a test contact."""
        return Contact.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=f'{first_name.lower()}.{last_name.lower()}@example.com',
            phone='123456789',
            address='123 Test Street',
            city='Test City',
            postal_code='12345',
            country='Test Country',
            is_active=True,
            created_by=user
        )
    
    def create_test_cost(self, user, bird, amount='50.00', description='Test Cost'):
        """Create a test cost entry."""
        return Costs.objects.create(
            bird=bird,
            description=description,
            amount=Decimal(amount),
            cost_date=timezone.now().date(),
            category='medical',
            invoice_number=f'INV-{timezone.now().timestamp()}',
            vendor='Test Vendor',
            notes='Test cost notes',
            created_by=user
        )


@pytest.fixture
def test_user():
    """Fixture for creating a test user."""
    return User.objects.create_user(
        username='fixtureuser',
        email='fixture@example.com',
        password='fixturepass123'
    )


@pytest.fixture
def admin_user():
    """Fixture for creating an admin user."""
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def test_aviary(test_user):
    """Fixture for creating a test aviary."""
    return Aviary.objects.create(
        name='Fixture Aviary',
        location='Fixture Location',
        capacity=15,
        current_occupancy=3,
        created_by=test_user
    )


@pytest.fixture
def bird_status():
    """Fixture for creating a bird status."""
    return BirdStatus.objects.create(
        name='Fixture Status',
        description='Fixture bird status'
    )


@pytest.fixture
def circumstance():
    """Fixture for creating a circumstance."""
    return Circumstance.objects.create(
        name='Fixture Circumstance',
        description='Fixture circumstance'
    )


@pytest.fixture
def test_bird(test_user, test_aviary, bird_status, circumstance):
    """Fixture for creating a test bird."""
    return Bird.objects.create(
        name='Fixture Bird',
        species='Fixture Species',
        age_group='adult',
        gender='male',
        weight=Decimal('95.75'),
        aviary=test_aviary,
        status=bird_status,
        circumstance=circumstance,
        created_by=test_user
    )


class TestUtilities:
    """Utility functions for tests."""
    
    @staticmethod
    def assert_model_fields(instance, expected_values):
        """Assert that model instance has expected field values."""
        for field, expected_value in expected_values.items():
            actual_value = getattr(instance, field)
            assert actual_value == expected_value, f"Field {field}: expected {expected_value}, got {actual_value}"
    
    @staticmethod
    def assert_form_errors(form, expected_errors):
        """Assert that form has expected validation errors."""
        assert not form.is_valid(), "Form should be invalid"
        for field, error_messages in expected_errors.items():
            assert field in form.errors, f"Field {field} should have errors"
            for error_message in error_messages:
                assert any(error_message in str(error) for error in form.errors[field]), \
                    f"Error message '{error_message}' not found in {form.errors[field]}"
    
    @staticmethod
    def assert_response_contains(response, expected_content):
        """Assert that response contains expected content."""
        if isinstance(expected_content, list):
            for content in expected_content:
                assert content in response.content.decode(), f"Content '{content}' not found in response"
        else:
            assert expected_content in response.content.decode(), f"Content '{expected_content}' not found in response"
    
    @staticmethod
    def create_form_data(**kwargs):
        """Create form data with default values."""
        defaults = {
            'name': 'Test Name',
            'species': 'Test Species',
            'age_group': 'adult',
            'gender': 'unknown',
            'weight': '100.00'
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def assert_redirect(response, expected_url=None):
        """Assert that response is a redirect."""
        assert response.status_code in [301, 302], f"Expected redirect, got {response.status_code}"
        if expected_url:
            assert expected_url in response.url, f"Expected redirect to {expected_url}, got {response.url}"


def sample_bird_data():
    """Return sample bird data for testing."""
    return [
        {
            'name': 'Robin',
            'species': 'European Robin',
            'age_group': 'adult',
            'gender': 'male',
            'weight': Decimal('18.5')
        },
        {
            'name': 'Sparrow',
            'species': 'House Sparrow', 
            'age_group': 'juvenile',
            'gender': 'female',
            'weight': Decimal('22.3')
        },
        {
            'name': 'Falcon',
            'species': 'Peregrine Falcon',
            'age_group': 'adult',
            'gender': 'unknown',
            'weight': Decimal('750.0')
        }
    ]


def sample_aviary_data():
    """Return sample aviary data for testing."""
    return [
        {
            'name': 'Forest Sanctuary',
            'location': 'Black Forest',
            'capacity': 25,
            'current_occupancy': 8
        },
        {
            'name': 'Lake Resort',
            'location': 'Lake Constance',
            'capacity': 30,
            'current_occupancy': 12
        },
        {
            'name': 'Mountain Refuge',
            'location': 'Bavarian Alps',
            'capacity': 15,
            'current_occupancy': 5
        }
    ]


def create_test_database_state():
    """Create a complete test database state with relationships."""
    # Create users
    admin = User.objects.create_user(
        username='testadmin',
        email='admin@testfbf.com',
        password='adminpass123',
        is_staff=True
    )
    
    user = User.objects.create_user(
        username='testuser',
        email='user@testfbf.com',
        password='userpass123'
    )
    
    # Create aviaries
    aviaries = []
    for aviary_data in sample_aviary_data():
        aviary = Aviary.objects.create(
            **aviary_data,
            created_by=admin
        )
        aviaries.append(aviary)
    
    # Create statuses and circumstances
    statuses = [
        BirdStatus.objects.create(name='Gesund', description='Healthy bird'),
        BirdStatus.objects.create(name='Krank', description='Sick bird'),
        BirdStatus.objects.create(name='Verletzt', description='Injured bird'),
    ]
    
    circumstances = [
        Circumstance.objects.create(name='Gefunden', description='Found bird'),
        Circumstance.objects.create(name='Gebracht', description='Brought bird'),
        Circumstance.objects.create(name='Übertragen', description='Transferred bird'),
    ]
    
    # Create birds
    birds = []
    for i, bird_data in enumerate(sample_bird_data()):
        bird = Bird.objects.create(
            **bird_data,
            aviary=aviaries[i % len(aviaries)],
            status=statuses[i % len(statuses)],
            circumstance=circumstances[i % len(circumstances)],
            found_date=timezone.now().date(),
            created_by=user
        )
        birds.append(bird)
    
    # Create contacts
    contacts = []
    contact_data = [
        ('John', 'Doe', 'john.doe@example.com'),
        ('Jane', 'Smith', 'jane.smith@example.com'),
        ('Bob', 'Johnson', 'bob.johnson@example.com'),
    ]
    
    for first_name, last_name, email in contact_data:
        contact = Contact.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone='123456789',
            created_by=user
        )
        contacts.append(contact)
    
    # Create costs
    costs = []
    for i, bird in enumerate(birds):
        cost = Costs.objects.create(
            bird=bird,
            description=f'Treatment for {bird.name}',
            amount=Decimal(f'{50 + i * 10}.75'),
            cost_date=timezone.now().date(),
            category='medical',
            created_by=user
        )
        costs.append(cost)
    
    return {
        'users': [admin, user],
        'aviaries': aviaries,
        'statuses': statuses,
        'circumstances': circumstances,
        'birds': birds,
        'contacts': contacts,
        'costs': costs
    }
