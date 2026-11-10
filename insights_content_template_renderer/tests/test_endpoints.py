from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from insights_content_template_renderer.data import (
    request_data_example,
    response_data_example,
)
from insights_content_template_renderer.endpoints import app

client = TestClient(app)

ENDPOINT__V1_RENDERED_REPORTS = "/v1/rendered_reports"


@pytest.mark.parametrize("method", [client.get, client.put, client.delete])
def test_bad_method(method):
    response = method(ENDPOINT__V1_RENDERED_REPORTS)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_no_data():
    response = client.post(ENDPOINT__V1_RENDERED_REPORTS)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_valid_data():
    response = client.post(ENDPOINT__V1_RENDERED_REPORTS, json=request_data_example)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data_example


@patch("insights_content_template_renderer.endpoints.render_reports")
def test_exception_handling(mock_render_reports):
    """Test that exceptions in render_reports are properly handled."""
    # Mock render_reports to raise an exception
    mock_render_reports.side_effect = Exception("Test exception")

    response = client.post(ENDPOINT__V1_RENDERED_REPORTS, json=request_data_example)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.text == "Internal Server Error"


ENDPOINT__V2_RENDERED_REPORTS = "/v2/rendered_reports"

BATCH_RENDER_REQUEST_EXAMPLE = {
    "items": [
        {
            "template": {
                "reason": "Workload {{=pydata.name}} has a finding",
                "resolution": "Apply the resolution to {{=pydata.name}}",
                "more_info": "",
            },
            "data": {"name": "test-app"},
        },
        {
            "template": {
                "reason": "Reason for {{=pydata.missing.value()}}",
            },
            "data": {"name": "test-app"},
        },
    ]
}


@pytest.mark.parametrize("method", [client.get, client.put, client.delete])
def test_render_bad_method(method):
    response = method(ENDPOINT__V2_RENDERED_REPORTS)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_render_no_data():
    response = client.post(ENDPOINT__V2_RENDERED_REPORTS)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_render_valid_data():
    response = client.post(
        ENDPOINT__V2_RENDERED_REPORTS, json=BATCH_RENDER_REQUEST_EXAMPLE
    )
    assert response.status_code == status.HTTP_200_OK

    payload = response.json()
    assert len(payload["items"]) == len(BATCH_RENDER_REQUEST_EXAMPLE["items"])

    first = payload["items"][0]
    assert first["rendered"]["reason"] == "Workload test-app has a finding"
    assert first["rendered"]["resolution"] == "Apply the resolution to test-app"
    # empty templates are skipped, not errors
    assert "more_info" not in first["rendered"]
    assert first["errors"] == {}

    second = payload["items"][1]
    # the failing field is reported as an error
    assert "reason" not in second["rendered"]
    assert "reason" in second["errors"]


def test_render_empty_items():
    response = client.post(ENDPOINT__V2_RENDERED_REPORTS, json={"items": []})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"items": []}


def test_render_error_message_has_no_stack_traces():
    response = client.post(
        ENDPOINT__V2_RENDERED_REPORTS, json=BATCH_RENDER_REQUEST_EXAMPLE
    )
    assert response.status_code == status.HTTP_200_OK

    second = response.json()["items"][1]
    error = second["errors"]["reason"]
    assert "Traceback" not in error
    assert "Stack Trace" not in error
    # the concise JS error is kept
    assert "pydata.missing" in error
