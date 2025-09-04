import io
import pytest
import pandas as pd
from pathlib import Path

from backend.api.files import UploadFileProcessor, FileType, PutDataBaseWrapper, UpstreamAnalysisWrapper
from backend.db.interface import PutDataBaseInterface

test_sample = "tests/upstream/test.xlsx"
rawdata_dir = "tests/upstream/ngs-test-data"
counts = "tests/upstream/samples_merged_counts.csv"
tpm = "tests/upstream/samples_merged_tpm.csv"


@pytest.fixture
def sample_xlsx():
    with open(test_sample, "rb") as f:
        sample_xlsx = io.BytesIO(f.read())
    return sample_xlsx


@pytest.fixture
def rawdata_dir_path():
    return Path(rawdata_dir)


@pytest.fixture
def tpm_in():
    return tpm


@pytest.fixture
def counts_in():
    return counts


@pytest.mark.parametrize(
    "file_type,make_file",
    [
        (FileType.csv, lambda df: io.BytesIO(
            df.to_csv(index=False).encode('utf-8'))),
        (FileType.parquet, lambda df: (lambda b: (
            df.to_parquet(b), b.seek(0), b)[-1])(io.BytesIO())),
        (FileType.xlsx, lambda df: (lambda b: (df.to_excel(b, index=False, sheet_name="SampleInfo"),
                                               b.seek(0), b)[-1])(io.BytesIO())),
    ]
)
def test_read_file_all_types(file_type, make_file):
    df = pd.DataFrame({
        "SampleID": ["A-1", "B-2"],
        "CollectionTime": ["2022-01-01", "2022-01-02"],
        "SampleAge": [10, 12]
    })
    file = make_file(df)
    result = UploadFileProcessor.read_file(file, file_type)
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["SampleID", "CollectionTime", "SampleAge"]
    assert result.shape == (2, 3)


@pytest.fixture
def sample_data_validation(sample_xlsx):
    df = pd.read_excel(sample_xlsx, sheet_name="SampleInfo", header=0,
                       dtype={"CollectionTime": str},
                       na_values=["", "NA", "null", "None", "999"])
    invalid_collection_time = df.copy()
    invalid_collection_time.at[1, "CollectionTime"] = "2023098"

    invalid_sample_id_format = df.copy()
    invalid_sample_id_format.at[0, "SampleID"] = "1A-1"
    invalid_sample_id_format.at[1, "SampleID"] = "B_2"

    duplicate_sample_id = df.copy()
    duplicate_sample_id.at[1, "SampleID"] = "A-1"
    duplicate_sample_id.at[0, "SampleID"] = "A-1"

    return invalid_collection_time, invalid_sample_id_format, duplicate_sample_id


@pytest.mark.parametrize(
    "df_key, expected_error, error_message",
    [
        ("invalid_collection_time", RuntimeError, "Error parsing file"),
        ("invalid_sample_id_format", ValueError,
         "SampleID contains invalid characters:"),
        ("duplicate_sample_id", ValueError, "SampleID contains duplicate values:"),
    ]
)
def test_invalid_sample_file(df_key, expected_error, error_message, sample_data_validation):
    invalid_collection_time, invalid_sample_id_format, duplicate_sample_id = sample_data_validation
    df_map = {
        "invalid_collection_time": invalid_collection_time,
        "invalid_sample_id_format": invalid_sample_id_format,
        "duplicate_sample_id": duplicate_sample_id,
    }
    df = df_map[df_key]
    with pytest.raises(expected_error, match=error_message):
        UploadFileProcessor.sample_data_validation("test", df)


def test_rawdata_validation(sample_xlsx, rawdata_dir_path):
    sample_sheet = UploadFileProcessor.read_file(sample_xlsx, FileType.xlsx)
    valid, missing = UploadFileProcessor.rawdata_validation(
        sample_sheet, rawdata_dir_path)
    assert valid is True
    assert missing == []


