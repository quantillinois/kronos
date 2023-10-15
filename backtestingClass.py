from typing import Callable, List, Tuple, Dict
class Backtester:
  def __init__(self, strategy: Callable):

    pass

  def testTicker(self, ticker: str, start: str, end: str, startingAmount: float = 1000000.00) -> List[float]: # takes in ticker symbol, start date, end date
    stock = yf.Ticker(ticker)
    data = stock.history(start=start, end=end)
    data = data['Close'].to_list()
    signals = self.strategy(data)

    amt = startingAmount
    histArr = []
    shares = 0
    prev = 0
    for price, signal in zip(data, signals):
      if prev != signal:
        if signal:
          shares = int(amt/price)
          amt -= shares * price
        else:
          amt += price * shares
          shares = 0
      prev = signal
      histArr.append(shares*price+amt)

      return histArr


  def testTickerReport(self, ticker: str, start: str, end: str) -> Tuple[Dict[str, float], List[float]]: # returns a tuple of a dictionary of dates and prices, and a list of returns
    pass

  def testCustom(self, data: List[float], start: str, end: str, startingAmount: float = 1000000.00) -> float:
    signals = self.strategy(data)

    amt = startingAmount
    histArr = []
    shares = 0
    prev = 0
    for price, signal in zip(data, signals):
      if prev != signal:
        if signal:
          shares = int(amt/price)
          amt -= shares * price
        else:
          amt += price * shares
          shares = 0
      prev = signal
      histArr.append(shares*price+amt)

      return histArr

  def testCustomReport(self, data: List[float]) -> Tuple[Dict[str, float], List[float]]:
    pass

  def graphTicker(self, ticker: str, start: str, end: str) -> None:
    pass

  def graphCustom(self, data: List[float]) -> None:
    pass

# How to factor in a look back period for a potential strategy
# Data clean up and organization between different sources