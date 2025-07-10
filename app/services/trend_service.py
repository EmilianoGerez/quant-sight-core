from app.infrastructure.alpaca_client import fetch_bars
from app.domain.ta_indicators_model import compute_trend_bias
from app.adapters.response_models import TrendPoint

async def get_trend_for_symbol(symbol: str, start: str, end: str) -> list[TrendPoint]:
    df = await fetch_bars(symbol, start, end)
    df = compute_trend_bias(df)

    return [
        TrendPoint(date=row["t"], close=row["close"], trend_bias=row["trend_bias"])
        for row in df.dropna(subset=["trend_bias"]).to_dict(orient="records")
    ]
