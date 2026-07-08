from .insurance_agent import InsuranceAgent
from .finance_agent import FinanceAgent
from .risk_agent import RiskAgent
from .summary_agent import SummaryAgent

insurance = InsuranceAgent()
finance = FinanceAgent()
risk = RiskAgent()
summary = SummaryAgent()


def route(analysis_type, query, pdf_path):

    if analysis_type == "Executive Summary":
        print(type(summary))
        print(summary)
        print(pdf_path)
        return {
            "agent": "Summary Agent",
            "result": summary.run(pdf_path)
        }

    elif analysis_type == "Risk Analysis":
        return {
            "agent": "Risk Agent",
            "result": risk.run(pdf_path)
        }

    elif analysis_type == "Ask Question":
        return {
            "agent": "Insurance Agent",
            "result": insurance.run(query)
        }

    return {
        "agent": "Insurance Agent",
        "result": insurance.run(query)
    }