import backtrader as bt

class MACD_RSI_Strategy(bt.Strategy):
    params = dict(
        macd_fast=12,
        macd_slow=26,
        macd_signal=9,
        rsi_period=14,
        rsi_buy=50,
        rsi_sell=40
    )

    def __init__(self):
        macd = bt.ind.MACD(
            self.data.close,
            period_me1=self.p.macd_fast,
            period_me2=self.p.macd_slow,
            period_signal=self.p.macd_signal
        )
        self.macd = macd.macd
        self.signal = macd.signal
        self.rsi = bt.ind.RSI(period=self.p.rsi_period)

    def log_trade(self, action, size):
        dt = self.datas[0].datetime.datetime(0)
        price = self.datas[0].close[0]
        cash = self.broker.get_cash()
        value = self.broker.get_value()
        name = self.datas[0]._name  # ✅ 获取股票代码
        print(f"{dt:%Y-%m-%d %H:%M:%S} | {action} {size} {name} @ {price:.2f} | Cash: {cash:.2f} | Portfolio: {value:.2f}")


    def next(self):
        if not self.position:
            if self.macd[0] > self.signal[0] and self.rsi[0] > self.p.rsi_buy:
                size = int((self.broker.get_cash() * 0.1) / self.data.close[0])
                if size > 0:
                    self.buy(size=size)
                    self.log_trade("BUY", size)

        else:
            if self.macd[0] < self.signal[0] or self.rsi[0] < self.p.rsi_sell:
                size = self.position.size
                self.sell(size=size)
                self.log_trade("SELL", size)