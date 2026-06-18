# Physical AI & Humanoid Robotics Textbook — Implementation Plan

**Version**: 2.0 (Reverse Engineered)
**Date**: 2026-06-18

## Architecture Overview

**Architectural Style**: Modular monolith with three independently deployable sub-projects

**Reasoning**: The system has three fundamentally different runtimes (Python async API, static React site, CLI ingestion script) with distinct lifecycles and deployment targets. Keeping them separate avoids coupling but requires clear contracts between them (Qdrant schema, API contract).

**Core Architectural Principle**: The LLM is never trusted with raw user input. Every query passes through three validation gates — input sanitization (`validation.py`), guardrail agent (`judge_agent`), and RAG grounding (only chunks + query go to the LLM).

## Layer Structure

### Sub-project 1: Backend (FastAPI + OpenAI Agents SDK)

**Responsibility**: Serve the RAG chatbot API, manage ChatKit protocol, persist conversations

```
backend/
├── app.py               # FastAPI application, routes, CORS, lifespan
├── agent.py             # OpenAI Agents SDK: agents, guardrails, instructions
├── config.py            # Environment-based configuration + validation
├── retrieval.py         # Cohere embedding + Qdrant vector search
├── chatkit_server.py    # ChatKit protocol bridge (extends ChatKitServer)
├── store.py             # SQLite persistence for ChatKit (extends Store)
├── models/
│   └── chat.py          # Pydantic schemas: ChatRequest, AgentResponse, HealthCheckResponse, etc.
├── utils/
│   └── validation.py    # Input sanitization: XSS, SQLi, code execution, path traversal
├── scripts/
│   └── read_db.py       # Debug utility to inspect chatkit.db
├── tests/               # pytest suite (15 tests)
├── Dockerfile           # python:3.13-alpine + uv
├── pyproject.toml       # Python dependencies
└── uv.lock              # Locked dependency versions
```

**Dependencies**: `→ Qdrant (cloud)`, `→ Cohere API`, `→ OpenRouter API`

### Sub-project 2: Frontend (Docusaurus + React)

**Responsibility**: Render textbook content, host ChatKit chat widget, inject page context

```
frontend/
├── docusaurus.config.ts    # Site config, plugins, navbar, footer
├── sidebars.ts             # Doc sidebar structure
├── package.json            # npm dependencies
├── vercel.json             # Vercel deployment config
├── docs/                   # MDX content (7 files: 6 chapters + glossary)
├── src/
│   ├── css/
│   │   └── custom.css      # Global styles: futuristic dark theme, glassmorphism
│   ├── pages/
│   │   ├── index.tsx        # Homepage: hero + module cards
│   │   └── index.module.css # Hero styles
│   ├── components/
│   │   ├── ChatKitWidget.tsx         # Floating chat widget
│   │   ├── ChatKitWidget.module.css  # Widget styles
│   │   └── HomepageFeatures/
│   │       ├── index.tsx             # Module cards
│   │       └── styles.module.css     # Card grid styles
│   ├── theme/
│   │   └── Root.tsx          # Global wrapper (includes ChatKitWidget)
│   └── utils/
│       ├── chatkit-fetch.ts         # Fetch interceptor (injects user ID + page context)
│       └── context-extractor.ts     # Extracts URL, title, headings from page
├── static/
│   ├── img/                 # Logo, favicon, social card
│   └── .nojekyll
└── code/                    # Code examples (URDF, ROS2, Unity, Python)
```

**Dependencies**: `→ Vercel (deploy)`, `→ Backend API (ChatKit endpoint)`

### Sub-project 3: Ingestion (Python CLI)

**Responsibility**: Convert MDX textbooks to vector embeddings in Qdrant

```
ingestion/
├── ingest_book.py       # CLI: scan MDX → convert → chunk → embed → store
├── requirements.txt     # pip dependencies
├── test_ingest_book.py  # Unit tests (unittest)
└── e2e_test.py          # End-to-end test
```

**Dependencies**: `→ Qdrant (cloud)`, `→ Cohere API`, `→ MDX files`

## Design Patterns Applied

### Pattern 1: ChatKit Protocol Bridge (Strategy)
- **Location**: `backend/chatkit_server.py`
- **Purpose**: Bridge the ChatKit protocol's `respond()` method to the RAG agent pipeline
- **Implementation**: `CustomChatKitServer(ChatKitServer[RequestContext])` overrides `respond()` to call `get_relevant_chunks()` + `Runner.run_streamed()` + `stream_agent_response()`

