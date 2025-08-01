import backtrader as bt
import pandas as pd

class BuyHoldStrategy(bt.Strategy):
    """
    一个简单的 Buy & Hold 策略：
    ✅ 回测第一天就用所有现金全仓买入
    ✅ 之后一直持有到回测结束
    """

    def __init__(self):
        self.buy_done = False

    def next(self):
        if not self.buy_done:
            size = int(self.broker.get_cash() / self.datas[0].close[0])
            if size > 0:
                self.buy(size=size)
                print(f"📈 Buy & Hold: 买入 {size} 股 @ {self.datas[0].close[0]:.2f}")
                self.buy_done = True

    def stop(self):
        last_price = self.datas[0].close[0]
        pos = self.getposition(self.datas[0])
        final_value = self.broker.get_cash() + pos.size * last_price
        print(f"✅ Buy & Hold 最终账户价值: {final_value:.2f}")
