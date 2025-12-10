"""Testing Guide."""

# Testing Documentation

## Test Structure

Tests are organized by component:

- `test_webhooks.py`: WhatsApp webhook tests
- `test_agents.py`: AI agent tests
- `test_business_logic.py`: Business logic tests
- `test_integration.py`: End-to-end integration tests

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_agents.py::TestReceptionistAgent::test_greeting_message
```

## Test Fixtures

Fixtures are defined in `conftest.py`:

- `mock_db`: Mock database session
- `mock_redis`: Mock Redis client
- `test_lead_data`: Sample lead data
- `test_property_data`: Sample property data

## Writing Tests

Tests should follow the Arrange-Act-Assert pattern:

```python
def test_example(test_lead_data):
    # Arrange
    lead = test_lead_data
    
    # Act
    result = process_lead(lead)
    
    # Assert
    assert result.is_qualified == True
```

## Coverage Goals

- Minimum 80% code coverage
- 100% coverage for business logic
- Unit tests for all utility functions
- Integration tests for workflows
