import os
from dotenv import load_dotenv

load_dotenv()

# ======================
# MODEL CONFIGURATION
# ======================

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-latest")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

#print("CLAUDE_MODEL =", CLAUDE_MODEL)

# ======================
# WORKFLOW SETTINGS
# ======================

MAX_RETRIES = 3
DEFAULT_CONFIDENCE = 0.75
REQUEST_TIMEOUT = 30

HIGH_CONFIDENCE = 0.9
LOW_CONFIDENCE = 0.2

# ======================
# WORKFLOW STATES
# ======================

WORKFLOW_STARTED = "workflow_started"
INTENT_CLASSIFICATION_COMPLETED = "intent_classification_completed"
INTENT_CLASSIFICATION_FAILED = "intent_classification_failed"

FALLBACK_STARTED = "fallback_started"
FALLBACK_COMPLETED = "fallback_completed"
FALLBACK_RESPONSE = "fallback_response"


WORKFLOW_COMPLETED = "workflow_completed"
WORKFLOW_FAILED = "workflow_failed"


QUERY_VALIDATION_FAILED = "query_validation_failed"

# ======================
# STRATEGIST
# ======================

STRATEGY_GENERATED = "strategy_generated"
STRATEGY_COMPLETED = "strategy_completed"
STRATEGY_FAILED = "strategy_failed"
STRATEGY_VALIDATION_FAILED = "strategy_validation_failed"
STRATEGY_STARTED = "strategy_generation_started"

# ======================
# RESEARCH
# ======================

QUERY_OPTIMIZATION_STARTED = "query_optimization_started"
QUERY_OPTIMIZATION_COMPLETED = "query_optimization_completed"

RETRIEVAL_STARTED = "retrieval_started"
RETRIEVAL_COMPLETED = "retrieval_completed"

SYNTHESIS_STARTED = "synthesis_started"
SYNTHESIS_COMPLETED = "synthesis_completed"

RESEARCH_COMPLETED = "research_completed"
RESEARCH_FAILED = "research_failed"

# ======================
# BLOG
# ======================

BLOG_GENERATED = "blog_generated"
BLOG_COMPLETED = "blog_completed"
BLOG_VALIDATION_FAILED = "blog_validation_failed"
BLOG_GENERATION_FAILED = "blog_generation_failed"
BLOG_STARTED="blog_started"
BLOG_STRUCTURE_GENERATED="blog_generated"

# ======================
# LINKEDIN
# ======================

LINKEDIN_GENERATED = "linkedin_generated"
LINKEDIN_COMPLETED = "linkedin_completed"
LINKEDIN_FAILED = "linkedin_failed"
LINKEDIN_VALIDATION_FAILED = "linkedin_validation_failed"
LINKEDIN_STARTED="linkedin_started"
LINKEDIN_STRUCTURE_GENERATED = "linkedin_structure_generated"
# ======================
# IMAGE
# ======================

IMAGE_GENERATED = "image_generated"
IMAGE_COMPLETED = "image_completed"
IMAGE_FAILED = "image_failed"
IMAGE_VALIDATION_FAILED = "image_validation_failed"
IMAGE_STARTED = "image_started"
FALLBACK_RESPONSE = """Sorry, I couldn't understand your request.

Try asking me to:

- 📝 Write a blog
- 💼 Create a LinkedIn post
- 🎨 Generate an image

Or simply describe what you'd like to create."""

# ======================
# VALID CATEGORIES
# ======================

VALID_CATEGORIES = {
    "blog",
    "linkedin",
    "image",
    "research",
    "none"
}