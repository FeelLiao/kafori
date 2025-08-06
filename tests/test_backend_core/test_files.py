import io
import pytest
import pandas as pd
from backend.api.files import UploadFileProcessor, FileType
from pathlib import Path

test_sample = "tests/upstream/test.xlsx"
rawdata_dir = "tests/upstream/ngs-test-data"


@pytest.fixture
def sample_xlsx():
    with open(test_sample, "rb") as f:
        sample_xlsx = io.BytesIO(f.read())
    return sample_xlsx


@pytest.fixture
def rawdata_dir_path():
    return Path(rawdata_dir)


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
        ("invalid_sample_id_format", ValueError, "SampleID contains invalid characters:"),
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
    valid, missing = UploadFileProcessor.rawdata_validation(sample_sheet, rawdata_dir_path)
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
    valid, missing = UploadFileProcessor.rawdata_validation(processor, rawdata_dir_path)
    assert valid is False
    assert "Atreated-2_1.fq" in missing


# def test_database_wrapper(sample_xlsx):
#     processor = UploadFileProcessor(sample_xlsx)
#     df = processor.database_wrapper()
#     assert "UniqueID" in df.columns
#     assert "UniqueEXID" in df.columns
#     assert df["UniqueID"].str.startswith("LRX").all()
#     assert df["UniqueEXID"].str.startswith("TRCRIE").all()
#     assert len(df["UniqueID"].unique()) == len(df)


# def test_trans_to_smk_samples(sample_xlsx, rawdata_dir_path, tmp_path):
#     processor = UploadFileProcessor(sample_xlsx)
#     db_df = processor.database_wrapper()
#     output_path = tmp_path / "samples.csv"
#     smk_df = UploadFileProcessor.trans_to_smk_samples(
#         db_df, rawdata_dir_path, to_file=True, output_path=output_path)
#     assert "sample" in smk_df.columns
#     assert "sample_id" in smk_df.columns
#     assert "read1" in smk_df.columns
#     assert "read2" in smk_df.columns
#     # Check file written
#     assert output_path.exists()
#     loaded = pd.read_csv(output_path)
#     assert loaded.equals(smk_df)
