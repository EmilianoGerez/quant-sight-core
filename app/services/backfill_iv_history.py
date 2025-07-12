import os
import time
import httpx
from datetime import datetime, timedelta
from app.db.session import SessionLocal
from app.db.models.watchlist import Watchlist
from app.db.models.iv_history import IvHistory
import pandas as pd

# === CONFIG ===
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"
LOOKBACK_DAYS = 60  # Set as needed

def daterange_business_days(start, end):
    """Yield business days between start and end, inclusive."""
    return pd.bdate_range(start, end).date

def get_existing_iv_dates(db, symbol):
    """Returns a set of all dates (as date objects) for which IV is already stored for this symbol."""
    result = db.query(IvHistory.date).filter(IvHistory.symbol == symbol).distinct().all()
    # Convert to set of date (no time)
    return set(r[0].date() for r in result if r[0] is not None)

def fetch_and_store_iv_for_date(db, symbol, watchlist_id, date):
    params = {
        "function": "HISTORICAL_OPTIONS",
        "symbol": symbol,
        "apikey": ALPHAVANTAGE_API_KEY,
        "date": date.strftime("%Y-%m-%d"),
    }
    try:
        response = httpx.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        options = data.get("data", [])
        if not options:
            print(f"  No data for {symbol} on {date}")
            return 0
        # Insert all contracts for that date (merge avoids duplicates by PK or unique constraints)
        new_count = 0
        for option in options:
            iv = option.get("implied_volatility")
            if not iv: continue
            contract_id = option.get("contractID")
            expiration = option.get("expiration")
            date_str = option.get("date")
            iv_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            iv_record = IvHistory(
                symbol=symbol,
                contract_id=contract_id,
                expiration=expiration,
                iv=float(iv),
                date=iv_date,
                watchlist_id=watchlist_id,
            )
            db.merge(iv_record)
            new_count += 1
        db.commit()
        print(f"  Stored {new_count} contracts for {symbol} on {date}")
        return new_count
    except Exception as ex:
        print(f"  Error fetching {symbol} on {date}: {ex}")
        return 0

def backfill_iv_history_for_symbol(db, symbol, watchlist_id, lookback_days=LOOKBACK_DAYS):
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=lookback_days * 2)  # Overfetch for holidays
    all_dates = daterange_business_days(start_date, end_date)
    existing_dates = get_existing_iv_dates(db, symbol)
    missing_dates = [d for d in all_dates if d not in existing_dates]
    print(f"Backfilling {symbol}: {len(missing_dates)} missing business days in window.")
    for i, date in enumerate(missing_dates):
        fetch_and_store_iv_for_date(db, symbol, watchlist_id, date)
        if i < len(missing_dates) - 1:
            print("  Sleeping 65 seconds to respect API rate limit...")
            time.sleep(65)  # Alpha Vantage free tier: 1 req/minute

def backfill_iv_for_watchlist():
    db = SessionLocal()
    try:
        symbols = db.query(Watchlist).all()
        if not symbols:
            print("No watchlist symbols found.")
            return
        for w in symbols:
            print(f"→ Processing {w.symbol} (id={w.id})")
            backfill_iv_history_for_symbol(db, w.symbol, w.id)
    finally:
        db.close()

if __name__ == "__main__":
    backfill_iv_for_watchlist()