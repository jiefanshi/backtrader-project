import backtrader as bt
from ib_insync import *

# Connect to IBKR Paper Account
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# Create Backtrader engine
cerebro = bt.Cerebro()

# Create IBKR contract
contract = Stock('AAPL', 'SMART', 'USD')

# Request historical data
bars = ib.reqHistoricalData(
    contract,
    endDateTime='',
    durationStr='1 D',
    barSizeSetting='5 mins',
    whatToShow='TRADES',
    useRTH=True,
    formatDate=1
)

# Convert IBKR bars to Backtrader DataFeed
class PandasData(bt.feeds.PandasData):
    params = dict(datetime=None, open=-1, high=-1, low=-1, close=-1, volume=-1, openinterest=-1)

import pandas as pd
df = util.df(bars)
df['datetime'] = pd.to_datetime(df['date'])
df.set_index('datetime', inplace=True)

data = PandasData(dataname=df)
cerebro.adddata(data)

# Add a simple strategy
class TestStrategy(bt.Strategy):
    def next(self):
        print(f"Price: {self.data.close[0]}")
        if not self.position:
            self.buy(size=1)
        elif len(self) >= 5:
            self.sell(size=1)

cerebro.addstrategy(TestStrategy)
cerebro.run()