# Define API endpoints related to global trends
from fastapi import APIRouter
from app.services.trend_service import get_trends

# Initialize the router for trend-related endpoints
router = APIRouter()

# Define a GET route for /trends to fetch current trending topics
@router.get("/trends")
def trends():
    # Fetches the current global trending topics
    # Return a hardcoded list of global trends 
    return get_trends()