"""
news_collector.py — Primary Topic Discovery Source (NewsAPI)

Fetches top headlines + topic-specific articles from NewsAPI.
This is the PRIMARY content source for trend detection, providing
fresh, authoritative news articles updated every hour.

Also enriches the query set from user searches stored in the DB,
so user-driven search topics get fresh news coverage too.
"""

import sys
import os
import requests
import pandas as pd
from datetime import datetime

# Add the parent directory to the path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# Default broad topics to search for news coverage
DEFAULT_TOPICS = [
    "technology", "artificial intelligence", "economy", "science",
    "business", "health", "climate", "cybersecurity", "finance", "startups"
]


def _get_user_search_topics() -> list:
    """Fetch recent user searches from the DB to include as news topics."""
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT query FROM searches ORDER BY id DESC LIMIT 10"))
            topics = [row[0] for row in result.fetchall()]
            if topics:
                print(f"[INFO] NewsAPI: Adding {len(topics)} user search topics to news queries.")
            return topics
    except Exception as e:
        print(f"[WARNING] Could not fetch user searches for NewsAPI: {e}")
        return []


def fetch_top_headlines(api_key: str, limit: int = 60) -> list:
    """Fetch current top headlines across all categories."""
    url = "https://newsapi.org/v2/top-headlines"
    params = {"language": "en", "pageSize": min(limit, 100), "apiKey": api_key}
    posts = []

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            print(f"[INFO] NewsAPI Top Headlines: fetched {len(articles)} articles.")
            for idx, item in enumerate(articles):
                post = _article_to_post(item, f"headlines_{idx}")
                if post:
                    posts.append(post)
        elif response.status_code == 401:
            print("[ERROR] NewsAPI: Invalid API key. Check NEWS_API_KEY in .env")
        elif response.status_code == 426:
            print("[WARNING] NewsAPI: Free plan doesn't support this endpoint. Trying /everything...")
        else:
            print(f"[ERROR] NewsAPI headlines returned {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"[ERROR] NewsAPI headlines fetch failed: {e}")

    return posts


def fetch_topic_news(api_key: str, topic: str, limit: int = 15) -> list:
    """Fetch news articles for a specific topic using /everything endpoint."""
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "language": "en",
        "sortBy": "publishedAt",   # Always get freshest articles
        "pageSize": min(limit, 100),
        "apiKey": api_key
    }
    posts = []

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            for idx, item in enumerate(articles):
                post = _article_to_post(item, f"{topic}_{idx}")
                if post:
                    posts.append(post)
        else:
            print(f"[WARNING] NewsAPI /everything for '{topic}' returned {response.status_code}")
    except Exception as e:
        print(f"[ERROR] NewsAPI /everything for '{topic}' failed: {e}")

    return posts


def _article_to_post(item: dict, id_suffix: str) -> dict | None:
    """Convert a NewsAPI article dict to the standard post dict format."""
    title = item.get("title", "")
    url = item.get("url", "")

    # Skip removed/placeholder articles
    if not title or not url:
        return None
    if "[Removed]" in title or title.strip() == "":
        return None

    # Build content text from available fields
    content_parts = []
    if item.get("description"):
        content_parts.append(item["description"])
    if item.get("content"):
        # NewsAPI truncates content at 200 chars with "[+N chars]" - clean that up
        raw_content = item["content"]
        raw_content = raw_content.split("[+")[0].strip()
        if raw_content:
            content_parts.append(raw_content)

    published_at = item.get("publishedAt", "")
    try:
        dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        dt = datetime.now()

    source_name = item.get("source", {}).get("name", "NewsAPI")
    # Create a stable post_id from URL hash
    post_id = f"news_{abs(hash(url)) % 10**10}"

    return {
        "post_id":      post_id,
        "title":        title,
        "text":         " | ".join(content_parts) if content_parts else title,
        "comments":     "",
        "score":        0,          # NewsAPI has no upvote signal
        "subreddit":    source_name,
        "datetime_utc": dt,
    }


def fetch_global_news(limit: int = 80) -> list:
    """
    Main entry point for the NewsAPI collector.
    Fetches top headlines + topic-specific articles + user-search topics.
    Returns a deduplicated list of post dicts.
    """
    api_key = config.NEWS_API_KEY
    if not api_key or api_key in ("", "your_news_api_key_here"):
        print("[WARNING] NEWS_API_KEY is missing or invalid. Skipping NewsAPI.")
        return []

    all_posts = {}  # Deduplicate by post_id

    # 1. Top Headlines (broad freshness)
    headlines = fetch_top_headlines(api_key, limit=60)
    for p in headlines:
        all_posts[p["post_id"]] = p

    # 2. Default topic searches
    topics = DEFAULT_TOPICS[:]

    # 3. Enrich with user search topics
    user_topics = _get_user_search_topics()
    topics.extend(user_topics)

    for topic in topics:
        articles = fetch_topic_news(api_key, topic, limit=10)
        for p in articles:
            all_posts[p["post_id"]] = p

    result = list(all_posts.values())
    print(f"[INFO] NewsAPI total unique articles: {len(result)}")
    return result


if __name__ == "__main__":
    print("[INFO] Starting News API Collector...")
    data = fetch_global_news()

    if data:
        df = pd.DataFrame(data)
        print(f"[SUCCESS] Fetched {len(df)} News API articles.")

        # Load directly to Postgres via DataLoader
        loader_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'loaders')
        sys.path.append(os.path.abspath(loader_path))
        try:
            from db_loader import DataLoader
            loader = DataLoader()
            # Rename to match db_loader's expected schema
            load_df = df.rename(columns={"text": "content", "score": "ups"})
            loader.load_to_postgres(load_df, "reddit_trends")
        except ImportError:
            print("[ERROR] Could not import DataLoader. Saving to CSV instead.")
            df.to_csv("news_data.csv", index=False)
    else:
        print("[WARNING] No data collected from NewsAPI.")
