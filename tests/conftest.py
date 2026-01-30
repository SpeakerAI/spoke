"""
Pytest configuration and shared fixtures for Spoke TTS tests.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch
import json

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Create mock speaker_statistics.json data for voice_matcher
# Must include all fields used by voice_matcher.py
MOCK_SPEAKER_DATA = {
    "p001": {"gender": "male", "age": "26-35", "ethnicity": "white or caucasian", "native language": "american english"},
    "p002": {"gender": "female", "age": "26-35", "ethnicity": "white or caucasian", "native language": "american english"},
    "p003": {"gender": "male", "age": "36-45", "ethnicity": "black or african american", "native language": "american english"},
    "p004": {"gender": "female", "age": "18-25", "ethnicity": "asian", "native language": "american english"},
    "p005": {"gender": "male", "age": "26-35", "ethnicity": "hispanic or latino", "native language": "american english"},
    "p032": {"gender": "male", "age": "36-45", "ethnicity": "white or caucasian", "native language": "british english"},
    "p050": {"gender": "female", "age": "46-55", "ethnicity": "white or caucasian", "native language": "american english"},
    "p107": {"gender": "male", "age": "56-65", "ethnicity": "black or african american", "native language": "american english"},
}

# Mock all heavy dependencies before any server imports
# StyleTTS2 and related
sys.modules['styletts2'] = MagicMock()
sys.modules['styletts2.tts'] = MagicMock()

# PyTorch
mock_torch = MagicMock()
mock_torch.load = MagicMock(return_value={})
mock_torch.optim = MagicMock()
mock_torch.optim.lr_scheduler = MagicMock()
sys.modules['torch'] = mock_torch
sys.modules['torch.optim'] = mock_torch.optim
sys.modules['torch.optim.lr_scheduler'] = mock_torch.optim.lr_scheduler

# NLTK
mock_nltk = MagicMock()
mock_nltk.download = MagicMock(return_value=True)
sys.modules['nltk'] = mock_nltk

# Scipy
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.io'] = MagicMock()
sys.modules['scipy.io.wavfile'] = MagicMock()

# Mock supabase
mock_supabase = MagicMock()
mock_supabase.create_client = MagicMock(return_value=MagicMock())
sys.modules['supabase'] = mock_supabase

# Mock the file open for speaker_statistics.json
_original_open = open

def mock_open_wrapper(file, *args, **kwargs):
    if 'speaker_statistics.json' in str(file):
        from io import StringIO
        return StringIO(json.dumps(MOCK_SPEAKER_DATA))
    return _original_open(file, *args, **kwargs)

# Apply the mock before importing server modules
import builtins
builtins._original_open = builtins.open
builtins.open = mock_open_wrapper

# Now we can safely import the server app
from server.server import app

# Restore original open after import
builtins.open = builtins._original_open


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
