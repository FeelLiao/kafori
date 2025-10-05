import pytest
from backend.db.interface import GetDataBaseInterface as database
from backend.analysis.framework import InputData
import polars as pl
import polars.testing as plt

test_tpm = "upload/gene_tpm_renamed.csv"
test_counts = "upload/gene_count_renamed.csv"
unique_id = ("LRX01d4693bb8b1063", "LRX075dee4dea9106f",
             "LRX0ccd5aa920a30a4", "LRX10a14a95ac7a08d")
samples = ["gene_id", "kk17306-2", "kk20213-2", "kk19711-2", "kk191115-3"]

gene_ids = ["g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8", "g9", "g10", "g198"]


@pytest.fixture
def unique_ids():
    return unique_id


@pytest.fixture
def gene_tpm(samples=samples):
    df = pl.read_csv(test_tpm)
    return df.select(samples)


@pytest.fixture
def gene_counts(samples=samples):
    df = pl.read_csv(test_counts)
    return df.select(samples)


@pytest.mark.asyncio
async def test_get_expression_v2(unique_ids, gene_tpm, gene_counts):
    data_tpm = await database.get_expression_v2(unique_ids, type=InputData.tpm)
    data_counts = await database.get_expression_v2(unique_ids, type=InputData.counts)
    assert data_tpm is not None
    assert data_counts is not None
    assert len(data_tpm) == len(data_counts)
    # 对齐列顺序
    data_tpm = data_tpm.select(gene_tpm.columns)
    data_counts = data_counts.select(gene_counts.columns)

    # 对齐 dtypes（避免 float32/float64 差异引发失败）
    for c, dt in zip(gene_tpm.columns, gene_tpm.dtypes):
        data_tpm = data_tpm.with_columns(pl.col(c).cast(dt))
    for c, dt in zip(gene_counts.columns, gene_counts.dtypes):
        data_counts = data_counts.with_columns(pl.col(c).cast(dt))

    # 断言相等（如需容差，将 check_exact=False, rtol=1e-6）
    plt.assert_frame_equal(data_tpm, gene_tpm, check_column_order=False, check_dtypes=False, check_exact=False)
    plt.assert_frame_equal(data_counts, gene_counts, check_column_order=False, check_dtypes=False, check_exact=False)


@pytest.mark.asyncio
async def test_get_expression_v2_gene_id_filter():
    data_tpm = await database.get_expression_v2(unique_id, type=InputData.tpm, gene_id=gene_ids)
    assert data_tpm is not None
    assert data_tpm.height == len(gene_ids)
