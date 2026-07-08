from rag.comparison_pipeline import compare_policies

class ComparisonAgent:

    def run(self, pdf_a, pdf_b):

        return compare_policies(pdf_a, pdf_b)