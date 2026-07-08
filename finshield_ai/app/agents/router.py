from .insurance_agent import InsuranceAgent
from .finance_agent import FinanceAgent
from .risk_agent import RiskAgent
from .summary_agent import SummaryAgent

insurance = InsuranceAgent()
finance = FinanceAgent()
risk = RiskAgent()
summary = SummaryAgent()


def route(query):

    q = query.lower()

    insurance_keywords = [
        "policy",
        "coverage",
        "claim",
        "premium",
        "exclusion",
        "insurance"
    ]

    finance_keywords = [
        "revenue",
        "profit",
        "cash flow",
        "balance sheet",
        "income",
        "finance"
    ]

    risk_keywords = [
        "risk",
        "exposure",
        "loss",
        "fraud"
    ]

    if any(k in q for k in insurance_keywords):
        return {
            "agent": "Insurance Agent",
            "result": insurance.run(query)
        }

    elif any(k in q for k in finance_keywords):
        return {
            "agent": "Finance Agent",
            "result": finance.run(query)
        }

    elif any(k in q for k in risk_keywords):
        return {
            "agent": "Risk Agent",
            "result": risk.run(query)
        }

    return {
        "agent": "Insurance Agent",
        "result": insurance.run(query)
    }