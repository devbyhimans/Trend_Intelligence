"""
reddit_collector.py — Social Sentiment Signal Collector

Fetches posts from a small, curated set of subreddits to provide
social/informal sentiment signals to the ML pipeline.

NewsAPI and HackerNews are the primary topic-discovery sources.
Reddit provides the human-tone sentiment balance.

Key improvements over v1:
  - Dual feed: fetches both /new and /hot per subreddit and deduplicates by post_id
  - Exponential backoff with 3 retries before skipping a source
  - Adaptive inter-source delay to stay within unauthenticated rate limits
  - Proper User-Agent string for Reddit compliance
"""

import requests
import pandas as pd
from datetime import datetime
import time
import random
import os
import sys

# Add the parent directory to the path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

HEADERS = {
    "User-Agent": config.USER_AGENT
}

session = requests.Session()
session.headers.update(HEADERS)

# Track rate-limit hits across the session to adaptively slow down
_rate_limit_hits = 0


def _backoff_sleep(attempt: int):
    """Exponential backoff: 15s, 30s, 60s for attempts 1, 2, 3."""
    wait = 15 * (2 ** attempt) + random.uniform(0, 3)
    print(f"  [BACKOFF] Waiting {wait:.0f}s before retry {attempt + 1}/3...")
    time.sleep(wait)


def _inter_source_delay():
    """
    Adaptive delay between subreddit fetches.
    Increases if we've been hitting rate limits this session.
    """
    global _rate_limit_hits
    base = 3.0
    extra = min(_rate_limit_hits * 4, 30)  # Cap extra at 30s
    delay = base + extra + random.uniform(0, 2)
    time.sleep(delay)


def fetch_comments(subreddit, post_id):
    """Fetch top-level comments for a post. Returns joined string or empty."""
    url = (
        f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
        f"?limit={config.COMMENT_LIMIT}&depth=1"
    )
    try:
        response = session.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1:
                comment_data = data[1]['data']['children']
                comments = [
                    c['data'].get('body', '')
                    for c in comment_data if c['kind'] == 't1'
                ]
                return " | ".join(comments) if comments else ""
    except Exception:
        pass
    return ""


def fetch_subreddit_feed(subreddit: str, sort: str, limit: int) -> list:
    """
    Fetch up to `limit` posts from a single subreddit feed (hot or new).
    Implements exponential backoff with 3 retries on 429.
    Returns a list of post dicts.
    """
    global _rate_limit_hits
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
    params = {"limit": limit}
    posts = []

    for attempt in range(3):  # Up to 3 retry attempts
        try:
            response = session.get(url, params=params, timeout=10)

            if response.status_code == 429:
                _rate_limit_hits += 1
                print(f"  [429] Rate limit on r/{subreddit} ({sort}). Hit #{_rate_limit_hits} this session.")
                if attempt < 2:
                    _backoff_sleep(attempt)
                    continue
                else:
                    print(f"  [SKIP] r/{subreddit} ({sort}) skipped after 3 failed attempts.")
                    return []

            if response.status_code != 200:
                print(f"  [ERROR] r/{subreddit} ({sort}) returned HTTP {response.status_code}. Skipping.")
                return []

            data = response.json().get('data', {})
            children = data.get('children', [])

            for post in children:
                p = post['data']
                title = p.get("title", "").lower()

                # Filter out meta/discussion threads
                if any(noise in title for noise in [
                    "megathread", "discussion thread", "daily thread",
                    "weekly thread", "monthly thread", "mod post"
                ]):
                    continue

                posts.append({
                    "post_id":      p.get("id"),
                    "title":        p.get("title", ""),
                    "text":         p.get("selftext", ""),
                    "comments":     "",  # Filled in below selectively
                    "score":        p.get("score", 0),
                    "subreddit":    p.get("subreddit", subreddit),
                    "datetime_utc": datetime.fromtimestamp(p.get("created_utc", 0)),
                    "_feed_type":   sort,  # Track which feed sourced this post
                })

            # Success — break out of retry loop
            break

        except Exception as e:
            print(f"  [ERROR] Exception fetching r/{subreddit} ({sort}): {e}")
            if attempt < 2:
                _backoff_sleep(attempt)
            else:
                return []

    return posts


def fetch_reddit_data(subreddit: str) -> list:
    """
    Fetch posts from both /hot and /new feeds for a subreddit.
    Deduplicates by post_id so overlapping posts are not double-counted.
    Fetches comments for the top 10 unique posts to save API calls.
    """
    limit = config.POST_LIMIT
    sort_modes = getattr(config, 'REDDIT_SORT_MODES', ['hot', 'new'])

    all_posts_by_id = {}

    for sort in sort_modes:
        print(f"  📡 Fetching r/{subreddit} [{sort}] ...")
        feed_posts = fetch_subreddit_feed(subreddit, sort, limit)
        for post in feed_posts:
            pid = post["post_id"]
            if pid and pid not in all_posts_by_id:
                all_posts_by_id[pid] = post
        # Small pause between sort modes for the same subreddit
        time.sleep(2)

    unique_posts = list(all_posts_by_id.values())
    print(f"  ✅ r/{subreddit}: {len(unique_posts)} unique posts (hot+new deduped)")

    # Fetch comments for top 10 posts only (by score) to conserve API quota
    unique_posts.sort(key=lambda x: x.get("score", 0), reverse=True)
    for i, post in enumerate(unique_posts[:10]):
        comments = fetch_comments(post["subreddit"], post["post_id"])
        unique_posts[i]["comments"] = comments
        time.sleep(0.5)

    return unique_posts


def build_dataset():
    """
    Main entry point: collect sentiment-signal posts from curated subreddits.
    Saves to CSV for the cleaning pipeline.
    """
    global _rate_limit_hits
    _rate_limit_hits = 0  # Reset for this session

    subreddits = config.SUBREDDITS
    final_list = []
    seen_ids = set()

    print(f"[INFO] Reddit Sentiment Collector starting ({len(subreddits)} subreddits)...")
    print(f"[INFO] Strategy: hot+new dual feed, {config.POST_LIMIT} posts each, deduped by post_id")

    for i, sub in enumerate(subreddits):
        print(f"\n[{i+1}/{len(subreddits)}] Processing r/{sub}...")
        posts = fetch_reddit_data(sub)

        for post in posts:
            pid = post.get("post_id")
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                final_list.append(post)

        # Adaptive delay between subreddits
        if i < len(subreddits) - 1:
            _inter_source_delay()

    # Remove internal tracking column before saving
    for post in final_list:
        post.pop("_feed_type", None)

    if final_list:
        df = pd.DataFrame(final_list)
        save_path = config.RAW_DATA_PATH
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path, index=False)
        print(f"\n[SUCCESS] Reddit Sentiment Collector done! Saved {len(df)} posts to {save_path}")
        print(f"[INFO] Total 429 rate-limit hits this session: {_rate_limit_hits}")
    else:
        print("\n[WARNING] No Reddit data collected. NewsAPI+HackerNews will still run.")


if __name__ == "__main__":
    build_dataset()