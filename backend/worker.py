"""
worker.py — Background ML Worker Daemon

Listens to a Redis queue for on-demand user search queries.
When a query arrives:
  1. Fetches live news articles for that query via NewsAPI /everything
  2. Falls back to HackerNews search if NewsAPI fails
  3. Runs the full ML pipeline (NLP, clustering, sentiment)
  4. Saves results to ml_trend_results (tagged as LIVE_SEARCH)

This keeps the frontend responsive: heavy ML work is done here,
not in the FastAPI request cycle.
"""

import os
import sys
import datetime
import redis
import time
import requests

# Fix path to load modules correctly when run from backend root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.db.connection import SessionLocal
from backend.app.models.ml_trend_result import MLTrendResult
from ml_engine.pipelines.trend_pipeline import TrendPipeline

# Load env config for NewsAPI key
from data_pipeline.config import config


def fetch_newsapi_posts(query: str, limit: int = 60) -> list:
    """
    Fetch live news articles for a query via NewsAPI /everything.
    Returns a list of (text, metadata) tuples.
    """
    api_key = config.NEWS_API_KEY
    if not api_key or api_key in ("", "your_news_api_key_here"):
        print(f"[{datetime.datetime.now()}] ⚠️ No NewsAPI key. Skipping NewsAPI for search.")
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": min(limit, 100),
        "apiKey": api_key,
    }

    posts = []
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            print(f"[{datetime.datetime.now()}] 📰 NewsAPI: {len(articles)} articles for '{query}'")
            for item in articles:
                title = item.get("title", "")
                desc = item.get("description", "")
                content = item.get("content", "").split("[+")[0].strip()
                source = item.get("source", {}).get("name", "NewsAPI")

                combined = f"{title}. {desc}. {content}".strip()
                if combined and combined != ".":
                    posts.append({
                        "text": combined,
                        "meta": {
                            "title": title,
                            "subreddit": f"LIVE_SEARCH|{source}",
                            "ups": 0,
                            "num_comments": 0,
                        }
                    })
        else:
            print(f"[{datetime.datetime.now()}] ❌ NewsAPI returned {response.status_code} for '{query}'")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] ❌ NewsAPI fetch error for '{query}': {e}")

    return posts


def fetch_hackernews_posts(query: str, limit: int = 20) -> list:
    """
    Fallback: search HackerNews for relevant stories via Algolia API.
    HN has a free search API at hn.algolia.com with no rate limits.
    """
    url = "https://hn.algolia.com/api/v1/search"
    params = {"query": query, "tags": "story", "hitsPerPage": limit}
    posts = []

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            hits = response.json().get("hits", [])
            print(f"[{datetime.datetime.now()}] 🔥 HackerNews: {len(hits)} stories for '{query}' (fallback)")
            for hit in hits:
                title = hit.get("title", "")
                story_text = hit.get("story_text", "") or ""
                url_text = hit.get("url", "")
                points = hit.get("points", 0) or 0
                num_comments = hit.get("num_comments", 0) or 0

                combined = f"{title}. {story_text}".strip()
                if combined and combined != ".":
                    posts.append({
                        "text": combined,
                        "meta": {
                            "title": title,
                            "subreddit": "LIVE_SEARCH|HackerNews",
                            "ups": points,
                            "num_comments": num_comments,
                        }
                    })
    except Exception as e:
        print(f"[{datetime.datetime.now()}] ❌ HackerNews fallback error for '{query}': {e}")

    return posts


def run_search_ml_pipeline(query: str):
    """
    Background worker job: perform deep ML analysis on a user's live search.
    Uses NewsAPI as primary source, HackerNews as fallback.
    """
    print(f"\n[{datetime.datetime.now()}] 🛠️ WORKER: Starting ML for query: '{query}'")

    # 1. Fetch live data
    posts = fetch_newsapi_posts(query)

    if len(posts) < 5:
        # Supplement or replace with HackerNews if NewsAPI gave too little
        hn_posts = fetch_hackernews_posts(query)
        posts.extend(hn_posts)

    if not posts:
        print(f"[{datetime.datetime.now()}] ❌ No data found for '{query}'. Aborting ML.")
        return

    print(f"[{datetime.datetime.now()}] 🧠 Running ML on {len(posts)} articles for '{query}'...")

    raw_texts = [p["text"] for p in posts]
    metadata  = [p["meta"] for p in posts]

    # 2. Run ML pipeline
    pipeline = TrendPipeline()
    results = pipeline.run(raw_texts, metadata=metadata)

    if not results:
        print(f"[{datetime.datetime.now()}] ⚠️ No significant clusters for '{query}'.")
        return

    print(f"[{datetime.datetime.now()}] 📊 Produced {len(results)} clusters for '{query}'.")

    # 3. Persist to DB
    db = SessionLocal()
    try:
        run_timestamp = datetime.datetime.now(datetime.timezone.utc)

        for res in results:
            new_ml_trend = MLTrendResult(
                run_at=run_timestamp,
                topic_id=int(res["topic_id"]),
                volume=int(res.get("volume", 0)),
                velocity=float(res.get("velocity", 0.0)),
                acceleration=float(res.get("acceleration", 0.0)),
                sentiment=float(res.get("sentiment", 0.0)),
                sentiment_label=str(res.get("sentiment_label", "neutral")),
                positive_pct=float(res.get("positive_pct", 0)),
                negative_pct=float(res.get("negative_pct", 0)),
                neutral_pct=float(res.get("neutral_pct", 0)),
                top_posts=str(res.get("top_posts", "")),
                subreddits=str(res.get("subreddits", "LIVE_SEARCH")),
                avg_ups=float(res.get("avg_ups", 0)),
                avg_comments=float(res.get("avg_comments", 0)),
                keywords=str(", ".join(res.get("keywords", []))),
                score=float(res.get("score", 0.0))
            )
            db.add(new_ml_trend)

        db.commit()
        print(f"[{datetime.datetime.now()}] ✅ Worker done. {len(results)} clusters persisted.")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] ❌ Worker DB error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    print("=" * 55)
    print("🔥 Trend Intelligence Background Worker Active 🔥")
    print("  Sources: NewsAPI (primary) + HackerNews (fallback)")
    print("  Queue: Redis 'search_queue' (localhost:6379)")
    print("  Waiting for user search jobs...")
    print("=" * 55)

    while True:
        try:
            result = redis_conn.brpop("search_queue", timeout=0)
            if result:
                _, query = result
                run_search_ml_pipeline(query)
        except Exception as e:
            print(f"[{datetime.datetime.now()}] ❌ Worker loop error: {e}")
            time.sleep(5)
