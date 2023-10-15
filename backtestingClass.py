from typing import Callable, List, Dict
import yfinance as yf
from pandas import DataFrame

class Backtester:
  def __init__(self, strategy: Callable[[DataFrame], List[float]]):
    self.strategy = strategy

  def testTicker(self, ticker: str, start: str, end: str) -> List[float]: # takes in ticker symbol, start date, end date
    stock = yf.Ticker(ticker)
    data = stock.h.history(start=start, end=end)
    data = data['Close'].to_list()
    return self.strategy(data)
    
  def testTickerReport(self, ticker: str, start: str, end: str) -> Dict[str, float]: # returns a tuple of a dictionary of dates and prices, and a list of returns
    pass

  def testCustom(self, data: List[float]) -> float:
    pass

  def testCustomReport(self, data: List[float]) -> Dict[str, float]:
    pass

  def graphTicker(self, ticker: str, start: str, end: str) -> None:
    pass

  def graphCustom(self, data: List[float]) -> None:
    pass

# How to factor in a look back period for a potential strategy
# Data clean up and organization between different sources