def test_rawdata_missing_file(sample_xlsx, rawdata_dir_path, caplog):
    processor1 = UploadFileProcessor.read_file(sample_xlsx, FileType.xlsx)
    processor1.at[0, "FileName1"] = "missing_file.fastq"
    processor1.at[0, "MD5checksum1"] = "dummy_md5"
    with caplog.at_level("ERROR"):
        UploadFileProcessor.rawdata_validation(processor1, rawdata_dir_path)
    assert "Error checking" in caplog.text


def test_rawdata_wrong_md5(sample_xlsx, rawdata_dir_path):
    processor = UploadFileProcessor.read_file(sample_xlsx, FileType.xlsx)
    processor.at[0, "MD5checksum1"] = "dummy_md5"
    valid, missing = UploadFileProcessor.rawdata_validation(
        processor, rawdata_dir_path)
    assert valid is False
    assert "Atreated-2_1.fq" in missing


@pytest.mark.asyncio
async def test_database_wrapper(sample_xlsx, tpm_in, counts_in):
    sample_sheet_data = UploadFileProcessor.read_file(
        sample_xlsx, FileType.xlsx)
    gene_tpm_data = UploadFileProcessor.read_file(tpm_in, FileType.csv)
    gene_counts_data = UploadFileProcessor.read_file(counts_in, FileType.csv)
    data_base_wrapper = PutDataBaseWrapper(
        sample_sheet_data, gene_tpm_data, gene_counts_data)
    exp_class_communication = data_base_wrapper.communicate_id_in_db()
    exp_class_communication_r = await PutDataBaseInterface.exclass_processing(exp_class_communication)

    exp_sheet, sample_sheet = data_base_wrapper.db_insert(
        exp_class_communication_r)
    tpm, counts = data_base_wrapper.expression_wrapper(sample_sheet)

    assert len(exp_class_communication) == len(exp_class_communication_r[1])
    assert type(exp_class_communication_r[0]) is list
    assert set(exp_sheet.columns.tolist()) == {
        "ExpClass", "UniqueEXID", "Experiment"}
    assert len(sample_sheet.columns.tolist()) == 12
    assert tpm.shape[0] == counts.shape[0]
    assert tpm.shape[1] == counts.shape[1]

    print(exp_class_communication)
    print(exp_class_communication_r)


test_path = Path("tests/upstream")


@pytest.fixture
def valid_paths():
    work_dir = test_path / "work_dir"
    rawdata_dir = test_path / "ngs-test-data"
    genome = test_path / "ref/Saccharomyces_cerevisiae.fa"
    annotation = test_path / "ref/Saccharomyces_cerevisiae.gtf"
    return work_dir, rawdata_dir, genome, annotation


def test_run_analysis_success(sample_xlsx, valid_paths):
    work_dir, rawdata_dir, genome, annotation = valid_paths
    sample_sheet = UploadFileProcessor.read_file(
        sample_xlsx, FileType.xlsx)
    analysis = UpstreamAnalysisWrapper(user="admin",
                                       work_dir=work_dir, rawdata_dir=rawdata_dir,
                                       sample_sheet=sample_sheet,
                                       genome=genome, annotation=annotation)

    result_dry_run = analysis.smk_dry_run()
    result_run = analysis.smk_run(8)
    res = analysis.post_process()

    tpm = res["quantification"][0]
    counts = res["quantification"][1]
    align_status = res["align_report"][0]
    align_report = res["align_report"][1]
    fastp_status = res["fastp_report"][0]
    fastp_report = res["fastp_report"][1]

    assert result_run is True
    assert result_dry_run is True

    assert tpm.shape[0] > 0 and tpm.shape[1] > 0
    assert counts.shape[0] > 0 and counts.shape[1] > 0
    assert align_status is True
    assert fastp_status is True
    assert align_report.shape[0] > 0 and align_report.shape[1] > 0
    assert fastp_report.shape[0] > 0 and fastp_report.shape[1] > 0
