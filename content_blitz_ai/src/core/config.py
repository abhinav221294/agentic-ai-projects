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