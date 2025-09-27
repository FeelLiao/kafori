import asyncio
import httpx
import pytest
from asgi_lifespan import LifespanManager
from backend.main import app

payload = {
    "analysis": "pca",
    "params": {"width": 900, "height": 600},
    "data_filter": {
        "unique_id": ["LRX68bd3639001", "LRX68bd3639002", "LRX68bd3639003",
                      "LRX68bd3639004", "LRX68bd3639005", "LRX68bd3639006",
                      "LRX68bd3639007", "LRX68bd3639008", "LRX68bd3639009"],
        "gene_name": [],
        "all_gene": True
    }
}


@pytest.mark.asyncio
async def test_pca_analysis_concurrent_inprocess():
    n = 5
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            rs = await asyncio.gather(*[
                client.post("/transcripts/analysis", json=payload)
                for _ in range(n)
            ])
    for i, r in enumerate(rs):
        assert r.status_code == 200, f"req{i}"
        body = r.json()
        assert body["code"] == 0, f"req{i} body={body}"
