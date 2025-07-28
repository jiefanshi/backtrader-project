from ibkr_realtime_data_checker import IBKRRealtimeDataChecker

checker = IBKRRealtimeDataChecker(port=7497)  # Paper account

# Example 1: Single ticker
result = checker.check_ticker("AAPL")
print(result)  # You also get a dict you can use

# Example 2: Multiple tickers
tickers = ["AAPL", "MSFT", "SPY"]
results = [checker.check_ticker(t) for t in tickers]
