
from fastapi.testclient import TestClient

from backend.main import app


def test_pca_analysis_success():
    # Mock DB response

    payload = {
        "analysis": "pca",
        "params": {"width": 900, "height": 600},
        "data_filter": {
            "unique_id": ["LRX68bd3639001", "LRX68bd3639002", "LRX68bd3639003", "LRX68bd3639004", "LRX68bd3639005",
                          "LRX68bd3639006", "LRX68bd3639007", "LRX68bd3639008", "LRX68bd3639009"],
            "gene_name": [],
            "all_gene": True
        }
    }
    with TestClient(app) as client:
        response = client.post("/transcripts/analysis", json=payload)
    assert response.status_code == 200
    assert response.json()["code"] == 0
