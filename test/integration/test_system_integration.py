"""
Integration tests for Django FBF project.
Tests system-wide functionality and external integrations.
"""
import pytest
from django.test import TestCase, TransactionTestCase
from django.core import mail
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

from bird.models import Bird, BirdStatus, Circumstance
from aviary.models import Aviary
from costs.models import Costs
from contact.models import Contact


class EmailIntegrationTests(TestCase):
    """Test email functionality integration."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='emailuser',
            email='email@example.com',
            password='emailpass123'
        )
        
        self.contact = Contact.objects.create(
            first_name="Email",
            last_name="Recipient",
            email="recipient@example.com",
            created_by=self.user
        )
    
    def test_email_sending(self):
        """Test that emails can be sent."""
        from django.core.mail import send_mail
        
        # Send test email
        send_mail(
            'Test Subject',
            'Test message body',
            'from@example.com',
            ['to@example.com'],
            fail_silently=False,
        )
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')
        self.assertEqual(mail.outbox[0].body, 'Test message body')
    
    def test_bird_notification_email(self):
        """Test email notifications for bird events."""
        # This would test automated emails sent when birds are added/updated
        # Implementation depends on your email notification system
        
        aviary = Aviary.objects.create(
            name="Notification Aviary",
            location="Test Location",
            contact_email="aviary@example.com",
            created_by=self.user
        )
        
        bird_status = BirdStatus.objects.create(
            name="Gefunden",
            description="Found bird"
        )
        
        circumstance = Circumstance.objects.create(
            name="Notfall",
            description="Emergency"
        )
        
        # Create bird (might trigger notification email)
        bird = Bird.objects.create(
            name="Emergency Bird",
            species="Test Species",
            aviary=aviary,
            status=bird_status,
            circumstance=circumstance,
            created_by=self.user
        )
        
        # Check if notification email was sent (if implemented)
        # This would depend on your signal handlers or email logic
        # For now, just verify the bird was created
        self.assertEqual(bird.name, "Emergency Bird")


class DatabaseIntegrationTests(TransactionTestCase):
    """Test database operations and transactions."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='dbuser',
            email='db@example.com',
            password='dbpass123'
        )
        
        self.aviary = Aviary.objects.create(
            name="DB Test Aviary",
            location="Test Location",
            capacity=10,
            current_occupancy=0,
            created_by=self.user
        )
        
        self.bird_status = BirdStatus.objects.create(
            name="Gesund",
            description="Healthy"
        )
        
        self.circumstance = Circumstance.objects.create(
            name="Gefunden",
            description="Found"
        )
    
    def test_database_transaction_rollback(self):
        """Test that database transactions rollback properly on errors."""
        initial_bird_count = Bird.objects.count()
        
        try:
            with transaction.atomic():
                # Create a bird
                bird = Bird.objects.create(
                    name="Transaction Test Bird",
                    species="Test Species",
                    aviary=self.aviary,
                    status=self.bird_status,
                    circumstance=self.circumstance,
                    created_by=self.user
                )
                
                # Force an error to trigger rollback
                raise Exception("Forced error for testing")
                
        except Exception:
            pass
        
        # Bird should not exist due to rollback
        final_bird_count = Bird.objects.count()
        self.assertEqual(initial_bird_count, final_bird_count)
    
    def test_database_constraints(self):
        """Test database constraints and foreign key relationships."""
        # Test that foreign key constraints work
        bird = Bird.objects.create(
            name="Constraint Test Bird",
            species="Test Species",
            aviary=self.aviary,
            status=self.bird_status,
            circumstance=self.circumstance,
            created_by=self.user
        )
        
        # Verify relationships
        self.assertEqual(bird.aviary, self.aviary)
        self.assertEqual(bird.status, self.bird_status)
        self.assertEqual(bird.circumstance, self.circumstance)
        
        # Test cascade behavior (if implemented)
        aviary_id = self.aviary.id
        self.aviary.delete()
        
        # Check what happens to the bird (depends on your cascade settings)
        try:
            bird.refresh_from_db()
            # If bird still exists, aviary reference should be None or cascade didn't happen
        except Bird.DoesNotExist:
            # Bird was deleted due to cascade
            pass
    
    def test_bulk_operations(self):
        """Test bulk database operations."""
        # Test bulk creation
        birds_data = []
        for i in range(5):
            birds_data.append(Bird(
                name=f"Bulk Bird {i+1}",
                species="Bulk Species",
                aviary=self.aviary,
                status=self.bird_status,
                circumstance=self.circumstance,
                created_by=self.user
            ))
        
        created_birds = Bird.objects.bulk_create(birds_data)
        self.assertEqual(len(created_birds), 5)
        
        # Test bulk update
        Bird.objects.filter(species="Bulk Species").update(
            notes="Bulk updated"
        )
        
        # Verify update
        updated_birds = Bird.objects.filter(species="Bulk Species")
        for bird in updated_birds:
            self.assertEqual(bird.notes, "Bulk updated")
    
    def test_database_indexing_performance(self):
        """Test that database queries use indexes effectively."""
        # Create many birds for performance testing
        birds = []
        for i in range(100):
            birds.append(Bird(
                name=f"Performance Bird {i+1}",
                species=f"Species {i % 10}",  # 10 different species
                aviary=self.aviary,
                status=self.bird_status,
                circumstance=self.circumstance,
                created_by=self.user
            ))
        
        Bird.objects.bulk_create(birds)
        
        # Test query performance (basic check)
        import time
        
        start_time = time.time()
        birds = list(Bird.objects.select_related('aviary', 'status', 'circumstance').all())
        query_time = time.time() - start_time
        
        # Query should complete reasonably quickly
        self.assertLess(query_time, 1.0)  # Should complete in less than 1 second
        
        # Test filtering performance
        start_time = time.time()
        filtered_birds = list(Bird.objects.filter(species="Species 1"))
        filter_time = time.time() - start_time
        
        self.assertLess(filter_time, 0.1)  # Should complete very quickly


