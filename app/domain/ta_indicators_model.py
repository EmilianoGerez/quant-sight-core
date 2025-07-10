import pandas as pd

def compute_ema(df: pd.DataFrame, period: int, column="close", name=None):
    col_name = name or f"ema_{period}"
    df[col_name] = df[column].ewm(span=period, adjust=False).mean()
    return df

def compute_rsi(df: pd.DataFrame, period: int = 14, column="close"):
    delta = df[column].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    gain = up.rolling(period).mean()
    loss = down.rolling(period).mean()
    rs = gain / (loss + 1e-10)
    df["rsi"] = 100 - (100 / (1 + rs))
    return df

def compute_trend_bias(df: pd.DataFrame, short_ema=21, long_ema=50, rsi_threshold=50):
    df = compute_ema(df, short_ema)
    df = compute_ema(df, long_ema)
    df = compute_rsi(df)

    df["trend_bias"] = "neutral"
    df.loc[(df[f"ema_{short_ema}"] > df[f"ema_{long_ema}"]) & (df["rsi"] > rsi_threshold), "trend_bias"] = "bullish"
    df.loc[(df[f"ema_{short_ema}"] < df[f"ema_{long_ema}"]) & (df["rsi"] < rsi_threshold), "trend_bias"] = "bearish"

    return df.reset_index()
