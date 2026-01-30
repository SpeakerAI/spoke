"""
Load testing with Locust for Spoke TTS API.

Run with: locust -f tests/load/locustfile.py --host=http://localhost:5000

For headless mode:
locust -f tests/load/locustfile.py --host=http://localhost:5000 --headless -u 10 -r 2 -t 1m
"""

from locust import HttpUser, task, between
import json
import random


class SpokeTTSUser(HttpUser):
    """Simulates a user interacting with the Spoke TTS API."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Called when a simulated user starts."""
        self.user_id = f"load_test_user_{random.randint(1000, 9999)}"
        self.classic_voices = [1, 2, 3, 4]
        self.emotions = ["neutral", "joy", "anger", "sadness", "fear"]

    @task(10)
    def health_check(self):
        """
        Task: Health check (high frequency)
        Weight: 10 (most common request)
        """
        self.client.get("/health")

    @task(8)
    def ping(self):
        """
        Task: Ping endpoint
        Weight: 8
        """
        self.client.get("/ping")

    @task(5)
    def get_owned_voices(self):
        """
        Task: Get user's owned voices
        Weight: 5
        """
        self.client.get(f"/voices/owned?user_id={self.user_id}")

    @task(3)
    def get_marketplace_catalog(self):
        """
        Task: Get marketplace catalog
        Weight: 3
        """
        self.client.get("/marketplace/catalog")

    @task(3)
    def get_random_voice_male(self):
        """
        Task: Get random male voice
        Weight: 3
        """
        self.client.post(
            "/random_voice",
            json={"gender": "male"}
        )

    @task(3)
    def get_random_voice_female(self):
        """
        Task: Get random female voice
        Weight: 3
        """
        self.client.post(
            "/random_voice",
            json={"gender": "female"}
        )

    @task(2)
    def get_available_voices(self):
        """
        Task: Get all available voices
        Weight: 2
        """
        self.client.get(f"/voices/available?user_id={self.user_id}")

    @task(1)
    def simulate_purchase(self):
        """
        Task: Simulate voice purchase (low frequency)
        Weight: 1
        """
        voice_id = random.randint(5, 107)
        self.client.post(
            "/marketplace/purchase",
            json={
                "user_id": self.user_id,
                "voice_id": voice_id
            }
        )


class SynthesisUser(HttpUser):
    """
    Simulates users making synthesis requests.
    Separated because synthesis is CPU-intensive and slow.
    """

    wait_time = between(5, 15)  # Longer wait for synthesis

    def on_start(self):
        """Called when a simulated user starts."""
        self.user_id = f"synth_user_{random.randint(1000, 9999)}"
        self.test_texts = [
            "Hello, this is a test.",
            "How are you today?",
            "The quick brown fox jumps over the lazy dog.",
            "Testing the text to speech system.",
            "This is a load test for performance evaluation."
        ]
        self.emotions = ["neutral", "joy", "anger", "sadness", "fear"]
        self.speakers = [1, 2, 3, 4]

    @task(1)
    def synthesize_short_text(self):
        """
        Task: Synthesize short text
        Note: This is resource-intensive, use with caution
        """
        with self.client.post(
            "/synthesize",
            json={
                "text": random.choice(self.test_texts),
                "emotion": random.choice(self.emotions),
                "speaker_id": random.choice(self.speakers)
            },
            catch_response=True,
            timeout=60  # 60 second timeout for synthesis
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 500:
                # Server error might be expected under heavy load
                response.failure(f"Server error: {response.status_code}")
            else:
                response.failure(f"Unexpected status: {response.status_code}")


class LightweightUser(HttpUser):
    """
    Lightweight user that only makes non-intensive requests.
    Good for stress testing the API layer without GPU load.
    """

    wait_time = between(0.5, 2)

    def on_start(self):
        self.user_id = f"light_user_{random.randint(1000, 9999)}"

    @task(10)
    def ping(self):
        self.client.get("/ping")

    @task(10)
    def health(self):
        self.client.get("/health")

    @task(5)
    def owned_voices(self):
        self.client.get(f"/voices/owned?user_id={self.user_id}")

    @task(5)
    def random_voice(self):
        gender = random.choice(["male", "female"])
        self.client.post("/random_voice", json={"gender": gender})

    @task(2)
    def catalog(self):
        self.client.get("/marketplace/catalog")


# Configuration presets for different test scenarios

class NormalLoadUser(SpokeTTSUser):
    """Normal load scenario - typical user behavior."""
    weight = 10


class HeavySynthesisUser(SynthesisUser):
    """Heavy synthesis scenario - stress test GPU."""
    weight = 1


class StressTestUser(LightweightUser):
    """Stress test scenario - many fast requests."""
    weight = 5
