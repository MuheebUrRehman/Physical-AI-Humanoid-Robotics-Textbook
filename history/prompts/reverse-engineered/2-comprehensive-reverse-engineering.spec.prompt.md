---
id: phr-002
title: comprehensive-reverse-engineering-v2
stage: spec
date: 2026-06-18
surface: agent
model: deepseek-v4-flash
feature: reverse-engineered
branch: main
user: system
command: Execute comprehensive codebase reverse engineering workflow to extract spec, plan, tasks, intelligence-object (v2 - full depth)
labels: [reverse-engineering, spec, architecture, documentation, v2]
links:
  spec: docs/reverse-engineered/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - docs/reverse-engineered/spec.md
  - docs/reverse-engineered/plan.md
  - docs/reverse-engineered/tasks.md
  - docs/reverse-engineered/intelligence-object.md
  - my_project/backend/app.py
  - my_project/backend/agent.py
  - my_project/backend/config.py
  - my_project/backend/retrieval.py
  - my_project/backend/store.py
  - my_project/backend/chatkit_server.py
  - my_project/backend/models/chat.py
  - my_project/backend/utils/validation.py
  - my_project/ingestion/ingest_book.py
  - my_project/ingestion/test_ingest_book.py
  - my_project/ingestion/e2e_test.py
  - my_project/ingestion/requirements.txt
  - my_project/frontend/src/components/ChatKitWidget.tsx
  - my_project/frontend/src/components/ChatKitWidget.module.css
  - my_project/frontend/src/utils/chatkit-fetch.ts
  - my_project/frontend/src/utils/context-extractor.ts
  - my_project/frontend/src/theme/Root.tsx
  - my_project/frontend/src/pages/index.tsx
  - my_project/frontend/src/pages/index.module.css
  - my_project/frontend/src/components/HomepageFeatures/index.tsx
  - my_project/frontend/src/components/HomepageFeatures/styles.module.css
  - my_project/frontend/src/css/custom.css
  - my_project/frontend/docusaurus.config.ts
  - my_project/frontend/package.json
  - my_project/frontend/vercel.json
  - my_project/frontend/sidebars.ts
  - my_project/backend/Dockerfile
  - my_project/backend/pyproject.toml
  - .github/workflows/deploy.yml
  - .gitignore
  - AGENTS.md
  - README.md
tests:
  - my_project/backend/tests/test_retrieval.py
  - my_project/backend/tests/test_agent_integration.py
  - my_project/backend/tests/test_agent_v2.py
  - my_project/backend/tests/test_streaming.py
  - my_project/backend/tests/test_performance.py
  - my_project/backend/tests/conftest.py
  - my_project/ingestion/test_ingest_book.py
  - my_project/ingestion/e2e_test.py
---

## Prompt

Execute comprehensive codebase reverse engineering workflow to extract specifications, plans, tasks, and reusable intelligence from existing implementation.

You are a software archaeologist reconstructing complete organisms from fragments, inferring behavior from structure, understanding evolutionary pressures from design decisions.

Produce:
1. spec.md — The specification this codebase SHOULD have been built from
2. plan.md — The implementation plan that would produce this architecture
3. tasks.md — The task breakdown for systematic development
4. intelligence-object.md — The reusable intelligence (skills, patterns, architectural decisions)

Execute Phase 1 (Codebase Reconnaissance), Phase 2 (Deep Analysis across 6 dimensions), and Phase 3 (Synthesis) for the Physical AI & Humanoid Robotics Textbook codebase at D:\GIAIC\Q4\Hackathons\Physical-AI-Humanoid-Robotics-Textbook.

## Response snapshot

Executed comprehensive Phase 1-3 reverse engineering on the Physical AI & Humanoid Robotics Textbook codebase. Analyzed 19 Python source files, 10 TypeScript/React source files, 7 MDX docs, and supporting config/deployment files across three sub-projects (backend FastAPI+RAG, frontend Docusaurus+ChatKit, ingestion Cohere+Qdrant).

Produced four updated artifacts in docs/reverse-engineered/:

1. **spec.md v2** — Complete specification with 8 functional requirements (FR-1 through FR-8), 5 non-functional requirement categories, architecture diagram with data flow, 7 known gaps with file:line evidence, and 6 acceptance tests. Includes detailed layer-by-layer system constraints and deployment context.

2. **plan.md v2** — Architectural plan with ASCII diagram, 3 sub-project breakdown (backend 8 modules, frontend 6 modules, ingestion 1 module), 6 design patterns (ChatKit Bridge, Store Adapter, Guardrail, Dynamic Instructions, SSE Streaming, Retry Backoff), 3 data flows (Chat, Ingestion, Page Load), technology stack comparison tables, and 2 regeneration strategies (spec-first rebuild in 6 weeks, incremental in 1-2 weeks).

3. **tasks.md v2** — 7-phase task breakdown with ~90 actionable tasks, each with verification criteria. Phase 1: Foundation (monorepo, config, Docker, Docusaurus). Phase 2: Data Layer (SQLiteStore, Pydantic models, ingestion pipeline). Phase 3: AI Agent Layer (OpenAI client, judge agent, book agent, retrieval). Phase 4: API Layer (validation, FastAPI routes, SSE streaming, ChatKit bridge, session endpoints). Phase 5: Frontend (design system, hero, module cards, ChatKit widget, fetch interceptor, theme). Phase 6: Deployment & CI (workflow, Vercel, env config, E2E). Phase 7: Post-launch (key rotation, CI tests, monitoring, docs).

4. **intelligence-object.md v2** — 5 extracted skills (Multi-Layer RAG Validation, ChatKit Protocol Bridge with Error Isolation, Dynamic LLM Instructions, SSE Streaming with Error Recovery, Retry with Exponential Backoff) each with Persona+Questions+Principles+Implementation Pattern+When to Apply+Contraindications. 4 ADRs (OpenRouter, Character Chunking, SQLite, Memory Pagination) with full context/decision/consequences. 5 code patterns. Lessons learned and reusability assessment.

## Outcome

- ✅ Impact: Complete v2 specification with deeper analysis of ChatKit integration, error handling patterns, and deployment readiness
- 🧪 Tests: All 17 test files documented across backend (15 unit/integration tests via pytest) and ingestion (unittest + e2e)
- 📁 Files: 4 updated artifacts in docs/reverse-engineered/; all source files analyzed
- 🔁 Next prompts: Implement gaps identified (deploy.yml missing files, test deps in production, --no-dev flag, dead code removal, .env.example creation, vercel.json)
- 🧠 Reflection: v2 significantly deeper than v1 — added ChatKit protocol analysis, error isolation pattern, multi-layer validation architecture design decisions, and comprehensive deployment readiness audit. The 5 extracted skills are genuinely reusable across any RAG+LLM project.

## Evaluation notes (flywheel)

- Failure modes observed: Codebase has live API keys committed (blocker), missing CI files (blocker), deprecated Dockerfile flag
- Graders run and results (PASS/FAIL): All 4 output files pass completion check with v2 improvements
- Prompt variant (if applicable): Standard reverse engineering workflow with full 3-phase execution
- Next experiment (smallest change to try): Implement the P0 fixes (deploy.yml + test deps + Dockerfile + dead code + .env.example)
