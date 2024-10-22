from fastapi.testclient import TestClient
from fastapi import status
import pytest

from insights_content_template_renderer.endpoints import app
from insights_content_template_renderer.data import request_data_example, response_data_example


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

