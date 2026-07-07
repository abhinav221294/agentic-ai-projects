from rag.rag_pipeline import ask_question


class RiskAgent:

    def run(self, query):

        return ask_question(query)