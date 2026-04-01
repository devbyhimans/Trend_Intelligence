# Trend Intelligence System — ML Engine Pipeline

> The ML Engine is **source-agnostic** — it processes text regardless of whether it came from Reddit, NewsAPI, or HackerNews. All three sources feed the same `reddit_trends` table which the pipeline reads from.

```mermaid
flowchart TD

classDef process    fill:#3b82f6,stroke:#1d4ed8,color:#fff;
classDef model      fill:#8b5cf6,stroke:#4c1d95,color:#fff;
classDef data       fill:#f59e0b,stroke:#b45309,color:#000;
classDef math       fill:#10b981,stroke:#065f46,color:#fff;
classDef source     fill:#6b7280,stroke:#374151,color:#fff;

REDDIT["📡 Reddit\n(5 subreddits, sentiment)"]:::source
NEWS["📰 NewsAPI\n(headlines + topics)"]:::source
HN["🔥 HackerNews\n(top + new stories)"]:::source

REDDIT & NEWS & HN -->|"Unified in reddit_trends\n(latest 500 rows)"| RAW

RAW["📝 Raw Texts\nTitles & Content\n(all 3 sources combined)"]:::data
META["📊 Metadata\nUpvotes, Source Names, Dates"]:::data

RAW --> PREPROC["🧹 PreprocessingPipeline\nRegex: Remove URLs, Emojis, Special Chars"]:::process

PREPROC --> VADER["😊 SentimentInference (NLTK)\nVADER Lexicon\nLabels: Pos/Neu/Neg & Score (-1 to 1)\nNote: Social tone (Reddit) balances formal\nnewspaper tone (NewsAPI) in aggregate"]:::model
VADER --> AGG

META --> AGG["Data Assembly\nper-cluster aggregation"]:::process

PREPROC --> EMBED["🧠 EmbeddingModel\n`sentence-transformers/all-MiniLM-L6-v2`\nTransforms text into 384-dimensional vectors"]:::model
EMBED --> CLUSTER["🧩 ClusterModel\nKMeans / AgglomerativeClustering\nGroups similar vectors semantically\nMin 3 posts to form valid cluster"]:::model
CLUSTER --> AGG

PREPROC --> TFIDF["🏷️ TopicLabeler (scikit-learn)\nTF-IDF Vectorizer\nFinds top 5 keywords per Cluster"]:::model
TFIDF --> AGG

AGG --> SCORE["📈 TrendScorer\nAggregates Meta/NLP per Topic ID\nvolume · sentiment · subreddits\ntop-3 posts by upvotes · avg_ups · avg_comments"]:::math
SCORE -->|"Current vs Previous Counts"| VEL["🚀 VelocityCalculator\ncurrent_volume − previous_volume"]:::math
SCORE -->|"Current vs Previous Velocity"| ACC["⚡ AccelerationCalculator\ncurrent_velocity − previous_velocity"]:::math

VEL & ACC --> FINAL_FORMULA["📊 Final Composite Score Formula:
(0.35 × Volume) + (0.30 × Velocity) +
(0.20 × Acceleration) + (0.15 × Sentiment)"]:::math

FINAL_FORMULA --> OUTPUT["🏆 Top 20 Ranked Trends\nStructured JSON payload arrays\nWritten to ml_trend_results"]:::data
```

## Score Formula Explanation

| Component | Weight | Source Signal |
|-----------|--------|--------------|
| **Volume** | 35% | Number of posts/articles in this cluster |
| **Velocity** | 30% | How fast this topic is growing vs last run |
| **Acceleration** | 20% | Whether growth is speeding up or slowing down |
| **Sentiment** | 15% | Average VADER compound score (−1 to +1) |

> **Sentiment note:** Reddit provides the informal social sentiment tone; NewsAPI and HackerNews contribute more neutral/formal language. The aggregate VADER score across all three sources gives a balanced sentiment picture.
