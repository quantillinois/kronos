import pandas as pd


def momentum_trading_strategy(data, short_window=50, long_window=200, entry_threshold=0.02, exit_threshold=0.01):
    """
    Parameters:
    - data: DataFrame with 'Date', 'Price', and any additional columns needed for analysis.
    - short_window: Short-term moving average window.
    - long_window: Long-term moving average window.
    - entry_threshold: Minimum price change required to trigger a buy/sell signal (percentage).
    - exit_threshold: Minimum price change required to exit a position (percentage).

    Returns:
    - signals: DataFrame with buy/sell signals (1 for buy, -1 for sell, 0 for hold).
    """

    data['Short_MA'] = data['Price'].rolling(window=short_window, min_periods=1).mean()
    data['Long_MA'] = data['Price'].rolling(window=long_window, min_periods=1).mean()

    data['Signal'] = 0

    data['Returns'] = data['Price'].pct_change()

    for i in range(1, len(data)):
        if (
            data['Short_MA'][i] > data['Long_MA'][i] and
            data['Returns'][i] > entry_threshold
        ):
            data.at[i, 'Signal'] = 1  

        elif (
            data['Short_MA'][i] < data['Long_MA'][i] and
            data['Returns'][i] < -entry_threshold
        ):
            data.at[i, 'Signal'] = -1  

    for i in range(1, len(data)):
        if (
            data['Signal'][i - 1] == 1 and
            data['Returns'][i] < -exit_threshold
        ):
            data.at[i, 'Signal'] = 0  

        elif (
            data['Signal'][i - 1] == -1 and
            data['Returns'][i] > exit_threshold
        ):
            data.at[i, 'Signal'] = 0  

    return data[['Date', 'Price', 'Short_MA', 'Long_MA', 'Signal']]

