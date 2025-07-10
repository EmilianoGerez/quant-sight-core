from fastapi import APIRouter, Query
from app.services.trend_service import get_trend_for_symbol
from app.adapters.response_models import TrendPoint
from typing import List

router = APIRouter()

@router.get("/", response_model=List[TrendPoint])
async def trend_bias(
    symbol: str = Query(...),
    start: str = Query(...),
    end: str = Query(...)
):
    return await get_trend_for_symbol(symbol, start, end)
