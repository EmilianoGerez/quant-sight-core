import pandas as pd
import numpy as np
from app.domain.hmm_model import compute_hmm

def test_hmm_regime_detection():
    # Create dummy price data with an upward trend and noise
    data = {
        "t": pd.date_range(start="2023-01-01", periods=100, freq="D"),
        "close": pd.Series(100 + (pd.Series(range(100)) * 0.2) + np.random.normal(0, 1, 100))
    }
    df = pd.DataFrame(data).set_index("t")

    result = compute_hmm(df, n_components=3)

    assert not result.empty
    assert {"t", "close", "regime"}.issubset(result.columns)
    assert result["regime"].nunique() <= 3
