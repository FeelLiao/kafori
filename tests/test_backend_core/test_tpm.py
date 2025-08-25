import pytest

from backend.db.interface import GetDataBaseInterface

database = GetDataBaseInterface()

@pytest.mark.asyncio
async def test_get_gene_tpm():
    gene_id: tuple[str] = ('g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7')
    unique_id: tuple[str] = ('D-1', 'M-1')
    res = await database.get_gene_tpm(gene_id, unique_id)
    print(res)
