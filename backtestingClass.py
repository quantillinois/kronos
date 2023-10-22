from typing import Callable, List, Tuple, Dict, Any
import yfinance as yf
from pandas import DataFrame, Series
from datetime import datetime

class Backtester:
  def __init__(self, strategy: Callable):
    self.strategy = strategy


  def testTickerReport(self, ticker: str, start: str, end: str, startingAmount: float = 1000000.00) -> Dict[str, Any]: # returns a tuple of a dictionary of dates and prices, and a list of returns
    stock = yf.Ticker(ticker)
    data = stock.history(start=start, end=end)
    data = data['Close'].to_list()
    return self.testCustomReport(data, start, end, startingAmount)

  @staticmethod
  def getRatios(pctChanges: List[float], maxDrawdown: float, overallReturn: float, n: int) -> List[float]:
    pct = Series(pctChanges)
    riskFreeRate = yf.download('^IRX', start=pct.index[0], end=pct.index[-1])['Close'].pct_change().mean()

    sharpe = (overallReturn-riskFreeRate)/pct.std()
    sortino = (overallReturn-riskFreeRate)/pct[pct < 0].std()
    calmar = overallReturn/maxDrawdown
    return [sharpe, sortino, calmar]


  def testCustomReport(self, data: List[float], start: str, end: str, startingAmount: float = 1000000.00) -> float:
    signals = self.strategy(data)
    amt = startingAmount
    histArr = []
    trades = []
    drawdowns = []
    bought = False
    boughtPrice = 0
    shares = 0
    prev = 0
    for price, signal in zip(data, signals):
      if prev != signal:
        if signal: # Buying a stock
          bought = True
          boughtPrice = minPrice = price
          currentDuration = 0
          currentDrawdownDuration = 0
          shares = int(amt/price)
          amt -= shares * price
        else: # Selling a stock
          bought = False
          trades.append((currentDuration, (price-boughtPrice)/boughtPrice))
          drawdowns.append((minPrice-price)/price)
          amt += price * shares
          shares = 0
      if bought:
        if price < boughtPrice:
          currentDrawdownDuration += 1
        else:
          drawdowns.append((currentDrawdownDuration, (minPrice-price)/price))
          currentDrawdownDuration = 0

        currentDuration += 1
        minPrice = min(minPrice, price)
      prev = signal
      histArr.append(shares*price+amt)
    totals = histArr
    
    report = {}
    report['Start'] = start
    report['End'] = end
    report['Duration'] = len(totals)
    report['Exposure Time'] = sum([x[0] for x in trades])/len(trades)
    report['Net Worth'] = totals

    report['Equity Final'] = totals[-1]
    report['Equity Peak'] = max(totals)

    report['Return'] = (totals[-1]-startingAmount)/startingAmount
    report['Buy and Hold Return'] = (data[-1]-data[0])/data[0]

    report['Max Drawdown'] = min(d[1] for d in drawdowns)
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
    pass

  def graphCustom(self, data: List[float]) -> None:
    pass

# How to factor in a look back period for a potential strategy
# Data clean up and organization between different sources