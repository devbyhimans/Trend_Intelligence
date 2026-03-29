from app.db.connection import SessionLocal
from app.models.search import Search

def get_region_trends(state: str):
    db = SessionLocal()

    data = db.query(Search)\
        .filter(Search.region == state)\
        .order_by(Search.trend_score.desc())\
        .limit(5)\
        .all()

    db.close()

    return [
        {
            "query": item.query,
            "trend_score": item.trend_score,
            "region": item.region
        }
        for item in data
    ]