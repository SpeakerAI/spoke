"""
Pytest configuration and shared fixtures for Spoke TTS tests.
"""

import sys
import os
import pytest

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from server.server import app


@pytest.fixture
def client():
    """Flask test client fixture."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing."""
    return "test_user_123"


@pytest.fixture
def valid_emotions():
    """List of valid emotions."""
    return [
        "anger", "sadness", "joy", "fear", "neutral",
        "amusement", "contentment", "adoration", "amazement",
        "confusion", "cuteness", "desire", "disappointment",
        "disgust", "distress", "embarassment", "extasy",
        "guilt", "interest", "pain", "pride"
    ]


@pytest.fixture
def invalid_emotions():
    """List of invalid emotions for testing."""
    return ["happy", "mad", "excited", "invalid", "", None]


@pytest.fixture
def valid_speaker_ids():
    """List of valid speaker IDs."""
    return [1, 2, 3, 4, 50, 107]


@pytest.fixture
def invalid_speaker_ids():
    """List of invalid speaker IDs."""
    return [0, -1, 108, 200, "abc"]


@pytest.fixture
def sample_synthesis_payload():
    """Sample payload for synthesis endpoint."""
    return {
        "text": "Hello, this is a test message.",
        "emotion": "neutral",
        "speaker_id": 1
    }


@pytest.fixture
def sample_synthesis_payload_with_user():
    """Sample payload for synthesis with user verification."""
    return {
        "text": "Hello, this is a test message.",
        "emotion": "neutral",
        "speaker_id": 1,
        "user_id": "test_user_123"
    }