### Pattern 2: Store Adapter (Repository)
- **Location**: `backend/store.py`
- **Purpose**: Abstract SQLite persistence behind ChatKit's `Store[Any]` interface
- **Implementation**: `SQLiteStore(Store[Any])` implements all required methods with aiosqlite; lazy initialization via `_ensure_initialized()`

### Pattern 3: Guardrail (Decorator)
- **Location**: `backend/agent.py`
- **Purpose**: Pre-filter off-topic queries before they reach the LLM
- **Implementation**: `@input_guardrail` decorator on `check_query_relevance()` which runs `judge_agent` to classify the query
- **Fail-open**: On error, `tripwire_triggered=False` (let query through rather than block)

### Pattern 4: Dynamic Instructions (Function Injection)
- **Location**: `backend/agent.py` + `chatkit_server.py`
- **Purpose**: Inject conversation history, page context, and retrieved chunks into the LLM system prompt
- **Implementation**: `book_knowledge_instructions()` reads `ctx.context["book_chunks"]`; `chatkit_server.py` wraps it with history + page context

### Pattern 5: SSE Streaming (Observer)
- **Location**: `backend/app.py` + `chatkit_server.py`
- **Purpose**: Stream LLM tokens to the client in real-time
- **Implementation**: `chat_stream_generator()` yields SSE-formatted events from `Runner.run_streamed()`; ChatKit protocol uses `stream_agent_response()` with `ChatKitAgentContext`

### Pattern 6: Retry with Exponential Backoff
- **Location**: `backend/retrieval.py`, `ingestion/ingest_book.py`
- **Purpose**: Handle transient API failures (Cohere, Qdrant)
- **Implementation**: `for attempt in range(max_retries): try...except: await asyncio.sleep(2 ** attempt)` — 1s, 2s, 4s

## Data Flow

### Chat Query Flow
```
1. User types question in ChatKit widget
2. chatkit-fetch.ts intercepts fetch, injects X-User-ID + pageContext
3. FastAPI receives POST /chatkit
4. CustomChatKitServer.respond() is called with thread + message + context
5. Load last 10 items from SQLite for conversation history
6. Format history string + page context string
7. get_relevant_chunks() embeds query with Cohere v2 → searches Qdrant
8. Dynamic instructions built: history + page context + chunks + base instructions
9. Runner.run_streamed() with transient agent clone
10. stream_agent_response() yields ChatKit SSE events
11. SQLiteStore.save_item() persists the exchange
```

### Ingestion Flow
```
1. CLI args parsed: --docs-dir, --chunk-size, --chunk-overlap, etc.
2. scan_mdx_files() walks docs directory for .mdx files
3. For each file:
   a. read_mdx_file() with size validation + encoding fallback
   b. extract_module_and_chapter_from_path()
   c. convert_mdx_to_text() strips JSX, Markdown, code blocks
   d. chunk_text(512 chars, 50 overlap)
   e. cohere.embed(texts, model="embed-multilingual-v3.0", input_type="search_document")
   f. Batch store in Qdrant (100 per batch)
4. verify_stored_vectors() samples and validates metadata
```

### Frontend Page Load Flow
```
1. Docusaurus builds static HTML from MDX + React components
2. Root.tsx renders page content + ChatKitWidget (always mounted)
3. ChatKitWidget creates persisted student ID (localStorage)
4. ChatKit SDK initializes with custom fetch interceptor
5. User navigates → context-extractor.ts captures URL/title/headings
6. On chat message → chatkit-fetch.ts injects page context into protocol body
```

## Technology Stack

### Backend
| Component | Choice | Rationale |
|---|---|---|
| Language | Python 3.13 | Async support, rich AI/ML ecosystem |
| Web Framework | FastAPI 0.137+ | Native async, Pydantic integration, auto-validation |
| LLM SDK | openai-agents 0.17.5+ | Multi-agent orchestration, guardrails, streaming |
| Vector DB | Qdrant Cloud | Async client, high-performance, managed |
| Embeddings | Cohere API v2 | Multilingual, high-quality, async client |
| LLM Provider | OpenRouter | Multi-model access, fallback chain |
| Persistence | SQLite (aiosqlite) | Zero-config, async, sufficient for single-process |
| Chat Protocol | openai-chatkit 1.6.5+ | Managed conversation threads, SSE streaming |
| Package Manager | uv | Fast, deterministic, Python 3.13 compatible |
| Container | python:3.13-alpine | Minimal image size (~120MB) |

