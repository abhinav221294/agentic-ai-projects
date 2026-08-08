from src.core.config import CLAUDE_MODEL, GEMINI_MODEL


MODEL_PRICING = {
    GEMINI_MODEL: {
        "input_per_1m": 0.30,
        "output_per_1m": 2.50,
    },

    CLAUDE_MODEL: {
        "input_per_1m": 1.00,
        "output_per_1m": 5.00,
    },

    # Actual model ID returned by Anthropic
    "claude-haiku-4-5-20251001": {
        "input_per_1m": 1.00,
        "output_per_1m": 5.00,
    },
}


def calculate_llm_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:

    pricing = MODEL_PRICING.get(model)

    if pricing is None:
        return 0.0

    input_cost = (
        input_tokens / 1_000_000
    ) * pricing["input_per_1m"]

    output_cost = (
        output_tokens / 1_000_000
    ) * pricing["output_per_1m"]

    return round(
        input_cost + output_cost,
        8,
    )
