from rag.rag_pipeline import ask_question


class FinanceAgent:

    def run(self, query):

        return ask_question(query)