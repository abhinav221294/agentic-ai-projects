# 🤖 Agentic AI Projects

A collection of hands-on **Generative AI and Agentic AI projects** exploring how LLMs, agents, RAG, tool calling, evaluation, memory, and application development can be combined to build practical AI systems.

This repository contains three projects built around different agentic AI use cases:

| Project                                    | Description                                                               | Key Concepts                                                              |
| ------------------------------------------ | ------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **[Content Blitz AI](./content_blitz_ai)** | Agentic content generation and research platform                          | Multi-agent workflows, LLM routing, web research, RAG, evaluation, memory |
| **[Finnie AI](./finnie_ai)**               | Agentic financial assistant for market, news, risk and investment queries | Agent routing, tool calling, RAG, hybrid rule + LLM decisions             |
| **[FinShield AI](./finshield_ai)**         | AI-powered insurance policy intelligence system                           | Multi-agent AI, RAG, vector search, document processing, risk analysis    |

---

## 📁 Projects

### 1. Content Blitz AI

**Content Blitz AI** is an agentic content-generation platform designed to transform user requests into research-backed content.

The system can support workflows such as:

* Blog generation
* LinkedIn content generation
* Web research and information synthesis
* AI image generation
* Research-backed content creation

The application uses an **intent/router layer** to determine the appropriate workflow and specialized agents for research and content generation. It also incorporates external research, multiple LLM providers, persistent storage, evaluation, and tool-based execution.

**Key technologies:**

* Python
* FastAPI
* LangChain / LangGraph
* Claude
* Google Gemini
* OpenAI
* Tavily
* PostgreSQL + pgvector
* Redis
* RAGAS
* LLM-as-a-Judge
* Docker
* AWS

The project also includes a frontend, automated tests, evaluation components, and Docker-based deployment support.

➡️ **[Explore Content Blitz AI](./content_blitz_ai)**

---

### 2. Finnie AI

**Finnie AI** is an agentic financial assistant that uses intelligent query routing to determine which specialized capability should handle a user's request.

Instead of sending every query directly to an LLM, Finnie AI uses a **hybrid routing approach**:

* Rule-based signals for high-confidence queries
* LLM-based classification for ambiguous queries
* Specialized agents for domain-specific tasks

The system includes:

* 📊 Market Agent — market and stock information
* 📰 News Agent — financial news retrieval
* ⚠️ Risk Agent — risk analysis
* 💡 Advisor Agent — investment-oriented guidance
* 📚 RAG Agent — knowledge retrieval and explanations
* 🔀 Router Agent — determines the appropriate workflow

The application also includes a Streamlit interface, external financial APIs, search capabilities, ChromaDB-based RAG, and automated router tests.

**Key technologies:**

* Python
* LangChain
* LangGraph
* OpenAI
* ChromaDB
* Pandas / NumPy
* Yahoo Finance
* Finnhub
* Tavily
* Streamlit

The repository includes evaluation of routing accuracy, RAG performance, robustness to noisy and ambiguous queries, and latency.

➡️ **[Explore Finnie AI](./finnie_ai)**

---

### 3. FinShield AI

**FinShield AI** is an AI-powered insurance policy intelligence system designed to help users understand complex insurance documents.

Users can upload an insurance policy and perform tasks such as:

* 📄 Generate executive summaries
* ❓ Ask questions about policy coverage
* ⚠️ Identify risks, exclusions and limitations
* 📘 Explain complex policy clauses
* ⚖️ Compare multiple insurance policies

The application uses a **router agent and specialized agents** for insurance questions, summaries, risk analysis, and policy comparison.

Its RAG pipeline processes uploaded PDFs, generates embeddings, stores them in ChromaDB, retrieves relevant sections, and provides context to the LLM before generating the response.

**Key technologies:**

* Python
* Streamlit
* Groq / Llama 3
* LangChain
* ChromaDB
* Sentence Transformers
* PyPDF
* RAG

The project also includes separate modules for agents, prompts, RAG, evaluation, testing, and Docker-based execution.

➡️ **[Explore FinShield AI](./finshield_ai)**

---

## 🧠 What This Repository Demonstrates

Across these projects, the repository explores several core areas of modern AI engineering:

* **LLM application development**
* **Agentic AI architectures**
* **Multi-agent systems**
* **Intent detection and routing**
* **Tool calling**
* **Retrieval-Augmented Generation (RAG)**
* **Vector databases**
* **External API integration**
* **Prompt engineering**
* **LLM evaluation**
* **AI application memory**
* **Testing and robustness**
* **FastAPI / Streamlit application development**
* **Docker-based deployment**

The projects progress from individual agent capabilities toward more complete AI applications combining **LLMs, agents, tools, data, retrieval, evaluation, and application interfaces**.

---

## 🗂️ Repository Structure

```text
agentic-ai-projects/
│
├── content_blitz_ai/
│   ├── backend/
│   ├── frontend/
│   ├── tests/
│   └── README.md
│
├── finnie_ai/
│   ├── agents/
│   ├── graph/
│   ├── tools/
│   ├── tests/
│   ├── ui/
│   └── README.md
│
├── finshield_ai/
│   ├── app/
│   ├── rag/
│   ├── llm/
│   ├── prompts/
│   ├── evaluation/
│   ├── data/
│   └── README.md
│
└── README.md
```

---

## 🎯 Purpose

These projects are part of an ongoing exploration of **Generative AI and Agentic AI engineering**, with an emphasis on moving beyond simple LLM demonstrations toward systems that combine:

**LLMs → Agents → Tools → Data → Retrieval → Evaluation → Applications**

Each project focuses on a different problem domain while experimenting with different approaches to building reliable and useful AI applications.
