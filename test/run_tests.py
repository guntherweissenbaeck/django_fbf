#!/usr/bin/env python3
"""
Test runner script for Django FBF project.
Runs all tests with proper configuration.
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    # Set up Django environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_settings")
    
    # Add the app directory to Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))
    
    # Setup Django
    django.setup()
    
    # Get the Django test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run tests
    failures = test_runner.run_tests(["test"])
    
    if failures:
        sys.exit(1)
    else:
        print("All tests passed!")
        sys.exit(0)
