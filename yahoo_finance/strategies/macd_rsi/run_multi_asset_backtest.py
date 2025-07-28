import sys, os
# ✅ 自动把项目根目录加入 Python 模块搜索路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

import backtrader as bt
import yfinance as yf
import pandas as pd
from yahoo_finance.strategies.macd_rsi.macd_rsi_strategy import MACD_RSI_Strategy
from yahoo_finance.util.qqq_holdings import QQQHoldingsFetcher


class FixedPercentSizer(bt.Sizer):
    def __init__(self, perc=0.1):
        self.perc = perc

    def _getsizing(self, comminfo, cash, data, isbuy):
        return int((cash * self.perc) / data.close[0])


def select_top_momentum(tickers, lookback=60):
    momentum = []

    for t in tickers:
        try:
            df = yf.download(t, period=f"{lookback+1}d", auto_adjust=True, progress=False)

            # ✅ 如果 df 为空直接跳过
            if df is None or df.empty or len(df.index) < lookback:
                print(f"⚠️ Skipping {t}: insufficient data")
                continue

            # ✅ 确保是普通 DataFrame（去掉 MultiIndex）
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close_start = df["Close"].iloc[0]
            close_end = df["Close"].iloc[-1]

            # ✅ 强制转为 float，避免 Series
            close_start = float(close_start)
            close_end = float(close_end)

            if pd.isna(close_start) or pd.isna(close_end):
                print(f"⚠️ Skipping {t}: NaN close values")
                continue

            ret = close_end / close_start - 1
            momentum.append((t, ret))

        except Exception as e:
            print(f"⚠️ Failed to fetch {t}: {e}")

    if not momentum:
        raise ValueError("No valid tickers found for momentum calculation")

    dfm = pd.DataFrame(momentum, columns=["Ticker", "Return"])
    dfm = dfm.sort_values("Return", ascending=False)
    return dfm["Ticker"].iloc[:3].tolist()



def run_backtest_multi(start="2023-01-01", end="2025-07-01", cash=10000):
    fetcher = QQQHoldingsFetcher()
    all_tickers = fetcher.fetch_holdings()
    print(f"Fetched {len(all_tickers)} QQQ holdings")

    top3 = select_top_momentum(all_tickers, lookback=60)
    print(f"Top 3 momentum tickers: {top3}")

    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(cash)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addsizer(FixedPercentSizer, perc=1 / len(top3))

    for t in top3:
        df = yf.download(t, start=start, end=end, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        datafeed = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(datafeed, name=t)

    cerebro.addstrategy(MACD_RSI_Strategy)

    print(f"Starting Portfolio: {cerebro.broker.getvalue():.2f}")
    results = cerebro.run()
    print(f"Final Portfolio: {cerebro.broker.getvalue():.2f}")

    total_comm = 0
    for strat in results:
        for d in strat._trades.values():
            for trades in d.values():
                for tr in trades:
                    total_comm += tr.commission
    print(f"Total Commission Paid: {total_comm:.2f}")

    cerebro.plot()


if __name__ == "__main__":
    run_backtest_multi()

