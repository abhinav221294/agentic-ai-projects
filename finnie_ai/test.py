import yfinance as yf

data = yf.download("AAPL", period="5d")
print(data)
print("Empty:", data.empty)