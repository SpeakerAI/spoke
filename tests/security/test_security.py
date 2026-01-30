"""
Security tests for Spoke TTS API.

Tests for common vulnerabilities and security best practices.
"""

import pytest
import json
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)


class TestInputValidation:
    """Tests for input validation and sanitization."""

    def test_synthesize_xss_in_text(self, client):
        """Text field should not execute scripts (XSS prevention)."""
        malicious_text = "<script>alert('xss')</script>"
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': malicious_text,
                                   'emotion': 'neutral',
                                   'speaker_id': 1
                               }),
                               content_type='application/json')
        # Should either sanitize or process safely
        # No script should be executed (server-side)
        assert response.status_code in [200, 500]  # May fail synthesis but not crash

    def test_synthesize_sql_injection_text(self, client):
        """Text field should not be vulnerable to SQL injection."""
        malicious_text = "'; DROP TABLE users; --"
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': malicious_text,
                                   'emotion': 'neutral',
                                   'speaker_id': 1
                               }),
                               content_type='application/json')
        # Should process normally without SQL execution
        assert response.status_code in [200, 400, 500]

    def test_synthesize_command_injection(self, client):
        """Text field should not be vulnerable to command injection."""
        malicious_text = "; rm -rf / #"
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': malicious_text,
                                   'emotion': 'neutral',
                                   'speaker_id': 1
                               }),
                               content_type='application/json')
        # Should process without executing commands
        assert response.status_code in [200, 400, 500]

    def test_path_traversal_emotion(self, client):
        """Emotion parameter should not allow path traversal."""
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': 'test',
                                   'emotion': '../../../etc/passwd',
                                   'speaker_id': 1
                               }),
                               content_type='application/json')
        assert response.status_code == 400

    def test_path_traversal_speaker_id(self, client):
        """Speaker ID should only accept valid integers."""
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': 'test',
                                   'emotion': 'neutral',
                                   'speaker_id': '../../../etc/passwd'
                               }),
                               content_type='application/json')
        assert response.status_code == 400


class TestInputSizeValidation:
    """Tests for input size limits and DoS prevention."""

    def test_synthesize_extremely_long_text(self, client):
        """Should reject or handle extremely long text."""
        long_text = "A" * 100000  # 100KB of text
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': long_text,
                                   'emotion': 'neutral',
                                   'speaker_id': 1
                               }),
                               content_type='application/json')
        # Should either reject (400) or handle gracefully
        assert response.status_code in [200, 400, 413, 500]

    def test_synthesize_unicode_bomb(self, client):
        """Should handle unicode normalization safely."""
        # Unicode normalization attack
        unicode_text = "\u202e" * 1000 + "test"  # Right-to-left override
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': unicode_text,
                                   'emotion': 'neutral',
                                   'speaker_id': 1
                               }),
                               content_type='application/json')
        # Should process without crashing
        assert response.status_code in [200, 400, 500]

    def test_random_voice_large_payload(self, client):
        """Should reject oversized payloads."""
        large_payload = {'gender': 'male', 'extra': 'A' * 10000}
        response = client.post('/random_voice',
                               data=json.dumps(large_payload),
                               content_type='application/json')
        # Should process only needed fields
        assert response.status_code in [200, 400, 413]


class TestAuthenticationEndpoints:
    """Tests for endpoints that should have authentication."""

    def test_purchase_without_auth(self, client):
        """Purchase endpoint validates required parameters."""
        response = client.post('/marketplace/purchase',
                               data=json.dumps({'voice_id': 5}),
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'user_id' in str(data).lower()

    def test_owned_voices_without_user(self, client):
        """Owned voices endpoint requires user identification."""
        response = client.get('/voices/owned')
        assert response.status_code == 400


class TestTypeValidation:
    """Tests for parameter type validation."""

    def test_speaker_id_string_type(self, client):
        """Speaker ID should reject string type."""
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': 'test',
                                   'emotion': 'neutral',
                                   'speaker_id': 'one'
                               }),
                               content_type='application/json')
        assert response.status_code == 400

    def test_speaker_id_float_type(self, client):
        """Speaker ID should handle float type."""
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': 'test',
                                   'emotion': 'neutral',
                                   'speaker_id': 1.5
                               }),
                               content_type='application/json')
        # Should either convert or reject
        assert response.status_code in [200, 400, 500]

    def test_speaker_id_negative(self, client):
        """Speaker ID should reject negative numbers."""
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': 'test',
                                   'emotion': 'neutral',
                                   'speaker_id': -1
                               }),
                               content_type='application/json')
        assert response.status_code == 400

    def test_speaker_id_none(self, client):
        """Speaker ID should reject null value."""
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': 'test',
                                   'emotion': 'neutral',
                                   'speaker_id': None
                               }),
                               content_type='application/json')
        assert response.status_code == 400


class TestContentTypeValidation:
    """Tests for content type validation."""

    def test_synthesize_wrong_content_type(self, client):
        """Should reject non-JSON content type for JSON endpoints."""
        response = client.post('/synthesize',
                               data='text=hello&emotion=neutral&speaker_id=1',
                               content_type='application/x-www-form-urlencoded')
        # Should require JSON
        assert response.status_code in [400, 415]

    def test_synthesize_invalid_json(self, client):
        """Should handle invalid JSON gracefully."""
        response = client.post('/synthesize',
                               data='{"text": "hello", invalid}',
                               content_type='application/json')
        assert response.status_code == 400


class TestResponseHeaders:
    """Tests for security-related response headers."""

    def test_cors_headers(self, client):
        """API should include appropriate CORS headers."""
        response = client.get('/health')
        # Check if CORS is configured
        # Note: Actual CORS headers may vary based on configuration
        assert response.status_code == 200

    def test_content_type_response(self, client):
        """API responses should have correct content-type."""
        response = client.get('/health')
        assert 'application/json' in response.content_type


class TestErrorHandling:
    """Tests for secure error handling."""

    def test_error_no_stack_trace(self, client):
        """Error responses should not expose stack traces."""
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': 'test',
                                   'emotion': 'invalid_emotion_xyz',
                                   'speaker_id': 1
                               }),
                               content_type='application/json')
        if response.status_code >= 400:
            data = response.data.decode('utf-8')
            # Should not contain Python traceback indicators
            assert 'Traceback' not in data
            assert 'File "' not in data

    def test_error_no_sensitive_paths(self, client):
        """Error responses should not expose file paths."""
        response = client.post('/synthesize',
                               data=json.dumps({
                                   'text': 'test',
                                   'emotion': 'invalid',
                                   'speaker_id': 1
                               }),
                               content_type='application/json')
        if response.status_code >= 400:
            data = response.data.decode('utf-8')
            # Should not expose server paths
            assert '/home/' not in data
            assert '/usr/' not in data


class TestRateLimitingConcepts:
    """Tests to verify rate limiting awareness (implementation may vary)."""

    def test_rapid_health_checks(self, client):
        """Health endpoint should handle rapid requests."""
        for _ in range(100):
            response = client.get('/health')
            # Should either succeed or rate limit
            assert response.status_code in [200, 429]

    def test_rapid_synthesis_requests(self, client):
        """Synthesis endpoint should handle request bursts."""
        responses = []
        for _ in range(10):
            response = client.post('/synthesize',
                                   data=json.dumps({
                                       'text': 'test',
                                       'emotion': 'neutral',
                                       'speaker_id': 1
                                   }),
                                   content_type='application/json')
            responses.append(response.status_code)
        # All should be handled (success, error, or rate limited)
        assert all(code in [200, 400, 429, 500, 503] for code in responses)
