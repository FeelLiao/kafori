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
