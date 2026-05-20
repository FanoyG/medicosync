import pytest
from unittest.mock import patch
from app.models.user import User

# Apply asyncio marker to all tests in this file
pytestmark = pytest.mark.asyncio

# Explicitly scope your mock data or turn it into a fixture
@pytest.fixture
def auth_payload():
    return {
        "email": "doctorbishu@gmail.com",
        "password": "bishu#123",
        "full_name": "Bishu Arpit",
        "specialty": "Surgen"
    }

# 1. This test stays clean and checks normal registration
async def test_register_valid_data(client, db_session, auth_payload):
    response = await client.post(
        "/auth/register",
        json=auth_payload
    )

    assert response.status_code == 201
    data = response.json()

    expected_fields = ["id", "email", "full_name"]
    for field in expected_fields:
        assert field in data
    
    assert "password" not in data
    assert "hashed_password" not in data


# 2. This test checks your database unique constraint
async def test_register_duplicate_emial(client, db_session, auth_payload):
    existing_user = User(
        email=auth_payload["email"],
        hashed_password="fake_passsword_for_test_pass@!23",
        full_name="Abhishek",
        specialty="Ortho"
    )
    db_session.add(existing_user)
    await db_session.flush()
    
    response = await client.post(
        "/auth/register",
        json=auth_payload
    )

    assert response.status_code == 409


# 3. PLACED CORRECTLY HERE: Decorator sits right above the function that uses it
@pytest.mark.parametrize(
    "invalid_email",
    [
        "nobishu5455.abc",         # Missing @ symbol entirely
        "bhishu@",                 # Missing domain entirely
        "@hospital.com",           # Missing username entirely
        "bhishu@noextension",      # Missing dot extension entirely
        "bhishu @ hospital.com",   # Contains spaces
        "",                        # Completely empty string
    ]
)
async def test_register_invalid_email(client, db_session, auth_payload, invalid_email):
    auth_payload["email"] = invalid_email

    response = await client.post(
        "/auth/register",
        json=auth_payload
    )

    assert response.status_code == 422

async def test_login_successfull(client, db_session, auth_payload):
    register_response = await client.post(
        "/auth/register",
        json=auth_payload
    )

    assert register_response.status_code == 201

    login_payload = {
        "email" : auth_payload["email"],
        "password" : auth_payload["password"]
    }

    login_response = await client.post(
        "/auth/login",
        json=login_payload
    )

    assert login_response.status_code == 200
    data = login_response.json()

    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"].lower() == "bearer"


async def test_login_wrong_password(client, db_session, auth_payload):
    await client.post("/auth/register", json=auth_payload)

    login_payload = {
        "email" : auth_payload["email"],
        "password" : "my_fake_password_to_test_123444"
    }

    response = await client.post("/auth/login", json=login_payload)

    assert response.status_code == 401

async def test_login_email_not_found(client, db_session):
    unregistered_user = {
        "email" : "pappu@123.abc",
        "password" : "pappu098099"
    }

    response = await client.post("/auth/login", json=unregistered_user)

    assert response.status_code == 401
    