from fastapi import APIRouter, Query, HTTPException
from app.adapters.response_models import RegimePoint
from app.services.hmm_service import get_regimes_for_symbol
from typing import List

router = APIRouter()

@router.get("/regimes", response_model=List[RegimePoint])
async def detect_regimes(
    symbol: str = Query(..., description="The stock symbol to analyze"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    components: int = Query(3, ge=2, le=5, description="Number of HMM components (2-5)")
):
    """
    Detect market regimes for a given stock symbol within a specified date range.
    """
    try:
        regimes = await get_regimes_for_symbol(symbol, start_date, end_date, components)
        return regimes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))