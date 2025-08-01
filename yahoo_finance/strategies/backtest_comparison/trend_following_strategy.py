import backtrader as bt

class TrendFollowingStrategy(bt.Strategy):
    params = dict(short_ma=50, long_ma=200)

    def __init__(self):
        self.sma_short = {}
        self.sma_long = {}
        for data in self.datas:
            self.sma_short[data] = bt.indicators.SMA(data.close, period=self.p.short_ma)
            self.sma_long[data] = bt.indicators.SMA(data.close, period=self.p.long_ma)

    def next(self):
        for data in self.datas:
            pos = self.getposition(data)

            if self.sma_short[data][0] > self.sma_long[data][0]:
                if pos.size == 0:
                    size = int(self.broker.get_cash() / len(self.datas) / data.close[0])
                    self.buy(data=data, size=size)

            elif self.sma_short[data][0] < self.sma_long[data][0]:
                if pos.size > 0:
                    self.close(data=data)
