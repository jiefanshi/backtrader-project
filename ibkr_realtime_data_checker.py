from ib_insync import IB, Stock

class IBKRRealtimeDataChecker:
    def __init__(self, host='127.0.0.1', port=7497, client_id=1):
        self.ib = IB()
        self.ib.connect(host, port, clientId=client_id)

    def __del__(self):
        try:
            self.ib.disconnect()
        except:
            pass

    def _get_subscription_suggestion(self, primary_exchange):
        if primary_exchange in ["NASDAQ", "ISLAND"]:
            return "NASDAQ Level 1"
        elif primary_exchange in ["NYSE", "ARCA", "AMEX"]:
            return "NYSE Level 1 (covers ARCA/AMEX for most users)"
        else:
            return f"Check exchange subscription for {primary_exchange}"

    def check_ticker(self, ticker):
        contract = Stock(ticker, 'SMART', 'USD')
        self.ib.qualifyContracts(contract)

        market_data = self.ib.reqMktData(contract, '', False, False)
        self.ib.sleep(2)

        has_realtime = not (market_data.bid != market_data.bid)  # NaN check
        exchange = contract.primaryExchange or "UNKNOWN"
        suggestion = self._get_subscription_suggestion(exchange)

        result = {
            "ticker": ticker,
            "realtime": has_realtime,
            "exchange": exchange,
            "bid": market_data.bid if has_realtime else None,
            "ask": market_data.ask if has_realtime else None,
            "suggestion": suggestion if not has_realtime else None
        }

        # Print the result
        if has_realtime:
            print(f"✅ {ticker}: Real-time data ({exchange}, Bid={result['bid']}, Ask={result['ask']})")
        else:
            print(f"❌ {ticker}: No real-time data ({exchange}) → Suggestion: {suggestion}")

        return result
