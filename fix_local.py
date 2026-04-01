import nltk
from backend.app.db.connection import engine
from sqlalchemy import text

print("Downloading local NLTK datasets...")
nltk.download('vader_lexicon')

print("Syncing database schema (creating ml_trend_results)...")
with engine.begin() as conn:
    with open('database/postgres/schema.sql', 'r') as f:
        sql = f.read()
        conn.execute(text(sql))

print("Local fixes completed successfully! Your Uvicorn server should now work perfectly.")
