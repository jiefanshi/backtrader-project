import backtrader as bt
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from macd_rsi_td_strategy import MACD_RSI_TD_Strategy

class FixedPercentSizer(bt.Sizer):
    def __init__(self, perc=0.1):
        self.perc = perc

    def _getsizing(self, comminfo, cash, data, isbuy):
        return int((cash * self.perc) / data.close[0])


def run_backtest(ticker="AAPL", start="2023-01-01", end="2025-07-01", cash=10000):
    data = yf.download(ticker, start=start, end=end, auto_adjust=True)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    datafeed = bt.feeds.PandasData(dataname=data)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(MACD_RSI_TD_Strategy)
    cerebro.adddata(datafeed)
    cerebro.broker.set_cash(cash)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addsizer(FixedPercentSizer, perc=1)

    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")

    results = cerebro.run()

    print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")

    total_commission = 0.0
    for strat in results:
        for data_trades in strat._trades.values():
            for trades in data_trades.values():
                for trade in trades:
                    total_commission += trade.commission
    print(f"Total Commission Paid: {total_commission:.2f}")

    figs = cerebro.plot(style="candlestick")
    for fig in figs:
        for ax in fig.axes:
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=10))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            fig.autofmt_xdate()


if __name__ == "__main__":
    run_backtest("AAPL", start="2023-01-01", end="2025-07-25")
