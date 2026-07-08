from rag.risk_pipeline import analyze_risk

result = analyze_risk()

print("=" * 80)
print("RISK ANALYSIS")
print("=" * 80)

print(result["answer"])