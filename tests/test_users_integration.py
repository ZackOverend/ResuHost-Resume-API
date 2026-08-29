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

    profile = client.get(f"/v1/users/{user_id}/profile", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["contact"]["email"] == email
    assert profile.json()["experiences"] == []
    assert len(profile.json()["profile_version"]) == 64

    updated = client.patch(
        f"/v1/users/{user_id}/profile",
        headers=headers,
        json={"phone": "555-0100"},
    )
    assert updated.status_code == 200
    assert updated.json()["contact"]["phone"] == "555-0100"
    assert updated.json()["profile_version"] != profile.json()["profile_version"]

    verified_contact = client.post(
        f"/v1/users/{user_id}/profile/verify",
        headers=headers,
    )
    assert verified_contact.status_code == 200
    assert verified_contact.json()["contact"]["verified_at"] is not None

    experience = client.post(
        f"/v1/users/{user_id}/experiences",
        headers=headers,
        json={
            "company": "Acme",
            "role": "Engineer",
            "start_date": "2025-01",
            "is_current": True,
        },
    )
    assert experience.status_code == 201
    experience_id = experience.json()["id"]

    patched_experience = client.patch(
        f"/v1/users/{user_id}/experiences/{experience_id}",
        headers=headers,
        json={"role": "Senior Engineer"},
    )
    assert patched_experience.status_code == 200
    assert patched_experience.json()["role"] == "Senior Engineer"

    verified_experience = client.post(
        f"/v1/users/{user_id}/experiences/{experience_id}/verify",
        headers=headers,
    )
    assert verified_experience.status_code == 200
    assert verified_experience.json()["verified_at"] is not None

    reordered = client.post(
        f"/v1/users/{user_id}/experiences/reorder",
        headers=headers,
        json={"ids": [experience_id]},
    )
    assert reordered.status_code == 200

    archived = client.post(
        f"/v1/users/{user_id}/experiences/{experience_id}/archive",
        headers=headers,
    )
    assert archived.status_code == 200
    assert archived.json()["is_archived"] is True

    restored = client.post(
        f"/v1/users/{user_id}/experiences/{experience_id}/restore",
        headers=headers,
    )
    assert restored.status_code == 200
    assert restored.json()["is_archived"] is False

    education = client.post(
        f"/v1/users/{user_id}/education",
        headers=headers,
        json={
            "institution": "Example University",
            "degree": "BSc",
            "start_date": "2021-09",
            "end_date": "2025-05",
        },
    )
    assert education.status_code == 201
    education_id = education.json()["id"]

    patched_education = client.patch(
        f"/v1/users/{user_id}/education/{education_id}",
        headers=headers,
        json={"degree": "BSc Computer Science"},
    )
    assert patched_education.status_code == 200
    assert patched_education.json()["degree"] == "BSc Computer Science"

    archived_education = client.post(
        f"/v1/users/{user_id}/education/{education_id}/archive",
        headers=headers,
    )
    assert archived_education.status_code == 200
    assert archived_education.json()["is_archived"] is True
