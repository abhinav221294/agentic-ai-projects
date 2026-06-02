import os
from dotenv import load_dotenv

load_dotenv()

# ======================
# MODEL CONFIGURATION
# ======================

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-latest")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# ======================
# WORKFLOW SETTINGS
# ======================

MAX_RETRIES = 3
DEFAULT_CONFIDENCE = 0.75
REQUEST_TIMEOUT = 30

# ======================
# WORKFLOW STATES
# ======================

WORKFLOW_STARTED = "workflow_started"
INTENT_CLASSIFICATION_COMPLETED = "intent_classification_completed"
INTENT_CLASSIFICATION_FAILED = "intent_classification_failed"

RESEARCH_COMPLETED = "research_completed"
RESEARCH_FAILED = "research_failed"

FALLBACK_STARTED = "fallback_started"
FALLBACK_COMPLETED = "fallback_completed"
FALLBACK_RESPONSE = "fallback_response"

# ======================
# STRATEGIST
# ======================

STRATEGY_GENERATED = "strategy_generated"
STRATEGY_COMPLETED = "strategy_completed"
STRATEGY_FAILED = "strategy_failed"
STRATEGY_VALIDATION_FAILED = "strategy_validation_failed"
STRATEGY_STARTED = "strategy_generation_started"

# ======================
# BLOG
# ======================

BLOG_GENERATED = "blog_generated"
BLOG_COMPLETED = "blog_completed"
BLOG_FAILED = "blog_failed"
BLOG_VALIDATION_FAILED = "blog_validation_failed"
BLOG_GENERATION_FAILED = "blog_generation_failed"

# ======================
# LINKEDIN
# ======================

LINKEDIN_GENERATED = "linkedin_generated"
LINKEDIN_COMPLETED = "linkedin_completed"
LINKEDIN_FAILED = "linkedin_failed"
LINKEDIN_VALIDATION_FAILED = "linkedin_validation_failed"



FALLBACK_RESPONSE = """Sorry, I could not understand the request properly.

Please try asking for:
- blog generation
- linkedin post
- research
- image generation
- strategy"""

# ======================
# VALID CATEGORIES
# ======================

VALID_CATEGORIES = {
    "blog",
    "linkedin",
    "research",
    "image",
    "strategy",
    "none"
}