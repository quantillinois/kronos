from typing import Callable, List, Tuple, Dict, Any
import yfinance as yf
from pandas import Series, Timestamp
from datetime import datetime, timedelta

class Backtester:
  def __init__(self, strategy: Callable):
    self.strategy = strategy



  @staticmethod
  def getRatios(pctChanges: List[float], maxDrawdown: float, overallReturn: float, n: int) -> List[float]:
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

  def testTickerReport(self, ticker: str, start: str, end: str, startingAmount: float = 1000000.00) -> Dict[str, Any]: # returns a tuple of a dictionary of dates and prices, and a list of returns
    stock = yf.Ticker(ticker)
    data = stock.history(start=start, end=end)
    # data = data['Close']
    return self.testCustomReport(data, start, end, startingAmount)

  def testCustomReport(self, data: Series, startingAmount: float = 1000000.00) -> float:
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
    totals = Series(totals)
    totals.index = data.index
    
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
    pass

  def graphCustom(self, data: Series) -> None:
    pass