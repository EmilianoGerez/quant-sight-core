from fastapi import APIRouter, Depends, HTTPException

from app.db.models.watchlist import Watchlist
from app.services.get_iv_rank_service import get_iv_rank_and_pct, get_iv_window
from app.domain.iv_rank import compute_iv_metrics
from app.db.session import get_db
from sqlalchemy.orm import Session


router = APIRouter(tags=["iv"])


@router.get("/rank/{symbol}")
def iv_rank(symbol: str, db: Session = Depends(get_db)):
    watch = db.query(Watchlist).filter_by(symbol=symbol, track_iv=True).first()
    if not watch:
        raise HTTPException(status_code=404, detail="Symbol not found or not trackable")

    result = get_iv_rank_and_pct(db, watch)
    if not result:
        raise HTTPException(status_code=400, detail="Not enough IV history")
    return result

@router.get("/metrics/{symbol}")
def iv_metrics(
    symbol: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    watch = (
        db.query(Watchlist)
          .filter_by(symbol=symbol, track_iv=True, is_active=True)
          .first()
    )
    if not watch:
        raise HTTPException(404, f"{symbol} not found or not tracking IV")

    iv_window = get_iv_window(db, watch.id, days)
    print(f"Fetched {len(iv_window)} IV data points for {symbol}")
    if len(iv_window) < days:
        raise HTTPException(400, "Not enough IV history to compute metrics")

    metrics = compute_iv_metrics(iv_window)
    return {"symbol": symbol, "days": days, **metrics}