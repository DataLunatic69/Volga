"""Test configuration and fixtures."""
import pytest
from typing import Generator


@pytest.fixture
def mock_db():
    """Mock database session for tests."""
    # TODO: Implement mock database session
    pass


@pytest.fixture
def mock_redis():
    """Mock Redis client for tests."""
    # TODO: Implement mock Redis client
    pass


@pytest.fixture
def test_lead_data():
    """Sample lead data for tests."""
    return {
        "phone_number": "+1234567890",
        "name": "Test User",
        "email": "test@example.com",
        "location": "New York",
        "budget_min": 200000,
        "budget_max": 500000
    }


@pytest.fixture
def test_property_data():
    """Sample property data for tests."""
    return {
        "id": "prop_001",
        "title": "Modern Apartment",
        "description": "Beautiful modern apartment in downtown",
        "price": 350000,
        "bedrooms": 2,
        "bathrooms": 2,
        "location": "New York"
    }