### Frontend
| Component | Choice | Rationale |
|---|---|---|
| Language | TypeScript 5.6 | Type safety, better DX |
| Framework | React 19 | Latest React with concurrent features |
| Static Site | Docusaurus 3.9 | Optimized for documentation, MDX support |
| Chat SDK | @openai/chatkit-react 1.4+ | ChatKit protocol React wrapper |
| CDN Chat | chatkit.js (OpenAI CDN) | Required by ChatKit React import |
| Styling | CSS Modules + custom.css | Scoped styles + global design system |
| Code Examples | raw-loader | Load .py/.cs/.world files as raw strings |

### Infrastructure
| Component | Choice | Rationale |
|---|---|---|
| Backend Hosting | Hugging Face Spaces | Free tier, Docker support, GPU optional |
| Frontend Hosting | Vercel | Free tier, automatic deploys from GitHub |
| CI/CD | GitHub Actions | Integrated with GitHub, free for public repos |
| Version Control | Git (GitHub) | Industry standard |

## Module Breakdown

### Module: app.py (FastAPI Application)
- **Purpose**: HTTP entry point; route handlers, CORS, lifespan, middleware
- **Routes**: `GET /`, `GET /health`, `POST /chat`, `POST /chatkit`, `POST /api/chatkit/session`, `POST /api/chatkit/refresh`, `GET /api/chatkit/user`
- **Key Functions**: `chat_stream_generator()` — SSE producer from agent stream; `chatkit_protocol()` — ChatKit endpoint handler
- **Complexity**: High (orchestrates agent, retrieval, ChatKit, SSE)
- **Dependencies**: agent, retrieval, chatkit_server, models, utils.validation

### Module: agent.py (OpenAI Agents SDK)
- **Purpose**: Define AI agents, guardrails, and dynamic instruction builder
- **Key Classes/Functions**: `judge_agent` (off-topic classifier), `book_knowledge_agent` (RAG answerer), `check_query_relevance()` (guardrail), `book_knowledge_instructions()` (dynamic prompt), `_build_openai_client()` (factory)
- **Complexity**: Medium
- **Dependencies**: config, models.chat, agents SDK

### Module: retrieval.py (Vector Search)
- **Purpose**: Embed user query with Cohere, search Qdrant, return formatted chunks
- **Key Functions**: `get_relevant_chunks()` — retry wrapper around embed + search; `embed_query()` — standalone embedding
- **Dependencies**: config, cohere SDK, qdrant-client

### Module: chatkit_server.py (ChatKit Bridge)
- **Purpose**: Extend ChatKitServer to bridge protocol to RAG pipeline
- **Key Methods**: `respond()` — builds history + context + dynamic instructions, runs agent, streams events; `initialize_chatkit_server()` — factory
- **Complexity**: High (multi-step orchestration with error isolation)
- **Dependencies**: store, agent, retrieval, models.chat

### Module: store.py (SQLite Persistence)
- **Purpose**: Implement ChatKit's Store interface with SQLite
- **Key Methods**: `initialize()`, `load_thread()`, `create_thread()`, `save_thread()`, `load_thread_items()`, `add_thread_item()`, `save_item()`, `load_item()`, `delete_thread()`, `delete_thread_item()`, `save/load/delete_attachment()`, `load_threads()`
- **Complexity**: Medium (12 CRUD methods)
- **Dependencies**: aiosqlite, chatkit.store, chatkit.types

### Module: ingest_book.py (Ingestion CLI)
- **Purpose**: End-to-end pipeline: scan → read → convert → chunk → embed → store → verify
- **Key Classes/Functions**: `VectorRecord` (data model), `ProgressTracker`, `retry_with_backoff()`, `setup_cohere_client()`, `setup_qdrant_client()`, `process_file_for_vectorization()`, `create_qdrant_collection()`, `store_vectors_in_qdrant()`, `verify_stored_vectors()`, `main()`
- **Complexity**: High (file I/O + API orchestration + error handling)
- **Dependencies**: cohere, qdrant-client, dotenv

