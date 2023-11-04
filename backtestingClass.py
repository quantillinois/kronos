import plotly.graph_objs as go
import plotly.express as px

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
    """Generate a graph for a specific ticker within a given date range.

    Args:
    - ticker (str): Stock ticker symbol.
    - start (str): Start date for graphing.
    - end (str): End date for graphing.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(start=start, end=end)
    fig = px.line(data, x=data.index, y='Close', title=f'{ticker} Closing Prices')
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Close Price (USD)')
    fig.show()

def graphCustom(self, data: List[float], dates: List[datetime]) -> None:
    """Generate a custom graph based on input data.

    Args:
    - data (List[float]): List of data values to plot.
    - dates (List[datetime]): List of datetime objects corresponding to the data values.
    """
    fig = go.Figure(data=go.Scatter(x=dates, y=data))
    fig.update_layout(title='Custom Data Plot', xaxis_title='Date', yaxis_title='Value')
    fig.show()
