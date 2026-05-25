# =========================
# IMPORTS
# =========================

# pytest is the testing framework used to run test cases
import pytest

# MagicMock helps create fake/mock objects
# patch temporarily replaces real objects/functions during testing
from unittest.mock import MagicMock, patch


# sklearn metrics used for evaluating classification performance
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix


# importing the actual routing function to test
from src.agents.query_handler import query_handler


# =========================
# LABEL ENCODING
# =========================

# Machine learning metrics require numerical labels
# so we map each intent/category to integer values

LABEL_MAP = {

    # blog-related intent
    "blog": 0,

    # linkedin content generation intent
    "linkedin": 1,

    # research/query analysis intent
    "research": 2,

    # image generation intent
    "image": 3,

    # business/marketing strategy intent
    "strategy": 4,

    # fallback / no valid intent detected
    "none": 5
}


# =========================
# TEST DATASET
# =========================

# This dataset simulates real user queries
# expected = ground truth label
# llm_response = mocked LLM output

TEST_QUERIES = [

    # -------------------------
    # BLOG INTENT TEST CASES
    # -------------------------
    {
        "query": "Write a blog on AI agents",

        # actual expected category
        "expected": "blog",

        # fake LLM response returned during mocking
        "llm_response": "blog"
    },

    {
        "query": "Create detailed article on cloud computing",
        "expected": "blog",
        "llm_response": "blog"
    },

    # -------------------------
    # LINKEDIN INTENT TEST CASES
    # -------------------------
    {
        "query": "Create LinkedIn post for GenAI",
        "expected": "linkedin",
        "llm_response": "linkedin"
    },

    {
        "query": "Write professional LinkedIn content",
        "expected": "linkedin",
        "llm_response": "linkedin"
    },

    # -------------------------
    # RESEARCH INTENT TEST CASES
    # -------------------------
    {
        "query": "Research latest AI trends",
        "expected": "research",
        "llm_response": "research"
    },

    {
        "query": "Analyze LLM architectures",
        "expected": "research",
        "llm_response": "research"
    },

    # -------------------------
    # IMAGE GENERATION TEST CASES
    # -------------------------
    {
        "query": "Generate futuristic AI image",
        "expected": "image",
        "llm_response": "image"
    },

    {
        "query": "Create cyberpunk illustration",
        "expected": "image",
        "llm_response": "image"
    },

    # -------------------------
    # STRATEGY TEST CASES
    # -------------------------
    {
        "query": "Create AI marketing strategy",
        "expected": "strategy",
        "llm_response": "strategy"
    },

    {
        "query": "Build content growth strategy",
        "expected": "strategy",
        "llm_response": "strategy"
    },

    # -------------------------
    # NONE / GENERAL CHAT TEST CASES
    # -------------------------
    {
        "query": "Hello",
        "expected": "none",
        "llm_response": "none"
    },

    {
        "query": "What is your name?",
        "expected": "none",
        "llm_response": "none"
    }
]


# =========================
# BASE STATE
# =========================

# This function creates the default state object
# required by query_handler()

# Every query starts with a clean workflow state

def build_base_state(query: str):

    return {

        # unique user identifier
        "user_id": "user_001",

        # current session id
        "session_id": "session_001",

        # actual user query
        "user_query": query,

        # message history
        "messages": [],

        # conversation memory/history
        "conversation_history": [],

        # predicted intent
        "current_intent": None,

        # active task
        "current_task": None,

        # which agent is currently active
        "active_agent": None,

        # current workflow stage
        "workflow_step": None,

        # temporary intermediate outputs
        "intermediate_outputs": {},

        # tool/API outputs
        "tool_outputs": {},

        # retrieved memories from memory system
        "retrieved_memories": [],

        # user preferences/configurations
        "user_preferences": {},

        # long-term memory
        "memory": [],

        # research results
        "research_data": None,

        # external sources/citations
        "sources": [],

        # generated blog content
        "blog_content": None,

        # generated linkedin content
        "linkedin_content": None,

        # prompt used for image generation
        "image_prompt": None,

        # image output URL
        "image_url": None,

        # generated files/assets
        "generated_assets": [],

        # workflow execution status
        "status": None,

        # retry count for failed operations
        "retry_count": 0,

        # captured errors
        "errors": [],

        # execution logs
        "execution_logs": [],

        # next action in workflow
        "next_action": None,

        # final response returned to user
        "final_response": None,

        # metadata information
        "metadata": {},

        # execution trace/debugging
        "trace": [],

        # predicted category
        "category": None,

        # model confidence score
        "confidence": None,

        # whether decision came from rules/LLM/etc.
        "decision_source": None,

        # answer source
        "answer_source": None,

        # total execution time
        "execution_time": None,

        # final generated answer
        "answer": None
    }


# =========================
# MOCK RESPONSE CLASS
# =========================

# Simulates response returned by an LLM

class MockLLMResponse:

    def __init__(self, content):

        # stores predicted intent
        self.content = content


# =========================
# PRECISION + RECALL TEST
# =========================

# patch replaces claude_client_llm with a mock object
# prevents real API calls during testing

