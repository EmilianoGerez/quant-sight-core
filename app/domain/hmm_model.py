import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM

def compute_hmm(df: pd.DataFrame, n_components: int = 3) -> pd.DataFrame:
    """
    Fits an HMM to log returns and volatility features and returns the DataFrame
    with predicted market regime labels.
    
    Parameters:
    - df: DataFrame with 'close' price indexed by datetime
    - n_components: Number of regimes to detect
    
    Returns:
    - DataFrame with ['t', 'close', 'regime'] columns
    """

    # Step 1: Calculate log returns
    df['log_ret'] = np.log(df['close'] / df['close'].shift(1))

    # Step 2: Calculate rolling volatility (20-day standard deviation of returns)
    df['vol'] = df['log_ret'].rolling(20).std()

    # Step 3: Drop rows with NaNs from rolling calculations
    features = df[['log_ret', 'vol']].dropna()

    # Step 4: Fit the HMM model
    model = GaussianHMM(n_components=n_components, covariance_type='full', n_iter=1000)
    model.fit(features)

    # Step 5: Predict regime labels
    hidden_states = model.predict(features)

    # Step 6: Insert regime column back into original DataFrame
    df = df.copy()
    df['regime'] = np.nan
    df.loc[features.index, 'regime'] = hidden_states

    # Step 7: Final cleanup: convert to output format
    df = df.reset_index().dropna(subset=['regime'])
    df['regime'] = df['regime'].astype(int)

    return df[['t', 'close', 'regime']]
