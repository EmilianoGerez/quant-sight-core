from sqlalchemy import select
from app.db.models.iv_history import IvHistory

def get_iv_series(db: Session, watch_id: int, lookback_days: int = 252):
    stmt = (
        select(IvHistory.date, IvHistory.iv)
        .where(IvHistory.watchlist_id == watch_id)
        .order_by(IvHistory.date.desc())
        .limit(lookback_days)
    )
    rows = db.execute(stmt).all()
    # rows is list of (date, iv) tuples, newest first
    return pd.DataFrame(rows, columns=["date","iv"]).set_index("date").sort_index()
