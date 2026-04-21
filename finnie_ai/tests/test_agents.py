from agents import rag_agent,market_agent,risk_agent,advisor_agent

tests = [
    ("rag", "What is SIP?"),
    ("market", "Price of Tesla stock"),
    ("risk", "Is crypto risky?"),
    ("advisor", "Where should I invest?")
]

for name, query in tests:
    state = {"query": query}

    if name == "rag":
        print(rag_agent(state))
    elif name == "market":
        print(market_agent(state))
    elif name == "risk":
        print(risk_agent(state))
    elif name == "advisor":
        print(advisor_agent(state))