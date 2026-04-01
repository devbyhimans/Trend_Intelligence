# Database Reference — Trend Intelligence System

A complete reference for every database, table, column, and Redis key used in this project.

---

## Overview — Databases in Use

| # | Database | Type | Port | Docker Container | Purpose |
|---|---|---|---|---|---|
| 1 | `reddit_db` | PostgreSQL 15 | `5433` (host) → `5432` (container) | `trend_postgres` | Primary persistent store — all structured data |
| 2 | Redis | Redis 7 Alpine | `6379` | `trend_redis` | Job queue + API response cache |

> MongoDB was **permanently removed** from this architecture. PostgreSQL handles all structured persistence.

---

## 1. 🐘 PostgreSQL — `reddit_db`

**Connection string (from `.env`):**
```
postgresql://postgres:<DB_PASSWORD>@localhost:5433/reddit_db
```

**SQLAlchemy URI (built in `data_pipeline/config.py`):**
```python
SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```

**Schema file:** [`database/postgres/schema.sql`](database/postgres/schema.sql)

PostgreSQL contains **3 tables:**

---

### Table 1 — `reddit_trends`

**Role:** The ML engine's unified input feed. Stores cleaned posts and articles from all three data sources: Reddit (sentiment signals), NewsAPI (topic discovery), and HackerNews (tech discourse).

**Written by:**
- `data_pipeline/loaders/db_loader.py` → Reddit CSV path (via `DataLoader.load_to_postgres()`)
- `data_pipeline/collectors/news_collector.py` → NewsAPI articles (direct, no CSV step)
- `data_pipeline/collectors/hacker_news_collector.py` → HN stories (direct, no CSV step)

**Read by:** `ml_engine/pipelines/ml_runner.py` → `fetch_latest_posts()` (latest 500 rows)
**Auto-pruned:** Every ML run deletes rows where `processed_at < NOW() - INTERVAL '24 hours'`

| Column | Type | Constraint | Description |
|---|---|---|---|
| `id` | `SERIAL` | `PRIMARY KEY` | Auto-incrementing internal row ID |
| `post_id` | `VARCHAR(50)` | `UNIQUE` | Reddit's native post ID (e.g. `t3_abc123`). Prevents duplicate ingestion. |
| `title` | `TEXT` | `NOT NULL` | NLP-cleaned post title |
| `content` | `TEXT` | — | NLP-cleaned post body / selftext |
| `ups` | `INTEGER` | — | Reddit upvote count at time of scrape |
| `num_comments` | `INTEGER` | — | Number of top-level comments extracted |
| `subreddit` | `VARCHAR(100)` | — | Source identifier. For Reddit: subreddit name (e.g. `technology`). For NewsAPI: publisher name (e.g. `BBC News`). For HackerNews: `HackerNews`. |
| `created_utc` | `TIMESTAMP` | — | Original Reddit post creation time (UTC) |
| `sentiment_score` | `FLOAT` | `DEFAULT 0.0` | Reserved — not actively populated by current pipeline |
| `processed_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Timestamp of last upsert by `db_loader.py`. Used for 24h pruning and ML batch ordering. |

**Upsert logic (ON CONFLICT):**
```sql
ON CONFLICT (post_id) DO UPDATE SET
    ups           = EXCLUDED.ups,
    num_comments  = EXCLUDED.num_comments,
    content       = EXCLUDED.content,
    processed_at  = CURRENT_TIMESTAMP;
```

---

### Table 2 — `ml_trend_results`

**Role:** The ML engine's output store. Each row is one topic cluster produced by a pipeline run. This is the primary source for the Global Trends and India Trends pages.

**Written by:**
- `ml_engine/pipelines/ml_runner.py` → `save_results()` — real batch runs (many rows, shared `run_at`)
- `backend/worker.py` → `run_search_ml_pipeline()` — live search stubs (1 row per search, unique `run_at`)

**Read by:**
- `backend/app/services/trend_service.py` → Global Trends page
- `backend/app/services/region_service.py` → India Trends page
- `backend/app/services/search_service.py` → ML score lookup for search queries

**Auto-pruned:** Every ML run deletes rows where `run_at < NOW() - INTERVAL '24 hours'`

**Batch detection rule:** The services distinguish real batch runs from live-search stubs by querying only `run_at` timestamps that have **≥ 3 rows** (`HAVING COUNT(*) >= 3`).

| Column | Type | Constraint | Description |
|---|---|---|---|
| `id` | `SERIAL` | `PRIMARY KEY` | Auto-incrementing internal row ID |
| `topic_id` | `INTEGER` | `NOT NULL` | KMeans / AgglomerativeClustering label assigned to this cluster |
| `keywords` | `TEXT` | — | Top-5 TF-IDF keywords for this cluster (comma-separated string) |
| `volume` | `INTEGER` | — | Number of Reddit posts assigned to this cluster |
| `velocity` | `FLOAT` | — | Volume growth rate: `current_volume − previous_volume` |
| `acceleration` | `FLOAT` | — | Change in velocity: `current_velocity − previous_velocity` |
| `sentiment` | `FLOAT` | — | Average VADER compound score across cluster posts (range: −1.0 → +1.0) |
| `sentiment_label` | `VARCHAR(20)` | — | Majority sentiment: `positive`, `neutral`, or `negative` |
| `positive_pct` | `FLOAT` | `DEFAULT 0` | % of posts in cluster with positive VADER score |
| `negative_pct` | `FLOAT` | `DEFAULT 0` | % of posts in cluster with negative VADER score |
| `neutral_pct` | `FLOAT` | `DEFAULT 0` | % of posts in cluster with neutral VADER score |
| `top_posts` | `TEXT` | — | Top 3 post titles by upvotes within this cluster (pipe `\|\|` separated, max 120 chars each) |
| `subreddits` | `TEXT` | — | Comma-separated list of unique subreddits contributing to this cluster. Used by `region_service.py` for India state filtering via `ILIKE`. |
| `avg_ups` | `FLOAT` | `DEFAULT 0` | Average upvote count across all posts in this cluster |
| `avg_comments` | `FLOAT` | `DEFAULT 0` | Average comment count across all posts in this cluster |
| `score` | `FLOAT` | — | **Composite trend score** (displayed on frontend): `0.35×Volume + 0.30×Velocity + 0.20×Acceleration + 0.15×Sentiment` |
| `run_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Batch run timestamp. All clusters from one real pipeline run share the **same** `run_at`. Used to group and retrieve the latest batch. |

