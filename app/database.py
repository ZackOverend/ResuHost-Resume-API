from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

def resolve_database_url() -> str:
    """Pick Postgres URL from env. See .env.example for DATABASE_TARGET and URL vars."""
    target = (os.getenv("DATABASE_TARGET") or "auto").strip().lower()
    if target in ("", "auto"):
        url = os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError(
                "DATABASE_URL is not set. Set DATABASE_URL for default/auto mode, or set "
                "DATABASE_TARGET=local with LOCAL_DATABASE_URL, or DATABASE_TARGET=supabase "
                "with SUPABASE_DATABASE_URL."
            )
        return url
    if target == "local":
        url = os.getenv("LOCAL_DATABASE_URL")
        if not url:
            raise RuntimeError(
                "DATABASE_TARGET=local but LOCAL_DATABASE_URL is not set."
            )
        return url
    if target == "supabase":
        url = os.getenv("SUPABASE_DATABASE_URL")
        if not url:
            raise RuntimeError(
                "DATABASE_TARGET=supabase but SUPABASE_DATABASE_URL is not set."
            )
        return url
    raise RuntimeError(
        f"Invalid DATABASE_TARGET={target!r}. Use 'local', 'supabase', or 'auto'."
    )


DATABASE_URL = resolve_database_url()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()