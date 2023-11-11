from typing import List
import plotly.graph_objects as go
import random

from typing import Callable, List, Tuple, Dict, Any
import yfinance as yf
from pandas import Series, Timestamp, DataFrame
from datetime import datetime, timedelta

class Backtester:
  def __init__(self, strategy: Callable[[DataFrame], Series]):
    """Initializes the Backtester class with a trading strategy.

    Args:
    - strategy (Callable): Trading strategy function.
    """
    self.strategy = strategy

  @staticmethod
  def getRatios(pctChanges: List[float], maxDrawdown: float, overallReturn: float, n: int) -> List[float]:
    """Compute performance metrics for a trading strategy.

    Args:
    - pctChanges (List[float]): List of percentage changes.
    - maxDrawdown (float): Maximum drawdown.
    - overallReturn (float): Overall return of the strategy.
    - n (int): Number of trades.

    Returns:
    - List[float]: List containing Sharpe ratio, Sortino ratio, and Calmar ratio.
    """
   
    pct = Series(pctChanges)

    current_date = Timestamp(datetime.today())
    if current_date.weekday() == 5:  # Saturday
      current_date -= timedelta(days=1)
    elif current_date.weekday() == 6:  # Sunday
      current_date -= timedelta(days=2)
    riskFreeRate = yf.download('^IRX', start=current_date, end=current_date)['Adj Close'][0]/100
    print(riskFreeRate)

    sharpe = (overallReturn-riskFreeRate)/pct.std()
    sortino = (overallReturn-riskFreeRate)/pct[pct < 0].std()
    calmar = (overallReturn-riskFreeRate)/abs(maxDrawdown)
    return [sharpe, sortino, calmar]

  def testTickerReport(self, ticker: str, start: str, end: str, startingAmount: float = 1000000.00) -> Dict[str, Any]: 
    """Test a trading strategy on a specific ticker within a given date range.

    Args:
    - ticker (str): Stock ticker symbol.
    - start (str): Start date for backtesting (inclusive).
    - end (str): End date for backtesting (inclusive).
    - startingAmount (float): Starting capital for backtesting.

    Returns:
    - Dict[str, Any]: Backtesting report dictionary.
    """
  
  
    stock = yf.Ticker(ticker)
    data = stock.history(start=start, end=end)
    # data = data['Close']
    return self.testCustomReport(data, start, end, startingAmount)
  
  def testTicker(ticker: str, start: str, end: str) -> List[float]:
    stock = yf.Ticker(ticker)
    data = stock.history(start=start, end=end)
    prices = data['Close'].to_list()
    arr = [1000000]
    for i in range(1, len(prices)):
        arr.append(arr[i - 1] * (1 + (random.randrange(-100, 100) / 1000)))
    return arr

  def testCustomReport(self, data: Series, startingAmount: float = 1000000.00) -> float:
    
    """Test a trading strategy on custom price data.

    Args:
    - data (Series): Series of closing prices.
    - start (str): Start date for backtesting (inclusive).
    - end (str): End date for backtesting (inclusive).
    - startingAmount (float): Starting capital for backtesting.

    Returns:
    - Dict[str, Any]: Backtesting report dictionary.
      """
    signals = self.strategy(data) # Should return list of -1, 0, 1
    amt = startingAmount
    histArr = []
    trades = []
    drawdowns = []
    bought = False
    boughtPrice = 0
    shares = 0
    for price, signal in zip(data, signals):
      if signal == 1 and not bought: # Buying a stock
        bought = True
        boughtPrice = minPrice = price
        currentDuration = 0
        currentDrawdownDuration = 0
        shares = amt // price
        amt -= (shares * price)
      elif signal == -1 and bought: # Selling a stock
        bought = False
        trades.append((currentDuration, (price-boughtPrice)/boughtPrice))
        if currentDrawdownDuration:drawdowns.append((currentDrawdownDuration, (minPrice-price)/price))
        amt += (shares * price)
        shares = 0
      if bought:
        if price < boughtPrice:
          currentDrawdownDuration += 1
        else:
          if currentDrawdownDuration:drawdowns.append((currentDrawdownDuration, (minPrice-price)/price))
          currentDrawdownDuration = 0

        currentDuration += 1
        minPrice = min(minPrice, price)
      histArr.append(shares*price+amt)
    if bought:
      trades.append((currentDuration, (price-boughtPrice)/boughtPrice))
      if currentDrawdownDuration:drawdowns.append((currentDrawdownDuration, (minPrice-price)/price))
    totals = histArr
    
    report = {}
    report['Start'] = data.index[0]
    report['End'] = data.index[-1]
    report['Duration'] = len(totals)
    report['Exposure Time'] = sum([x[0] for x in trades])/len(trades)
    report['Net Worth'] = totals

    report['Equity Final'] = totals[-1]
    report['Equity Peak'] = max(totals)

    report['Return'] = (totals[-1]-startingAmount)/startingAmount
    report['Buy and Hold Return'] = (data[-1]-data[0])/data[0]

    report['Max Drawdown'] = min([d[1] for d in drawdowns])
    report['Avg Drawdown'] = sum(d[1] for d in drawdowns)/len(drawdowns)
    report["Max Drawdown Duration"] = max(d[0] for d in drawdowns)
    report["Avg Drawdown Duration"] = sum(d[0] for d in drawdowns)/len(drawdowns)
    
    report["# Trades"] = len(trades)
    report["Win Rate"] = sum(1 for t in trades if t[1] > 0)/len(trades)
    report["Best Trade"] = max(t[1] for t in trades)
    report["Worst Trade"] = min(t[1] for t in trades)

    report["Max Trade Duration"] = max(t[0] for t in trades)
    report["Avg Trade Duration"] = sum(t[0] for t in trades)/len(trades)

    report["Sharpe Ratio"], report["Sortino Ratio"], report["Calmar Ratio"] = self.getRatios([x[1] for x in trades], report["Max Drawdown"], report["Return"], len(trades))
    
    return report

  def graphTicker(self, ticker: str, start: str, end: str) -> None:
    stock = yf.Ticker(ticker)
    data = stock.history(start=start, end=end)
    prices = data['Close'].to_list()
    dates = data.index.to_list()
    backtests = self.testCustomReport(data['Close'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines', name='Stock Price'))

    fig.add_trace(go.Scatter(x=dates, y=backtests['Net Worth'], mode='lines', name='Strategy Performance', yaxis='y2'))

    # Create axis objects
    fig.update_layout(
        yaxis=dict(title='Stock Price'),
        yaxis2=dict(
            title='Strategy Performance',
            overlaying='y',
            side='right'
        ),
        title=f"{ticker} Strategy Performance",
        xaxis_title="Date"
    )

    fig.show()

    def graphCustom(self, data: Series) -> None:
      prices = data.values
      dates = data.index

      signals = self.strategy(data)
      backtests = []

      balance = 1000000
      for price, signal in zip(prices, signals):
          balance *= 1 + (signal * random.randrange(-100, 100) / 1000)
          backtests.append(balance)

      fig = go.Figure()

      fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines', name='Stock Price'))

      fig.add_trace(go.Scatter(x=dates, y=backtests, mode='lines', name='Strategy Performance', yaxis='y2'))

      fig.update_layout(
          yaxis=dict(title='Stock Price'),
          yaxis2=dict(
              title='Strategy Performance',
              overlaying='y',
              side='right'
          ),
          title="Custom Stock and Strategy Performance",
          xaxis_title="Date"
      )

      fig.show()

# Example usage
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

    shorts = data.rolling(window=short_window, min_periods=1).mean()
    longs = data.rolling(window=long_window, min_periods=1).mean()

    signals = [0] * len(data)

    returns = data.pct_change()

    for i in range(1, len(data)):
        if (
            shorts[i] > longs[i] and
            returns[i] > entry_threshold
        ):
            signals[i] = 1  

        elif (
            shorts[i] < longs[i] and
            returns[i] < -entry_threshold
        ):
            signals[i] = -1  

    for i in range(1, len(data)):
        if (
            signals[i] == 1 and
            returns[i] < -exit_threshold
        ):
            signals[i] = 0  

        elif (
            signals[i] == -1 and
            returns[i] > exit_threshold
        ):
            signals[i] = 0  

    return signals

def wrapper(data):
  return momentum_trading_strategy(data, short_window=50, long_window=200, entry_threshold=0.02, exit_threshold=0.01)

bt = Backtester(wrapper)

bt.graphTicker("AAPL", "2020-01-01", "2020-12-31")