INPUT_COST_PER_1M = 0.05
OUTPUT_COST_PER_1M = 0.08


def get_token_usage(response):
    """
    Extract token usage and estimated cost from a LangChain response.
    """

    usage = response.response_metadata.get("token_usage", {})

    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", 0)

    input_cost = (
        prompt_tokens / 1_000_000
    ) * INPUT_COST_PER_1M

    output_cost = (
        completion_tokens / 1_000_000
    ) * OUTPUT_COST_PER_1M

    total_cost = input_cost + output_cost

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "input_cost": round(input_cost, 8),
        "output_cost": round(output_cost, 8),
        "estimated_cost": round(total_cost, 8),
    }