from rag.summary_pipeline import generate_summary

result = generate_summary()

print("=" * 80)
print("EXECUTIVE SUMMARY")
print("=" * 80)

print(result["answer"])