@patch("src.agents.query_handler.claude_client_llm")
def test_agent_routing_precision_recall(mock_llm):

    # stores actual labels
    y_true = []

    # stores predicted labels
    y_pred = []

    # iterate through all test queries
    for sample in TEST_QUERIES:

        # create fresh workflow state
        state = build_base_state(sample["query"])

        # create fake/mock model
        mock_model = MagicMock()

        # fake invoke() response from LLM
        mock_model.invoke.return_value = MockLLMResponse(
            sample["llm_response"]
        )

        # replace real LLM with mocked model
        mock_llm.return_value = mock_model

        # execute routing logic
        result = query_handler(state)

        # predicted intent from routing system
        predicted_intent = result["current_intent"]

        # append actual class label
        y_true.append(LABEL_MAP[sample["expected"]])

        # append predicted class label
        y_pred.append(LABEL_MAP[predicted_intent])

    # calculate macro precision
    # macro = average precision across all classes equally

    precision = precision_score(
        y_true,
        y_pred,

        # each class treated equally
        average="macro",

        # avoid division-by-zero warning
        zero_division=0
    )

    # calculate macro recall
    recall = recall_score(
        y_true,
        y_pred,
        average="macro"
    )

    print("\n")
    print("Precision:", precision)
    print("Recall:", recall)

    # detailed class-wise metrics
    print("\nClassification Report:\n")
    print(classification_report(y_true, y_pred))

    # confusion matrix shows actual vs predicted labels
    print("\nConfusion Matrix:\n")
    print(confusion_matrix(y_true, y_pred))

    # minimum expected performance threshold
    assert precision >= 0.80
    assert recall >= 0.80


# =========================
# NOISY PREDICTION TEST
# =========================

# Simulates imperfect LLM predictions

@patch("src.agents.query_handler.claude_client_llm")
def test_routing_with_noisy_predictions(mock_llm):

    y_true = []
    y_pred = []

    # intentionally wrong predictions added
    noisy_dataset = [

        # correct prediction
        ("Write AI blog", "blog", "blog"),

        # correct prediction
        ("Research AI", "research", "research"),

        # incorrect prediction
        # expected linkedin but predicted blog
        ("Create LinkedIn content", "linkedin", "blog"),

        # correct prediction
        ("Generate image", "image", "image"),

        # incorrect prediction
        # expected strategy but predicted research
        ("Create strategy", "strategy", "research")
    ]

    for query, expected, predicted in noisy_dataset:

        state = build_base_state(query)

        mock_model = MagicMock()

        # mocked wrong/correct prediction
        mock_model.invoke.return_value = MockLLMResponse(predicted)

        mock_llm.return_value = mock_model

        result = query_handler(state)

        y_true.append(LABEL_MAP[expected])
        y_pred.append(LABEL_MAP[result["current_intent"]])

    # calculate precision
    precision = precision_score(
        y_true,
        y_pred,
        average="macro"
    )

    # calculate recall
    recall = recall_score(
        y_true,
        y_pred,
        average="macro"
    )

    print("\nNoisy Routing Precision:", precision)
    print("Noisy Routing Recall:", recall)

    # lower thresholds because predictions are noisy
    assert precision >= 0.40
    assert recall >= 0.50


# =========================
# STRESS TEST
# =========================

# Checks whether routing works consistently
# for large number of requests

@patch("src.agents.query_handler.claude_client_llm")
def test_large_batch_routing(mock_llm):

    # repeating dataset 100 times
    queries = [
        ("Write blog on AI", "blog"),
        ("Create LinkedIn post", "linkedin"),
        ("Research OpenAI", "research"),
        ("Generate image", "image"),
        ("Marketing strategy", "strategy")
    ] * 100

    # tracks correct predictions
    correct_predictions = 0

    for query, expected in queries:

        state = build_base_state(query)

        mock_model = MagicMock()

        # always returning correct prediction
        mock_model.invoke.return_value = MockLLMResponse(expected)

        mock_llm.return_value = mock_model

        result = query_handler(state)

        # check if prediction matches
        if result["current_intent"] == expected:
            correct_predictions += 1

    # simple accuracy calculation

    accuracy = correct_predictions / len(queries)

    print("\nStress Test Accuracy:", accuracy)

    # expected very high consistency
    assert accuracy >= 0.95


# =========================
# MULTI-INTENT TEST
# =========================

# Tests queries containing multiple intents

@patch("src.agents.query_handler.claude_client_llm")
def test_multi_intent_queries(mock_llm):

    dataset = [

        # contains research + linkedin
        (
            "Research AI agents and create LinkedIn post",
            "research"
        ),

        # contains blog + image
        (
            "Write blog and generate image",
            "blog"
        ),

        # contains research + strategy
        (
            "Research cloud and create strategy",
            "research"
        )
    ]

    for query, expected in dataset:

        state = build_base_state(query)

        mock_model = MagicMock()

        # mocked chosen intent
        mock_model.invoke.return_value = MockLLMResponse(expected)

        mock_llm.return_value = mock_model

        result = query_handler(state)

        # verify selected intent
        assert result["current_intent"] == expected


# =========================
# RUN COMMAND
# =========================

# Run all tests with verbose output

# pytest tests/test_agent_routing_metrics.py -v