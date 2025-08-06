import io
from fastapi.testclient import TestClient
import pytest
from backend.main import app
import pandas as pd

test_sample = "tests/upstream/test.xlsx"
rawdata_dir = "tests/upstream/ngs-test-data"


@pytest.fixture
def sample_xlsx():
    with open(test_sample, "rb") as f:
        sample_xlsx = io.BytesIO(f.read())
    return sample_xlsx


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

    return df, invalid_collection_time, invalid_sample_id_format, duplicate_sample_id


def get_token_header():
    with TestClient(app) as client:
        response = client.post(
            "/token",
            data={"username": "admin", "password": "secret"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize(
    "df_key, status, respond_message",
    [
        ("sample_data", True, "success"),
        ("invalid_collection_time", False, "Error parsing file"),
        ("invalid_sample_id_format", False,
         "SampleID contains invalid characters:"),
        ("duplicate_sample_id", False, "SampleID contains duplicate values:"),
    ]
)
def test_upload_sample_sheet(sample_data_validation, df_key, status, respond_message):
    with TestClient(app) as client:
        sample_data, invalid_collection_time, invalid_sample_id_format, duplicate_sample_id = sample_data_validation
        df = {
            "sample_data": sample_data,
            "invalid_collection_time": invalid_collection_time,
            "invalid_sample_id_format": invalid_sample_id_format,
            "duplicate_sample_id": duplicate_sample_id
        }[df_key]
        excel_io = io.BytesIO()
        df.to_excel(excel_io, index=False, sheet_name="SampleInfo")
        excel_io.seek(0)
        response = client.post(
            "/pipeline/sample_sheet/",
            files={"file": ("test.xlsx", excel_io,
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers=get_token_header()
        )
        assert response.status_code == 200
        json_data = response.json()
        assert "success" in json_data
        assert "msg" in json_data

        if status:
            assert json_data["success"] is True
            assert json_data["msg"] == "Sample sheet uploaded successfully."
        else:
            assert json_data["success"] is False
            assert respond_message in json_data["msg"]


# def test_upload_gene_ex_tpm():
#     fake_csv = io.BytesIO(b"gene_id,sample1\nG1,10\nG2,20")
#     response = client.post(
#         "/pipeline/gene_ex_tpm/",
#         files={"file": ("test.csv", fake_csv, "text/csv")},
#         headers=get_token_header()
#     )
#     assert response.status_code == 200
#     assert "success" in response.json()


# def test_upload_gene_ex_counts():
#     fake_csv = io.BytesIO(b"gene_id,sample1\nG1,5\nG2,15")
#     response = client.post(
#         "/pipeline/gene_ex_counts/",
#         files={"file": ("test.csv", fake_csv, "text/csv")},
#         headers=get_token_header()
#     )
#     assert response.status_code == 200
#     assert "success" in response.json()
