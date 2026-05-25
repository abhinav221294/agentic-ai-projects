ALLOCATION_MAP = {

    # LOW RISK
    ("low", "income"): {
    "equity": 30,
    "debt": 50,
    "gold": 20},
    

    ("low", "growth"): {
    "equity": 30,
    "debt": 50,
    "gold": 20
    }, 
 
    # MEDIUM
    ("medium", "income"): {
    "equity": 40,
    "debt": 40,
    "gold": 20},

    ("medium", "growth"):
     {"equity": 60,
    "debt": 25,
    "gold": 15},

    # HIGH RISK
    ("high", "income"): {
    "equity": 70,
    "debt": 20,
    "gold": 10},

    ("high", "growth"): {
    "equity": 80,
    "debt": 15,
    "gold": 5}
    }


ASSET_MAP = {
    "equity": ["equity", "stocks", "shares", "mutual fund", "mutual funds", "mf"],
    "debt": ["debt", "bonds", "fixed income"],
    "gold": ["gold"],
    "crypto": ["crypto", "bitcoin", "ethereum"],
    "real_estate": ["real estate", "property"],
}

MAX_LIMITS = {
    "crypto": 20,
    "gold": 30
}

FUND_SUGGESTIONS = {

    # ---------------- LOW RISK ----------------
    ("low", "income", "sip"): [
        "HDFC Corporate Bond Fund (SIP)",
        "ICICI Prudential Equity Savings Fund (SIP)",
        "SBI Conservative Hybrid Fund (SIP)",
        "Axis Banking & PSU Debt Fund (SIP)",
        "Kotak Debt Hybrid Fund (SIP)",
        "Aditya Birla Corporate Bond Fund (SIP)",
        "UTI Short Duration Fund (SIP)",
        "DSP Banking & PSU Debt Fund (SIP)",
        "Nippon India Low Duration Fund (SIP)",
        "Tata Corporate Bond Fund (SIP)"
    ],

    ("low", "income", "lump sum"): [
        "HDFC Short Term Debt Fund",
        "ICICI Corporate Bond Fund",
        "Axis Banking & PSU Debt Fund",
        "SBI Magnum Medium Duration Fund",
        "Kotak Low Duration Fund",
        "Aditya Birla Medium Term Plan",
        "UTI Short Duration Fund",
        "DSP Bond Fund",
        "Nippon India Short Term Fund",
        "Tata Banking & PSU Fund"
    ],

    ("low", "growth", "sip"): [
        "HDFC Balanced Advantage Fund",
        "ICICI Balanced Advantage Fund",
        "SBI Equity Hybrid Fund",
        "Kotak Balanced Advantage Fund",
        "Axis Balanced Advantage Fund",
        "DSP Dynamic Asset Allocation Fund",
        "Aditya Birla Balanced Advantage Fund",
        "UTI Balanced Advantage Fund",
        "Tata Balanced Advantage Fund",
        "Nippon India Balanced Advantage Fund"
    ],

    ("low", "growth", "lump sum"): [
        "ICICI Balanced Advantage Fund",
        "HDFC Hybrid Equity Fund",
        "SBI Balanced Advantage Fund",
        "Kotak Equity Hybrid Fund",
        "Axis Hybrid Fund",
        "DSP Equity & Bond Fund",
        "Aditya Birla Hybrid Fund",
        "UTI Hybrid Equity Fund",
        "Tata Hybrid Equity Fund",
        "Nippon India Hybrid Fund"
    ],

    # ---------------- MEDIUM RISK ----------------
    ("medium", "income", "sip"): [
        "ICICI Regular Savings Fund",
        "HDFC Hybrid Debt Fund",
        "SBI Equity Savings Fund",
        "Kotak Equity Savings Fund",
        "Axis Regular Savings Fund",
        "Aditya Birla Regular Savings Fund",
        "DSP Equity Savings Fund",
        "UTI Regular Savings Fund",
        "Tata Equity Savings Fund",
        "Nippon India Equity Savings Fund"
    ],

    ("medium", "income", "lump sum"): [
        "ICICI Equity Savings Fund",
        "HDFC Balanced Advantage Fund",
        "UTI Regular Savings Fund",
        "Kotak Equity Savings Fund",
        "Axis Equity Saver Fund",
        "DSP Equity Savings Fund",
        "Aditya Birla Equity Savings Fund",
        "Tata Equity Savings Fund",
        "Nippon India Equity Savings Fund",
        "Franklin Equity Income Fund"
    ],

    ("medium", "growth", "sip"): [
        "Parag Parikh Flexi Cap Fund",
        "ICICI Bluechip Fund",
        "Mirae Asset Large Cap Fund",
        "Axis Growth Opportunities Fund",
        "UTI Flexi Cap Fund",
        "Kotak Flexi Cap Fund",
        "Canara Robeco Bluechip Equity Fund",
        "DSP Flexi Cap Fund",
        "HDFC Top 100 Fund",
        "SBI Bluechip Fund"
    ],

    ("medium", "growth", "lump sum"): [
        "UTI Flexi Cap Fund",
        "Kotak Flexi Cap Fund",
        "Axis Growth Opportunities Fund",
        "Canara Robeco Bluechip Equity Fund",
        "DSP Flexi Cap Fund",
        "HDFC Top 100 Fund",
        "SBI Bluechip Fund",
        "ICICI Large Cap Fund",
        "Aditya Birla Flexi Cap Fund",
        "Tata Large Cap Fund"
    ],

    # ---------------- HIGH RISK ----------------
    ("high", "income", "sip"): [
        "HDFC Dividend Yield Fund",
        "ICICI Equity & Debt Fund",
        "UTI Equity Income Fund",
        "SBI Dividend Yield Fund",
        "Templeton India Equity Income Fund",
        "Aditya Birla Dividend Yield Fund",
        "DSP Dividend Yield Fund",
        "Tata Dividend Yield Fund",
        "Nippon India Dividend Yield Fund",
        "ICICI Dividend Yield Fund"
    ],

    ("high", "income", "lump sum"): [
        "ICICI Dividend Yield Fund",
        "HDFC Equity Savings Fund",
        "SBI Equity Income Fund",
        "UTI Dividend Yield Fund",
        "Axis Dividend Yield Fund",
        "Aditya Birla Dividend Yield Fund",
        "DSP Dividend Yield Fund",
        "Tata Dividend Yield Fund",
        "Nippon Dividend Yield Fund",
        "Franklin Dividend Yield Fund"
    ],

    ("high", "growth", "sip"): [
        "SBI Small Cap Fund",
        "Nippon India Small Cap Fund",
        "Axis Growth Opportunities Fund",
        "Kotak Small Cap Fund",
        "HDFC Small Cap Fund",
        "Quant Small Cap Fund",
        "DSP Small Cap Fund",
        "Aditya Birla Small Cap Fund",
        "UTI Small Cap Fund",
        "Canara Robeco Small Cap Fund"
    ],

    ("high", "growth", "lump sum"): [
        "Quant Small Cap Fund",
        "Nippon Small Cap Fund",
        "SBI Focused Equity Fund",
        "Axis Small Cap Fund",
        "HDFC Mid-Cap Opportunities Fund",
        "Kotak Emerging Equity Fund",
        "DSP Midcap Fund",
        "Aditya Birla Midcap Fund",
        "UTI Mid Cap Fund",
        "Tata Midcap Growth Fund"
    ],
}


RISK_KEYWORDS = {
        "low": ["low risk", "safe", "secure", "no loss"],
        "medium": ["balanced", "moderate", "some risk"],
        "high": ["high risk", "aggressive", "maximize return", "fast growth"]
        }

RETURN_KEYWORDS = {
        "low": ["low return", "stable income", "fixed income"],
        "medium": ["decent return", "steady growth"],
        "high": ["high return", "maximum return", "high growth"]
        }

GOAL_KEYWORDS = {
        "growth": ["growth", "aggressive growth", "long term growth"],
        "income": ["income", "cash flow", "regular income"]
        }