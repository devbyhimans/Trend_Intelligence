from app.db.connection import SessionLocal
from app.models.search import Search
from app.utils.logger import log
from fastapi import HTTPException


def search_logic(query: str):
    # Calculates a trend score for the query and saves it to the DB
    log(f"Search query: {query}")

    try:
        db = SessionLocal()

        trend_score = len(query)

        new_search = Search(
            query=query,
            trend_score=trend_score,
            region="Earth" 
        )

        db.add(new_search)
        db.commit()
        db.close()

        return {
            "query": query,
            "trend_score": trend_score,
            "message": "saved to DB"
        }
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))


#ML processing data
def call_ml(query: str):
    # Simulates an ML prediction returning a dummy trend and score
    # Simulated machine learning engine response (placeholder for real ML model)
    return {
        "trend": "dummy trend",
        "score": 0.95  # Mock confidence score
    }

# reads all data from database and returns it as JSON
def get_all_searches():
    # Retrieves all past search queries from the DB
    db = SessionLocal()

    data = db.query(Search).all()

    result = []
    for item in data:
        result.append({
            "id": item.id,
            "query": item.query,
            "trend_score": item.trend_score
        })

    db.close()
    return result


def get_search_by_id(search_id: int):
    # Fetches a specific search record by its DB ID
    db = SessionLocal()

    data = db.query(Search).filter(Search.id == search_id).first()

    db.close()

    if not data:
        raise HTTPException(status_code=404, detail="Search not found")

    return {
        "id": data.id,
        "query": data.query,
        "trend_score": data.trend_score
    }

def delete_search(search_id: int):
    # Removes a specific search record from the DB by ID
    try:
        db = SessionLocal()

        data = db.query(Search).filter(Search.id == search_id).first()

        if not data:
            raise HTTPException(status_code=404, detail="Search not found")

        db.delete(data)
        db.commit()

        db.close()

        return {"message": "deleted"}

    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))