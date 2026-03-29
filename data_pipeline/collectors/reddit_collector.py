import requests
import pandas as pd
from datetime import datetime
import time
from tqdm import tqdm
import os

# 🔹 FIX 1: Use a very specific User-Agent to avoid being flagged as a "bad bot"
HEADERS = {
    "User-Agent": "pc:trend_intelligence_collector:v1.0 (by /u/abdullah_khan_nitw)"
}

BATCH_SIZE = 25  # Reduced batch size slightly for better stability
LIMIT_COMMENTS = 5

session = requests.Session()
session.headers.update(HEADERS)

def fetch_comments(subreddit, post_id):
    # Added 'depth=1' to avoid loading deep nested replies (saves time)
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json?limit={LIMIT_COMMENTS}&depth=1"
    try:
        # Reduced timeout to 3 seconds. If Reddit doesn't respond, we skip it.
        response = session.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1:
                comment_data = data[1]['data']['children']
                comments = [c['data'].get('body', '') for c in comment_data if c['kind'] == 't1']
                return " | ".join(comments)
    except:
        return "No Comments (Timeout)"
    return "No Comments"

def fetch_reddit_data(source_type, query, total_needed):
    all_posts = []
    after = None
    
    pbar = tqdm(total=total_needed, desc=f" 🔍 Fetching {query}", leave=True)

    while len(all_posts) < total_needed:
        base_url = f"https://www.reddit.com/r/{query}/hot.json" if source_type == "subreddit" else "https://www.reddit.com/search.json"
        params = {
            "limit": BATCH_SIZE,
            "q": query if source_type == "keyword" else None,
            "after": after
        }

        try:
            # FIX 2: Increased timeout for the main post list
            response = session.get(base_url, params=params, timeout=10)
            
            if response.status_code == 429:
                # FIX 3: Longer back-off sleep if Reddit blocks us
                time.sleep(10)
                continue
                
            if response.status_code != 200:
                break

            data = response.json().get('data', {})
            children = data.get('children', [])
            if not children:
                break

            for post in children:
                p = post['data']
                
                # Fetch comments
                comments = fetch_comments(p.get("subreddit"), p.get("id"))

                all_posts.append({
                    "title": p.get("title"),
                    "text": p.get("selftext", "No Text"),
                    "comments": comments,
                    "score": p.get("score"),
                    "subreddit": p.get("subreddit"),
                    "datetime_utc": datetime.fromtimestamp(p.get("created_utc", 0))
                })
                
                pbar.update(1)
                if len(all_posts) >= total_needed:
                    break

            after = data.get('after')
            if not after:
                break
            
            # Small delay to be polite to the server
            time.sleep(1)

        except Exception as e:
            print(f" Error on {query}: {e}")
            break

    pbar.close()
    return all_posts

def build_dataset():
    # Reduced numbers slightly to ensure the pipeline finishes quickly for testing
    subreddits = ["technology", "news", "science"]
    keywords = ["AI", "Nvidia"]
    
    final_list = []
    
    print("🚀 Starting Data Collection...")
    for sub in subreddits:
        final_list.extend(fetch_reddit_data("subreddit", sub, 20))
    for key in keywords:
        final_list.extend(fetch_reddit_data("keyword", key, 20))
        
    if final_list:
        df = pd.DataFrame(final_list)
        save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reddit_data.csv")
        df.to_csv(save_path, index=False)
        print(f"\n✅ Done! Saved {len(df)} rows to {save_path}")
    else:
        print("\n❌ No data collected. Check your internet or Reddit status.")

if __name__ == "__main__":
    build_dataset()