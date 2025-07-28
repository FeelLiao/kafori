import pytest
import pandas as pd
from backend.api.files import UploadFileProcessor
from pathlib import Path

test_sample = "tests/upstream/test.xlsx"
rawdata_dir = "tests/upstream/ngs-test-data"


@pytest.fixture
def sample_xlsx():
    return test_sample


@pytest.fixture
def rawdata_dir_path():
    return Path(rawdata_dir)


@pytest.fixture
def invalid_collection_time(tmp_path, sample_xlsx):
    df = pd.read_excel(sample_xlsx, sheet_name="SampleInfo", header=0,
                       dtype={"CollectionTime": str},
                       na_values=["", "NA", "null", "None", "999"])
    df.at[1, "CollectionTime"] = "2023098"
    invalid_file = tmp_path / "invalid_collection_time.xlsx"
    with pd.ExcelWriter(invalid_file) as writer:
        df.to_excel(writer, sheet_name="SampleInfo", index=False)
    return invalid_file


@pytest.fixture
def invalid_sample_id_format(tmp_path, sample_xlsx):
    df = pd.read_excel(sample_xlsx, sheet_name="SampleInfo", header=0,
                       dtype={"CollectionTime": str},
                       na_values=["", "NA", "null", "None", "999"])
    df.at[0, "SampleID"] = "1A-1"
    df.at[1, "SampleID"] = "B_2"
    invalid_file = tmp_path / "invalid_sample_id_format.xlsx"
    with pd.ExcelWriter(invalid_file) as writer:
        df.to_excel(writer, sheet_name="SampleInfo", index=False)
    return invalid_file


@pytest.fixture
def duplicate_sample_id(tmp_path, sample_xlsx):
    df = pd.read_excel(sample_xlsx, sheet_name="SampleInfo", header=0,
                       dtype={"CollectionTime": str},
                       na_values=["", "NA", "null", "None", "999"])
    df.at[1, "SampleID"] = "A-1"  # Duplicate SampleID
    df.at[0, "SampleID"] = "A-1"  # Duplicate SampleID
    duplicate_file = tmp_path / "duplicate_sample_id.xlsx"
    with pd.ExcelWriter(duplicate_file) as writer:
        df.to_excel(writer, sheet_name="SampleInfo", index=False)
    return duplicate_file


def test_init_valid_file(sample_xlsx):
    processor = UploadFileProcessor(sample_xlsx)
    assert isinstance(processor.valid_dataframe, pd.DataFrame)
    assert processor.valid_dataframe.shape[0] == 4
    assert isinstance(processor.modified_time, str)
    assert processor.experiment_categories == ["drought"]
    assert processor.experiments == ["drought for 3 weeks", "control"]
    assert processor.collection_parts == ["stem"]
    assert processor.valid_dataframe["CollectionTime"].dtype == "datetime64[ns]"
    assert processor.valid_dataframe["SampleAge"].dtype == "Int64"


def test_file_not_found(tmp_path, caplog):
    with caplog.at_level("ERROR"):
        with pytest.raises(FileNotFoundError):
            UploadFileProcessor(tmp_path / "nonexistent.xlsx")
    assert "uploaded sample sheet does not exist" in caplog.text


def test_invalid_extension(tmp_path):
    fake_file = tmp_path / "file.txt"
    fake_file.write_text("dummy")
    with pytest.raises(ValueError):
        UploadFileProcessor(fake_file)


def test_invalid_collection_time(invalid_collection_time):
    with pytest.raises(RuntimeError):
        UploadFileProcessor(invalid_collection_time)


def test_invalid_sample_id_format(invalid_sample_id_format, caplog):
    with caplog.at_level("ERROR"):
        with pytest.raises(ValueError):
            UploadFileProcessor(invalid_sample_id_format)
    assert "SampleID contains invalid characters: ['1A-1', 'B_2']" in caplog.text


def test_duplicate_sampleid(duplicate_sample_id, caplog):
    with caplog.at_level("ERROR"):
        with pytest.raises(ValueError):
            UploadFileProcessor(duplicate_sample_id)
    assert "SampleID contains duplicate values: ['A-1']" in caplog.text


def test_rawdata_validation(sample_xlsx, rawdata_dir_path):
    processor1 = UploadFileProcessor(sample_xlsx)
    valid, missing = processor1.rawdata_validation(rawdata_dir_path)
    assert valid is True
    assert missing == []


def test_rawdata_missing_file(sample_xlsx, rawdata_dir_path, caplog):
    processor1 = UploadFileProcessor(sample_xlsx)
    processor1.valid_dataframe.at[0, "FileName1"] = "missing_file.fastq"
    processor1.valid_dataframe.at[0, "MD5checksum1"] = "dummy_md5"
    with caplog.at_level("ERROR"):
        processor1.rawdata_validation(rawdata_dir_path)
    assert "Error checking" in caplog.text


def test_rawdata_wrong_md5(sample_xlsx, rawdata_dir_path):
    processor = UploadFileProcessor(sample_xlsx)
    processor.valid_dataframe.at[0, "MD5checksum1"] = "dummy_md5"
    valid, missing = processor.rawdata_validation(rawdata_dir_path)
    assert valid is False
    assert "Atreated-2_1.fq" in missing


def test_database_wrapper(sample_xlsx):
    processor = UploadFileProcessor(sample_xlsx)
    df = processor.database_wrapper()
    assert "UniqueID" in df.columns
    assert "UniqueEXID" in df.columns
    assert df["UniqueID"].str.startswith("LRX").all()
    assert df["UniqueEXID"].str.startswith("TRCRIE").all()
    assert len(df["UniqueID"].unique()) == len(df)


def test_trans_to_smk_samples(sample_xlsx, rawdata_dir_path, tmp_path):
    processor = UploadFileProcessor(sample_xlsx)
    db_df = processor.database_wrapper()
    output_path = tmp_path / "samples.csv"
    smk_df = UploadFileProcessor.trans_to_smk_samples(
        db_df, rawdata_dir_path, to_file=True, output_path=output_path)
    assert "sample" in smk_df.columns
    assert "sample_id" in smk_df.columns
    assert "read1" in smk_df.columns
    assert "read2" in smk_df.columns
    # Check file written
    assert output_path.exists()
    loaded = pd.read_csv(output_path)
    assert loaded.equals(smk_df)
