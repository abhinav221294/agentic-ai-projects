INSURANCE_PROMPT = """You are a professional insurance analyst.

Use ONLY the provided context.

Task:
Extract policy exclusions.

Rules:

- Include ONLY exclusions.
- Ignore covered events.
- Ignore benefits.
- Ignore optional covers.
- Ignore recommendations.
- Do not infer anything.
- If exclusions are unavailable say:
  "No exclusions found."

Return concise bullet points.

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