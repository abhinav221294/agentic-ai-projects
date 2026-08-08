from src.core.llm_pricing import calculate_llm_cost
from src.core.config import GEMINI_MODEL


def test_llm_cost_calculation():

    cost = calculate_llm_cost(
        model=GEMINI_MODEL,
        input_tokens=1_000_000,
        output_tokens=1_000_000,
    )

    assert cost >= 0