---

### Table 3 — `searches`

**Role:** Audit log of every query a user has submitted through the Search page. Not used for trend calculations — purely a history record.

**Written by:** `backend/app/services/search_service.py` → `search_logic()` — one row per user search  
**Read by:** `backend/app/services/search_service.py` → `get_all_searches()`, `get_search_by_id()`  
**ORM Model:** `backend/app/models/search.py`

| Column | Type | Constraint | Description |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY` | Auto-incrementing internal row ID |
| `query` | `STRING` | — | The exact search term the user entered |
| `trend_score` | `INTEGER` | — | The trend score calculated and returned for this query |
| `region` | `STRING` | — | Always `"Global"` in the current implementation |

> **Note:** This table is never pruned. It grows indefinitely as users submit searches.

---

## 2. 🟠 Redis — Cache & Queue

**Connection:** `localhost:6379`, DB index `0`  
**No password** in local development  

Redis does not use tables. It uses **keys** with different data types:

---

### Structure 1 — `search_queue` (List)

**Type:** Redis List  
**Purpose:** Job queue between the FastAPI backend and the background `worker.py` daemon.

| Operation | Who does it | Command | When |
|---|---|---|---|
| Enqueue job | `search_service.py` | `LPUSH search_queue <query>` | When a user searches and the ML DB score returns 0 (cache miss) |
| Dequeue job | `worker.py` | `BRPOP search_queue timeout=0` | Continuously — blocks until a job appears |

**Flow:**
```
User searches "AI" → search_service LPUSH "AI" → worker BRPOP → process → write to ml_trend_results
```

---

### Structure 2 — Cache Keys (Strings)

**Type:** Redis String  
**Purpose:** Short-lived API response cache to avoid repeated PostgreSQL hits for identical search queries.

| Operation | Command | TTL |
|---|---|---|
| Cache write | `SETEX <key> <ttl> <value>` | Set by service |
| Cache read | `GET <key>` | — |

> In the current implementation, the `searches` table in PostgreSQL serves as the primary record. Redis cache is a performance layer — if Redis is empty or restarted, the system falls back to PostgreSQL automatically.

---

## Data Lifecycle Summary

```
Reddit Posts (sentiment signals, 5 subreddits, hot+new)
    ↓  [Phase 1 — reddit_collector → raw_to_clean → db_loader]
NewsAPI Articles (primary topics, headlines + keyword search)
    ↓  [Phase 2 — news_collector → direct to DB]
HackerNews Stories (tech discourse, top + new)
    ↓  [Phase 3 — hacker_news_collector → direct to DB]
reddit_trends          ← Unified ML input feed (all sources, 24h TTL)
    ↓  [Phase 4 — ml_runner.py, reads latest 500 rows]
ml_trend_results       ← ML output (trend clusters, 24h TTL)
    ↓  [FastAPI services]
Frontend               ← Global Trends, India Trends, Search pages

User searches
    ↓  [search_service.py]
searches               ← Permanent audit log (no pruning)
search_queue (Redis)   ← Triggers worker.py for deep ML processing
                           (worker uses NewsAPI + HN Algolia, not Reddit)
```

---

## Environment Variables (`.env`)

```env
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=127.0.0.1
DB_PORT=5433
DB_NAME=reddit_db

# External APIs
NEWS_API_KEY=your_newsapi_key_here
```

> **Port note:** Docker maps the container's internal `5432` to host port `5433`. Use `5433` when connecting from DB GUIs (DBeaver, pgAdmin). The backend code connects via this port as configured in `.env`.

> **Reddit credentials:** No OAuth credentials are required. The pipeline uses Reddit's public JSON API with a reduced 5-subreddit set and exponential backoff. Reddit is used for sentiment signals only, not as the primary data source.
