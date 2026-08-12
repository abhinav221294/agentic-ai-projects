# 🚀 Content Blitz AI

## AI-Powered Agentic Content Marketing Assistant

Content Blitz AI is an **agentic AI-powered content marketing assistant** that can understand a user's request, determine the appropriate workflow, optionally perform web research, generate a content strategy, and produce different types of marketing content.

The system is built using a **LangGraph-based multi-agent architecture** with specialized agents for research, strategy, blog generation, LinkedIn generation, and image generation.

---

# 📌 Table of Contents

* [Project Overview](#-project-overview)
* [Architecture](#-architecture)
* [AWS Deployment Architecture](#-aws-deployment-architecture)
* [Key Features](#-key-features)
* [Agentic Workflow](#-agentic-workflow)
* [Agents](#-agents)
* [Tools](#-tools)
* [Research Pipeline](#-research-pipeline)
* [Memory and Retrieval](#-memory-and-retrieval)
* [LLM Stack](#-llm-stack)
* [Evaluation Framework](#-evaluation-framework)
* [AWS Services](#-aws-services)
* [Project Structure](#-project-structure)
* [Technology Stack](#-technology-stack)
* [Configuration](#-configuration)
* [Local Development](#-local-development)
* [Docker](#-docker)
* [Testing](#-testing)
* [Security](#-security)
* [Observability](#-observability)
* [Future Improvements](#-future-improvements)

---

# 🎯 Project Overview

Content Blitz AI allows users to request different types of marketing content using natural language.

Examples:

```text
Write a detailed blog about Agentic AI
```

```text
Create a LinkedIn post about RAG
```

```text
Generate a futuristic AI agent visual
```

```text
Research the latest developments in Agentic AI
```

Instead of sending every request directly to a single LLM, Content Blitz AI uses an **agentic workflow** to determine:

1. What the user wants.
2. Whether external research is required.
3. Which tools should be executed.
4. What content strategy should be followed.
5. Which specialized content agent should generate the response.
6. How the generated output should be evaluated.

---

# 🏗️ Architecture

## Agentic AI Architecture

The application uses **LangGraph** to orchestrate the multi-agent workflow.

### Agentic Architecture Diagram

**[INSERT AGENTIC ARCHITECTURE DIAGRAM HERE]**

> Replace this placeholder with:
>
> `content_blitz_architecture.png`

The architecture diagram illustrates the complete agentic workflow, including:

* Query Handler
* Research Decision
* Research Agent
* Strategist
* Content Dispatcher
* Blog Writer
* LinkedIn Writer
* Image Generation
* Fallback
* Workflow completion

### High-Level Flow

```text
User
  ↓
Query Handler
  ↓
Research Decision
  │
  ├── NO_RESEARCH ─────────────┐
  │                            │
  └── RESEARCH                 │
       ↓                       │
   Research Agent              │
       ↓                       │
   Strategist ◄───────────────┘
       ↓
Content Dispatcher
       │
       ├── Blog Writer
       ├── LinkedIn Writer
       └── Image Generation
       │
       ↓
     Output
       ↓
      END
```

---

# ☁️ AWS Deployment Architecture

Content Blitz AI is containerized and designed for deployment on AWS using managed infrastructure.

### AWS Architecture Diagram

**[INSERT AWS ARCHITECTURE DIAGRAM HERE]**

> Replace this placeholder with the AWS deployment architecture diagram.

The AWS architecture should illustrate the production infrastructure, including:

* Frontend hosting
* Backend API
* Application Load Balancer
* ECS / Fargate
* Amazon ECR
* PostgreSQL / pgvector
* Redis
* AWS Secrets Manager
* IAM
* CloudWatch
* VPC networking
* External AI providers

### High-Level AWS Flow

```text
                    Internet
                       │
                       ▼
                 Frontend
                       │
                       ▼
             Application Load Balancer
                       │
                       ▼
                 ECS / Fargate
                  Backend API
                       │
        ┌──────────────┼───────────────┐
        │              │               │
        ▼              ▼               ▼
 PostgreSQL          Redis       Secrets Manager
 + pgvector
        │
        ▼
 Persistent Memory

Backend
   │
   ├── Claude
   ├── Gemini
   ├── OpenAI
   └── Tavily
```

---

# ✨ Key Features

## Multi-Agent Architecture

The system contains specialized agents for different responsibilities:

* Query handling
* Research decision
* Web research
* Content strategy
* Blog generation
* LinkedIn generation
* Image generation
* Fallback handling

---

## Intelligent Research Decision

The system determines whether external research is required.

Examples:

| Request                    | Research            |
| -------------------------- | ------------------- |
| What is a vector database? | Usually unnecessary |
| Latest AI developments     | Required            |
| Current LLM API pricing    | Required            |
| Latest Databricks changes  | Required            |

This reduces unnecessary web searches, latency, and API costs.

---

## Web Research

When research is required, the research agent:

1. Optimizes the user query.
2. Generates search queries.
3. Executes web search.
4. Collects sources.
5. Formats retrieved information.
6. Synthesizes the research.

---

## Content Generation

The application supports:

### 📝 Blog Generation

The Blog Writer Agent generates:

* Title
* Outline
* Long-form content
* Research-backed content
* Word count

### 💼 LinkedIn Generation

The LinkedIn Writer Agent generates:

* Hook
* LinkedIn post
* CTA
* Professional formatting

### 🎨 Image Generation

The Image Agent:

1. Validates the request.
2. Builds the image prompt.
3. Invokes the image generation tool.
4. Returns the generated image URL.

---

# 🤖 Agentic Workflow

## 1. Query Handler

Processes the initial user request and determines the appropriate workflow.

## 2. Research Decision

Determines whether external research is required.

## 3. Research Agent

Performs query optimization, retrieval, source aggregation, and synthesis.

## 4. Strategist

Creates a content strategy using the user request, research context, and conversation context.

## 5. Content Dispatcher

Routes the strategy to the appropriate content generation agent.

## 6. Specialized Content Agent

Generates the final blog, LinkedIn post, or image.

---

# 📊 Evaluation

The project includes a dedicated evaluation framework covering:

* Intent classification
* Research decision
* Tool calling
* Research quality
* LLM output validation
* RAGAS evaluation
* Final output quality
* LLM-as-a-Judge evaluation

### Current Results

```text
Tool Calling Accuracy       : 100%
Research Quality             : 6/6
LLM Output Validation        : 12/12
Final Output Quality         : 4.02/5
```

The final-output evaluator evaluates generated content against criteria specific to each content type.

---

# 🏁 Project Status

**Status:** Capstone / Production-oriented Agentic AI Application

**Core Areas:**

* Agentic AI
* LangGraph
* Multi-agent orchestration
* Tool calling
* Web research
* RAG
* Vector memory
* LLM orchestration
* Content generation
* Image generation
* Automated evaluation
* Docker
* AWS deployment

---
