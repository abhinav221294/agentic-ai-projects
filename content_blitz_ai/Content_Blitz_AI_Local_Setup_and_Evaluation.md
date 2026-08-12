# Content Blitz AI --- Local Setup & Evaluation Guide

## 1. Prerequisites

Install:

-   Python 3.12
-   Node.js and npm
-   Git
-   Docker Desktop (optional)
-   PostgreSQL with pgvector
-   Redis

You also need API keys for the external AI and research services.

------------------------------------------------------------------------

## 2. Clone the Repository

``` bash
git clone git clone https://github.com/abhinav221294/agentic-ai-projects.git
cd agentic-ai-projects/content_blitz_ai
```

------------------------------------------------------------------------

## 3. Backend Setup

``` powershell
cd backend
python -m venv con_blitz
.\con_blitz\Scripts\Activate.ps1
pip install -r requirements.txt
```

For Linux/macOS:

``` bash
python3 -m venv con_blitz
source con_blitz/bin/activate
pip install -r requirements.txt
```


# 📦 Requirements

# ============================================

# Content Blitz AI - Requirements

# Python 3.12

# ============================================

# ============================================

# LLM + Agents

# ============================================

langchain==0.3.27
langgraph==0.6.6
langchain-core==0.3.75
langchain-community==0.3.29

# ============================================

# OpenAI

# ============================================

openai==1.101.0
langchain-openai==0.3.30

# ============================================

# Anthropic / Claude

# ============================================

anthropic==0.64.0
langchain-anthropic==0.3.18

# ============================================

# Google Gemini

# ============================================

google-genai==1.31.0
langchain-google-genai==2.1.9

# ============================================

# RAG / Vector Database / Embeddings

# ============================================

pgvector==0.4.1
psycopg2-binary==2.9.10
sqlalchemy==2.0.43
sentence-transformers==5.1.0

# ============================================

# Redis / Memory

# ============================================

redis==5.2.1

# ============================================

# Backend API

# ============================================

fastapi==0.116.1
uvicorn[standard]==0.35.0
python-multipart==0.0.20

# ============================================

# Authentication / Security

# ============================================

python-jose[cryptography]==3.5.0
passlib[bcrypt]==1.7.4
bcrypt==4.1.3

# ============================================

# Frontend

# ============================================

streamlit==1.48.1

# ============================================

# Research / Search APIs

# ============================================

tavily-python==0.7.11

# ============================================

# Image Processing

# ============================================

pillow==11.3.0

# ============================================

# Data Processing

# ============================================

numpy==2.3.2
pandas==2.3.1

# ============================================

# Environment / Configuration

# ============================================

python-dotenv==1.1.1
pydantic==2.11.7
pydantic-settings==2.10.1
email-validator==2.2.0

# ============================================

# HTTP / Networking

# ============================================

httpx==0.28.1
requests==2.32.5

# ============================================

# Logging / Retries

# ============================================

tenacity==9.1.2
loguru==0.7.3
python-json-logger==2.0.7

# ============================================

# Testing

# ============================================

pytest==8.4.1
pytest-asyncio==1.1.0

# ============================================

# Evaluation / Observability

# ============================================

scikit-learn==1.7.1
ragas==0.2.15
langsmith==0.4.14
tiktoken==0.11.0
grandalf



------------------------------------------------------------------------

## 4. Environment Variables

Create a `.env` file in `backend/`.

