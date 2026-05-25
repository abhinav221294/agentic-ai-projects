from dataclasses import dataclass


@dataclass
class TokenUsage:

    input_tokens: int

    output_tokens: int


@dataclass
class ModelPricing:

    model_name: str

    input_cost_per_million: float

    output_cost_per_million: float


def calculate_token_cost(
    usage: TokenUsage,
    pricing: ModelPricing
) -> float:

    input_cost = (
        usage.input_tokens / 1_000_000
    ) * pricing.input_cost_per_million

    output_cost = (
        usage.output_tokens / 1_000_000
    ) * pricing.output_cost_per_million

    total_cost = input_cost + output_cost

    return round(total_cost, 6)