import os
from dotenv import load_dotenv

load_dotenv()




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
BLOG_STRUCTURE_GENERATED="blog_structure_generated"

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

MIN_IMPORTANCE = 0
MAX_IMPORTANCE = 10



# ==========================================
# API Keys
# ==========================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
# ==========================================
# Models
# ==========================================

# ======================
# MODEL CONFIGURATION
# ======================

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-latest")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gpt-image-1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
VECTOR_DIMENSION = 3072

EVALUATION_LLM_MODEL = "gemini-3.5-flash"
EVALUATION_LLM_TEMPERATURE = 0
EVALUATION_LLM_MAX_TOKENS = 1000
EVALUATION_EMBEDDING_MODEL = "models/text-embedding-004"

# ==========================================
# Redis
# ==========================================

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# ==========================================
# PostgreSQL
# ==========================================

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))

# ==========================================
# Authentication
# ==========================================

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
)

# ==========================================
# Admin
# ==========================================

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

APP_BASE_URL = os.getenv(
    "APP_BASE_URL",
    "http://127.0.0.1:8000",
)