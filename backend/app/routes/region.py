# state-wise trends
from fastapi import APIRouter
from app.services.region_service import get_region_trends

router = APIRouter(tags=["Region"])

@router.get("/region")
def region(state: str):
    return get_region_trends(state)