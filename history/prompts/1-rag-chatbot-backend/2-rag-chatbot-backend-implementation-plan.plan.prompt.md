---
id: 2
title: rag-chatbot-backend-implementation-plan
stage: plan
date: '2025-12-17'
surface: agent
model: Claude Sonnet 4.5
feature: rag-chatbot-backend
branch: 2-rag-chatbot-backend
user: user
command: /sp.plan
labels:
  - plan
  - rag
  - chatbot
  - backend
  - architecture
links:
  spec: specs/1-rag-chatbot-backend/spec.md
  ticket: null
  adr: null
  pr: null
files_yaml:
  - specs/1-rag-chatbot-backend/plan.md
  - specs/1-rag-chatbot-backend/checklists/implementation.md
tests_yaml: []
---

# RAG Chatbot Backend Implementation Plan

## Prompt Text

Update the prompt and the plan.md with this modification.
Use 'openai-agents' to install OpenAI Agents SDK
Don't use requirements.txt; use project.toml instead
And access the api keys at the project root, not the backend folder root
Use official docs for the technologies used for development
OpenAI agents SDK: https://openai.github.io/openai-agents-python/
Chatkit: https://platform.openai.com/docs/guides/chatkit
fastapi:https://fastapi.tiangolo.com/
Hard constraints:
- The chat user interface MUST use the official ChatKit package
- No custom chat UI components are allowed
- No alternative chat libraries are allowed
- ChatKit is responsible only for UI and message transport
- Chat UI: ChatKit (official package only)
- Chatkit chatbot will be a floating widget on all web pages
- ChatKit MUST send user messages to a FastAPI POST endpoint as before
Non-negotiable rules:
- ChatKit MUST be the only chat UI
- Frontend must not implement custom chat state, rendering, or transport
- Backend responses must strictly follow ChatKit's expected API schema
- don't change backend if isnt necessary

## Response Text

Updated the implementation plan for the RAG chatbot backend with the requested modifications:

- Changed dependency from 'openai' to 'openai-agents==0.6' for the OpenAI Agents SDK (specific version requirement)
- Replaced requirements.txt with project.toml for dependency management
- Updated project structure to show project.toml inside the backend folder
- Updated configuration to access API keys from .env file at project root
- Added official documentation URLs for OpenAI Agents SDK, ChatKit, and FastAPI
- Updated implementation steps to reference project.toml instead of requirements.txt
- Updated configuration module to load secrets from .env file at project root
- Updated dependencies section to reference openai-agents==0.6 with official docs URL
- Updated configuration requirements to specify .env file at project root
- Enhanced agent.py module description to specify initialization using openai-agents v0.6 following official SDK documentation
- Updated agent.py implementation to inject retrieved chunks into the Agent class `context` property exactly as documented
- Updated agent.py implementation to pass user query via the documented runner class
- Added requirement to apply documented guardrail mechanisms to restrict answers to book content
- Updated technical context to include hard rule constraints (use openai-agents==0.6 exclusively, follow official SDK documentation verbatim, etc.)
- Added complexity tracking for the openai-agents==0.6 constraint
- Incorporated hard constraints for ChatKit usage including floating widget implementation and exclusive use of official ChatKit package
- Added non-negotiable rules ensuring ChatKit is the only chat UI, frontend doesn't implement custom chat state/rendering/transport, and backend responses strictly follow ChatKit's expected API schema

## Outcome

Successfully updated the implementation plan document at specs/1-rag-chatbot-backend/plan.md with the requested modifications. The updated plan now includes openai-agents==0.6 dependency (specific version), project.toml for dependency management, API keys accessed from project root, official documentation references, enhanced agent.py module specifications for proper context injection and guardrails, technical context with hard rule constraints, non-negotiable ChatKit requirements, and complexity tracking. The plan is ready for the next phase (/sp.tasks).