from src.utils.token_cost_estimator import (
    TokenUsage,
    ModelPricing,
    calculate_token_cost
)

from src.config.model_pricing import MODEL_PRICING


def test_model_cost_comparison():

    usage = TokenUsage(
        input_tokens=50000,
        output_tokens=10000
    )


    claude_pricing = MODEL_PRICING["claude-sonnet"]

    haiku_pricing = MODEL_PRICING["claude-haiku"]
    
    gemini_pricing = MODEL_PRICING["gemini-1.5-flash"]

    claude_cost = calculate_token_cost(
        usage,
        claude_pricing
    )

    haiku_cost = calculate_token_cost(
    usage,
    haiku_pricing
    )


    gemini_cost = calculate_token_cost(
        usage,
        gemini_pricing
    )

    print("\n===== MODEL PRICING =====")

    print(
    f"Claude Input Cost per 1M Tokens: "
    f"${claude_pricing.input_cost_per_million}"
    )

    print(
    f"Claude Output Cost per 1M Tokens: "
    f"${claude_pricing.output_cost_per_million}"
    )

    print(
    f"Haiku Input Cost per 1M Tokens: "
    f"${haiku_pricing.input_cost_per_million}"
    )

    print(
    f"Gemini Input Cost per 1M Tokens: "
    f"${gemini_pricing.input_cost_per_million}"
    )

    print(
    f"Haiku Output Cost per 1M Tokens: "
    f"${haiku_pricing.output_cost_per_million}"
    )

    print(
    f"Gemini Output Cost per 1M Tokens: "
    f"${gemini_pricing.output_cost_per_million}"
    )

    print("\n===== REQUEST COST =====")

    print(f"Claude Sonnet Cost: ${claude_cost}")

    print(f"Claude Haiku Cost: ${haiku_cost}")

    print(f"Gemini Cost: ${gemini_cost}")

    

    assert claude_cost > haiku_cost
    assert claude_cost > gemini_cost