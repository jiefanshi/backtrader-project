import backtrader as bt
import yfinance as yf
import pandas as pd
import datetime

# ======================
# 策略定义
# ======================
class MomentumRotationStrategy(bt.Strategy):
    params = dict(
        lookback=60,   # 回看 60 天
        top_n=3,       # 每次选取动量最高的 3 只股票
        rebalance_days=5  # 每 60 天调仓
    )

    def __init__(self):
        self.last_rebalance = None  # 上次调仓的日期

    def next(self):
        # 1️⃣ 判断是否到达调仓日
        if self.last_rebalance and (self.datetime.date(0) - self.last_rebalance).days < self.p.rebalance_days:
            return  # 还没到调仓日

        # 2️⃣ 计算动量
        momentums = {}
        for data in self.datas:
            if len(data) > self.p.lookback:
                momentum = (data.close[0] - data.close[-self.p.lookback]) / data.close[-self.p.lookback]
                momentums[data._name] = momentum

        # 如果没有足够数据，跳过
        if len(momentums) == 0:
            return

        top_names = sorted(momentums, key=momentums.get, reverse=True)[:self.p.top_n]
        if not top_names:
            return

        # 3️⃣ 卖出不在 Top3 的股票
        for data in self.datas:
            if self.getposition(data).size > 0 and data._name not in top_names:
                self.close(data)

        # 4️⃣ 资金分配买入 Top3
        cash_per_stock = self.broker.get_cash() / len(top_names)

        for name in top_names:
            data = self.getdatabyname(name)
            size = int(cash_per_stock / data.close[0])
            if size > 0:
                self.buy(data=data, size=size)
                print(f"{self.datetime.date(0)} | BUY {name} | price={data.close[0]:.2f} | size={size} | cash={self.broker.get_cash():.2f}")

        self.last_rebalance = self.datetime.date(0)

# ======================
# 运行回测
# ======================
def run_backtest():
    tickers = ["MSFT", "AMZN", "META", "NVDA"]  # 你可以改成自己想要的股票池
    start = "2020-01-01"
    end = "2024-12-31"

    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(90000)
    cerebro.broker.setcommission(commission=0.001)

    for ticker in tickers:
        df = yf.download(ticker, start=start, end=end, progress=False)

        # 修正列名
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df[["Open","High","Low","Close","Volume"]].dropna()

        data = bt.feeds.PandasData(dataname=df, name=ticker)
        cerebro.adddata(data)


    cerebro.addstrategy(MomentumRotationStrategy)

    print("🚀 Running Momentum Rotation...")
    cerebro.run()

    print(f"✅ Final Portfolio Value = {cerebro.broker.getvalue():.2f}")

if __name__ == "__main__":
    run_backtest()
