from src.utils.token_cost_estimator import ModelPricing


MODEL_PRICING = {

    "claude-sonnet": ModelPricing(
        model_name="claude-sonnet",
        input_cost_per_million=3.0,
        output_cost_per_million=15.0
    ),

    "claude-haiku": ModelPricing(
        model_name="claude-haiku",
        input_cost_per_million=0.25,
        output_cost_per_million=1.25
    ),

    "gemini-1.5-flash": ModelPricing(
        model_name="gemini-1.5-flash",
        input_cost_per_million=0.35,
        output_cost_per_million=1.05
    )
}