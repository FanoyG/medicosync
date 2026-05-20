# medico/backend/tests/test_patients.py
import pytest
from app.models.patient import Patient
pytestmark = pytest.mark.asyncio


async def test_doctor_create_patient_successfully(client, db_session, auth_headers, patient_payload):
    response = await client.post(
        "/patients/",  
        json=patient_payload,
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["first_name"] == "John"

async def test_anonymous_user_cannot_create_patient(client, patient_payload):
    response = await client.post("/patients/", json=patient_payload)
    assert response.status_code == 401


async def test_duplicate_patient_exist(client, db_session, auth_headers, patient_payload):
    first_response = await client.post(
        "/patients/",
        json=patient_payload,
        headers=auth_headers
    )
    assert first_response.status_code == 201

    second_response = await client.post(
        "/patients/",
        json=patient_payload,
        headers=auth_headers
    )

    assert second_response.status_code == 400    


async def test_get_patients_list_returns_only_doctors_patients(client, db_session, auth_headers, patient_payload):
    response_one = await client.post("/patients/", json=patient_payload, headers=auth_headers)
    assert response_one.status_code == 201
    patient_one_id = response_one.json()["id"]

    # 🛠️ FIXED TRAP 1: Clean dictionary copy to prevent data overlap bugs
    patient_payload_two = patient_payload.copy()
    patient_payload_two["first_name"] = "Jane"
    
    response_two = await client.post("/patients/", json=patient_payload_two, headers=auth_headers)
    assert response_two.status_code == 201
    patient_two_id = response_two.json()["id"]

    get_response = await client.get("/patients/", headers=auth_headers)
    
    assert get_response.status_code == 200
    data = get_response.json()
    
    assert isinstance(data, list)
    assert len(data) == 2

    returned_ids = [patient["id"] for patient in data]
    assert patient_one_id in returned_ids
    assert patient_two_id in returned_ids


async def test_patients_valid_id(client, db_session, auth_headers, patient_payload):
    create_response = await client.post("/patients/", json=patient_payload, headers=auth_headers)
    assert create_response.status_code == 201

    patient_id = create_response.json()["id"]

    response = await client.get(
        f"/patients/{patient_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == patient_id
    assert data["first_name"] == "John"

async def test_doctor_cannot_access_other_dr_patient(client, db_session, auth_headers, patient_payload):
     # 1. Create a patient under DOCTOR A (using your global auth_headers)
    create_response = await client.post(
        "/patients/",
        json=patient_payload,
        headers=auth_headers
    )
    assert create_response.status_code == 201
    doctor_a_patient_id = create_response.json()["id"]

     # 2. Register DOCTOR B manually
    doctor_b_payload = {
        "email": "doctor_b@clinic.com",
        "password": "securepassword456",
        "full_name": "Dr. Bruce Banner",
        "specialty": "Radiology"
    }

    doctor_b = await client.post(
        "auth/register",
        json=doctor_b_payload,
    )
    assert doctor_b.status_code == 201

    doctor_b_login_payload = {
        "email" : doctor_b_payload["email"],
        "password" : doctor_b_payload["password"]  
    }
    login_b = await client.post(
        "auth/login",
        json=doctor_b_login_payload
    )

    assert login_b.status_code == 200
    token_b = login_b.json()["access_token"]
    doctor_b_header = {
        "Authorziation" : f"Bearer {token_b}"
    }

    response = await client.get(
        f"/patinets/{doctor_a_patient_id}",
        headers=doctor_b_header
    )

    assert response.status_code == 404

async def test_delete_patients(client, db_session, patient_payload, auth_headers):
    create_response = await client.post(
        "/patients/",
        json=patient_payload,
        headers=auth_headers
    )

    assert create_response.status_code == 201
    patient_id = create_response.json()["id"]

    response = await client.delete(
        f"/patients/{patient_id}",
        headers=auth_headers
    )

    assert response.status_code == 204

async def test_anonymous_user_cannot_delete_patient(client, patient_payload, auth_headers):
    create_response = await client.post(
        "/patients/",
        json=patient_payload,
        headers=auth_headers
    )

    assert create_response.status_code == 201
    patient_id = create_response.json()["id"]

    response = await client.delete(
        f"/patients/{patient_id}",
    )
    assert response.status_code == 401
