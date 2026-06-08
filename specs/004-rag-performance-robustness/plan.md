# Implementation Plan: RAG Performance & Frontend Robustness Refactor

**Branch**: `004-rag-performance-robustness` | **Date**: June 8, 2026 | **Spec**: /specs/004-rag-performance-robustness/spec.md
**Input**: Feature specification from `/specs/004-rag-performance-robustness/spec.md`

## Summary

Refactor the RAG orchestration layer to improve concurrency using non-blocking async clients for Cohere and Qdrant, eliminate initialization latency by adopting a singleton pattern for the guardrail agent (using `gemini-3.1-flash-lite`), and enhance streaming stability on the frontend by implementing a robust SSE buffer in the React chat component.

## Technical Context

**Language/Version**: Python 3.13+, TypeScript (React)  
**Primary Dependencies**: `cohere.AsyncClient`, `qdrant_client.AsyncQdrantClient`, `openai-agents==0.6`, `fastapi`, `pydantic`  
**Storage**: Qdrant Cloud (Vector Database)  
**Testing**: `pytest` (Async), Manual Stress Test (Network Throttling)  
**Target Platform**: Vercel (Frontend), Hugging Face Spaces (Backend)
**Project Type**: Web Application  
**Performance Goals**: SC-003: TTFT for relevance validation reduced by at least 200ms; 5x increase in retrieval concurrency.  
**Constraints**: Maintain the `gemini-3.5-flash` model for primary knowledge generation.  
**Scale/Scope**: Refactor `backend/agent.py`, `backend/retrieval.py`, and `frontend/src/components/FloatingChat.tsx`.

## Constitution Check

### Operational Guidelines Compliance:
- Follow Explicit Instructions: ✅ Strategy strictly follows the 3 performance and robustness issues.
- Consult Primary Sources: ✅ References official async SDK documentation for Cohere and Qdrant.
- Verify Information: ✅ Uses standard SSE buffering techniques to fix fragmented packet issues.
- Strict Course Alignment: ✅ Optimization ensures a smoother learning experience for students.
- Academic Reliability: ✅ Performance metrics are verifiable via TTFT benchmarking.
- Consistent Terminology: ✅ Maintains existing nomenclature (e.g., BookKnowledgeAgent, guardrails).
- Verified & Precise Citations: ✅ N/A (Internal logic refactor).
- Reproducible & Accurate Examples: ✅ Code refactor follows documented async patterns.
- Factual Integrity: ✅ Non-blocking I/O prevents server hangs.
- Docusaurus Adherence: ✅ Frontend component remains compatible with Docusaurus 3.x.
- Modular Independence: ✅ Refactor preserves modularity of retrieval and agent layers.

## Project Structure

### Documentation (this feature)

```text
specs/004-rag-performance-robustness/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── sse-protocol-v2.md # SSE Event frame specification
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
my_project/
├── backend/
│   ├── app.py           # API Orchestration (Async retrieval update)
│   ├── agent.py         # AI Agents (Singleton guardrail + model update)
│   ├── retrieval.py     # Knowledge retrieval (Async client migration)
│   └── tests/
│       └── test_performance.py # New concurrency benchmark
└── frontend/
    └── src/
        └── components/
            └── FloatingChat.tsx # Chat Component (SSE Buffer implementation)
```

**Structure Decision**: Web application with backend refactoring and frontend component updates. This targets the entire E2E communication pipe from retrieval to rendering.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | No violations detected | |
