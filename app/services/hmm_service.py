from app.infrastructure.alpaca_client import fetch_bars
from app.domain.hmm_model import compute_hmm
from app.adapters.response_models import RegimePoint

async def get_regimes_for_symbol(symbol: str, start_date: str, end_date: str, components: int = 3) -> list[RegimePoint]:
    df = await fetch_bars(symbol, start_date, end_date)
    labeled_df = compute_hmm(df, n_components=components)
    return [RegimePoint(date=row["t"], close=row.close, regime=row.regime) for row in labeled_df.to_dict(orient="records")]