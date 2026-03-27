import json
import sys

import app.models  # noqa: F401
from app.database import Base, SessionLocal, engine
from app.models import Activity, Education, Experience, Project, SkillCategory, User


def seed(path: str):
    with open(path) as f:
        users = json.load(f)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        for data in users:
            user = User(
                name=data["name"],
                email=data["email"],
                phone=data.get("phone"),
                linkedin=data.get("linkedin"),
                website=data.get("website"),
            )
            db.add(user)
            db.flush()

            for e in data.get("education", []):
                db.add(Education(
                    user_id=user.id,
                    institution=e["institution"],
                    degree=e.get("degree"),
                    location=e.get("location"),
                    start_date=e.get("start_date"),
                    end_date=e.get("end_date"),
                    notes=e.get("notes"),
                ))

            for e in data.get("experiences", []):
                db.add(Experience(
                    user_id=user.id,
                    company=e["company"],
                    role=e["role"],
                    location=e.get("location"),
                    start_date=e.get("start_date"),
                    end_date=e.get("end_date"),
                    bullets=e.get("bullets"),
                ))

            for p in data.get("projects", []):
                db.add(Project(
                    user_id=user.id,
                    name=p["name"],
                    subtitle=p.get("subtitle"),
                    start_date=p.get("start_date"),
                    end_date=p.get("end_date"),
                    bullets=p.get("bullets"),
                ))

            for a in data.get("activities", []):
                db.add(Activity(
                    user_id=user.id,
                    role=a["role"],
                    organization=a["organization"],
                    start_date=a.get("start_date"),
                    end_date=a.get("end_date"),
                    bullets=a.get("bullets"),
                ))

            for s in data.get("skill_categories", []):
                db.add(SkillCategory(
                    user_id=user.id,
                    name=s["name"],
                    skills=s.get("skills"),
                ))

            print(f"✅ Seeded user: {user.name}")

        db.commit()
        print("✅ Done.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "seed_data.json"
    seed(path)
