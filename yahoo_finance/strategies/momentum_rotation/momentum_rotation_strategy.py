import backtrader as bt

class MomentumRotationStrategy(bt.Strategy):
    params = dict(
        lookback=90,
        top_n=10
    )

    def log(self, txt):
        dt = self.datas[0].datetime.date(0)
        print(f"{dt} | {txt}")

    def __init__(self):
        self.last_rebalance = None

    def next(self):
        if self.last_rebalance and (self.datas[0].datetime.date(0) - self.last_rebalance).days < 60:
            return

        momentum = {}
        for data in self.datas:
            if len(data) > self.p.lookback:
                past_price = data.close[-self.p.lookback]
                if past_price > 0:
                    momentum[data._name] = (data.close[0] / past_price - 1) * 100

        if not momentum:
            return

        # 取前 N 个股票
        top_momentum = dict(sorted(momentum.items(), key=lambda x: x[1], reverse=True)[:self.p.top_n])

        self.log("📊 Top 10 Momentum Ranking:")
        for symbol, mom in top_momentum.items():
            print(f"  {symbol:<6} {mom:6.2f}%")

        # 卖出不在榜单里的股票
        for data in list(self.getpositions().keys()):
            symbol = data._name
            if symbol not in top_momentum:
                self.close(data=data)

        # 买入榜单里的股票
        cash_per_stock = self.broker.get_cash() / len(top_momentum)
        for symbol in top_momentum.keys():
            data = self.getdatabyname(symbol)
            size = int(cash_per_stock / data.close[0])
            if size > 0:
                self.log(f"BUY {symbol} | size={size}")
                self.buy(data=data, size=size)

        self.last_rebalance = self.datas[0].datetime.date(0)
