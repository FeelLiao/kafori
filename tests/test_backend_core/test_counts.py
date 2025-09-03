import pytest

from backend.db.interface import GetDataBaseInterface

database = GetDataBaseInterface()

@pytest.mark.asyncio
async def test_get_gene_tpm():
    gene_id: tuple[str] = ("YDL248W",)
    unique_id: tuple[str] = ("LRX68b567d3003",)
    res = await database.get_gene_counts(gene_id=gene_id, unique_id=unique_id, gene_id_is_all=False)
    print(res)