import asyncio
import httpx
import pytest
from asgi_lifespan import LifespanManager
from backend.main import app

payload = {
    "analysis": "pca",
    "params": {"width": 900, "height": 600},
    "data_filter": {
        "unique_id": [
            "LRX4bf8d67d2a150c1",
            "LRX75d6e121b8390c3",
            "LRX331980d78abe0bf",
            "LRX4791517c2b8c0be",
            "LRXa88e8a8bc4050bd",
            "LRX75762da903270c0",
            "LRX3566c0d048cd0ba",
            "LRX666ef8a9d7750bc",
            "LRX98a8faeddb5d0bb",
            "LRXd8a2bd33687f0b9",
            "LRX9582fd1ac6e90c2",
            "LRXaca1b8513b8b0c4",
            "LRX19713794c22e0b7",
            "LRX39fe0fb2501b0b8",
            "LRX8edbb61026f60b6",
            "LRXf758193263560b5"
        ],
        "gene_name": [],
        "all_gene": True
    }
}


@pytest.mark.asyncio
async def test_pca_analysis_concurrent_inprocess():
    n = 1
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


# 以下为 DEG 分析脚本测试
deg_payload = {
    "analysis": "deg",
    "params": {
        "width": 900,
        "height": 600
    },
    "data_filter": {
        "unique_id": [
            "LRX4bf8d67d2a150c1",
            "LRX75d6e121b8390c3",
            "LRX331980d78abe0bf",
            "LRX4791517c2b8c0be",
            "LRXa88e8a8bc4050bd",
            "LRX75762da903270c0",
            "LRX3566c0d048cd0ba",
            "LRX666ef8a9d7750bc",
            "LRX98a8faeddb5d0bb",
            "LRXd8a2bd33687f0b9",
            "LRX9582fd1ac6e90c2",
            "LRXaca1b8513b8b0c4",
            "LRX19713794c22e0b7",
            "LRX39fe0fb2501b0b8",
            "LRX8edbb61026f60b6",
            "LRXf758193263560b5"
        ],
        "gene_name": [],
        "all_gene": True
    }
}


@pytest.mark.asyncio
async def test_deg_analysis_concurrent_inprocess():
    n = 1
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            rs = await asyncio.gather(*[
                client.post("/transcripts/analysis", json=deg_payload)
                for _ in range(n)
            ])
    for i, r in enumerate(rs):
        assert r.status_code == 200, f"req{i}"
        body = r.json()
        assert body["code"] == 0, f"req{i} body={body}"
        tables = body["data"]["tables"]
        assert len(tables) == 6
