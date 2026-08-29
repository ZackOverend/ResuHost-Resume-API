import pytest
from pydantic import ValidationError

from app.schemas import ExperienceCreate, TailorRequest, UserCreate


def test_collection_defaults_are_independent():
    first = ExperienceCreate(company="Acme", role="Engineer")
    second = ExperienceCreate(company="Beta", role="Engineer")

    first.bullets.append("Built a service")

    assert second.bullets == []


def test_required_text_is_trimmed():
    user = UserCreate(name="  Zack  ", email="zack@example.com")

    assert user.name == "Zack"


@pytest.mark.parametrize("length", [0, 49, 50_001])
def test_job_description_length_is_bounded(length):
    with pytest.raises(ValidationError):
        TailorRequest(job_description="x" * length)


def test_tailor_request_does_not_accept_provider_credentials():
    with pytest.raises(ValidationError):
        TailorRequest(
            job_description="x" * 50,
            host="http://attacker.invalid",
            api_key="not-allowed",
        )
