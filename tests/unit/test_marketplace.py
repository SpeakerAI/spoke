"""
Unit tests for marketplace module.

Tests the voice marketplace functionality with Supabase integration.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from server.marketplace import (
    MarketplaceManager,
    get_speaker_info,
    create_marketplace_voice_from_speaker
)


class TestMarketplaceManagerInitUser:
    """Tests for MarketplaceManager.init_user method."""

    def test_init_user_without_supabase(self):
        """init_user should return False when Supabase is not configured."""
        # When supabase client is None, it should return False
        with patch('server.marketplace.supabase', None):
            result = MarketplaceManager.init_user("test_user")
            assert result == False

    @patch('server.marketplace.supabase')
    def test_init_user_with_supabase(self, mock_supabase):
        """init_user should return True when Supabase call succeeds."""
        mock_supabase.table.return_value.upsert.return_value.execute.return_value = Mock()
        result = MarketplaceManager.init_user("test_user")
        assert result == True

    @patch('server.marketplace.supabase')
    def test_init_user_creates_4_classic_voices(self, mock_supabase):
        """init_user should create 4 classic voices."""
        mock_supabase.table.return_value.upsert.return_value.execute.return_value = Mock()
        MarketplaceManager.init_user("test_user")

        # Check that upsert was called with 4 voices
        call_args = mock_supabase.table.return_value.upsert.call_args
        voices = call_args[0][0]
        assert len(voices) == 4
        assert all(v['voice_id'] in [1, 2, 3, 4] for v in voices)


class TestMarketplaceManagerGetUserVoices:
    """Tests for MarketplaceManager.get_user_voices method."""

    def test_get_user_voices_without_supabase(self):
        """Should return default voices [1,2,3,4] when Supabase is not configured."""
        with patch('server.marketplace.supabase', None):
            result = MarketplaceManager.get_user_voices("test_user")
            assert result == [1, 2, 3, 4]

    @patch('server.marketplace.supabase')
    def test_get_user_voices_with_supabase(self, mock_supabase):
        """Should return voices from Supabase."""
        mock_response = Mock()
        mock_response.data = [
            {'voice_id': 1},
            {'voice_id': 2},
            {'voice_id': 3},
            {'voice_id': 4},
            {'voice_id': 25}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        result = MarketplaceManager.get_user_voices("test_user")
        assert result == [1, 2, 3, 4, 25]


class TestMarketplaceManagerHasVoice:
    """Tests for MarketplaceManager.has_voice method."""

    @patch.object(MarketplaceManager, 'get_user_voices')
    def test_has_voice_true(self, mock_get_voices):
        """has_voice should return True when user owns the voice."""
        mock_get_voices.return_value = [1, 2, 3, 4, 25]
        result = MarketplaceManager.has_voice("test_user", 25)
        assert result == True

    @patch.object(MarketplaceManager, 'get_user_voices')
    def test_has_voice_false(self, mock_get_voices):
        """has_voice should return False when user doesn't own the voice."""
        mock_get_voices.return_value = [1, 2, 3, 4]
        result = MarketplaceManager.has_voice("test_user", 25)
        assert result == False

    @patch.object(MarketplaceManager, 'get_user_voices')
    def test_has_voice_classic(self, mock_get_voices):
        """has_voice should return True for classic voices."""
        mock_get_voices.return_value = [1, 2, 3, 4]
        for voice_id in [1, 2, 3, 4]:
            assert MarketplaceManager.has_voice("test_user", voice_id) == True


class TestMarketplaceManagerGetMarketplaceVoices:
    """Tests for MarketplaceManager.get_marketplace_voices method."""

    def test_get_marketplace_voices_without_supabase(self):
        """Should return empty list when Supabase is not configured."""
        with patch('server.marketplace.supabase', None):
            result = MarketplaceManager.get_marketplace_voices()
            assert result == []

    @patch('server.marketplace.supabase')
    def test_get_marketplace_voices_with_supabase(self, mock_supabase):
        """Should return voices from Supabase."""
        mock_response = Mock()
        mock_response.data = [
            {'voice_id': 5, 'name': 'Voice 5', 'price': 9.99},
            {'voice_id': 10, 'name': 'Voice 10', 'price': 14.99}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response

        result = MarketplaceManager.get_marketplace_voices(limit=50)
        assert len(result) == 2
        assert result[0]['voice_id'] == 5


class TestMarketplaceManagerPurchaseVoice:
    """Tests for MarketplaceManager.purchase_voice method."""

    def test_purchase_voice_without_supabase(self):
        """Should return failure when Supabase is not configured."""
        with patch('server.marketplace.supabase', None):
            success, message = MarketplaceManager.purchase_voice("test_user", 25)
            assert success == False
            assert "not configured" in message.lower()

    @patch.object(MarketplaceManager, 'get_voice_details')
    @patch.object(MarketplaceManager, 'has_voice')
    def test_purchase_voice_already_owned(self, mock_has_voice, mock_get_details):
        """Should fail when user already owns the voice."""
        mock_get_details.return_value = {'voice_id': 25, 'name': 'Test', 'price': 9.99}
        mock_has_voice.return_value = True

        with patch('server.marketplace.supabase', Mock()):
            success, message = MarketplaceManager.purchase_voice("test_user", 25)
            assert success == False
            assert "already own" in message.lower()

    @patch.object(MarketplaceManager, 'get_voice_details')
    def test_purchase_voice_not_found(self, mock_get_details):
        """Should fail when voice is not found."""
        mock_get_details.return_value = None

        with patch('server.marketplace.supabase', Mock()):
            success, message = MarketplaceManager.purchase_voice("test_user", 999)
            assert success == False
            assert "not found" in message.lower()


class TestGetSpeakerInfo:
    """Tests for get_speaker_info helper function."""

    def test_get_speaker_info_valid(self):
        """Should return speaker info for valid ID."""
        result = get_speaker_info(1)
        assert result is not None
        assert "gender" in result
        assert "age" in result

    def test_get_speaker_info_invalid(self):
        """Should return None for invalid ID."""
        result = get_speaker_info(999)
        assert result is None

    def test_get_speaker_info_boundary(self):
        """Should work for boundary IDs (1 and 107)."""
        result_first = get_speaker_info(1)
        result_last = get_speaker_info(107)
        assert result_first is not None
        assert result_last is not None


class TestCreateMarketplaceVoiceFromSpeaker:
    """Tests for create_marketplace_voice_from_speaker helper function."""

    def test_create_valid_speaker(self):
        """Should create marketplace voice for valid speaker."""
        result = create_marketplace_voice_from_speaker(10)
        assert result is not None
        assert "voice_id" in result
        assert "name" in result
        assert "price" in result
        assert result["voice_id"] == 10

    def test_create_invalid_speaker(self):
        """Should return None for invalid speaker."""
        result = create_marketplace_voice_from_speaker(999)
        assert result is None

    def test_default_price(self):
        """Created voice should have default price of 9.99."""
        result = create_marketplace_voice_from_speaker(10)
        assert result["price"] == 9.99
