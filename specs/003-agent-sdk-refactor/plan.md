# Implementation Plan: OpenAI Agents SDK Compliance & Streaming Refactor

**Branch**: `003-agent-sdk-refactor` | **Date**: June 8, 2026 | **Spec**: /specs/003-agent-sdk-refactor/spec.md
**Input**: Feature specification from `/specs/003-agent-sdk-refactor/spec.md`

## Summary

Refactor the AI orchestration layer in `my_project/backend/agent.py` and `app.py` to align with native OpenAI Agents SDK (v0.6.x) patterns. This includes implementing native input guardrails using `@input_guardrail`, defining structured output schemas with Pydantic and `AgentOutputSchema`, utilizing `RunContextWrapper` for dynamic instruction injection, and transitioning the chat endpoint to a streaming Server-Sent Events (SSE) architecture using `Runner.run_streamed`.

## Technical Context

**Language/Version**: Python 3.13+  
**Primary Dependencies**: `openai-agents>=0.6.3`, `fastapi`, `pydantic`, `qdrant-client`, `cohere`  
**Storage**: Qdrant (Vector Database)  
**Testing**: `pytest`, `httpx` (for async client testing)  
**Target Platform**: Vercel (Frontend), Hugging Face Spaces (Backend)
**Project Type**: Single project with backend focus  
**Performance Goals**: SC-001: Perceived latency (time to first token) reduced by 50% via streaming.  
**Constraints**: DO NOT change the model identifier `gemini-3.5-flash`.  
**Scale/Scope**: Refactor `agent.py` and `app.py` within `my_project/backend`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Operational Guidelines Compliance:
- Follow Explicit Instructions: ✅ Implementation aligns with the 4 core refactor requirements.
- Consult Primary Sources: ✅ References OpenAI Agents SDK v0.6 documentation patterns.
- Verify Information: ✅ Uses verified SDK patterns for guardrails and context.
- Strict Course Alignment: ✅ Maintains focus on Physical AI & Humanoid Robotics content.
- Academic Reliability: ✅ Grounding remains based on textbook content.
- Consistent Terminology: ✅ Maintains robotics terminology.
- Verified & Precise Citations: ✅ Citations are now a first-class citizen in the structured output.
- Reproducible & Accurate Examples: ✅ Examples will follow the new SDK patterns.
- Factual Integrity: ✅ Grounding remains strictly within the provided chunks.
- Docusaurus Adherence: ✅ (Frontend remains Docusaurus, unaffected by backend refactor).
- Modular Independence: ✅ (Backend service remains independent).

## Project Structure

### Documentation (this feature)

```text
specs/003-agent-sdk-refactor/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── chat-api-v2.md   # Updated Chat API with SSE
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
my_project/backend/
├── app.py              # Main API application (FastAPI SSE update)
├── agent.py            # AI agent implementation (SDK v0.6 refactor)
├── retrieval.py        # Vector retrieval (remains unchanged)
├── pyproject.toml      # Dependency management
├── models/
│   └── chat.py         # Updated Pydantic models for structured output
└── tests/
    ├── test_agent_v2.py # New tests for SDK compliance
    └── test_streaming.py# New tests for SSE endpoint
```

**Structure Decision**: Single project structure within `my_project/backend`. This feature specifically targets the orchestration layer.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | No violations detected | |
