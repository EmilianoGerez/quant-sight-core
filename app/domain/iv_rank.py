import pandas as pd
from statistics import pstdev
import numpy as np

def compute_iv_rank(iv_series: pd.Series) -> float:
    """
    Given a pd.Series of IV values (index=date, sorted ascending),
    returns today's IV rank between 0 and 1.
    """
    today_iv = iv_series.iloc[-1]
    iv_min, iv_max = iv_series.min(), iv_series.max()
    if iv_max == iv_min:
        return 0.0
    return (today_iv - iv_min) / (iv_max - iv_min)

def compute_iv_percentile(iv_series: pd.Series) -> float:
    """
    Percentage of days where IV <= today's IV.
    """
    today_iv = iv_series.iloc[-1]
    return (iv_series <= today_iv).mean()


def compute_iv_metrics(iv_window: pd.Series) -> dict:
    """
    Given a 30‐point IV series (index=date), returns:
    - iv_rank (0–1)
    - iv_pct  (0–1)
    - iv_low, iv_low_date
    - iv_high, iv_high_date
    - hist_vol (30d realized volatility of returns)
    """
    today_iv = iv_window.iloc[-1]
    iv_min, iv_max = iv_window.min(), iv_window.max()
    iv_rank = 0.0 if iv_max == iv_min else (today_iv - iv_min) / (iv_max - iv_min)
    iv_pct  = (iv_window <= today_iv).mean()

    iv_low_date  = iv_window.idxmin().date()
    iv_high_date = iv_window.idxmax().date()

    # For historical vol, we need price returns, not IV.  
    # If you’ve stored close‐price in IvHistory (or join from a price table), 
    # you can compute realized vol of returns here.  Otherwise skip or compute from IV changes:
    # Example: 30‐day stdev of IV changes annualized
    returns = iv_window.pct_change().dropna()
    hist_vol = pstdev(returns) * np.sqrt(252)  # annualized

    return {
        "iv_rank":       round(iv_rank*100, 2),
        "iv_pct":        round(iv_pct*100, 2),
        "iv_low":        round(iv_min, 2),
        "iv_low_date":   str(iv_low_date),
        "iv_high":       round(iv_max, 2),
        "iv_high_date":  str(iv_high_date),
        "hist_vol":      round(hist_vol*100, 2),
    }
