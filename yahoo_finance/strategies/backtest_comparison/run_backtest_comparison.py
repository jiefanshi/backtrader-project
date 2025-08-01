import sys
import os
import yfinance as yf
import backtrader as bt
import pandas as pd

# 修正路径，确保可以正确 import 其他策略文件
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from yahoo_finance.strategies.momentum_rotation.momentum_rotation_strategy import MomentumRotationStrategy
from yahoo_finance.strategies.backtest_comparison.trend_following_strategy import TrendFollowingStrategy
from yahoo_finance.strategies.backtest_comparison.buy_hold_strategy import BuyHoldStrategy


START_CASH = 90000
TICKER = "QQQ"


def get_data(ticker):
    df = yf.download(ticker, start="2013-01-01", end="2024-12-31")

    # 解决 MultiIndex 列名的问题
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]

    print(f"✅ 下载 {ticker} 数据: {len(df)} 行, 列名: {list(df.columns)}")
    return df


def run_strategy(strategy_class, cash, df):
    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(cash)

    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)

    cerebro.addstrategy(strategy_class)
    cerebro.run()
    return cerebro.broker.getvalue()


def run_backtest_comparison():
    df = get_data(TICKER)

    print("\n🚀 Running Buy & Hold...")
    buy_hold_value = run_strategy(BuyHoldStrategy, START_CASH, df)
    print(f"✅ Buy & Hold 最终账户价值: {buy_hold_value:.2f}")

    print("\n🚀 Running Momentum Rotation...")
    momentum_value = run_strategy(MomentumRotationStrategy, START_CASH, df)

    print("\n🚀 Running Trend Following...")
    trend_value = run_strategy(TrendFollowingStrategy, START_CASH, df)

    print("\n✅ Results:")
    print(f"Buy & Hold       | Final Portfolio Value = {buy_hold_value:.2f}")
    print(f"Momentum Rotation| Final Portfolio Value = {momentum_value:.2f}")
    print(f"Trend Following  | Final Portfolio Value = {trend_value:.2f}")


if __name__ == "__main__":
    run_backtest_comparison()
