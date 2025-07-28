import backtrader as bt
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from yahoo_finance.strategies.moving_average_crossover.moving_average_crossover import MovingAverageCrossover

# Custom position sizer: Use a fixed % of cash per trade
class FixedPercentSizer(bt.Sizer):
    def __init__(self, perc=0.1):
        self.perc = perc

    def _getsizing(self, comminfo, cash, data, isbuy):
        return int((cash * self.perc) / data.close[0])


def run_backtest(ticker="AAPL", start="2024-01-01", end="2024-06-01", cash=10000):
    # Download historical data
    data = yf.download(ticker, start=start, end=end, auto_adjust=True)

    # Fix MultiIndex columns
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    datafeed = bt.feeds.PandasData(dataname=data)

    # Create Backtrader engine
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MovingAverageCrossover)
    cerebro.adddata(datafeed)

    # Set starting cash
    cerebro.broker.set_cash(cash)

    # Add commission (0.1%)
    cerebro.broker.setcommission(commission=0.001)

    # Add custom position sizer
    cerebro.addsizer(FixedPercentSizer, perc=1)

    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")

    results = cerebro.run()

    print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")

    # Calculate total commissions paid
    total_commission = 0.0
    for strat in results:
        for data_trades in strat._trades.values():
            for trades in data_trades.values():
                for trade in trades:
                    total_commission += trade.commission

    print(f"Total Commission Paid: {total_commission:.2f}")

    # Plot with cleaner x-axis
    figs = cerebro.plot(style="candlestick")
    for fig in figs:
        for ax in fig.axes:
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=10))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            fig.autofmt_xdate()


if __name__ == "__main__":
    run_backtest("QQQ", start="2023-01-01", end="2025-07-01", cash= 100000)
