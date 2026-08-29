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


def test_experience_dates_use_month_precision():
    experience = ExperienceCreate(
        company="Acme",
        role="Engineer",
        start_date="2026-01",
        is_current=True,
    )

    assert experience.start_date == "2026-01"
    assert experience.end_date is None


@pytest.mark.parametrize("end_date", ["2025", "2025-13", "January 2025"])
def test_experience_rejects_invalid_month_dates(end_date):
    with pytest.raises(ValidationError):
        ExperienceCreate(company="Acme", role="Engineer", end_date=end_date)


def test_current_experience_rejects_end_date():
    with pytest.raises(ValidationError):
        ExperienceCreate(
            company="Acme",
            role="Engineer",
            start_date="2025-01",
            end_date="2026-01",
            is_current=True,
        )


def test_experience_rejects_reversed_date_range():
    with pytest.raises(ValidationError):
        ExperienceCreate(
            company="Acme",
            role="Engineer",
            start_date="2026-01",
            end_date="2025-01",
        )