``` env
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
TAVILY_API_KEY=your_tavily_api_key

CLAUDE_MODEL=claude-3-5-haiku-latest
GEMINI_MODEL=gemini-3.5-flash
IMAGE_MODEL=gpt-image-1
EMBEDDING_MODEL=gemini-embedding-001

POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=content_blitz
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379

SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Never commit `.env` or API keys to GitHub.**

------------------------------------------------------------------------

## 5. Start PostgreSQL and Redis

Start PostgreSQL and Redis locally, or use Docker if they are defined in
the Compose configuration:

``` bash
docker compose up -d postgres redis
```

Make sure PostgreSQL has the `pgvector` extension enabled.

------------------------------------------------------------------------

## 6. Run the Backend

From `backend/`:

``` bash
uvicorn src.main:app --reload
```

Backend:

``` text
http://127.0.0.1:8000
```

Swagger API documentation:

``` text
http://127.0.0.1:8000/docs
```

------------------------------------------------------------------------

## 7. Run the Frontend

Open a second terminal:

``` powershell
cd frontend
npm install
npm run dev
```

Frontend:

``` text
http://localhost:5173
```

------------------------------------------------------------------------

## 8. Run with Docker

From the project root:

``` bash
docker compose up --build
```

Background mode:

``` bash
docker compose up --build -d
```

Stop:

``` bash
docker compose down
```

------------------------------------------------------------------------

# Testing

## 9. Unit Tests

From `backend/`:

``` bash
pytest
```

------------------------------------------------------------------------

# Evaluation

The project includes an evaluation framework covering routing, research,
tool calling, LLM outputs, and final generated content.

## 10. Intent Evaluation

``` bash
python evaluation/evaluators/intent_evaluator.py
```

Evaluates intent classification.

## 11. Research Decision Evaluation

``` bash
python evaluation/evaluators/research_decision_evaluator.py
```

Evaluates whether research is correctly selected.

## 12. Tool Calling Evaluation

``` bash
python evaluation/evaluators/tool_calling_evaluator.py
```

Evaluates whether the correct tools are selected and invoked.

## 13. Research Quality Evaluation

``` bash
python evaluation/evaluators/research_quality_evaluator.py
```

Evaluates retrieval, synthesis, and freshness-related checks.

## 14. LLM Output Evaluation

``` bash
python evaluation/evaluators/llm_output_evaluator.py
```

Evaluates LLM output validation and expected response formats.

## 15. Final Output Quality Evaluation

``` bash
python evaluation/evaluators/final_output_evaluator.py
```

Uses an LLM-as-a-Judge approach to evaluate the actual generated output.

Criteria include:

-   Relevance
-   Structure
-   Accuracy
-   Completeness
-   Instruction following
-   Technical depth
-   Architecture detail
-   Beginner readability
-   Professional tone
-   Hook quality
-   CTA quality
-   Engagement

The dataset is:

``` text
backend/evaluation/datasets/content/content_quality_cases.json
```

------------------------------------------------------------------------

# Evaluation Flow

``` text
User Request
     │
     ▼
Intent Evaluation
     │
     ▼
Research Decision Evaluation
     │
     ▼
Tool Calling Evaluation
     │
     ▼
Research Quality Evaluation
     │
     ▼
LLM Output Evaluation
     │
     ▼
Final Output Quality Evaluation
     │
     ▼
LLM-as-a-Judge / RAGAS
```

------------------------------------------------------------------------

# Current Evaluation Results

``` text
Tool Calling Accuracy       : 100%
Research Quality             : 6/6
LLM Output Validation        : 12/12
Final Output Quality         : 4.02/5
```

These results represent the current evaluation datasets and
configuration.

------------------------------------------------------------------------

# Quick Start

### Terminal 1 --- Backend

``` powershell
cd backend
.\con_blitz\Scripts\Activate.ps1
uvicorn src.main:app --reload
```

### Terminal 2 --- Frontend

``` powershell
cd frontend
npm install
npm run dev
```

Open:

``` text
http://localhost:5173
```

------------------------------------------------------------------------

# Project Structure

``` text
content_blitz_ai/
│
├── backend/
│   ├── src/
│   │   ├── agents/
│   │   ├── core/
│   │   ├── embeddings/
│   │   ├── integrations/
│   │   ├── memory/
│   │   ├── prompts/
│   │   ├── tools/
│   │   └── workflows/
│   │
│   └── evaluation/
│
├── frontend/
│   └── src/
│
├── docker-compose.yml
└── README.md
```

For the detailed agentic workflow and AWS deployment architecture, see
the architecture diagrams in the main project README.
