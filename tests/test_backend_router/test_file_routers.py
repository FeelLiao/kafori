import io
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def get_token_header():
    # 用测试账号 admin/your_password 获取 token
    response = client.post(
        "/token",
        data={"username": "admin", "password": "secret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_sample_sheet():
    # 构造一个假的xlsx文件内容
    fake_xlsx = io.BytesIO(b"PK\x03\x04fake_xlsx_content")
    response = client.post(
        "/pipeline/sample_sheet/",
        files={"file": ("test.xlsx", fake_xlsx,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers=get_token_header()
    )
    assert response.status_code == 200
    assert "success" in response.json()


def test_upload_gene_ex_tpm():
    fake_csv = io.BytesIO(b"gene_id,sample1\nG1,10\nG2,20")
    response = client.post(
        "/pipeline/gene_ex_tpm/",
        files={"file": ("test.csv", fake_csv, "text/csv")},
        headers=get_token_header()
    )
    assert response.status_code == 200
    assert "success" in response.json()


def test_upload_gene_ex_counts():
    fake_csv = io.BytesIO(b"gene_id,sample1\nG1,5\nG2,15")
    response = client.post(
        "/pipeline/gene_ex_counts/",
        files={"file": ("test.csv", fake_csv, "text/csv")},
        headers=get_token_header()
    )
    assert response.status_code == 200
    assert "success" in response.json()