### Module: ChatKitWidget.tsx (React Component)
- **Purpose**: Floating chat assistant with text selection support
- **Key Features**: `useChatKit()` hook, `createChatKitFetch()` interceptor, text selection "Ask AI" button, error banner with auto-dismiss
- **Complexity**: Medium
- **Dependencies**: @openai/chatkit-react, utils/chatkit-fetch, ChatKitWidget.module.css

## Regeneration Strategy

### Option 1: Specification-First Rebuild (Recommended)

**Timeline**: 4-6 weeks (senior full-stack engineer)

#### Phase 1: Foundation (Week 1)
1. Set up monorepo structure with three sub-projects
2. Configure uv for backend, npm for frontend
3. Implement `config.py` with env var loading + validation
4. Set up Dockerfile for backend
5. Set up Docusaurus scaffold with futuristic theme

#### Phase 2: Data Layer (Week 2)
1. Implement `SQLiteStore` with all 12 CRUD methods + lazy init
2. Implement ingestion pipeline (`ingest_book.py`): MDX → text → chunks
3. Integrate Cohere embedding + Qdrant storage
4. Add retry logic with exponential backoff
5. Add verification tests

#### Phase 3: AI Layer (Week 3)
1. Implement `agent.py`: OpenAIChatCompletionsModel, dynamic instructions, guardrail
2. Implement `retrieval.py`: embed + search with retry
3. Implement `chatkit_server.py`: CustomChatKitServer with respond()
4. Wire up agent + retrieval + store in chat_stream_generator
5. Add SSE streaming

#### Phase 4: API Layer (Week 4)
1. Implement `app.py`: all routes, CORS, lifespan, middleware
2. Implement `validation.py`: XSS/SQLi/code-exec/path-traversal checks
3. Wire ChatKit protocol endpoint
4. Add health check + root endpoints

#### Phase 5: Frontend (Week 5)
1. Build `ChatKitWidget.tsx` with useChatKit, text selection, error handling
2. Build `chatkit-fetch.ts` + `context-extractor.ts` interceptors
3. Build homepage with hero + module cards
4. Implement custom.css futuristic design system
5. Configure Docusaurus navbar, footer, plugins

#### Phase 6: Deployment & CI (Week 6)
1. Write `deploy.yml` with all required files + test step
2. Configure HF Space Docker deployment
3. Configure Vercel deployment
4. Set up GitHub secrets for API keys
5. E2E testing across all three sub-projects

### Option 2: Incremental Refactoring (Current Codebase)

**Timeline**: 1-2 weeks

1. Fix deploy.yml (add missing files)
2. Move test deps to dev group
3. Fix Dockerfile uv flag
4. Remove dead code (initialize_agent)
5. Add .env.example
6. Add test execution to CI
7. Add `.gitignore` coverage for `backend/.env`
8. Rotate/remove committed API keys

## Improvement Opportunities

### Technical Improvements
- [ ] **Replace raw SQLite queries with migration system**: Current `CREATE TABLE IF NOT EXISTS` approach has no migration path for schema changes
- [ ] **Add structured logging (JSON)**: Current `logging` module outputs plain text; structured JSON would enable log aggregation
- [ ] **Add request ID tracing**: `X-Request-ID` middleware for correlating logs across calls
- [ ] **Add OpenAPI/Swagger docs**: FastAPI generates these automatically but they're not exposed

### Architectural Improvements
- [ ] **Extract RAG pipeline into standalone service**: Agent orchestration is duplicated between `app.py` (chat_stream_generator) and `chatkit_server.py` (respond method)
- [ ] **Implement connection pooling for Cohere/Qdrant**: Currently creates new clients on module import; no explicit pooling
- [ ] **Add `__init__.py` to `models/` and `utils/`**: Works via implicit namespace packages in Python 3.13, but best practice

### Operational Improvements
- [ ] **Run tests in CI**: Add `uv run pytest tests/` step before deploy
- [ ] **Health check with dependency verification**: Current `/health` returns "healthy" even if Qdrant/Cohere are unreachable
- [ ] **Graceful shutdown**: Lifespan should close Qdrant/Cohere client connections
- [ ] **Monitoring**: Add Prometheus metrics for request count, latency, error rate
