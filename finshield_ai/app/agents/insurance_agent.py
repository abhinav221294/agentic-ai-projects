from rag.rag_pipeline import ask_question


class InsuranceAgent:

    def run(self, query):

        return ask_question(query)