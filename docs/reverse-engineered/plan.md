# Physical AI & Humanoid Robotics Textbook — Implementation Plan

**Version**: 3.1 (Reverse Engineered)
**Date**: 2026-06-21

## Architecture Overview

**Architectural Style**: Modular monolith with three independently deployable sub-projects

**Reasoning**: The system has three fundamentally different runtimes (Python async API, static React site, CLI ingestion script) with distinct lifecycles and deployment targets. Keeping them separate avoids coupling but requires clear contracts between them (Qdrant schema, API contract).

**Core Architectural Principle**: The LLM is never trusted with raw user input. Every query passes through three validation gates — input sanitization (`validation.py`), guardrail agent (`judge_agent`), and RAG grounding (only chunks + query go to the LLM).

## Layer Structure

### Sub-project 1: Backend (FastAPI + OpenAI Agents SDK)

**Responsibility**: Serve the RAG chatbot API, manage ChatKit protocol, persist conversations

```
backend/
├── app.py               # FastAPI application, routes, CORS, lifespan, middleware
├── agent.py             # OpenAI Agents SDK: agents, guardrails, dynamic instructions
├── config.py            # Environment-based configuration + classmethod validation
├── retrieval.py         # Cohere embedding + Qdrant vector search (with retry)
├── chatkit_server.py    # ChatKit protocol bridge (extends ChatKitServer[RequestContext])
├── store.py             # SQLite persistence for ChatKit (extends Store[Any])
├── models/
│   └── chat.py          # Pydantic schemas: ChatRequest, AgentResponse, SSEMessage, etc.
├── utils/
│   └── validation.py    # Input sanitization: XSS, SQLi, code exec, path traversal
├── scripts/
│   └── read_db.py       # Debug utility to inspect chatkit.db
├── tests/               # pytest suite (99 tests across 12 files)
├── Dockerfile           # python:3.13-alpine + uv
├── pyproject.toml       # Python deps (openai-agents, openai-chatkit, cohere, qdrant)
├── uv.lock              # Locked dependency versions
└── .python-version      # Python version pin for CI
```

**Dependencies**: `-> Qdrant (cloud)`, `-> Cohere API v2`, `-> OpenRouter API`

### Sub-project 2: Frontend (Docusaurus + React 19)

**Responsibility**: Render textbook content, host ChatKit chat widget, inject page context

```
frontend/
├── docusaurus.config.ts    # Site config, customFields, plugins (raw-loader, proxy)
├── sidebars.ts             # Auto-generated sidebar from docs/ folder
├── package.json            # npm deps (Docusaurus 3.9, React 19, ChatKit React)
├── tsconfig.json           # Extends @docusaurus/tsconfig
├── vercel.json             # Vercel deployment config
├── docs/                   # MDX content (7 files: 6 chapters + glossary)
├── src/
│   ├── css/
│   │   └── custom.css      # Global theme: dark/light, glassmorphism, gradients
│   ├── pages/
│   │   ├── index.tsx       # Homepage: hero section + module cards
│   │   └── index.module.css
│   ├── components/
│   │   ├── ChatKitWidget.tsx         # Floating chat widget (126 lines)
│   │   ├── ChatKitWidget.module.css  # Widget positioning and styling
│   │   └── HomepageFeatures/
│   │       ├── index.tsx             # 4 module cards with icons and links
│   │       └── styles.module.css
│   ├── theme/
│   │   └── Root.tsx         # Global wrapper (renders ChatKitWidget everywhere)
│   └── utils/
│       ├── chatkit-fetch.ts         # Fetch interceptor (injects user ID + page context)
│       └── context-extractor.ts     # Extracts URL, title, headings from DOM
├── static/
│   ├── img/                 # Logo, favicon, social card
│   └── .nojekyll
├── code/                    # Code example files (URDF, ROS2, Unity, Python)
└── pyrightconfig.json       # Pyright config for Python code in docs
```

**Dependencies**: `-> Vercel (deploy)`, `-> Backend API (ChatKit endpoint)`

### Sub-project 3: Ingestion (Python CLI with uv)

**Responsibility**: Convert MDX textbooks to vector embeddings in Qdrant

