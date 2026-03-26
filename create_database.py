from sqlalchemy import inspect
import app.models  # noqa: F401 — registers all models with Base.metadata
from app.database import engine, Base

def create_tables():
    print("🔄 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        tables = inspect(engine).get_table_names()
        print(f"✅ Tables created: {', '.join(tables)}")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_tables()
