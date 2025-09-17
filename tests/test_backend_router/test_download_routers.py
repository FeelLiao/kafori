import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.mark.asyncio
def test_download_catalog():
    with TestClient(app) as client:
        response = client.get("/download/catalog/")
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["message"] == "Success"