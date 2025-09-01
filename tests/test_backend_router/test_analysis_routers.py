import pytest

from backend.analysis.tpm_analysis import AnalysisType
from backend.routers.analysis_routers import db_extract_gene_data

@pytest.mark.asyncio
@pytest.mark.parametrize("gene_id, unique_id, type", [
    ((), ("LRX68b567d3003"), (AnalysisType.deg)),
    ((), ("LRX68b567d3003"), (AnalysisType.pca)),
    ((), ("LRX68b567d3003"), (AnalysisType.tpm_heatmap))
])
async def test_db_extract_gene_data(gene_id, unique_id, type):
    result = await db_extract_gene_data(
        gene_name=gene_id, unique_ids=unique_id, type=type)
    assert result is not None
    print(result)
    assert "gene_id" in result.columns
