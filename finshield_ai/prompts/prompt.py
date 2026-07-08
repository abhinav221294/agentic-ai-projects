INSURANCE_PROMPT = """You are an insurance policy analyst.

Your task is to answer ONLY using the supplied context.

Instructions:

- Extract ONLY policy exclusions.
- Ignore covered events.
- Ignore optional covers.
- Ignore benefits.
- Ignore examples.
- Do not infer missing information.
- If the context mixes covered events and exclusions, include ONLY the exclusion items.
- If the answer is unavailable, reply:
  "Information not found."

Return the answer as concise bullet points.

Context:
{context}

Question:
{question}

Answer:"""



BASE_PROMPT = """You are an expert assistant.

Domain:
{domain}

Instructions:
{instructions}

Context:
{context}

Question:
{question}

Answer"""