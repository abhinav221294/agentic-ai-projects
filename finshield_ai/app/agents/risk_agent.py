from rag.risk_pipeline import analyze_risk


class RiskAgent:

    def run(self, pdf_path):

        return analyze_risk(pdf_path)