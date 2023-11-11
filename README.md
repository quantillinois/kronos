# kronos-backtester
## Preview
<img width="1398" alt="graph-example" src="https://github.com/quantillinois/kronos/assets/62070812/f3bd2d05-f48e-4e75-b069-e56ae473dd34">


## Installation
``` {.sourceCode .bash}
$ pip install kronos-backtester
```

### Requirements

-   [Python](https://www.python.org) \>= 3.7.1
-   [Pandas](https://github.com/pydata/pandas) \>= 1.3.0
-   [YFinance](https://github.com/ranaroussi/yfinance)

---

## Quick Start

```python
from kronos_backtester import Backtester

# Example strategy to be backtested
def momentumStrategy(df, short_window=50, long_window=200, entry_threshold=0.02, exit_threshold=0.01):
    # Strategy code here
    # Inputs: Pandas Dataframe of price data, any relevant parameters for the strategy
        # The Dataframe will have columns 'Close', 'Open', 'High', 'Low', and 'Volume'
    # Output: Pandas Series of signals which are integers -1, 0, 1
        # -1 : Sell, 0 : Hold, 1 : Buy
        # Index of Series should be dates

# The wrapper should only take in a DataFrame and output a Series of signals
# This is essentially one version of the strategy with a specific set of parameters.
def testWrapper(df): 
    return momentumStrategy(df, long_window=100)

bt = Backtester(testWrapper)

# This backtests on a particular ticker with given start and end date
bt.testTickerReport('AAPL', '2010-01-01', '2020-01-01')

# You can also backtest on a custom DataFrame of price data
bt.testCustomReport(customDF)
```

### Backtesting report output (dictionary)

    Start 2010-01-01
    End 2020-01-01
    Duration 2516
    Exposure Time 470.5
    Net Worth [1000000, ... ,8166774.230371475]
    Equity Final 8166774.230371475
    Equity Peak 8166774.230371475
    Return 7.166774230371475
    Buy and Hold Return 10.038871419853216
    Max Drawdown -0.1029208755830342
    Avg Drawdown -0.09627259509420738
    Max Drawdown Duration 19
    Avg Drawdown Duration 8.857142857142858
    # Trades 4
    Win Rate 1.0
    Best Trade 0.984095270845883
    Worst Trade 0.48189821881601236
    Max Trade Duration 669
    Avg Trade Duration 470.5
    Sharpe Ratio 33.99413578326285
    Sortino Ratio nan
    Calmar Ratio 69.11692296006356
