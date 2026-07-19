import uuid

def test_register_user(api_client):

    payload = {
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"{uuid.uuid4().hex[:8]}@gmail.com",
        "password": "Password123"
    }

    response = api_client.post(
        "/auth/register",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]


def test_duplicate_email(api_client):

    payload = {
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": "duplicate@gmail.com",
        "password": "Password123"
    }

    api_client.post(
        "/auth/register",
        json=payload,
    )

    payload["username"] = "another_user"

    response = api_client.post(
        "/auth/register",
        json=payload,
    )

    assert response.status_code == 400


def test_login_success(api_client):

    payload = {
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"{uuid.uuid4().hex[:8]}@gmail.com",
        "password": "Password123"
    }

    api_client.post(
        "/auth/register",
        json=payload,
    )

    response = api_client.post(
        "/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"]
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(api_client):

    payload = {
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"{uuid.uuid4().hex[:8]}@gmail.com",
        "password": "Password123"
    }

    api_client.post(
        "/auth/register",
        json=payload,
    )

    response = api_client.post(
        "/auth/login",
        json={
            "email": payload["email"],
            "password": "WrongPassword"
        },
    )

    assert response.status_code == 401