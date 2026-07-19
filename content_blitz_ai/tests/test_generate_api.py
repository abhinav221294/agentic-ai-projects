import uuid


def register_login(client):

    payload = {
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"{uuid.uuid4().hex[:8]}@gmail.com",
        "password": "Password123"
    }

    client.post(
        "/auth/register",
        json=payload,
    )

    response = client.post(
        "/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"]
        },
    )

    return response.json()["access_token"]


def test_generate_requires_auth(api_client):

    response = api_client.post(
        "/generate",
        json={
            "query": "Hello",
            "conversation_id": 1
        },
    )

    assert response.status_code == 401


def test_generate_invalid_token(api_client):

    response = api_client.post(
        "/generate",
        headers={
            "Authorization": "Bearer invalid"
        },
        json={
            "query": "Hello",
            "conversation_id": 1
        },
    )

    assert response.status_code == 401