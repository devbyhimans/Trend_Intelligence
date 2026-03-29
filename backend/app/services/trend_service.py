from app.db.connection import SessionLocal
from app.models.search import Search

def get_trends():
    db = SessionLocal()

   # getting top 5 searches sorted by hightest trend score
    data = db.query(Search).order_by(Search.trend_score.desc()).limit(5).all()

    db.close()

    result = []
    for item in data:
        result.append({
            "query": item.query,
            "trend_score": item.trend_score
        })

    return result