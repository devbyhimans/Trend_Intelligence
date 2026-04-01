"""
cron_jobs.py — Master Pipeline Scheduler

Runs the full ETL + ML pipeline on a schedule.

Data Collection Strategy (Hybrid):
  1. Reddit (sentiment signals)   → CSV → clean → load to DB
  2. NewsAPI (primary topics)     → direct to DB
  3. HackerNews (tech discourse)  → direct to DB
  4. ML Engine Analysis           → reads all from DB → writes trend results

This hybrid approach ensures:
  - Fresh, authoritative content from NewsAPI (sortBy=publishedAt)
  - Tech community discourse from HackerNews (no rate limits)
  - Social/informal sentiment tone from Reddit (reduced subreddit set)
"""

import schedule
import sys
import time
import subprocess
import os
from datetime import datetime

# Paths to pipeline scripts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLLECTOR      = os.path.join(BASE_DIR, "collectors", "reddit_collector.py")
NEWS_COLLECTOR = os.path.join(BASE_DIR, "collectors", "news_collector.py")
HN_COLLECTOR   = os.path.join(BASE_DIR, "collectors", "hacker_news_collector.py")
PROCESSOR      = os.path.join(BASE_DIR, "processors", "raw_to_clean.py")
LOADER         = os.path.join(BASE_DIR, "loaders", "db_loader.py")

PROJECT_ROOT = os.path.dirname(BASE_DIR)
ML_RUNNER    = os.path.join(PROJECT_ROOT, "ml_engine", "pipelines", "ml_runner.py")


def run_task(script_path, task_name):
    """Execute a Python script as a subprocess and log the result."""
    print(f"\n--- [START] {task_name} at {datetime.now().strftime('%H:%M:%S')} ---")
    try:
        result = subprocess.run([sys.executable, script_path], check=True)
        print(f"[SUCCESS] {task_name} finished.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {task_name} failed: {e}")
        return False


def full_pipeline_job():
    """
    Master pipeline sequence:
      Phase 1 — Reddit (sentiment signals, CSV path)
      Phase 2 — NewsAPI (topic discovery, direct to DB)
      Phase 3 — HackerNews (tech discourse, direct to DB)
      Phase 4 — ML Engine Analysis (reads all sources from DB)
    """
    print(f"\n{'='*60}")
    print(f"  SCHEDULED RUN STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    # ── Phase 1: Reddit Sentiment Signals (CSV pipeline) ──────────────
    print("\n📡 PHASE 1: Reddit Sentiment Signals")
    reddit_ok = run_task(COLLECTOR, "Reddit Collector (sentiment, 5 subreddits, hot+new)")
    if reddit_ok:
        clean_ok = run_task(PROCESSOR, "Data Cleaning (CSV)")
        if clean_ok:
            run_task(LOADER, "Database Loading (Reddit CSV → Postgres)")

    # ── Phase 2: NewsAPI Topic Discovery (direct to DB) ───────────────
    print("\n📰 PHASE 2: NewsAPI Topic Discovery")
    run_task(NEWS_COLLECTOR, "NewsAPI Collector (headlines + topics)")

    # ── Phase 3: HackerNews Tech Discourse (direct to DB) ─────────────
    print("\n🔥 PHASE 3: HackerNews Tech Discourse")
    run_task(HN_COLLECTOR, "HackerNews Collector (top + new stories)")

    # ── Phase 4: ML Engine (runs on all sources combined) ─────────────
    print("\n🧠 PHASE 4: ML Engine Analysis")
    run_task(ML_RUNNER, "ML Engine Analysis (NLP + Clustering + Sentiment)")

    print(f"\n{'='*60}")
    print(f"  PIPELINE RUN FINISHED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")


# ── Schedule ──────────────────────────────────────────────────────────
schedule.every(1).hours.do(full_pipeline_job)

if __name__ == "__main__":
    print("=" * 60)
    print("  🚀 Trend Intelligence Scheduler Active")
    print("  Sources: Reddit (sentiment) + NewsAPI + HackerNews")
    print("  Frequency: Every 1 hour")
    print("  Press Ctrl+C to stop.")
    print("=" * 60)

    # Run immediately on startup
    full_pipeline_job()

    while True:
        schedule.run_pending()
        time.sleep(60)