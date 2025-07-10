import os
import logging
from datetime import datetime
from typing import List, Optional

import httpx
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.watchlist import Watchlist
from app.db.models.iv_history import IvHistory

# ── configure logging ────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# ── constants ────────────────────────────────────────────────────
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"


def fetch_historical_options(symbol: str) -> List[dict]:
    """
    Call AlphaVantage HISTORICAL_OPTIONS endpoint and return the raw list of option data.
    """
    params = {
        "function": "HISTORICAL_OPTIONS",
        "symbol": symbol,
        "apikey": ALPHAVANTAGE_API_KEY,
    }
    resp = httpx.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    return payload.get("data", [])


def parse_option_record(raw: dict) -> Optional[IvHistory]:
    """
    Convert a single raw option dict into an IvHistory object.
    Return None if required fields are missing or invalid.
    """
    try:
        contract_id = raw["contractID"]
        expiration  = raw["expiration"]
        iv          = float(raw["implied_volatility"])
        date        = datetime.strptime(raw["date"], "%Y-%m-%d")
    except (KeyError, TypeError, ValueError) as e:
        logger.debug("Skipping record with keys %s due to parse error: %s", list(raw.keys()), e)
        return None

    return IvHistory(
        contract_id=contract_id,
        expiration=expiration,
        iv=iv,
        date=date,
    )


def get_last_iv_date(db: Session, watch: Watchlist) -> datetime:
    """
    Return the most recent IvHistory.date for this watch. If none exist, returns datetime.min.
    """
    last = (
        db.query(func.max(IvHistory.date))
          .filter(IvHistory.watchlist_id == watch.id)
          .scalar()
    )
    return last or datetime.min


def update_iv_for_symbol(db: Session, watch: Watchlist):
    """
    Fetch and insert only new IV history rows for the given watchlist entry.
    """
    logger.info("→ Processing %s (id=%d)", watch.symbol, watch.id)

    # 1️⃣ See how far we've already got
    last_date = get_last_iv_date(db, watch)
    logger.info("   Last stored date for %s: %s", watch.symbol, last_date.date())

    # 2️⃣ Fetch raw option data
    raw_data = fetch_historical_options(watch.symbol)
    logger.info("   Fetched %d raw records", len(raw_data))
    if not raw_data:
        logger.warning("   No data to process for %s", watch.symbol)
        return

    # 3️⃣ Parse & collect only new records
    new_records: List[IvHistory] = []
    for raw in raw_data:
        # skip any records on-or-before last_date
        try:
            rec_date = datetime.strptime(raw["date"], "%Y-%m-%d")
        except Exception:
            continue
        if rec_date <= last_date:
            continue

        record = parse_option_record(raw)
        if not record:
            continue

        # attach FK and symbol
        record.watchlist_id = watch.id
        record.symbol       = watch.symbol
        new_records.append(record)

    logger.info("   %d new records to insert", len(new_records))
    if not new_records:
        return

    # 4️⃣ Bulk-add and commit
    db.add_all(new_records)
    db.commit()
    logger.info("   ✔ inserted %d new IV records for %s", len(new_records), watch.symbol)


def update_all_iv_history():
    """
    Main entrypoint: finds every active, IV-tracked symbol and updates its history.
    """
    with SessionLocal() as db:
        watches = (
            db.query(Watchlist)
              .filter(Watchlist.track_iv.is_(True), Watchlist.is_active.is_(True))
              .all()
        )
        symbols = [w.symbol for w in watches]
        logger.info("Found %d symbols to update: %s", len(watches), symbols)

        for watch in watches:
            try:
                update_iv_for_symbol(db, watch)
            except Exception as e:
                logger.exception("Failed updating IV for %s: %s", watch.symbol, e)


if __name__ == "__main__":
    update_all_iv_history()
