import uuid

import pytest


pytestmark = pytest.mark.integration


def test_create_and_get_user(client, db_session):
    headers = {"X-API-Key": "test-secret"}
    email = f"{uuid.uuid4()}@example.com"

    created = client.post(
        "/users/",
        headers=headers,
        json={"name": "Test User", "email": email},
    )

    assert created.status_code == 200
    user_id = created.json()["id"]

    fetched = client.get(f"/users/{user_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["email"] == email
    assert fetched.json()["experiences"] == []
