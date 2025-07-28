from yahooquery import Ticker
import pandas as pd

class QQQHoldingsFetcher:
    def fetch_holdings(self):
        """
        使用 yahooquery 获取 QQQ 成分股，返回 symbol 列表
        """
        qqq = Ticker("QQQ")
        info = qqq.fund_holding_info.get("QQQ", {})
        if not info or "holdings" not in info:
            raise ValueError("Failed to fetch QQQ holdings")
        holdings = info["holdings"]
        return [h["symbol"] for h in holdings]

    def fetch_as_dataframe(self):
        """
        返回 DataFrame，包含 symbol、holdingPercent 等详细信息
        """
        qqq = Ticker("QQQ")
        info = qqq.fund_holding_info.get("QQQ", {})
        if not info or "holdings" not in info:
            raise ValueError("Failed to fetch QQQ holdings")
        return pd.DataFrame(info["holdings"])
