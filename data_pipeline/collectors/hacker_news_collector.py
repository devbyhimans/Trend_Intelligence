"""
hacker_news_collector.py — Tech Trend Signal Source (Hacker News)

Fetches top and newest stories from Hacker News (official Firebase API).
No authentication required. No rate limits. Always fresh.

HN provides high-quality tech/startup discourse signals that complement
NewsAPI's broad news coverage with deeper technical community sentiment.
"""

import sys
import os
import requests
import pandas as pd
from datetime import datetime
import time

# Add the parent directory to the path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

HN_BASE = "https://hacker-news.firebaseio.com/v0"


def _fetch_story(sid: int, session: requests.Session) -> dict | None:
    """Fetch a single HackerNews story item by ID. Returns None if invalid."""
    try:
        resp = session.get(f"{HN_BASE}/item/{sid}.json", timeout=5)
        if resp.status_code == 200:
            item = resp.json()
            if (
                item
                and item.get("type") == "story"
                and not item.get("deleted")
                and not item.get("dead")
                and item.get("title")
            ):
                return item
    except Exception:
        pass
    return None


def fetch_hacker_news(limit: int = 60) -> list:
    """
    Fetch top + newest stories from Hacker News.
    Deduplicates by story ID and returns at most `limit` unique posts.
    """
    session = requests.Session()
    session.headers.update({"User-Agent": "TrendIntelligence/2.0"})

    # Fetch both top stories (engagement) and new stories (recency)
    story_ids = set()
    posts = []

    feeds = {
        "topstories": limit,
        "newstories": limit // 2,  # Fewer new ones as they have less context
    }

    for feed_name, feed_limit in feeds.items():
        try:
            resp = session.get(f"{HN_BASE}/{feed_name}.json", timeout=10)
            if resp.status_code == 200:
                ids = resp.json()[:feed_limit * 2]  # Fetch extra to compensate for filtered-out items
                print(f"[INFO] HackerNews: Fetching {feed_limit} from {feed_name}...")

                fetched = 0
                for sid in ids:
                    if sid in story_ids:
                        continue
                    if fetched >= feed_limit:
                        break

                    item = _fetch_story(sid, session)
                    if item:
                        story_ids.add(sid)
                        fetched += 1

                        content_parts = []
                        if item.get("text"):
                            content_parts.append(item["text"])
                        if item.get("url"):
                            content_parts.append(f"Link: {item['url']}")

                        posts.append({
                            "post_id":      f"hn_{sid}",
                            "title":        item.get("title", ""),
                            "text":         " | ".join(content_parts) if content_parts else "",
                            "comments":     "",
                            "score":        item.get("score", 0),
                            "subreddit":    "HackerNews",
                            "datetime_utc": datetime.fromtimestamp(item.get("time", 0)),
                        })

                    # Small delay to be respectful to Firebase API
                    time.sleep(0.1)

        except Exception as e:
            print(f"[ERROR] HackerNews {feed_name} failed: {e}")

    print(f"[INFO] HackerNews: {len(posts)} unique stories fetched (top+new deduped).")
    return posts


if __name__ == "__main__":
    print("[INFO] Starting Hacker News Collector...")
    data = fetch_hacker_news(config.POST_LIMIT)

    if data:
        df = pd.DataFrame(data)
        print(f"[SUCCESS] Fetched {len(df)} HackerNews stories.")

        # Load directly to Postgres via DataLoader
        loader_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'loaders')
        sys.path.append(os.path.abspath(loader_path))
        try:
            from db_loader import DataLoader
            loader = DataLoader()
            load_df = df.rename(columns={
                "text": "content", 
                "score": "ups",
                "datetime_utc": "created_utc"
            })
            load_df["num_comments"] = 0
            loader.load_to_postgres(load_df, "reddit_trends")
        except ImportError:
            print("[ERROR] Could not import DataLoader. Saving to CSV instead.")
            df.to_csv("hn_data.csv", index=False)
    else:
        print("[WARNING] No data collected from HackerNews.")
