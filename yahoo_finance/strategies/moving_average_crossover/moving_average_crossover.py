import backtrader as bt

class MovingAverageCrossover(bt.Strategy):
    params = dict(fast_period=10, slow_period=30)

    def __init__(self):
        sma_fast = bt.ind.SMA(period=self.p.fast_period)
        sma_slow = bt.ind.SMA(period=self.p.slow_period)
        self.crossover = bt.ind.CrossOver(sma_fast, sma_slow)

    def log_trade(self, action, size):
        dt = self.datas[0].datetime.datetime(0)  # Get current datetime
        price = self.datas[0].close[0]
        cash = self.broker.get_cash()
        value = self.broker.get_value()
        print(
            f"{dt.strftime('%Y-%m-%d %H:%M:%S')} | {action} {size} @ {price:.2f} "
            f"| Cash: {cash:.2f} | Portfolio: {value:.2f}"
        )

    def next(self):
        if not self.position:  # No position → check for Buy
            if self.crossover > 0:
                self.buy()

        elif self.crossover < 0:  # If in position and signal is sell
            size = self.position.size
            self.sell(size=size)
            self.log_trade("SELL", size)
