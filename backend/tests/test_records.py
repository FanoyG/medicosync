import pytest
from io import BytesIO
from unittest.mock import patch, AsyncMock

pytestmark = pytest.mark.asyncio


@pytest.fixture
def record_payload():
    return {
        "title": "Knee Joint Scan",
        "record_type": "xray"
    }


# ==============================================================================
# TEST 1: LIVE INTEGRATION (Talks to your running MinIO engine on port 9000)
# ==============================================================================
async def test_valid_file_upload_live_minio(client, db_session, auth_headers, patient_payload, record_payload):
    # 1. Register a real patient profile via API
    patient_response = await client.post("/patients/", json=patient_payload, headers=auth_headers)
    assert patient_response.status_code == 201
    patient_id = patient_response.json()["id"]
    record_payload["patient_id"] = patient_id

    # 2. Build a stream layout simulating an active upload
    fake_file = BytesIO(b"dummy binary data representing my live file content test")
    files_payload = {
        "file": ("xray_scan.png", fake_file, "image/png")
    }

    # 3. Action: Hit your endpoint directly to process live aiobotocore updates
    response = await client.post(
        "/records/",
        data=record_payload,
        files=files_payload,
        headers=auth_headers
    )

    # 4. Assertions: Verifies everything saves and links cleanly to local MinIO
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["record_type"] == "xray"
    assert "localhost:9000" in data["download_url"]  # Asserts it processed on your live port!

