import pytest
import pandas as pd
from backend.api.utils import UploadFileProcessor


@pytest.fixture
def valid_xlsx(tmp_path):
    # Create a valid DataFrame
    df = pd.DataFrame({
        "SampleID": ["A001", "B002"],
        "CollectionTime": ["2024/01/01", "2024/01/02"],
        "SampleAge": [10, 20]
    })
    file_path = tmp_path / "valid.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, sheet_name="SampleInfo", index=False)
    return file_path


@pytest.fixture
def invalid_sampleid_xlsx(tmp_path):
    df = pd.DataFrame({
        # First SampleID does not start with a letter
        "SampleID": ["001A", "B002"],
        "CollectionTime": ["2024/01/01", "2024/01/02"],
        "SampleAge": [10, 20]
    })
    file_path = tmp_path / "invalid_sampleid.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, sheet_name="SampleInfo", index=False)
    return file_path


@pytest.fixture
def wrong_extension_file(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("Not an xlsx file")
    return file_path


def test_valid_file_processing(valid_xlsx):
    processor = UploadFileProcessor(valid_xlsx)
    df = processor.valid_dataframe
    assert isinstance(df, pd.DataFrame)
    assert list(df["SampleID"]) == ["A001", "B002"]
    assert pd.api.types.is_datetime64_any_dtype(df["CollectionTime"])
    assert pd.api.types.is_integer_dtype(df["SampleAge"])


def test_unique_sample_ids(valid_xlsx):
    processor = UploadFileProcessor(valid_xlsx)
    df = processor.unique_sample_ids()
    assert "UniqueID" in df.columns
    # Check that UniqueID is a 32-character hex string
    assert all(df["UniqueID"].str.match(r"^[a-f0-9]{32}$"))


def test_file_not_found(tmp_path):
    missing_file = tmp_path / "missing.xlsx"
    with pytest.raises(FileNotFoundError):
        UploadFileProcessor(missing_file)


def test_wrong_extension(wrong_extension_file):
    with pytest.raises(ValueError, match="File must be an xlsx file."):
        UploadFileProcessor(wrong_extension_file)


def test_invalid_sampleid(invalid_sampleid_xlsx):
    with pytest.raises(ValueError,
                       match="SampleID contains invalid characters"):
        UploadFileProcessor(invalid_sampleid_xlsx)


def test_invalid_sheet_name(tmp_path):
    # Create xlsx with wrong sheet name
    df = pd.DataFrame({
        "SampleID": ["A001"],
        "CollectionTime": ["2024/01/01"],
        "SampleAge": [10]
    })
    file_path = tmp_path / "wrong_sheet.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, sheet_name="WrongSheet", index=False)
    with pytest.raises(RuntimeError):
        UploadFileProcessor(file_path)

        def test_trans_to_smk_samples_basic(tmp_path):
            # Prepare a minimal DataFrame
            df = pd.DataFrame({
                "FileName1": ["A001_R1.fastq", "B002_R1.fastq"],
                "FileName2": ["A001_R2.fastq", "B002_R2.fastq"],
                "UniqueID": ["LRX123abc001", "LRX123abc002"]
            })
            rawdata_path = tmp_path
            # Create dummy files
            for fname in df["FileName1"].tolist() + df["FileName2"].tolist():
                (rawdata_path / fname).write_text("dummy")
            result = UploadFileProcessor.trans_to_smk_samples(df, rawdata_path)
            assert list(result["sample"]) == ["A001", "B002"]
            assert list(result["sample_id"]) == [
                "LRX123abc001", "LRX123abc002"]
            assert all(rawdata_path.name in p for p in result["read1"])
            assert all(rawdata_path.name in p for p in result["read2"])

        def test_trans_to_smk_samples_to_file(tmp_path):
            df = pd.DataFrame({
                "FileName1": ["C003_R1.fastq"],
                "FileName2": ["C003_R2.fastq"],
                "UniqueID": ["LRX123abc003"]
            })
            rawdata_path = tmp_path
            for fname in df["FileName1"].tolist() + df["FileName2"].tolist():
                (rawdata_path / fname).write_text("dummy")
            output_path = tmp_path / "samples.csv"
            result = UploadFileProcessor.trans_to_smk_samples(
                df, rawdata_path, to_file=True, output_path=output_path
            )
            assert output_path.exists()
            loaded = pd.read_csv(output_path)
            assert list(loaded["sample"]) == ["C003"]
            assert list(loaded["sample_id"]) == ["LRX123abc003"]

        def test_trans_to_smk_samples_handles_missing_columns():
            df = pd.DataFrame({
                "FileName1": ["D004_R1.fastq"],
                "UniqueID": ["LRX123abc004"]
                # Missing FileName2
            })
            rawdata_path = Path("/tmp")
            try:
                UploadFileProcessor.trans_to_smk_samples(df, rawdata_path)
            except KeyError as e:
                assert "FileName2" in str(e)
