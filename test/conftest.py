"""
Test configuration for Django FBF project.
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# Add the test directory to the Python path for test_settings
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings for tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')

# Setup Django
django.setup()
