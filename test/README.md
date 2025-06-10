# Django FBF Test Suite

Comprehensive test suite for the Django FBF (Falken-, Bussard- und Fischadler) project.

## Test Structure

```
test/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration
├── test_settings.py            # Django test settings
├── run_tests.py               # Custom test runner script
├── fixtures.py                # Test fixtures and utilities
├── requirements.txt           # Test-specific dependencies
├── README.md                  # This file
├── unit/                      # Unit tests
│   ├── __init__.py
│   ├── test_bird_models.py    # Bird model tests
│   ├── test_bird_forms.py     # Bird form tests
│   ├── test_bird_views.py     # Bird view tests
│   ├── test_aviary_models.py  # Aviary model tests
│   ├── test_aviary_forms.py   # Aviary form tests
│   ├── test_contact_models.py # Contact model tests
│   └── test_costs_models.py   # Costs model tests
├── functional/                # Functional tests
│   ├── __init__.py
│   └── test_workflows.py      # User workflow tests
└── integration/               # Integration tests
    ├── __init__.py
    └── test_system_integration.py  # System integration tests
```

## Test Categories

### Unit Tests
Tests individual components in isolation:
- **Model Tests**: Test Django models, validation, relationships
- **Form Tests**: Test Django forms, validation, field behavior
- **View Tests**: Test Django views, permissions, responses

### Functional Tests
Tests complete user workflows and feature interactions:
- **Bird Management Workflows**: Creating, editing, transferring birds
- **Aviary Management**: Capacity management, bird assignments
- **Search and Filtering**: Testing search functionality
- **User Permissions**: Access control and authentication flows

### Integration Tests
Tests system-wide functionality and external integrations:
- **Database Integration**: Transaction handling, constraints, performance
- **Email Integration**: Email sending and notification systems
- **File Handling**: Static files, media uploads
- **API Integration**: External API calls (if any)
- **Cache Integration**: Caching functionality (if implemented)

## Running Tests

### Method 1: Using the Custom Test Runner

```bash
# Run all tests
cd /Users/maximilianfischer/git/django_fbf
python3 test/run_tests.py
```

### Method 2: Using Django's manage.py

```bash
# Run all tests
cd /Users/maximilianfischer/git/django_fbf/app
python3 manage.py test test --settings=test.test_settings

# Run specific test categories
python3 manage.py test test.unit --settings=test.test_settings
python3 manage.py test test.functional --settings=test.test_settings
python3 manage.py test test.integration --settings=test.test_settings

# Run specific test files
python3 manage.py test test.unit.test_bird_models --settings=test.test_settings
```

### Method 3: Using pytest (if installed)

```bash
# Install test requirements first
pip install -r test/requirements.txt

# Run all tests
cd /Users/maximilianfischer/git/django_fbf/test
pytest -v

# Run with coverage
pytest --cov=../app --cov-report=html

# Run specific test categories
pytest unit/ -v
pytest functional/ -v
pytest integration/ -v

# Run specific test files
pytest unit/test_bird_models.py -v
```

### Method 4: Using the Rebuild Script

The rebuild script automatically runs all tests as part of the rebuild process:

```bash
cd /Users/maximilianfischer/git/django_fbf
./rebuild_project.sh
```

## Test Configuration

### Test Settings (`test_settings.py`)
- Uses SQLite in-memory database for speed
- Disables migrations for faster test setup
- Uses simple password hasher for performance
- Configures email backend for testing
- Sets up test-specific logging

### Test Fixtures (`fixtures.py`)
- `TestDataMixin`: Provides common test data creation methods
- Pytest fixtures for common objects
- Sample data generators
- Test utilities for assertions and validations

### Environment Setup
- Tests use separate settings from development/production
- Isolated test database (in-memory SQLite)
- Mock external dependencies
- Clean state for each test

## Test Data

### Sample Data Available
- **Birds**: Robin, Sparrow, Falcon with different attributes
- **Aviaries**: Forest Sanctuary, Lake Resort, Mountain Refuge
- **Statuses**: Gesund (Healthy), Krank (Sick), Verletzt (Injured)
- **Circumstances**: Gefunden (Found), Gebracht (Brought), Übertragen (Transferred)
- **Users**: Admin and regular users with different permissions

### Creating Test Data
Use the `TestDataMixin` class or pytest fixtures:

```python
from test.fixtures import TestDataMixin

class MyTest(TestCase, TestDataMixin):
    def setUp(self):
        self.user = self.create_test_user()
        self.aviary = self.create_test_aviary(self.user)
        self.bird = self.create_test_bird(self.user, self.aviary, ...)
```

## Coverage Goals

### Current Test Coverage
- **Models**: All model fields, methods, and relationships
- **Forms**: Form validation, field types, error handling
- **Views**: Authentication, permissions, CRUD operations
- **Workflows**: Complete user journeys
- **Integration**: Database, email, file handling

### Coverage Targets
- Unit Tests: >90% code coverage
- Functional Tests: All major user workflows
- Integration Tests: All external dependencies

## Common Test Patterns

### Model Testing
```python
def test_bird_creation(self):
    bird = Bird.objects.create(**valid_data)
    self.assertEqual(bird.name, "Test Bird")
    self.assertTrue(isinstance(bird, Bird))
```

### Form Testing
```python
def test_form_valid_data(self):
    form = BirdAddForm(data=valid_form_data)
    self.assertTrue(form.is_valid())

def test_form_invalid_data(self):
    form = BirdAddForm(data=invalid_form_data)
    self.assertFalse(form.is_valid())
    self.assertIn('field_name', form.errors)
```

### View Testing
```python
def test_view_requires_login(self):
    response = self.client.get(url)
    self.assertEqual(response.status_code, 302)

def test_view_authenticated(self):
    self.client.login(username='user', password='pass')
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure Django settings are configured: `DJANGO_SETTINGS_MODULE=test.test_settings`
   - Check Python path includes the app directory

2. **Database Errors**
   - Tests use in-memory SQLite, migrations are disabled
   - Each test gets a fresh database state

3. **Missing Dependencies**
   - Install test requirements: `pip install -r test/requirements.txt`
   - Ensure Django and all app dependencies are installed

4. **URL Reversing Errors**
   - Some tests use try/except blocks for URL reversing
   - Update URL names in tests to match your actual URLs

### Debug Mode

Run tests with verbose output:
```bash
python3 manage.py test test --verbosity=2
pytest -v -s  # -s shows print statements
```

### Test Database

The test database is automatically created and destroyed. To inspect:
```bash
# Run with keepdb to preserve test database
python3 manage.py test test --keepdb
```

## Contributing Tests

### Adding New Tests

1. **Unit Tests**: Add to appropriate file in `unit/`
2. **Functional Tests**: Add to `functional/test_workflows.py`
3. **Integration Tests**: Add to `integration/test_system_integration.py`

### Test Guidelines

- Use descriptive test method names: `test_bird_creation_with_valid_data`
- Include both positive and negative test cases
- Test edge cases and error conditions
- Use fixtures and test utilities for common setup
- Keep tests independent and isolated
- Add docstrings for complex tests

### Running Before Commits

Always run tests before committing:
```bash
# Quick unit tests
python3 manage.py test test.unit

# Full test suite
./rebuild_project.sh
```

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:
- Fast execution with in-memory database
- Clear pass/fail status
- Comprehensive coverage reporting
- Integration with the rebuild script

For CI/CD integration, use:
```bash
cd /Users/maximilianfischer/git/django_fbf
python3 test/run_tests.py
```

This will exit with code 0 for success, 1 for failure.
