# medico/backend/tests/test_dashboard.py
import pytest
from unittest.mock import patch, AsyncMock

pytestmark = pytest.mark.asyncio

# ==============================================================================
# Case 18: GET /dashboard | Secure Metrics Count Check | Expect 200 OK + Data
# ==============================================================================

async def test_get_dashboard_metrics_successfully(client, db_session, auth_headers, patient_payload):
    # Step 1: Create a mock patient profile first to populate our counts row
    patient_res = await client.post("/patients/", json=patient_payload, headers=auth_headers)
    assert patient_res.status_code == 201

    # Step 2: Hit your dashboard endpoint with your active doctor token
    # (Note: Check if your dashboard route uses a trailing slash or not!)
    response = await client.get("/dashboard", headers=auth_headers)
    
    # Step 3: Assertions
    assert response.status_code == 200
    data = response.json()
    
    # Senior check: Verify key analytics categories exist inside your system data
    assert "total_patients" in data
    assert "total_records" in data
    
    # Step 4: Verify the count accurately registers our created patient row
    assert data["total_patients"] >= 1


async def test_anonymous_user_cannot_access_dashboard(client):
    # Action: Try to pull metrics without passing our doctor auth_headers dictionary
    response = await client.get("/dashboard")
    
    # Assertion: Secure dashboard blocks unauthenticated requests instantly
    assert response.status_code == 401