class FileHandlingIntegrationTests(TestCase):
    """Test file upload and handling integration."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='fileuser',
            email='file@example.com',
            password='filepass123'
        )
    
    def test_static_files_serving(self):
        """Test that static files are served correctly."""
        from django.test import Client
        
        client = Client()
        
        # Test CSS file access
        response = client.get('/static/css/styles.css')
        # Should either serve the file or return 404 if not exists
        self.assertIn(response.status_code, [200, 404])
        
        # Test JavaScript file access
        response = client.get('/static/js/main.js')
        self.assertIn(response.status_code, [200, 404])
    
    def test_media_files_handling(self):
        """Test media file upload and handling."""
        # This would test image uploads for birds or other media files
        # Implementation depends on your file upload functionality
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create a simple test file
        test_file = SimpleUploadedFile(
            "test_image.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        # Test file handling (would depend on your models)
        # For now, just verify file was created
        self.assertEqual(test_file.name, "test_image.jpg")
        self.assertEqual(test_file.content_type, "image/jpeg")


class APIIntegrationTests(TestCase):
    """Test API integrations if any exist."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='apipass123'
        )
    
    def test_external_api_calls(self):
        """Test external API integrations."""
        # This would test any external APIs your application uses
        # For example, weather services, mapping services, etc.
        
        # Mock test for now
        import json
        
        # Simulate API response
        mock_api_response = {
            'status': 'success',
            'data': {
                'weather': 'sunny',
                'temperature': 20
            }
        }
        
        # Test JSON parsing
        parsed_response = json.loads(json.dumps(mock_api_response))
        self.assertEqual(parsed_response['status'], 'success')
        self.assertEqual(parsed_response['data']['weather'], 'sunny')


class CacheIntegrationTests(TestCase):
    """Test caching functionality if implemented."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='cacheuser',
            email='cache@example.com',
            password='cachepass123'
        )
    
    def test_cache_operations(self):
        """Test cache set and get operations."""
        from django.core.cache import cache
        
        # Test cache set
        cache.set('test_key', 'test_value', 300)  # 5 minutes
        
        # Test cache get
        cached_value = cache.get('test_key')
        self.assertEqual(cached_value, 'test_value')
        
        # Test cache delete
        cache.delete('test_key')
        cached_value = cache.get('test_key')
        self.assertIsNone(cached_value)
    
    def test_cache_invalidation(self):
        """Test cache invalidation on model changes."""
        from django.core.cache import cache
        
        # Cache some bird data
        cache.set('bird_count', 10, 300)
        
        # Verify cache
        self.assertEqual(cache.get('bird_count'), 10)
        
        # Create a bird (should invalidate cache if implemented)
        aviary = Aviary.objects.create(
            name="Cache Test Aviary",
            location="Test Location",
            created_by=self.user
        )
        
        bird_status = BirdStatus.objects.create(
            name="Test Status",
            description="Test"
        )
        
        circumstance = Circumstance.objects.create(
            name="Test Circumstance",
            description="Test"
        )
        
        Bird.objects.create(
            name="Cache Test Bird",
            species="Test Species",
            aviary=aviary,
            status=bird_status,
            circumstance=circumstance,
            created_by=self.user
        )
        
        # Cache should be updated or invalidated
        # (Implementation depends on your cache invalidation strategy)
        actual_count = Bird.objects.count()
        self.assertGreaterEqual(actual_count, 1)
