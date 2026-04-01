import os
import sys
from pathlib import Path

# Add backend directory to sys.path so we can import from app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from sqlalchemy import text
from app.db.connection import engine

def clear_db():
    print("Clearing database...")
    try:
        with engine.connect() as conn:
            # Drop everything in public schema
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            
            # Recreate from schema.sql
            schema_path = Path(__file__).resolve().parent.parent / "database" / "postgres" / "schema.sql"
            with open(schema_path, "r") as f:
                schema_sql = f.read()
                
            conn.execute(text(schema_sql))
            conn.commit()
            
            print("Database cleared and schema recreated successfully.")
            
            # Also recreate SQLAlchemy defined ones
            from app.models.search import Base as SearchBase
            SearchBase.metadata.create_all(bind=engine)
            print("SQLAlchemy tables (searches) recreated.")
            
    except Exception as e:
        print(f"Failed to clear database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    clear_db()
