import backtrader as bt

class MACD_RSI_TD_Strategy(bt.Strategy):
    params = dict(
        macd_fast=12,
        macd_slow=26,
        macd_signal=9,
        rsi_period=14,
        rsi_buy=50,
        rsi_sell=40
    )

    def __init__(self):
        # MACD
        macd = bt.ind.MACD(
            self.data.close,
            period_me1=self.p.macd_fast,
            period_me2=self.p.macd_slow,
            period_signal=self.p.macd_signal
        )
        self.macd = macd.macd
        self.signal = macd.signal

        # RSI
        self.rsi = bt.ind.RSI(period=self.p.rsi_period)

        # TD Sequential 计数器
        self.td_count = 0
        self.prev_close = None

    def next(self):
        # 计算 TD Sequential 计数
        if self.prev_close is None:
            self.prev_close = self.data.close[-4] if len(self) > 4 else self.data.close[0]

        if len(self) > 4 and self.data.close[0] > self.data.close[-4]:
            self.td_count += 1
        else:
            self.td_count = 0

        self.prev_close = self.data.close[0]

        # 交易逻辑
        if not self.position:
            if self.macd[0] > self.signal[0] and self.rsi[0] > self.p.rsi_buy and self.td_count < 9:
                size = int((self.broker.get_cash() * 0.1) / self.data.close[0])
                if size > 0:
                    self.buy(size=size)
                    self.log_trade("BUY", size)
        else:
            if (
                self.macd[0] < self.signal[0]
                or self.rsi[0] < self.p.rsi_sell
                or self.td_count >= 9
            ):
                size = self.position.size
                self.sell(size=size)
                self.log_trade("SELL", size)

    def log_trade(self, action, size):
        dt = self.datas[0].datetime.datetime(0)
        price = self.datas[0].close[0]
        cash = self.broker.get_cash()
        value = self.broker.get_value()
        print(
            f"{dt.strftime('%Y-%m-%d %H:%M:%S')} | {action} {size} @ {price:.2f} "
            f"| Cash: {cash:.2f} | Portfolio: {value:.2f} | TD={self.td_count}"
        )