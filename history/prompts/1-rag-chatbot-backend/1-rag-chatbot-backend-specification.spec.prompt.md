---
id: 1
title: rag-chatbot-backend-specification
stage: spec
date: '2025-12-17'
surface: agent
model: Claude Sonnet 4.5
feature: rag-chatbot-backend
branch: 1-rag-chatbot-backend
user: user
command: /sp.specify
labels:
  - specification
  - rag
  - chatbot
  - backend
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - specs/1-rag-chatbot-backend/spec.md
  - specs/1-rag-chatbot-backend/checklists/requirements.md
tests_yaml: []
---

# RAG Chatbot Backend Specification

## Prompt Text

Create a new folder inside specs and define requirements for a backend RAG chatbot integrated into a technical book website.
Context:
- Docusaurus frontend with ChatKit
- FastAPI backend (UV-managed project)
- OpenAI Agents SDK using Gemini as LLM
- Cohere embeddings
- Qdrant Cloud as vector store
- Book content already ingested
Requirements:
- Expose a single POST chat endpoint for ChatKit
- Embed user queries using Cohere
- Retrieve top-K relevant book chunks from Qdrant
- Provide retrieved chunks to the Agent's context.
- Pass the user query through the Agent runner
- Generate answers grounded only in book content
- Enforce guardrails to reject non-book-related queries
Hard constraints:
- The chat user interface MUST use the official ChatKit package
- No custom chat UI components are allowed
- No alternative chat libraries are allowed
- ChatKit is responsible only for UI and message transport
- Chat UI: ChatKit (official package only)
- Chatkit chatbot will be a floating widget on all web pages
- ChatKit MUST send user messages to a FastAPI POST endpoint as before
Constraints:
- Python 3.13 only
- No ingestion or chunking logic
- No LangChain or LlamaIndex
- All secrets loaded from root-level `.env` (Gemini API key placeholder required)
Success:
- Book-related questions return grounded answers
- Off-topic questions are safely refused

## Response Text

Created a comprehensive specification for the RAG chatbot backend feature. The specification includes:
- User scenarios with prioritized user stories
- Hard constraints defining strict requirements for ChatKit usage
- Functional requirements covering all specified functionality
- Success criteria with measurable outcomes
- A quality checklist validating the specification

The spec defines a system that exposes a POST chat endpoint, processes queries through Cohere embeddings, retrieves relevant content from Qdrant Cloud, uses OpenAI Agents SDK with Gemini for responses, enforces book-content-only guardrails, and implements a floating chat widget using the official ChatKit package exclusively.

## Outcome

Successfully created feature specification document at specs/1-rag-chatbot-backend/spec.md with accompanying quality checklist.