```
ingestion/
├── ingest_book.py       # CLI pipeline: scan MDX -> convert -> token-chunk -> embed -> store -> verify
├── pyproject.toml       # Python deps (cohere, qdrant-client, tiktoken, python-dotenv)
├── uv.lock              # Locked dependency versions
├── tests/               # pytest suite (79 tests across 12 files)
│   ├── conftest.py
│   ├── test_chunking.py
│   ├── test_cli_validation.py
│   ├── test_e2e.py
│   ├── test_embedding.py
│   ├── test_file_operations.py
│   ├── test_main_pipeline.py
│   ├── test_mdx_conversion.py
│   ├── test_path_utils.py
│   ├── test_progress_tracker.py
│   ├── test_qdrant_operations.py
│   ├── test_retry_utils.py
│   └── test_vector_record.py
└── .python-version
```

**Dependencies**: `-> Qdrant (cloud)`, `-> Cohere API v2`, `-> MDX files on disk`

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
- **Implementation**: `book_knowledge_instructions()` reads `RunContextWrapper.context["book_chunks"]`; `chatkit_server.py` wraps with history + page context via cloned agent

### Pattern 5: SSE Streaming (Observer)
- **Location**: `backend/app.py` + `chatkit_server.py`
- **Purpose**: Stream LLM tokens to the client in real-time
- **Implementation**: `chat_stream_generator()` yields SSE-formatted events from `Runner.run_streamed()`; ChatKit protocol uses `stream_agent_response()` with `ChatKitAgentContext`

### Pattern 6: Retry with Exponential Backoff
- **Location**: `backend/retrieval.py`, `backend/ingest_book.py`
- **Purpose**: Handle transient API failures (Cohere, Qdrant)
- **Implementation**: `for attempt in range(max_retries): try...except: await asyncio.sleep(2 ** attempt)` -- 1s, 2s, 4s

### Pattern 7: In-Memory Sliding Window Rate Limiter
- **Location**: `backend/app.py`
- **Purpose**: Prevent abuse by limiting requests per IP
- **Implementation**: `InMemoryRateLimiter` with configurable window (default 60s) and max requests (default 60); applied via middleware that returns 429 on overflow

### Pattern 8: Lazy Initialization
- **Location**: `backend/store.py`, `backend/chatkit_server.py`
- **Purpose**: Avoid resource usage until first actual use
- **Implementation**: `_ensure_initialized()` called at start of every public method; tables created on first access

## Data Flow

### Chat Query Flow
```
1. User types question in ChatKit widget
2. chatkit-fetch.ts intercepts fetch, injects X-User-ID + pageContext
3. FastAPI receives POST /chatkit or POST /chat (depends on protocol)
4. CustomChatKitServer.respond() called with thread + message + context
5. Load last 10 items from SQLite for conversation history
6. Format history string + page context string
7. get_relevant_chunks() embeds query with Cohere v2 -> searches Qdrant
8. Dynamic instructions built: history + page context + chunks + base grounding
9. Runner.run_streamed() with transient agent clone
10. stream_agent_response() yields ChatKit SSE events (or raw SSE for /chat)
11. SQLiteStore.save_item() persists the exchange
```

### Ingestion Flow
```
1. CLI args parsed: --docs-dir, --chunk-size, --chunk-overlap, etc.
2. load_config() reads env vars with defaults
3. scan_mdx_files() walks docs directory for .mdx files (with path validation)
4. For each file:
   a. read_mdx_file() with size validation (50MB) + encoding fallback (UTF-8 -> latin-1)
   b. extract_module_and_chapter_from_path() -> (module1, chapter1)
   c. convert_mdx_to_text() strips JSX, imports/exports, code blocks, Markdown syntax
   d. chunk_text(token_size=512, overlap=50) using tiktoken cl100k_base
      - Split on paragraph boundaries first
      - Then sentence boundaries for oversized paragraphs
   e. cohere.embed(texts, model="embed-multilingual-v3.0", input_type="search_document")
   f. Batch store in Qdrant (100 per batch) with retry
5. verify_stored_vectors() samples and validates metadata fields
6. validate_all_files_processed() ensures no MDX file was skipped
```

