STOCK_MAP = {
    # -------------------------------
    # US Tech Giants
    # -------------------------------
    "TESLA": "TSLA",
    "TSLA": "TSLA",
    "APPLE": "AAPL",
    "AAPL": "AAPL",
    "MICROSOFT": "MSFT",
    "MSFT": "MSFT",
    "GOOGLE": "GOOGL",
    "ALPHABET": "GOOGL",
    "AMAZON": "AMZN",
    "AMZN": "AMZN",
    "META": "META",
    "FACEBOOK": "META",
    "NETFLIX": "NFLX",
    "NVIDIA": "NVDA",
    "NVDA": "NVDA",

    # -------------------------------
    # US Finance / Others
    # -------------------------------
    "JPMORGAN": "JPM",
    "JPM": "JPM",
    "GOLDMAN SACHS": "GS",
    "GS": "GS",
    "VISA": "V",
    "MASTERCARD": "MA",
    "WALMART": "WMT",
    "COCA COLA": "KO",
    "PEPSI": "PEP",

    # -------------------------------
    # ETFs / Index
    # -------------------------------
    "S&P500": "SPY",
    "SP500": "SPY",
    "NASDAQ": "QQQ",
    "DOW JONES": "DIA",

    # -------------------------------
    # Indian Stocks
    # -------------------------------
    "RELIANCE": "RELIANCE.NS",
    "RELIANCE INDUSTRIES": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "TATA CONSULTANCY": "TCS.NS",
    "INFOSYS": "INFY.NS",
    "INFY": "INFY.NS",
    "HDFC": "HDFCBANK.NS",
    "HDFC BANK": "HDFCBANK.NS",
    "ICICI": "ICICIBANK.NS",
    "ICICI BANK": "ICICIBANK.NS",
    "SBI": "SBIN.NS",
    "STATE BANK OF INDIA": "SBIN.NS",
    "WIPRO": "WIPRO.NS",
    "BHARTI AIRTEL": "BHARTIARTL.NS",
    "AIRTEL": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "LT": "LT.NS",
    "LARSEN": "LT.NS",
    "ADANI ENTERPRISES": "ADANIENT.NS",
    "ADANI": "ADANIENT.NS",
    "ADANI PORTS": "ADANIPORTS.NS",

    # -------------------------------
    # Global / Others
    # -------------------------------
    "SAMSUNG": "005930.KS",
    "SONY": "SONY",
    "TOYOTA": "TM",
    "BABA": "BABA",
    "ALIBABA": "BABA",

    # -------------------------------
    # Crypto (optional if you support it)
    # -------------------------------
    "BITCOIN": "BTC-USD",
    "BTC": "BTC-USD",
    "ETHEREUM": "ETH-USD",
    "ETH": "ETH-USD",
}


#def normalize_stock(symbol: str) -> str:
#    symbol = symbol.upper().strip()
#    return STOCK_MAP.get(symbol, symbol)


def normalize_stock(symbol: str) -> str:
    symbol = symbol.upper().strip()

    # Remove noise
    for word in ["SHARE", "STOCK", "LTD", "LIMITED", "PRICE", "OF"]:
        symbol = symbol.replace(word, "")

    symbol = symbol.strip()

    # Exact match
    if symbol in STOCK_MAP:
        return STOCK_MAP[symbol]

    # Partial match
    for key in STOCK_MAP:
        if key in symbol:
            return STOCK_MAP[key]

    return None   # ✅ FIXED