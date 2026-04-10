"""Test the /metrics endpoint."""

from fastapi.testclient import TestClient

from insights_content_template_renderer.endpoints import app


class TestMetricsEndpoint:  # pylint: disable=too-few-public-methods
    """Check the /metrics endpoint expose some metrics."""

    def test_http_requests_total(self):
        """Check that the http_requests_total metric exists."""
        with TestClient(app) as client:
            response = client.get("/metrics")
            assert response.status_code == 200
            assert "http_requests_total" in response.text
