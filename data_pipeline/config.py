import os
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

# Explicitly find the .env at the project root (works regardless of cwd)
# override=True ensures .env values win over any stale shell env vars
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_FILE, override=True)

class Config:
    # 📂 1. Directory Paths
    # This automatically finds the root of your project
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = os.path.join(BASE_DIR, "data_pipeline", "collectors")
    
    RAW_DATA_PATH = os.path.join(DATA_DIR, "reddit_data.csv")
    CLEAN_DATA_PATH = os.path.join(DATA_DIR, "reddit_data_cleaned.csv")

    # 🌐 2. Reddit Scraping Settings
    # 🌐 2. Reddit Scraping Settings
    # 🎯 Sentiment-focused subreddits only (reduced to prevent 429 rate-limits).
    # NewsAPI + HackerNews now handle topic discovery; Reddit provides social sentiment signals.
    SUBREDDITS = [
        "worldnews",       # Global events sentiment
        "technology",      # Tech discourse tone
        "AskReddit",       # Broad public opinion
        "science",         # Scientific community sentiment
        "economy",         # Financial sentiment
    ]
    KEYWORDS = []  # Keywords now handled by NewsAPI search, not Reddit

    # Fetch both hot (engagement) and new (recency) posts per subreddit
    REDDIT_SORT_MODES = ["new", "hot"]

    POST_LIMIT = 20       # Posts per subreddit per sort mode (20 hot + 20 new = 40 max, deduped)
    COMMENT_LIMIT = 3     # Fewer comments per post to reduce API calls
    USER_AGENT = "TrendIntelligence/2.0 (personal research bot)"
    
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

    # 🗄️ 3. Database Configurations
    # Postgres (SQL)
    DB_USER = os.getenv("DB_USER", "postgres").strip()
    DB_PASS = os.getenv("DB_PASSWORD", "").strip()
    DB_HOST = os.getenv("DB_HOST", "localhost").strip()
    DB_PORT = os.getenv("DB_PORT", "5432").strip()
    DB_NAME = os.getenv("DB_NAME", "reddit_db").strip()
    
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{urllib.parse.quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"



    # 🕒 4. Scheduler Settings
    RUN_EVERY_HOURS = 1

# Instantiate the config to be used across the app
config = Config()