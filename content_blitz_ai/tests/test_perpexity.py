from src.integrations.perplexity_client import perplexity_search

print("BEFORE PERPLEXITY", flush=True)

result = perplexity_search(
    "Agentic AI frameworks 2026 comparison"
)

print("AFTER PERPLEXITY", flush=True)
print(type(result), flush=True)
print(result, flush=True)