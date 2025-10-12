# Testing Documentation

## Overview

This project uses **pytest** for comprehensive testing of all functionality. Tests are organized by category and use function-based testing (not classes).

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Fixtures and configuration
├── test_models.py           # Model tests
├── test_routes.py           # Route/endpoint tests
├── test_import.py           # Exam import tests
├── test_admin.py            # Admin interface tests
└── test_integration.py      # Integration/workflow tests
```

## Installation

Install test dependencies:

```bash
pip install -r requirements-dev.txt
```

Or install everything:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Running Tests

### Run All Tests

```bash
pytest
# or
./run_tests.sh
```

### Run Specific Test Categories

```bash
# Model tests
pytest tests/test_models.py
./run_tests.sh models

# Route tests
pytest tests/test_routes.py
./run_tests.sh routes

# Import tests
pytest tests/test_import.py
pytest -m exam_import
./run_tests.sh import

# Admin tests
pytest tests/test_admin.py
./run_tests.sh admin

# Integration tests
pytest tests/test_integration.py
./run_tests.sh integration
```

### Run Tests by Marker

```bash
# All model tests
pytest -m models

# All route tests
pytest -m routes

# All admin tests
pytest -m admin

# All import tests
pytest -m exam_import

# Skip integration tests (faster)
pytest -m "not integration"
./run_tests.sh fast
```

### Run Specific Tests

```bash
# Run a specific test function
pytest tests/test_models.py::test_user_creation

# Run tests matching a pattern
pytest -k "user"
pytest -k "import"
```

## Code Coverage

Generate coverage report:

```bash
pytest --cov=. --cov-report=html --cov-report=term
# or
./run_tests.sh coverage
```

View HTML coverage report:

```bash
open htmlcov/index.html
```

## Test Categories

### 1. Model Tests (`test_models.py`)

Tests for all database models:
- User creation and authentication
- Question creation with optional fields
- Section and question relationships
- Exam creation and section linking
- Test instance creation
- Test answer recording
- Cascade deletes
- Model relationships

**Run:** `pytest tests/test_models.py -v`

### 2. Route Tests (`test_routes.py`)

Tests for all application routes:
- Authentication (register, login, logout)
- Exam listing
- Starting exams
- Taking exams
- Submitting answers
- Viewing results
- Download example JSON
- Authorization checks

**Run:** `pytest tests/test_routes.py -v`

### 3. Import Tests (`test_import.py`)

Tests for exam import functionality:
- Successful import from JSON
- Section creation
- Question creation
- Validation errors
- Missing required fields
- Invalid data handling
- Rollback on errors
- Optional fields support

**Run:** `pytest tests/test_import.py -v`

### 4. Admin Tests (`test_admin.py`)

Tests for admin interface:
- Authentication requirements
- Accessing admin panels
- Viewing model lists
- Import exam interface
- File upload validation
- Creating/editing restrictions
- Admin-only operations

**Run:** `pytest tests/test_admin.py -v`

### 5. Integration Tests (`test_integration.py`)

End-to-end workflow tests:
- Complete user workflow
- Admin import and user take exam
- Multiple users same exam
- Resume incomplete exam
- Exam scoring accuracy
- Multi-section exams

**Run:** `pytest tests/test_integration.py -v`

## Fixtures

Common fixtures available in `conftest.py`:

- `app` - Test Flask application
- `client` - Test client for making requests
- `auth_client` - Authenticated test client
- `test_user` - Test user account
- `test_admin` - Test admin account
- `test_question` - Sample question
- `test_section` - Sample section with question
- `test_exam` - Sample exam with section
- `sample_exam_json` - Sample JSON for import testing

## Writing New Tests

### Test Function Template

```python
import pytest

@pytest.mark.category_name
def test_feature_name(client, app, fixture_name):
    """Test description"""
    # Arrange
    # ... setup code ...
    
    # Act
    response = client.get('/endpoint')
    
    # Assert
    assert response.status_code == 200
    assert b'expected content' in response.data
```

### Best Practices

1. **Use descriptive names**: `test_user_cannot_access_other_user_test`
2. **Add markers**: `@pytest.mark.routes`, `@pytest.mark.models`, etc.
3. **Use docstrings**: Explain what the test verifies
4. **Follow AAA pattern**: Arrange, Act, Assert
5. **Use fixtures**: Don't repeat setup code
6. **Test edge cases**: Invalid inputs, missing data, etc.
7. **Keep tests isolated**: Each test should be independent

### Example Test

```python
@pytest.mark.routes
def test_submit_answer(auth_client, app, test_user, test_exam, test_question):
    """Test submitting an answer to a question"""
    # Arrange: Create test
    with app.app_context():
        test = Test(exam_id=test_exam, user_id=test_user['id'])
        db.session.add(test)
        db.session.commit()
        test_id = test.id
    
    # Act: Submit answer
    response = auth_client.post(f'/test/{test_id}/answer', data={
        'question_id': test_question,
        'selected_answer': 2
    })
    
    # Assert: Check success
    assert response.status_code == 200
    assert b'success' in response.data
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Troubleshooting

### Tests Fail with Database Errors

Tests use a temporary SQLite database. Make sure no other instances are accessing the test database.

### Import Errors

Make sure you're in the project root and the virtual environment is activated:

```bash
cd /Users/kalildelima/workspace/nihongo
pyenv activate nihongo
pytest
```

### Fixtures Not Found

Ensure `conftest.py` is in the `tests/` directory and properly configured.

### Authentication Tests Fail

Check that `WTF_CSRF_ENABLED` is set to `False` in test configuration.

## Test Coverage Goals

- **Models**: 100% coverage
- **Routes**: 95%+ coverage
- **Import**: 100% coverage
- **Admin**: 90%+ coverage
- **Overall**: 90%+ coverage

## Quick Reference

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific category
pytest -m models

# Run specific file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::test_user_creation

# Run tests matching pattern
pytest -k "user"

# Show coverage
pytest --cov=.

# Generate HTML coverage report
pytest --cov=. --cov-report=html

# Fast tests (skip integration)
pytest -m "not integration"

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Show print statements
pytest -s
```

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest fixtures](https://docs.pytest.org/en/latest/fixture.html)
- [pytest markers](https://docs.pytest.org/en/latest/mark.html)
- [pytest-flask](https://pytest-flask.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)

