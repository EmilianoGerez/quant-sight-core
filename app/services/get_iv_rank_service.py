from sqlalchemy import select
from sqlalchemy.orm import Session
import pandas as pd
from app.db.models.iv_history import IvHistory
from app.db.models.watchlist import Watchlist
from app.domain.iv_rank import compute_iv_rank, compute_iv_percentile
from datetime import timedelta, datetime

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

def get_iv_rank_and_pct(db: Session, watch: Watchlist, lookback: int = 252):
    df = get_iv_series(db, watch.id, lookback)
    if df.empty or len(df) < 2:
        return None  # insufficient data

    rank       = compute_iv_rank(df["iv"])
    percentile = compute_iv_percentile(df["iv"])
    return {"symbol": watch.symbol, "iv_rank": rank, "iv_pct": percentile}

def get_iv_window(db: Session, watch_id: int, days: int = 30) -> pd.Series:
    """
    Returns a pd.Series of length `days`, indexed by date, containing
    the DAILY MEAN IV for the given watchlist_id.

    Steps:
    1) Fetch up to days*4 contract-level rows (to cover non-trading days).
    2) Build a DataFrame, convert iv to float.
    3) Group by date & take mean => one value per date.
    4) If we have >= days points, return the last `days`.
    """
    # 1️⃣ Fetch
    stmt = (
        select(IvHistory.date, IvHistory.iv)
        .where(IvHistory.watchlist_id == watch_id)
        .order_by(IvHistory.date.desc())
        .limit(days * 4)
    )
    rows = db.execute(stmt).all()
    print(f"Fetched {len(rows)} IV rows for watchlist {watch_id}")
    if not rows:
        return pd.Series(dtype=float)

    # 2️⃣ Build DF & ensure numeric
    df = pd.DataFrame(rows, columns=["date", "iv"])
    df["iv"] = df["iv"].astype(float)
    
    print(f"Initial IV DataFrame for watchlist {watch_id}:\n{df.head()}")

    # 3️⃣ Group by date => daily mean IV, sort ascending
    daily = (
        df.groupby("date")["iv"]
          .mean()
          .sort_index()
    )
    print(f"Daily mean IV for watchlist {watch_id}:\n{daily.count()} rows, from {daily.index.min()} to {daily.index.max()}")
    # 4️⃣ Check length & slice last `days`
    if len(daily) < days:
        return pd.Series(dtype=float)

    return daily.iloc[-days:]
