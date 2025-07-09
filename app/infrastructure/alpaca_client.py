import os
import pandas as pd
import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("ALPACA_BASE_URL", "https://data.alpaca.markets/v2")
API_KEY = os.getenv("ALPACA_KEY_ID")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")

HEADERS = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": API_SECRET,
    "Content-Type": "application/json"
}

async def fetch_bars(symbol: str, start_date: str, end_date: str, timeframe: str = "1D") -> pd.DataFrame:
    url = f"{BASE_URL}/stocks/{symbol}/bars"
    params = {
        "start": start_date,
        "end": end_date,
        "timeframe": timeframe,
        "limit": 3000  # Adjust as needed
    }

    all_bars = []
    next_token = None

    async with httpx.AsyncClient() as client:
        while True:
            if next_token:
                params["page_token"] = next_token

            r = await client.get(url, headers=HEADERS, params=params)
            r.raise_for_status()
            json_data = r.json()

            bars = json_data.get("bars", [])
            all_bars.extend(bars)

            next_token = json_data.get("next_page_token")
            if not next_token:
                break

    # Parse the full result
    df = pd.DataFrame(all_bars)
    df["t"] = pd.to_datetime(df["t"])
    df.set_index("t", inplace=True)
    df.rename(columns={"c": "close"}, inplace=True)
    return df[["close"]]