### Frontend Page Load Flow
```
1. Docusaurus builds static HTML from MDX + React components
2. Root.tsx renders page content + ChatKitWidget (always mounted, toggled via CSS)
3. ChatKitWidget creates persistent student ID (localStorage)
4. ChatKit SDK initializes with custom fetch interceptor
5. User navigates -> context-extractor.ts captures URL/title/headings
6. On chat message -> chatkit-fetch.ts injects page context into protocol body
7. On text selection >10 chars -> "Ask AI" button appears above selection
8. Click "Ask AI" -> widget opens, composer pre-filled with selection text
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
| Styling | CSS Modules + custom.css | Scoped components + global design system |
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
- **Key Functions**: `chat_stream_generator()` -- SSE producer from agent stream; `chatkit_protocol()` -- ChatKit endpoint handler; `rate_limit_middleware` -- sliding window rate limiter
- **Complexity**: High (orchestrates agent, retrieval, ChatKit, SSE, rate limiting)
- **Dependencies**: agent, retrieval, chatkit_server, models, utils.validation

### Module: agent.py (OpenAI Agents SDK)
- **Purpose**: Define AI agents, guardrails, and dynamic instruction builder
- **Key Classes/Functions**: `judge_agent` (off-topic classifier), `book_knowledge_agent` (RAG answerer), `check_query_relevance()` (guardrail), `book_knowledge_instructions()` (dynamic prompt), `_build_openai_client()` (factory with OpenRouter headers)
- **Complexity**: Medium
- **Dependencies**: config, models.chat, agents SDK

### Module: retrieval.py (Vector Search)
- **Purpose**: Embed user query with Cohere, search Qdrant, return formatted chunks
- **Key Functions**: `get_relevant_chunks()` -- retry wrapper around embed + search; `embed_query()` -- standalone embedding with cache
- **Dependencies**: config, cohere SDK, qdrant-client

### Module: chatkit_server.py (ChatKit Bridge)
- **Purpose**: Extend ChatKitServer to bridge protocol to RAG pipeline
- **Key Methods**: `respond()` -- builds history + page context + dynamic instructions, runs agent, streams events with error isolation; `initialize_chatkit_server()` -- factory function
- **Complexity**: High (multi-step orchestration with sentinel flag error handling)
- **Dependencies**: store, agent, retrieval, models.chat

### Module: store.py (SQLite Persistence)
- **Purpose**: Implement ChatKit's Store interface with SQLite
- **Key Methods**: `initialize()`, `load_thread()`, `create_thread()`, `save_thread()`, `load_thread_items()`, `add_thread_item()`, `save_item()`, `load_item()`, `delete_thread()`, `delete_thread_item()`, `save/load/delete_attachment()`, `load_threads()`
- **Complexity**: Medium (12 CRUD methods + lazy init)
- **Dependencies**: aiosqlite, chatkit.store, chatkit.types

### Module: ingest_book.py (Ingestion CLI)
- **Purpose**: End-to-end pipeline: scan -> read -> convert -> token-chunk -> embed -> store -> verify
- **Key Classes/Functions**: `VectorRecord` (data model with payload/Qdrant serialization), `ProgressTracker`, `handle_api_call_with_retry()`, `setup_cohere_client()`, `setup_qdrant_client()`, `process_file_for_vectorization()`, `create_qdrant_collection()`, `batch_store_vectors_in_qdrant()`, `verify_stored_vectors()`, `main()`
- **Complexity**: High (file I/O + tiktoken chunking + API orchestration + retry + verification)
- **Dependencies**: cohere, qdrant-client, tiktoken, dotenv

### Module: ChatKitWidget.tsx (React Component)
- **Purpose**: Floating chat assistant with text selection support
- **Key Features**: `useChatKit()` hook with custom fetch interceptor, text selection "Ask AI" button, error banner with 10s auto-dismiss, persistent student ID in localStorage
- **Complexity**: Medium
- **Dependencies**: @openai/chatkit-react, utils/chatkit-fetch, ChatKitWidget.module.css

## Regeneration Strategy

### Option 1: Specification-First Rebuild (Recommended)

**Timeline**: 6-8 weeks (senior full-stack engineer)

#### Phase 1: Foundation (Week 1)
1. Set up monorepo structure with three sub-projects
2. Configure uv for backend + ingestion, npm for frontend
3. Implement `config.py` with env var loading + classmethod validation
4. Set up Dockerfile for backend (uv + python:3.13-alpine)
5. Set up Docusaurus scaffold with futuristic theme

#### Phase 2: Data Layer (Week 2)
1. Implement `SQLiteStore` with all 12 CRUD methods + lazy init
2. Implement ingestion pipeline (`ingest_book.py`): MDX -> text -> tiktoken chunks
3. Integrate Cohere embedding + Qdrant storage with retry
4. Add vector verification + all-files-processed validation
5. Write comprehensive test suite (79 tests)

#### Phase 3: AI Layer (Week 3-4)
1. Implement `agent.py`: OpenAIChatCompletionsModel with OpenRouter headers, dynamic instructions, guardrail
2. Implement `retrieval.py`: embed + search with retry + embedding cache
3. Implement `chatkit_server.py`: CustomChatKitServer with respond(), sentinel error handling
4. Wire up agent + retrieval + store in chat_stream_generator
5. Add SSE streaming with token/final/error event types
6. Add input guardrail with fail-open behavior

#### Phase 4: API Layer (Week 5)
1. Implement `app.py`: all 7 routes, CORS, lifespan, rate limiter middleware
2. Implement `validation.py`: XSS/SQLi/code-exec/path-traversal checks - 26 tests
3. Wire ChatKit protocol endpoint with page context extraction
4. Write comprehensive test suite (99 tests)

#### Phase 5: Frontend (Week 6)
1. Build `ChatKitWidget.tsx` with useChatKit, text selection, error handling
2. Build `chatkit-fetch.ts` + `context-extractor.ts` interceptors
3. Build homepage with hero + module cards
4. Implement custom.css futuristic design system (glassmorphism, gradients)
5. Configure Docusaurus navbar, footer, plugins, proxy

#### Phase 6: Deployment & CI (Week 7)
1. Write `deploy.yml` with test jobs + deploy to HF Space
2. Configure HF Space Docker deployment
3. Configure Vercel deployment
4. Set up GitHub secrets for API keys
5. E2E testing across all three sub-projects

### Option 2: Incremental Refactoring (Current Codebase)

**Timeline**: 1-2 weeks

1. Add `.env.example` with documented placeholders
2. Add `__init__.py` to `models/` and `utils/`
4. Add structured JSON logging
5. Add request ID tracing middleware
6. Rotate/remove committed API keys from git history
7. Expose FastAPI OpenAPI docs (currently disabled)
8. Extract shared RAG pipeline service (duplicated between app.py and chatkit_server.py)
9. Add connection lifecycle management (close Cohere/Qdrant clients on shutdown)

## Improvement Opportunities

### Technical Improvements
- [ ] **Replace in-memory rate limiter with Redis**: Current `InMemoryRateLimiter` is process-local and lost on restart; not effective with multiple instances
- [ ] **Add structured logging (JSON)**: Current logging uses plain text; structured JSON with correlation IDs would enable log aggregation
- [ ] **Add request ID tracing**: `X-Request-ID` middleware for correlating logs across service calls
- [ ] **Expose OpenAPI/Swagger docs**: FastAPI generates them automatically but they're not exposed at any route

### Architectural Improvements
- [ ] **Extract RAG pipeline into shared service**: Agent orchestration is duplicated between `app.py` (`chat_stream_generator`) and `chatkit_server.py` (`respond` method). Extract into a shared async function
- [ ] **Add connection pool for Qdrant/Cohere**: Clients initialized at module level with no explicit lifecycle management
- [ ] **Add Redis-based embedding cache**: Current in-memory cache is lost on restart; Redis would persist across deployments
- [ ] **Semantic chunking**: Replace current tiktoken-based chunking with paragraph/section-aware semantic chunking

### Operational Improvements
- [ ] **Health check with dependency verification**: Current `/health` returns "healthy" even if Qdrant/Cohere are unreachable
- [ ] **Graceful shutdown**: Lifespan should close Qdrant/Cohere client connections
- [ ] **Monitoring**: Add Prometheus metrics for request count, latency, error rate
- [ ] **Database migrations**: Add Alembic for schema migration management
