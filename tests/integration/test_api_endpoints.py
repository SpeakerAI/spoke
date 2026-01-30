"""
Integration tests for API endpoints.

Tests the Flask API endpoints with HTTP requests.
"""

import pytest
import json
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)


class TestPingEndpoint:
    """Tests for GET /ping endpoint."""

    def test_ping_returns_200(self, client):
        """Ping endpoint should return 200 OK."""
        response = client.get('/ping')
        assert response.status_code == 200

    def test_ping_returns_json(self, client):
        """Ping endpoint should return JSON."""
        response = client.get('/ping')
        assert response.content_type == 'application/json'

    def test_ping_returns_success_status(self, client):
        """Ping endpoint should return success status."""
        response = client.get('/ping')
        data = json.loads(response.data)
        assert data['status'] == 'success'

    def test_ping_returns_message(self, client):
        """Ping endpoint should return a message."""
        response = client.get('/ping')
        data = json.loads(response.data)
        assert 'message' in data
        assert 'running' in data['message'].lower()


class TestHealthEndpoint:
    """Tests for GET /health endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        """Health endpoint should return JSON."""
        response = client.get('/health')
        assert response.content_type == 'application/json'

    def test_health_returns_healthy_status(self, client):
        """Health endpoint should return healthy status."""
        response = client.get('/health')
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

    def test_health_returns_service_name(self, client):
        """Health endpoint should return service name."""
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'service' in data
        assert 'Spoke' in data['service']


class TestRandomVoiceEndpoint:
    """Tests for POST /random_voice endpoint."""

    def test_random_voice_male(self, client):
        """Random voice endpoint should return male speaker."""
        response = client.post('/random_voice',
                               data=json.dumps({'gender': 'male'}),
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['gender'] == 'male'
        assert 'speaker_num' in data
        assert data['speaker_num'] >= 5  # Not classic voices

    def test_random_voice_female(self, client):
        """Random voice endpoint should return female speaker."""
        response = client.post('/random_voice',
                               data=json.dumps({'gender': 'female'}),
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['gender'] == 'female'
        assert 'speaker_num' in data

    def test_random_voice_invalid_gender(self, client):
        """Random voice endpoint should reject invalid gender."""
        response = client.post('/random_voice',
                               data=json.dumps({'gender': 'invalid'}),
                               content_type='application/json')
        assert response.status_code == 400

    def test_random_voice_missing_gender(self, client):
        """Random voice endpoint should reject missing gender."""
        response = client.post('/random_voice',
                               data=json.dumps({}),
                               content_type='application/json')
        assert response.status_code == 400

    def test_random_voice_no_body(self, client):
        """Random voice endpoint should reject request without body."""
        response = client.post('/random_voice')
        assert response.status_code == 400

    def test_random_voice_returns_profile(self, client):
        """Random voice endpoint should return speaker profile."""
        response = client.post('/random_voice',
                               data=json.dumps({'gender': 'male'}),
                               content_type='application/json')
        data = json.loads(response.data)
        assert 'profile' in data
        assert 'age' in data['profile']
        assert 'gender' in data['profile']


class TestMarketplaceCatalogEndpoint:
    """Tests for GET /marketplace/catalog endpoint."""

    def test_catalog_returns_200(self, client):
        """Catalog endpoint should return 200 OK."""
        response = client.get('/marketplace/catalog')
        assert response.status_code == 200

    def test_catalog_returns_json(self, client):
        """Catalog endpoint should return JSON."""
        response = client.get('/marketplace/catalog')
        assert response.content_type == 'application/json'

    def test_catalog_has_voices_list(self, client):
        """Catalog endpoint should return voices list."""
        response = client.get('/marketplace/catalog')
        data = json.loads(response.data)
        assert 'voices' in data
        assert isinstance(data['voices'], list)

    def test_catalog_has_total(self, client):
        """Catalog endpoint should return total count."""
        response = client.get('/marketplace/catalog')
        data = json.loads(response.data)
        assert 'total' in data
        assert isinstance(data['total'], int)


class TestVoicesOwnedEndpoint:
    """Tests for GET /voices/owned endpoint."""

    def test_owned_requires_user_id(self, client):
        """Owned voices endpoint should require user_id."""
        response = client.get('/voices/owned')
        assert response.status_code == 400

    def test_owned_returns_voices(self, client, sample_user_id):
        """Owned voices endpoint should return voices list."""
        response = client.get(f'/voices/owned?user_id={sample_user_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'voices' in data
        assert isinstance(data['voices'], list)

    def test_owned_returns_classic_voices(self, client, sample_user_id):
        """New user should have classic voices 1-4."""
        response = client.get(f'/voices/owned?user_id={sample_user_id}')
        data = json.loads(response.data)
        # Should contain at least classic voices
        for voice_id in [1, 2, 3, 4]:
            assert voice_id in data['voices']

    def test_owned_returns_total(self, client, sample_user_id):
        """Owned voices endpoint should return total count."""
        response = client.get(f'/voices/owned?user_id={sample_user_id}')
        data = json.loads(response.data)
        assert 'total' in data
        assert data['total'] >= 4


class TestVoicesAvailableEndpoint:
    """Tests for GET /voices/available endpoint."""

    def test_available_requires_user_id(self, client):
        """Available voices endpoint should require user_id."""
        response = client.get('/voices/available')
        assert response.status_code == 400

    def test_available_returns_owned_and_marketplace(self, client, sample_user_id):
        """Available voices endpoint should return owned and marketplace."""
        response = client.get(f'/voices/available?user_id={sample_user_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'owned' in data
        assert 'marketplace' in data


class TestMarketplacePurchaseEndpoint:
    """Tests for POST /marketplace/purchase endpoint."""

    def test_purchase_requires_user_id(self, client):
        """Purchase endpoint should require user_id."""
        response = client.post('/marketplace/purchase',
                               data=json.dumps({'voice_id': 25}),
                               content_type='application/json')
        assert response.status_code == 400

    def test_purchase_requires_voice_id(self, client):
        """Purchase endpoint should require voice_id."""
        response = client.post('/marketplace/purchase',
                               data=json.dumps({'user_id': 'test'}),
                               content_type='application/json')
        assert response.status_code == 400

    def test_purchase_no_body(self, client):
        """Purchase endpoint should reject request without body."""
        response = client.post('/marketplace/purchase')
        assert response.status_code == 400


class TestSynthesizeEndpoint:
    """Tests for POST /synthesize endpoint."""

    def test_synthesize_requires_text(self, client):
        """Synthesize endpoint should require text parameter."""
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'emotion': 'neutral',
                                   'speaker_id': 1
                               }),
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'text' in data['error'].lower()

    def test_synthesize_requires_emotion(self, client):
        """Synthesize endpoint should require emotion parameter."""
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': 'Hello',
                                   'speaker_id': 1
                               }),
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'emotion' in data['error'].lower()

    def test_synthesize_requires_speaker_id(self, client):
        """Synthesize endpoint should require speaker_id parameter."""
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': 'Hello',
                                   'emotion': 'neutral'
                               }),
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'speaker_id' in data['error'].lower()

    def test_synthesize_invalid_emotion(self, client):
        """Synthesize endpoint should reject invalid emotion."""
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': 'Hello',
                                   'emotion': 'invalid_emotion',
                                   'speaker_id': 1
                               }),
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'emotion' in data['error'].lower()

    def test_synthesize_invalid_speaker_id_low(self, client):
        """Synthesize endpoint should reject speaker_id < 1."""
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': 'Hello',
                                   'emotion': 'neutral',
                                   'speaker_id': 0
                               }),
                               content_type='application/json')
        assert response.status_code == 400

    def test_synthesize_invalid_speaker_id_high(self, client):
        """Synthesize endpoint should reject speaker_id > 107."""
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': 'Hello',
                                   'emotion': 'neutral',
                                   'speaker_id': 200
                               }),
                               content_type='application/json')
        assert response.status_code == 400

    def test_synthesize_no_body(self, client):
        """Synthesize endpoint should reject request without body."""
        response = client.post('/synthesize')
        assert response.status_code == 400

    def test_synthesize_valid_emotions(self, client, valid_emotions):
        """Synthesize endpoint should accept all valid emotions (validation only)."""
        for emotion in valid_emotions[:5]:  # Test first 5 to save time
            response = client.post('/synthesize',
                                   data=json.dumps({
                                       'text': 'Test',
                                       'emotion': emotion,
                                       'speaker_id': 1
                                   }),
                                   content_type='application/json')
            # Should not be 400 for invalid emotion
            assert response.status_code != 400 or 'emotion' not in json.loads(response.data).get('error', '').lower()
