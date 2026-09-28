import uuid

import pytest
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from app import models, schemas
from app.api import tailoring_runs


pytestmark = pytest.mark.integration

HEADERS = {"X-API-Key": "test-secret"}
FIRST = "Reduced processing time by 30%."
SECOND = "Maintained the billing service."


def fake_agent(proposals):
    def build(settings, model_name):
        return Agent(
            TestModel(custom_output_args={"suggestions": proposals}),
            output_type=schemas.TailoringProposals,
        )

    return build


@pytest.fixture
def profile(client, db_session):
    user = client.post(
        "/users/",
        headers=HEADERS,
        json={"name": "Ada Lovelace", "email": f"{uuid.uuid4()}@example.com"},
    )
    user_id = user.json()["id"]
    experience = client.post(
        f"/v1/users/{user_id}/experiences",
        headers=HEADERS,
        json={
            "company": "Acme",
            "role": "Engineer",
            "start_date": "2025-01",
            "is_current": True,
            "bullets": [FIRST, SECOND],
        },
    )
    assert experience.status_code == 201
    return user_id, experience.json()["id"]


def create_run(client, monkeypatch, user_id, proposals):
    monkeypatch.setattr(tailoring_runs, "build_tailoring_agent", fake_agent(proposals))
    return client.post(
        f"/v1/users/{user_id}/tailoring-runs",
        headers=HEADERS,
        json={"job_description": "Seeking an engineer who improves performance."},
    )


def test_tailoring_lifecycle_never_changes_the_master_profile(
    client, db_session, monkeypatch, profile
):
    user_id, experience_id = profile
    run = create_run(
        client,
        monkeypatch,
        user_id,
        [
            {"bullet_ref": "b1", "proposed_text": "Cut processing time by 30%.", "reason": "Direct."},
            {"bullet_ref": "b2", "proposed_text": "Owned the billing service.", "reason": "Ownership."},
            {"bullet_ref": "b2", "proposed_text": "Ran billing on Kubernetes.", "reason": "Keyword."},
            {"bullet_ref": "b7", "proposed_text": "Invented.", "reason": "Unknown ref."},
        ],
    )

    assert run.status_code == 201
    body = run.json()
    assert body["status"] == "completed"
    suggestions = body["suggestions"]
    assert [suggestion["verification"]["status"] for suggestion in suggestions] == [
        "pass",
        "pass",
        "fail",
    ]
    assert {suggestion["entry_id"] for suggestion in suggestions} == {experience_id}

    failing = client.post(
        f"/v1/tailoring-runs/{body['id']}/variants",
        headers=HEADERS,
        json={
            "label": "Rejected attempt",
            "decisions": [{"suggestion_id": suggestions[2]["id"], "action": "accept"}],
        },
    )
    assert failing.status_code == 422

    variant = client.post(
        f"/v1/tailoring-runs/{body['id']}/variants",
        headers=HEADERS,
        json={
            "label": "Performance role",
            "decisions": [
                {"suggestion_id": suggestions[0]["id"], "action": "accept"},
                {
                    "suggestion_id": suggestions[1]["id"],
                    "action": "edit",
                    "edited_text": "Owned and maintained the billing service.",
                },
                {"suggestion_id": suggestions[2]["id"], "action": "reject"},
            ],
        },
    )
    assert variant.status_code == 201
    variant_body = variant.json()
    assert variant_body["status"] == "draft"
    assert variant_body["profile_version"] == body["profile_version"]
    bullets = [
        bullet["text"]
        for bullet in variant_body["document"]["sections"][0]["entries"][0]["bullets"]
    ]
    assert bullets == ["Cut processing time by 30%.", "Owned and maintained the billing service."]

    approved = client.post(f"/v1/resume-variants/{variant_body['id']}/approve", headers=HEADERS)
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert approved.json()["approved_at"]

    pdf = client.get(f"/v1/resume-variants/{variant_body['id']}/pdf", headers=HEADERS)
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")

    master = client.get(f"/v1/users/{user_id}/profile", headers=HEADERS).json()
    assert master["experiences"][0]["bullets"] == [FIRST, SECOND]
    assert master["profile_version"] == body["profile_version"]


def test_variant_creation_fails_after_profile_changes(client, db_session, monkeypatch, profile):
    user_id, experience_id = profile
    run = create_run(
        client,
        monkeypatch,
        user_id,
        [{"bullet_ref": "b1", "proposed_text": "Cut processing time by 30%.", "reason": "Direct."}],
    ).json()

    client.patch(
        f"/v1/users/{user_id}/experiences/{experience_id}",
        headers=HEADERS,
        json={"bullets": ["Reduced processing time by 40%.", SECOND]},
    )
    variant = client.post(
        f"/v1/tailoring-runs/{run['id']}/variants",
        headers=HEADERS,
        json={
            "label": "Stale",
            "decisions": [{"suggestion_id": run["suggestions"][0]["id"], "action": "accept"}],
        },
    )

    assert variant.status_code == 409


def test_failed_model_call_records_a_failed_run(client, db_session, monkeypatch, profile):
    user_id, _ = profile

    def broken(settings, model_name):
        raise_agent = Agent(TestModel(), output_type=schemas.TailoringProposals)

        async def run(prompt):
            raise RuntimeError("provider down")

        raise_agent.run = run
        return raise_agent

    monkeypatch.setattr(tailoring_runs, "build_tailoring_agent", broken)
    response = client.post(
        f"/v1/users/{user_id}/tailoring-runs",
        headers=HEADERS,
        json={"job_description": "Anything."},
    )

    assert response.status_code == 502
    run = db_session.query(models.TailoringRun).filter_by(user_id=uuid.UUID(user_id)).one()
    assert run.status == "failed"
    assert run.error_message
