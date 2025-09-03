import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.mark.asyncio
def test_query_transcripts_exp_class_success():
    # Mock DB response

    payload = {
        "query_type": "exp_class",
        "query_value": None
    }
    with TestClient(app) as client:
        response = client.post("/transcripts/query", json=payload)
    assert response.status_code == 200
    assert response.json()["code"] == 0
    assert {
      "ExpClass": "EXPC68b567d3001",
      "ExperimentCategory": "drought"
    } in response.json()["data"]


@pytest.mark.asyncio
def test_query_transcripts_exp_name_success():
    # Mock DB response

    payload = {
        "query_type": "exp_name",
        "query_value": ["EXPC68b567d3001"]
    }
    with TestClient(app) as client:
        response = client.post("/transcripts/query", json=payload)
    assert response.status_code == 200
    assert response.json()["code"] == 0
    assert {
      "UniqueEXID": "TRCRIE68b567d3002",
      "ExpClass": "EXPC68b567d3001",
      "Experiment": "drought for 3 weeks"
    } in response.json()["data"]


@pytest.mark.asyncio
def test_query_transcripts_sample_id_success():
    # Mock DB response

    payload = {
        "query_type": "sample_id",
        "query_value": ["TRCRIE68b567d3002"]
    }
    with TestClient(app) as client:
        response = client.post("/transcripts/query", json=payload)
    assert response.status_code == 200
    assert response.json()["code"] == 0
    assert {
      "UniqueID": "LRX68b567d3003",
      "SampleID": "Buntreated-1",
      "Sample": "null",
      "SampleAge": 10,
      "SampleDetail": "0 weeks ",
      "DepositDatabase": "nan",
      "Accession": "nan",
      "Origin": "nan",
      "CollectionPart": "stem",
      "CollectionTime": "2020-03-09"
    } in response.json()["data"]
