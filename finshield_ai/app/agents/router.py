from .insurance_agent import InsuranceAgent
from .finance_agent import FinanceAgent
from .risk_agent import RiskAgent


insurance = InsuranceAgent()

finance = FinanceAgent()

risk = RiskAgent()


def route(query):

    q = query.lower()

    insurance_keywords = [

        "policy",

        "coverage",

        "claim",

        "premium",

        "exclusion"

    ]

    finance_keywords = [

        "revenue",

        "profit",

        "cash flow",

        "balance sheet"

    ]

    risk_keywords = [

        "risk",

        "exposure",

        "loss"

    ]

    if any(k in q for k in insurance_keywords):

        return insurance.run(query)

    elif any(k in q for k in finance_keywords):

        return finance.run(query)

    elif any(k in q for k in risk_keywords):

        return risk.run(query)

    else:

        return insurance.run(query)