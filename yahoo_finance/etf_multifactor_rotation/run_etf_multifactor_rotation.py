import backtrader as bt
import pandas as pd
import yfinance as yf
from yahooquery import Ticker
import json, os

# 读取配置
config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_path, "r") as f:
    CONFIG = json.load(f)

TICKERS = CONFIG["tickers"]
INITIAL_CASH = CONFIG["initial_cash"]
START_DATE = CONFIG["start_date"]
END_DATE = CONFIG["end_date"]
LOOKBACK_DAYS = CONFIG["lookback_days"]
REBALANCE_DAYS = CONFIG["rebalance_days"]
WEIGHTS = CONFIG["weights"]

def get_price_data(ticker):
    df = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False)[
        ["Open", "High", "Low", "Close", "Volume"]
    ]
    df.columns = ["Open", "High", "Low", "Close", "Volume"]  # 确保列名是字符串
    df.dropna(inplace=True)
    return df

def get_fundamental_data(tickers):
    fundamentals = {}
    tq = Ticker(tickers)
    summary = tq.all_financial_data

    for t in tickers:
        try:
            roe = summary.loc[t].get("returnOnEquity", 0)
            pe = summary.loc[t].get("trailingPE", 0)
            growth = summary.loc[t].get("revenueGrowth", 0)
            fundamentals[t] = {"roe": roe or 0, "pe": pe or 0, "growth": growth or 0}
        except:
            fundamentals[t] = {"roe": 0, "pe": 0, "growth": 0}
    return fundamentals

class MultiFactorStrategy(bt.Strategy):
    params = dict(price_data=None)

    def __init__(self):
        self.price_data = self.p.price_data
        self.last_rebalance = None

    def next(self):
        today = self.datas[0].datetime.date(0)
        if self.last_rebalance is None or (today - self.last_rebalance).days >= REBALANCE_DAYS:
            self.rebalance(today)
            self.last_rebalance = today

    def rebalance(self, today):
        fundamentals = get_fundamental_data(TICKERS)
        scores = {}

        for ticker in TICKERS:
            df_hist = self.price_data[ticker].loc[:str(today)].tail(LOOKBACK_DAYS)
            if len(df_hist) < 2:
                continue

            momentum = df_hist["Close"].iloc[-1] / df_hist["Close"].iloc[0] - 1
            f = fundamentals[ticker]

            score = (
                WEIGHTS["momentum"] * momentum +
                WEIGHTS["roe"] * f["roe"] +
                WEIGHTS["pe"] * (1 / f["pe"] if f["pe"] and f["pe"] > 0 else 0)
            )
            scores[ticker] = score

        if not scores:
            return

        top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        top_names = [t for t, _ in top]

        total_value = self.broker.getvalue()
        target_value = total_value / len(top_names)

        print(f"\n📅 {today} | 调仓: {top_names}")

        # 卖掉不在 top 里的
        for d in self.datas:
            ticker = d._name
            pos = self.getposition(d)
            if ticker not in top_names and pos.size > 0:
                print(f"  🔻 SELL {ticker} | size={pos.size} | price={d.close[0]:.2f}")
                self.close(d)

        # 对 top 里的进行调仓
        for d in self.datas:
            if d._name in top_names:
                pos = self.getposition(d)
                current_value = pos.size * d.close[0]
                diff_cash = target_value - current_value
                if abs(diff_cash) / total_value > 0.01:
                    size = int(diff_cash / d.close[0])
                    if size > 0:
                        print(f"  ✅ BUY {d._name} | price={d.close[0]:.2f} | size={size}")
                        self.buy(data=d, size=size)
                    elif size < 0:
                        print(f"  🔻 SELL {d._name} | price={d.close[0]:.2f} | size={-size}")
                        self.sell(data=d, size=-size)

def run_backtest():
    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(INITIAL_CASH)
    cerebro.broker.setcommission(commission=0.001)

    price_data = {}
    for ticker in TICKERS:
        df = get_price_data(ticker)
        price_data[ticker] = df
        cerebro.adddata(bt.feeds.PandasData(dataname=df, name=ticker))  # ✅ 确保传入的是 DataFrame

    cerebro.addstrategy(MultiFactorStrategy, price_data=price_data)

    print("🚀 Running Multi-Factor ETF Rotation...")
    cerebro.run()
    print(f"\n✅ Final Portfolio Value = {cerebro.broker.getvalue():.2f}")

if __name__ == "__main__":
    run_backtest()
