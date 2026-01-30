"""
Unit tests for voice_matcher module.

Tests the voice matching algorithm based on user prompts.
"""

import pytest
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from server.voice_matcher import (
    match_voices,
    match_voices_simple,
    get_voice_description,
    extract_keywords,
    score_speaker,
    SPEAKERS,
    AGE_KEYWORDS,
    GENDER_KEYWORDS
)


class TestSpeakersData:
    """Tests for SPEAKERS data loading."""

    def test_speakers_loaded(self):
        """SPEAKERS should be loaded and non-empty."""
        assert isinstance(SPEAKERS, dict)
        assert len(SPEAKERS) > 0

    @pytest.mark.skipif(
        os.getenv('CI') == 'true' or len(SPEAKERS) < 100,
        reason="Skipped in CI - uses mock data with fewer speakers"
    )
    def test_speakers_has_107_entries(self):
        """SPEAKERS should have 107 entries (production only)."""
        assert len(SPEAKERS) == 107

    def test_speaker_format(self):
        """Each speaker should have required fields."""
        required_fields = ["age", "gender", "ethnicity", "native language"]
        for speaker_id, data in SPEAKERS.items():
            assert speaker_id.startswith("p")
            for field in required_fields:
                assert field in data, f"Missing '{field}' in speaker {speaker_id}"


class TestExtractKeywords:
    """Tests for extract_keywords function."""

    def test_extract_male_gender(self):
        """Should extract male gender from prompt."""
        result = extract_keywords("I need a male voice")
        assert "male" in result["gender"]

    def test_extract_female_gender(self):
        """Should extract female gender from prompt."""
        result = extract_keywords("Looking for a female speaker")
        assert "female" in result["gender"]

    def test_extract_young_age(self):
        """Should extract young age keywords."""
        result = extract_keywords("young energetic voice")
        assert len(result["age"]) > 0
        assert "18-25" in result["age"] or "26-35" in result["age"]

    def test_extract_mature_age(self):
        """Should extract mature age keywords."""
        result = extract_keywords("mature authoritative voice")
        assert len(result["age"]) > 0

    def test_extract_multiple_keywords(self):
        """Should extract multiple keywords from complex prompt."""
        result = extract_keywords("young female American voice")
        assert len(result["gender"]) > 0
        assert len(result["age"]) > 0

    def test_case_insensitive(self):
        """Extraction should be case insensitive."""
        result_lower = extract_keywords("male voice")
        result_upper = extract_keywords("MALE VOICE")
        assert result_lower["gender"] == result_upper["gender"]

    def test_empty_prompt(self):
        """Should return empty lists for empty prompt."""
        result = extract_keywords("")
        assert result["age"] == []
        assert result["gender"] == []

    def test_no_keywords_prompt(self):
        """Should return empty lists for prompt with no keywords."""
        result = extract_keywords("hello world test")
        assert len(result["age"]) == 0
        assert len(result["gender"]) == 0


class TestMatchVoices:
    """Tests for match_voices function."""

    def test_returns_list(self):
        """match_voices should return a list."""
        result = match_voices("male voice")
        assert isinstance(result, list)

    def test_returns_correct_count(self):
        """match_voices should return requested number of results."""
        result = match_voices("female voice", top_n=4)
        # In CI with mock data, we may have fewer speakers
        assert len(result) <= 4
        assert len(result) > 0

    def test_results_have_required_fields(self):
        """Each result should have speaker_id, score, and profile."""
        result = match_voices("male voice", top_n=1)
        assert len(result) > 0
        assert "speaker_id" in result[0]
        assert "score" in result[0]
        assert "profile" in result[0]

    def test_results_sorted_by_score(self):
        """Results should be sorted by score descending."""
        result = match_voices("young female voice", top_n=10)
        scores = [r["score"] for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_male_prompt_returns_males(self):
        """Male prompt should prioritize male speakers."""
        result = match_voices("deep male voice", top_n=4)
        male_count = sum(1 for r in result if r["profile"]["gender"] == "male")
        # At least half should be male
        assert male_count >= 2

    def test_female_prompt_returns_females(self):
        """Female prompt should prioritize female speakers."""
        result = match_voices("soft female voice", top_n=4)
        female_count = sum(1 for r in result if r["profile"]["gender"] == "female")
        # At least half should be female
        assert female_count >= 2


class TestMatchVoicesSimple:
    """Tests for match_voices_simple function."""

    def test_returns_list_of_strings(self):
        """match_voices_simple should return list of speaker IDs."""
        result = match_voices_simple("male voice")
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)

    def test_returns_4_results(self):
        """match_voices_simple should return up to 4 results by default."""
        result = match_voices_simple("female voice")
        # In CI with mock data, we may have fewer speakers
        assert len(result) <= 4
        assert len(result) > 0

    def test_speaker_id_format(self):
        """Speaker IDs should be in pXXX format."""
        result = match_voices_simple("young voice")
        for speaker_id in result:
            assert speaker_id.startswith("p")
            assert len(speaker_id) == 4


class TestGetVoiceDescription:
    """Tests for get_voice_description function."""

    def test_valid_speaker(self):
        """Should return description for valid speaker."""
        result = get_voice_description("p001")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_invalid_speaker(self):
        """Should return 'Unknown speaker' for invalid speaker."""
        result = get_voice_description("p999")
        assert "Unknown" in result

    def test_description_contains_gender(self):
        """Description should contain gender information."""
        result = get_voice_description("p001")
        assert "Male" in result or "Female" in result or "private" in result.lower()

    def test_description_contains_age(self):
        """Description should contain age information."""
        result = get_voice_description("p002")
        assert "years" in result.lower() or "private" in result.lower()


class TestScoreSpeaker:
    """Tests for score_speaker function."""

    def test_returns_float(self):
        """score_speaker should return a float."""
        keywords = {"age": [], "gender": ["male"], "ethnicity": [], "language": [], "quality": []}
        result = score_speaker("p001", SPEAKERS["p001"], keywords)
        assert isinstance(result, float)

    def test_matching_gender_increases_score(self):
        """Matching gender should increase score."""
        male_speaker = None
        for sid, data in SPEAKERS.items():
            if data["gender"] == "male":
                male_speaker = (sid, data)
                break

        if male_speaker:
            keywords_match = {"age": [], "gender": ["male"], "ethnicity": [], "language": [], "quality": []}
            keywords_no_match = {"age": [], "gender": ["female"], "ethnicity": [], "language": [], "quality": []}

            score_match = score_speaker(male_speaker[0], male_speaker[1], keywords_match)
            score_no_match = score_speaker(male_speaker[0], male_speaker[1], keywords_no_match)

            assert score_match > score_no_match

    def test_empty_keywords_returns_base_score(self):
        """Empty keywords should return base score."""
        keywords = {"age": [], "gender": [], "ethnicity": [], "language": [], "quality": []}
        result = score_speaker("p001", SPEAKERS["p001"], keywords)
        assert result >= 0
