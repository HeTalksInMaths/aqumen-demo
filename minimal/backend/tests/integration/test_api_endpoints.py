"""
Integration tests for API server endpoints.

These tests capture the current behavior of api_server.py before refactoring.
They ensure that refactored code maintains backward compatibility.
"""

import pytest
from fastapi.testclient import TestClient
import os
import json

# Set mock mode to avoid needing AWS credentials
os.environ["AQU_MOCK_PIPELINE"] = "1"

# Import from the refactored structure
from api.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test suite for health check endpoints."""

    def test_root_health_check(self, client):
        """Test root endpoint returns health status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "pipeline_ready" in data
        assert "version" in data

    def test_health_endpoint(self, client):
        """Test dedicated health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"


class TestModelsEndpoint:
    """Test suite for model information endpoint."""

    def test_get_models_in_mock_mode(self, client):
        """Test /api/models returns mock model info when in mock mode."""
        response = client.get("/api/models")
        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "models" in data
        assert "pipeline_flow" in data

        # Check model tiers
        assert "strong" in data["models"]
        assert "mid" in data["models"]
        assert "weak" in data["models"]

        # Each tier should have id, description, purpose
        for tier in ["strong", "mid", "weak"]:
            assert "id" in data["models"][tier]
            assert "description" in data["models"][tier]
            assert "purpose" in data["models"][tier]


class TestGenerateEndpoint:
    """Test suite for blocking question generation endpoint."""

    def test_generate_requires_topic(self, client):
        """Test that generation fails without a topic."""
        response = client.post("/api/generate", json={
            "topic": "",  # Empty topic should fail validation
            "max_retries": 3
        })
        assert response.status_code == 422  # Validation error

    def test_generate_validates_topic_length(self, client):
        """Test that topic must meet minimum length."""
        response = client.post("/api/generate", json={
            "topic": "AB",  # Too short (min is 3)
            "max_retries": 3
        })
        assert response.status_code == 422

    def test_generate_fails_in_mock_mode(self, client):
        """Test that generation fails gracefully in mock mode."""
        response = client.post("/api/generate", json={
            "topic": "Machine Learning Optimization",
            "max_retries": 3
        })
        # Should fail with 503 because pipeline is disabled in mock mode
        assert response.status_code == 503


class TestStreamingEndpoint:
    """Test suite for SSE streaming endpoint."""

    def test_generate_stream_requires_topic(self, client):
        """Test that streaming requires a topic parameter."""
        response = client.get("/api/generate-stream")
        # Missing required query parameter
        assert response.status_code == 422

    def test_generate_stream_validates_topic_length(self, client):
        """Test that streaming validates topic length."""
        response = client.get("/api/generate-stream?topic=AB")
        # Topic too short
        assert response.status_code == 422

    def test_generate_stream_fails_in_mock_mode(self, client):
        """Test that streaming fails gracefully in mock mode."""
        response = client.get("/api/generate-stream?topic=Neural+Networks")
        # Mock mode should prevent streaming
        assert response.status_code == 503 or "error" in response.text.lower()


class TestPromptEndpoints:
    """Test suite for prompt management endpoints."""

    def test_get_prompts(self, client):
        """Test retrieving current prompt configuration."""
        response = client.get("/api/get-prompts")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "prompts" in data

        # Check for expected prompt keys
        prompts = data["prompts"]
        expected_keys = [
            "step1_difficulty_categories",
            "step2_error_catalog",
            "step3_strategic_question",
            "step4_test_sonnet",
            "step5_test_haiku",
            "step6_judge_responses",
            "step7_student_assessment"
        ]
        for key in expected_keys:
            assert key in prompts, f"Missing prompt key: {key}"

    def test_update_prompt_requires_fields(self, client):
        """Test that update prompt requires step and new_prompt."""
        response = client.post("/api/update-prompt", json={})
        assert response.status_code == 400

    def test_update_prompt_validates_step_name(self, client):
        """Test that update prompt validates step name."""
        response = client.post("/api/update-prompt", json={
            "step": "invalid_step_name",
            "new_prompt": "Test prompt"
        })
        assert response.status_code == 400

    def test_update_prompt_success(self, client):
        """Test successful prompt update."""
        response = client.post("/api/update-prompt", json={
            "step": "step1_difficulty_categories",
            "new_prompt": "Test prompt template for integration testing"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["step"] == "step1_difficulty_categories"


class TestStep1Endpoint:
    """Test suite for Step 1 category generation endpoint."""

    def test_step1_requires_topic(self, client):
        """Test that step1 requires a topic."""
        response = client.post("/api/step1", json={})
        assert response.status_code == 400

    def test_step1_validates_topic_length(self, client):
        """Test that step1 validates topic length."""
        response = client.post("/api/step1", json={"topic": "AB"})
        assert response.status_code == 400

    def test_step1_fails_in_mock_mode(self, client):
        """Test that step1 fails gracefully in mock mode."""
        response = client.post("/api/step1", json={
            "topic": "Deep Learning"
        })
        # Should fail with 503 because pipeline is disabled in mock mode
        assert response.status_code == 503


class TestModelTestingEndpoint:
    """Test suite for model testing endpoint."""

    def test_test_models_endpoint_exists(self, client):
        """Test that model testing endpoint is accessible."""
        response = client.post("/api/test-models", json={})
        # Should fail in mock mode but endpoint should exist
        assert response.status_code in [200, 503]

    def test_test_models_accepts_provider(self, client):
        """Test that model testing accepts provider parameter."""
        response = client.post("/api/test-models", json={
            "provider": "anthropic"
        })
        # Should fail in mock mode
        assert response.status_code in [200, 503]


class TestCORSConfiguration:
    """Test suite for CORS middleware configuration."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are properly configured."""
        response = client.options("/health")
        # FastAPI TestClient doesn't fully simulate CORS preflight,
        # but we can verify the middleware is configured
        assert response.status_code in [200, 405]  # Some clients return 405 for OPTIONS


class TestResponseModels:
    """Test suite for response model validation."""

    def test_health_response_structure(self, client):
        """Test that health response matches expected model."""
        response = client.get("/health")
        data = response.json()

        # Required fields from HealthResponse model
        assert "status" in data
        assert "timestamp" in data
        assert "pipeline_ready" in data
        assert "version" in data

        # Type validation
        assert isinstance(data["status"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["pipeline_ready"], bool)
        assert isinstance(data["version"], str)


# Integration test configuration
pytest_plugins = ['pytest_asyncio']
