from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    print("🔄 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        
        # List the tables that were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Tables: {', '.join(tables)}")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    return True

if __name__ == "__main__":
    create_tables()