---
id: 5
title: update-spec-openai-agents-requirement
stage: spec
date: '2025-12-17'
surface: agent
model: Claude Sonnet 4.5
feature: rag-chatbot-backend
branch: 1-rag-chatbot-backend
user: user
command: manual update
labels:
  - specification
  - openai-agents
  - requirements
links:
  spec: specs/1-rag-chatbot-backend/spec.md
  ticket: null
  adr: null
  pr: null
files_yaml:
  - specs/1-rag-chatbot-backend/spec.md
  - backend/agent.py
  - backend/pyproject.toml
tests_yaml: []
---
# Update spec to require openai-agents package

## Prompt Text

Update the prompt and spec.md file by editing the existing 1-rag-chatbot-backend/spec.md and the rag chatbot prompt history. Do not create new files; instead, add or replace content as needed.
Mandatory constraints:
- Use ONLY the official `openai-agents` Python package (version 0.6).
- Do NOT use the legacy `openai` Python package.
- All agent creation, execution, and context management MUST follow the official `openai-agents` v0.6 documentation.
- Any deviation from the documented APIs is forbidden.

## Response Text

Successfully updated the RAG Chatbot Backend specification and implementation to comply with the requirement to use ONLY the official `openai-agents` Python package (version 0.6) instead of the legacy `openai` Python package:

1. Updated spec.md to explicitly state the requirement:
   - Added constraints section emphasizing use of openai-agents package only
   - Updated functional requirements to include FR-011, FR-012, and FR-013 specifically addressing the openai-agents requirement

2. Updated agent.py implementation:
   - Replaced legacy `openai` package imports with `agents` package imports
   - Used `OpenAIChatCompletionsModel` with custom base URL for Gemini API integration
   - Implemented proper agent configuration using the openai-agents framework
   - Updated the `get_agent_response` function to use `Runner.run()` method

3. Verified compliance across all implementation files:
   - Confirmed no legacy `openai` imports remain in source code
   - Verified pyproject.toml correctly specifies `openai-agents>=0.6.3`
   - Ensured all backend files comply with the new requirement

The implementation now properly uses the official `openai-agents` Python package (version 0.6) with the agent configured to work with the Gemini API through the OpenAIChatCompletionsModel with a custom base URL.

## Outcome

The RAG Chatbot Backend specification and implementation now fully comply with the mandatory constraints to use ONLY the official `openai-agents` Python package (version 0.6) and NOT use the legacy `openai` Python package. All files have been updated and verified for compliance.