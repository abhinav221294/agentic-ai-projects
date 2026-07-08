from rag.summary_pipeline import generate_summary


class SummaryAgent:

    def run(self, pdf_path):

        return generate_summary(pdf_path)