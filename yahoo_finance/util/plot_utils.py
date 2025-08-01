import matplotlib.pyplot as plt
import yfinance as yf

def plot_top_assets(top_assets, start="2023-01-01", end="2025-07-01"):
    """只绘制曾进入 Top3 的股票价格曲线"""
    plt.figure(figsize=(12, 6))
    for ticker in top_assets:
        df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
        if not df.empty:
            df["Close"].plot(label=ticker)

    plt.title("Performance of Assets that Entered Top3")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid()
    plt.show()
