from backend.src.utils.token_cost_estimator import (
    TokenUsage,
    ModelPricing,
    calculate_token_cost
)


def test_claude_cost_calculation():

    usage = TokenUsage(
        input_tokens=10000,
        output_tokens=5000
    )

    pricing = ModelPricing(
        model_name="claude-sonnet",
        input_cost_per_million=3.0,
        output_cost_per_million=15.0
    )

    cost = calculate_token_cost(
        usage,
        pricing
    )

    assert cost > 0


def test_zero_tokens():

    usage = TokenUsage(
        input_tokens=0,
        output_tokens=0
    )

    pricing = ModelPricing(
        model_name="test-model",
        input_cost_per_million=1.0,
        output_cost_per_million=1.0
    )

    cost = calculate_token_cost(
        usage,
        pricing
    )

    assert cost == 0