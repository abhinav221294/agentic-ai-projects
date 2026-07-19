import uuid


def get_token(client):

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


def test_create_conversation(api_client):

    token = get_token(api_client)

    response = api_client.post(
        "/conversation",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200


def test_create_conversation_without_token(api_client):

    response = api_client.post("/conversation")

    assert response.status_code == 401


def test_invalid_token(api_client):

    response = api_client.post(
        "/conversation",
        headers={
            "Authorization": "Bearer abcdef"
        },
    )

    assert response.status_code == 401