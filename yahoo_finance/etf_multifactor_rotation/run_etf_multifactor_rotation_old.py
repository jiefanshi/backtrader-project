import backtrader as bt
import yfinance as yf
import pandas as pd
from datetime import datetime


# ✅ 下载并清洗数据，确保返回单层 DataFrame
def download_data(ticker, start, end):
    raw = yf.download(ticker, start=start, end=end, progress=False, group_by="ticker")

    # 处理 tuple 返回值
    if isinstance(raw, tuple):
        raw = raw[0]

    # 处理 MultiIndex 列
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(-1)

    if not isinstance(raw, pd.DataFrame) or raw.empty:
        print(f"❌ 无法下载 {ticker} 数据")
        return None

    return raw[["Open", "High", "Low", "Close", "Volume"]].copy()


class MultiFactorStrategy(bt.Strategy):
    params = dict(
        rebalance_days=60,  # 每60天调仓
        tickers=["QQQ", "SPY", "IWM", "SOXX"],  # 4个ETF
    )

    def __init__(self):
        self.last_rebalance = None

    def next(self):
        if self.last_rebalance and (self.data.datetime.date(0) - self.last_rebalance).days < self.p.rebalance_days:
            return
        self.last_rebalance = self.data.datetime.date(0)
        self.rebalance_portfolio()

    def rebalance_portfolio(self):
        factor_scores = []

        for data in self.datas:
            close = pd.Series(data.close.get(size=90))
            if len(close) < 60:
                continue

            # ✅ 因子1：60日动量
            momentum = (close.iloc[-1] / close.iloc[-60]) - 1

            # ✅ 因子2：波动率（越低越好）
            vol = close.pct_change().std()

            score = momentum - vol
            factor_scores.append((data._name, score, data))

        if not factor_scores:
            return

        factor_scores.sort(key=lambda x: x[1], reverse=True)
        top_etfs = factor_scores[:3]

        for position in list(self.getpositions().keys()):
            if position._name not in [etf[0] for etf in top_etfs]:
                self.close(data=position)

        cash_per_etf = self.broker.get_cash() / len(top_etfs)

        for name, score, data in top_etfs:
            size = int(cash_per_etf / data.close[0])
            if size > 0:
                print(f"{self.data.datetime.date(0)} | BUY {name} | price={data.close[0]:.2f} | size={size} | cash={self.broker.get_cash():.2f}")
                self.buy(data=data, size=size)


def run_backtest():
    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(90000)
    cerebro.broker.set_coc(True)

    start, end = "2013-01-01", "2024-12-31"
    tickers = ["QQQ", "SPY", "IWM", "SOXX"]

    for ticker in tickers:
        df = download_data(ticker, start, end)
        if df is not None:
            data = bt.feeds.PandasData(dataname=df, name=ticker)
            cerebro.adddata(data)

    cerebro.addstrategy(MultiFactorStrategy, tickers=tickers)
    print("🚀 Running Multi-Factor ETF Rotation...")
    cerebro.run()

    print(f"✅ Final Portfolio Value = {cerebro.broker.getvalue():.2f}")


if __name__ == "__main__":
    run_backtest()

