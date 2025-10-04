import io
from fastapi.testclient import TestClient
import pytest
from backend.main import app
import pandas as pd

from backend.api.files import GeneDataType

test_sample = "tests/upstream/test.xlsx"
test_tpm = "tests/upstream/samples_merged_tpm.csv"
test_counts = "tests/upstream/samples_merged_counts.csv"
rawdata_dir = "tests/upstream/ngs-test-data"


@pytest.fixture
def sample_xlsx():
    with open(test_sample, "rb") as f:
        sample_xlsx = io.BytesIO(f.read())
    return sample_xlsx


@pytest.fixture
def gene_tpm():
    return pd.read_csv(test_tpm)


@pytest.fixture
def gene_counts():
    return pd.read_csv(test_counts)


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
    # 调用实际登录接口：/user/login
    with TestClient(app) as c:
        resp = c.post("/user/login", json={"username": "admin", "password": "secret"})
    assert resp.status_code == 200
    body = resp.json()
    # 期望结构: {"code":0,"message":"...","data":"Bearer <jwt>"}
    assert body.get("code") == 0, f"login failed: {body}"
    token = body["data"]
    # token 已包含 'Bearer ' 前缀，直接返回
    return {"Authorization": token}


def assert_result(resp, expect_ok: bool, expected_message_sub: str):
    assert resp.status_code == 200
    body = resp.json()
    assert "code" in body and "message" in body and "data" in body
    if expect_ok:
        assert body["code"] == 0
        assert body["message"] == expected_message_sub  # 精确匹配成功消息
    else:
        assert body["code"] == 1
        assert expected_message_sub in body["message"]


@pytest.mark.parametrize(
    "df_key, status, respond_message",
    [
        ("sample_data", True, "Sample sheet uploaded successfully."),
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
        resp = client.post(
            "/pipeline/sample_sheet/",
            files={"file": ("test.xlsx", excel_io,
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers=get_token_header()
        )
        assert_result(resp, status, respond_message)


def test_upload_gene_tpm(gene_tpm):
    with TestClient(app) as client:
        csv_io = io.BytesIO()
        gene_tpm.to_csv(csv_io, index=False)

        resp = client.post(
            "/pipeline/gene_ex_tpm/",
            files={"file": ("test.csv", csv_io,
                            "text/csv")},
            headers=get_token_header()
        )
        assert resp.json()["code"] == 0


def test_upload_gene_counts(gene_counts):
    with TestClient(app) as client:
        csv_io = io.BytesIO()
        gene_counts.to_csv(csv_io, index=False)

        resp = client.post(
            "/pipeline/gene_ex_counts/",
            files={"file": ("test.csv", csv_io,
                            "text/csv")},
            headers=get_token_header()
        )
        assert resp.json()["code"] == 0


def test_put_database():
    with TestClient(app) as client:

        resp = client.post(
            "/pipeline/put_database/",
            headers=get_token_header()
        )
        assert resp.json()["code"] == 1
