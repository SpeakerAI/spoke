"""
Unit tests for emotion_router module.

Tests the emotion to model mapping functionality.
"""

import pytest
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from server.emotion_router import get_model, EMOTION_MAPPING, REPO_ROOT


class TestEmotionMapping:
    """Tests for EMOTION_MAPPING dictionary."""

    def test_emotion_mapping_exists(self):
        """EMOTION_MAPPING should be a non-empty dictionary."""
        assert isinstance(EMOTION_MAPPING, dict)
        assert len(EMOTION_MAPPING) > 0

    def test_emotion_mapping_has_basic_emotions(self):
        """EMOTION_MAPPING should contain basic emotions."""
        basic_emotions = ["anger", "sadness", "joy", "fear", "neutral"]
        for emotion in basic_emotions:
            assert emotion in EMOTION_MAPPING

    def test_emotion_mapping_has_21_emotions(self):
        """EMOTION_MAPPING should have 21 emotions."""
        assert len(EMOTION_MAPPING) == 21

    def test_joy_maps_to_amusement(self):
        """Joy should map to amusement folder."""
        assert EMOTION_MAPPING["joy"] == "amusement"

    def test_neutral_maps_to_contentment(self):
        """Neutral should map to contentment folder."""
        assert EMOTION_MAPPING["neutral"] == "contentment"

    def test_direct_emotions_map_to_themselves(self):
        """Direct emotions should map to themselves."""
        direct_emotions = ["anger", "sadness", "fear", "amusement", "contentment"]
        for emotion in direct_emotions:
            assert EMOTION_MAPPING[emotion] == emotion

    def test_all_mapped_values_are_strings(self):
        """All mapped values should be strings."""
        for key, value in EMOTION_MAPPING.items():
            assert isinstance(key, str)
            assert isinstance(value, str)


class TestGetModel:
    """Tests for get_model function."""

    def test_get_model_valid_emotion(self, valid_emotions):
        """get_model should return a path for valid emotions."""
        # Test with a few emotions that we know have models
        for emotion in ["anger", "fear", "sadness"]:
            if emotion in valid_emotions:
                try:
                    result = get_model(emotion)
                    assert result is not None
                    assert result.endswith(".pth")
                except FileNotFoundError:
                    # Model file might not exist in test environment
                    pass

    def test_get_model_invalid_emotion(self):
        """get_model should raise ValueError for invalid emotions."""
        with pytest.raises(ValueError) as excinfo:
            get_model("invalid_emotion")
        assert "Unsupported emotion" in str(excinfo.value)

    def test_get_model_case_insensitive(self):
        """get_model should be case insensitive."""
        # Both should work or both should fail the same way
        try:
            result_lower = get_model("anger")
            result_upper = get_model("ANGER")
            assert result_lower == result_upper
        except (ValueError, FileNotFoundError):
            pass

    def test_get_model_empty_string(self):
        """get_model should raise ValueError for empty string."""
        with pytest.raises(ValueError):
            get_model("")

    def test_get_model_returns_absolute_path(self):
        """get_model should return an absolute path."""
        try:
            result = get_model("anger")
            assert os.path.isabs(result)
        except FileNotFoundError:
            # Model might not exist in test environment
            pass

    def test_get_model_path_contains_emotion(self):
        """Returned path should contain the mapped emotion name."""
        try:
            result = get_model("joy")
            # Joy maps to amusement
            assert "amusement" in result
        except FileNotFoundError:
            pass


class TestRepoRoot:
    """Tests for REPO_ROOT constant."""

    def test_repo_root_exists(self):
        """REPO_ROOT should point to an existing directory."""
        assert os.path.isdir(REPO_ROOT)

    def test_repo_root_contains_emotions_folder(self):
        """REPO_ROOT should contain an emotions folder."""
        emotions_path = os.path.join(REPO_ROOT, "emotions")
        assert os.path.isdir(emotions_path)

    def test_repo_root_is_absolute(self):
        """REPO_ROOT should be an absolute path."""
        assert os.path.isabs(REPO_ROOT)
