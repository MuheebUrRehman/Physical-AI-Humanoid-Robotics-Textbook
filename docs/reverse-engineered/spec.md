# Physical AI & Humanoid Robotics Textbook — Specification

**Version**: 3.0 (Reverse Engineered)
**Date**: 2026-06-19
**Source**: `D:\GIAIC\Q4\Hackathons\Physical-AI-Humanoid-Robotics-Textbook`

## Problem Statement

Students and professionals learning Physical AI and Humanoid Robotics lack an interactive, context-aware educational resource that combines comprehensive textbook content with an AI-powered question-answering system grounded in the material. Traditional static textbooks provide no means to ask clarification questions, get context-specific explanations, or search semantically across the content. Existing RAG chatbot tutorials show isolated components but fail to deliver a production-grade integration with a modern chat protocol (ChatKit), persistent conversation history, page-level context awareness, and a polished UI.

## System Intent

**Target Users**: Students, engineers, and researchers studying Physical AI, ROS 2, Gazebo/Unity simulation, NVIDIA Isaac, and Vision-Language-Action models.

**Core Value Proposition**: A browsable textbook with an embedded RAG chatbot that answers questions strictly from the book's own content, with page-level context awareness — turning a static reference into an interactive tutor that knows what the student is currently reading.

**Key Capabilities**:
- Browse 4 modules of textbook content (Foundations, Simulation, Advanced Simulation, Capstone) via a futuristic Docusaurus website
- Ask natural-language questions via a floating ChatKit chat widget and receive answers grounded in the textbook
- Select any text on a page and ask the AI to explain it further
- Retrieve relevant book chunks via semantic search (Cohere embeddings + Qdrant vector DB)
- Stream LLM responses token-by-token via Server-Sent Events (SSE)
- Maintain conversation history across sessions via ChatKit protocol with SQLite persistence
- Reject off-topic queries via an input guardrail agent before they reach the LLM
- Deploy backend to Hugging Face Spaces with GitHub Actions CI/CD (including test execution)
- Deploy frontend to Vercel

## Functional Requirements

### FR-1: Browsable Textbook Website
- **What**: Render 4 modules of educational content covering ROS 2, Gazebo/Unity, NVIDIA Isaac, and VLA models as a Docusaurus static site with futuristic dark-themed UI
- **Inputs**: MDX files in `frontend/docs/` (6 chapters + glossary)
- **Outputs**: A fully navigable documentation website with navbar, sidebar, and footer, deployed to Vercel
- **Side Effects**: None (static site generation)
- **Success Criteria**: All 6 chapters + glossary render without broken links; build completes with `npm run build`

### FR-2: RAG Chat Query (SSE)
- **What**: Accept a natural-language question via POST to `/chat`, retrieve relevant book chunks from Qdrant, and return a grounded answer via SSE stream
- **Inputs**: `{query: string (3-2000 chars), user_id: string, session_id: string}`
- **Outputs**: SSE events — `{type: "token", content: string}` for partial tokens, `{type: "final", content: AgentResponse}` for the complete answer with citations
- **Side Effects**: None (read-only query)
- **Error Responses**: 400 for invalid input, 500 for internal errors, `{type: "error", content: string}` for guardrail blocks or empty responses

### FR-3: ChatKit Protocol Integration
- **What**: Implement the OpenAI ChatKit protocol so the chatbot supports conversation threads, user identity, and page-level context
- **Inputs**: POST to `/chatkit` with ChatKit-compatible payload including `X-User-ID` header and optional `pageContext {url, title, headings}`
- **Outputs**: SSE stream via ChatKit protocol bridging to the same RAG agent
- **Side Effects**: Conversation threads persisted in SQLite (`chatkit.db`) via `SQLiteStore`
- **API Endpoints**: `/chatkit` (main protocol), `/api/chatkit/session` (create session), `/api/chatkit/refresh` (refresh token), `/api/chatkit/user` (user metadata)

### FR-4: Text Selection Query
- **What**: Select text on any textbook page, see a floating "Ask AI" button, click it to pre-fill the ChatKit widget with the selection
- **Inputs**: DOM `mouseup` event -> selection text (>10 chars)
- **Outputs**: ChatKit widget opens with pre-filled prompt: `Tell me more about this: "{selection}"`
- **Side Effects**: None
- **Success Criteria**: Selection button appears above selected text; clicking it opens chat with the selection as context

### FR-5: Content Ingestion Pipeline
- **What**: Scan MDX files in `frontend/docs/`, convert to plain text, token-aware chunk (512 chars with 50 char overlap via tiktoken), embed via Cohere `embed-multilingual-v3.0`, store in Qdrant `book_vectors` collection
- **Inputs**: CLI args: `--docs-dir`, `--chunk-size`, `--chunk-overlap`, `--collection-name`, `--batch-size`, `--qdrant-host`, `--qdrant-port`, `--cohere-model`
- **Outputs**: Vector embeddings stored in Qdrant collection with metadata: `content`, `source_file`, `module`, `chapter`, `chunk_index`, `created_at`
- **Side Effects**: Qdrant collection created/recreated via `recreate_collection`; ingestion log written to `ingestion.log`
- **Success Criteria**: All MDX files processed; `verify_stored_vectors()` confirms all vectors have expected metadata fields

### FR-6: Input Guardrail
- **What**: Reject off-topic queries (non-robotics/physical-AI) before they reach the LLM
- **Inputs**: User query text
- **Outputs**: GuardrailFunctionOutput with `tripwire_triggered=True` if off-topic
- **Side Effects**: None
- **Success Criteria**: Queries about unrelated topics return error; related queries pass through

### FR-7: Query Validation & Sanitization
- **What**: Validate and sanitize all user-supplied input (query, user_id, session_id) before processing
- **Inputs**: Raw user query, user ID, session ID
- **Outputs**: Sanitized query string or validation error
- **Validation Rules**: Min 3 chars, max 2000 chars, no XSS patterns, no SQL injection patterns, no code execution patterns, no path traversal
- **Side Effects**: None

### FR-8: Health Check & Root Endpoints
- **What**: Provide service health and root API info
- **Inputs**: GET to `/health` or `/`
- **Outputs**: `HealthCheckResponse {status, version, timestamp}` or root API metadata
- **Side Effects**: None

## Non-Functional Requirements

### Performance
- **Vector search**: Qdrant query timeout configurable via `QUERY_TIMEOUT` env var (default 30s)
- **LLM streaming**: Token-by-token SSE with configurable `max_tokens` (1000) and `temperature` (0.3)
- **Retry logic**: Cohere embedding and Qdrant search both implement exponential backoff (2^n seconds, max 3 retries)
- **Ingestion**: Performance tracking warns if estimated total exceeds 10 minutes; token-aware chunking via tiktoken `cl100k_base`
- **Rate limiting**: `InMemoryRateLimiter` with sliding window (default 60 requests per 60s per IP) applied via middleware

### Security
- **Input sanitization**: HTML escaping, regex-based XSS/SQLi/code-execution/path-traversal blocking via `utils/validation.py`
- **Guardrail**: Pre-LLM off-topic detection via Judge agent (OpenRouter)
- **ChatKit auth**: Stateless client secrets via `secrets.token_urlsafe(32)`
- **CORS**: Configurable `ALLOWED_ORIGINS` env var; default allows localhost:3000 and Vercel production URL
- **File validation**: `validate_file_path()` prevents directory traversal in ingestion

### Reliability
- **Graceful degradation**: If all retries fail in `get_relevant_chunks()`, returns empty list (not an error)
- **Guardrail fail-open**: If Judge agent throws an error, `tripwire_triggered=False` (query passes through)
- **ChatKit error isolation**: `ErrorEvent` only yielded if no tokens were streamed yet (avoids corrupting partial responses)
- **SQLite lazy init**: `_ensure_initialized()` called before every DB operation; tables auto-created on first use
- **Ingestion retries**: `handle_api_call_with_retry()` with exponential backoff (1s, 2s, 4s) for Cohere/Qdrant API calls

### Scalability
- **Stateless API**: All required user/context state passed via headers/body
- **Async everything**: FastAPI async handlers, async Cohere v2, async Qdrant, aiosqlite
- **Embedding cache**: In-memory dict cache (`_embed_cache`) with 300s TTL for Cohere embeddings (process-local, lost on restart)

### Observability
- **Structured logging**: `logging` module with `%(asctime)s - %(name)s - %(levelname)s - %(message)s` format
- **Request timing**: `X-Process-Time` response header on all requests via middleware
- **Health endpoint**: `GET /health` returns status, version, timestamp

### Deployment
- **Backend**: Docker container -> Hugging Face Spaces (uvicorn on port 7860)
- **Frontend**: Static site -> Vercel (Docusaurus build output)
- **CI/CD**: GitHub Actions workflow runs backend tests (99) + ingestion tests (79), then deploys backend to HF Space
- **Runtime**: Python 3.13 (alpine), uv package manager
- **Environment**: All config via env vars; no secrets in code

## System Constraints

### External Dependencies
- **Qdrant**: Vector database (cloud instance at `QDRANT_HOST`). Requires `QDRANT_API_KEY`
- **Cohere**: Embedding API v2. Requires `COHERE_API_KEY`. Model: `embed-multilingual-v3.0`
- **OpenRouter**: LLM provider (primary). Falls back to OpenAI/Gemini compatible endpoints. Requires `LLM_API_KEY` (or `OPENROUTER_API_KEY` / `GEMINI_API_KEY`)
- **ChatKit CDN**: `chatkit.js` loaded from `cdn.platform.openai.com` for the React component
- **SQLite**: Local file database via `aiosqlite` for conversation persistence

### Data Formats
- **Content source**: MDX (Markdown with JSX components) in `frontend/docs/`
- **API I/O**: JSON request/response bodies; SSE for streaming (`text/event-stream`)
- **Vector storage**: Qdrant points with payload: `{content, source_file, module, chapter, chunk_index, created_at}`
- **Conversations**: ChatKit `ThreadMetadata` and `ThreadItem` JSON-serialized in SQLite

### Deployment Context
- **Backend**: Hugging Face Spaces (Docker), `uvicorn app:app --host 0.0.0.0 --port 7860`
- **Frontend**: Vercel, static site from `build/` directory
- **Git**: Monorepo with three sub-projects under `my_project/`

### Compliance Requirements
- None explicitly enforced (educational textbook)

## Architecture

```
                         USER'S BROWSER
  ┌─────────────────────────────────────────────┐
  │  ┌──────────────────┐  ┌──────────────────┐ │
  │  │   Docusaurus     │  │  ChatKit Widget  │ │
  │  │   Textbook       │  │  (React, float)  │ │
  │  └────────┬─────────┘  └────────┬─────────┘ │
  │           │ selection            │ ChatKit   │
  │           ▼                      ▼           │
  │  ┌────────────────────────────────────────┐  │
  │  │   chatkit-fetch.ts (interceptor)       │  │
  │  │   injects X-User-ID + pageContext      │  │
  │  └────────────────────────────────────────┘  │
  └───────────────────────┬──────────────────────┘
                          │ HTTP/SSE
                          ▼
  ┌─────────────────────────────────────────────┐
  │   VERCEL (CDN) / Docusaurus dev proxy       │
  │   Proxies /chatkit -> backend:8000          │
  └───────────────────────┬──────────────────────┘
                          │
                          ▼
  ┌─────────────────────────────────────────────┐
  │         HUGGING FACE SPACES (Backend)        │
  │                                              │
  │  ┌──────────────┐  ┌──────────────────────┐ │
  │  │  FastAPI      │  │  ChatKitServer       │ │
  │  │  /health      │  │  respond() -> stream │ │
  │  │  /chat (SSE)  │  │  agent_response()    │ │
  │  │  /chatkit     │  └──────────────────────┘ │
  │  │  /api/chatkit │                           │
  │  └───────┬───────┘                           │
  │          │                                    │
  │    ┌─────┼──────────┬──────────────┐          │
  │    ▼     ▼          ▼              ▼          │
  │  ┌────┐ ┌────────┐ ┌──────────┐ ┌─────────┐ │
  │  │Age │ │ Config │ │Retrieval │ │SQLite   │ │
  │  │nt  │ │        │ │.py       │ │Store    │ │
  │  │.py │ │.py     │ │(Cohere+  │ │(chatkit │ │
  │  │    │ │        │ │ Qdrant)  │ │.db)     │ │
  │  └─┬──┘ └────────┘ └────┬─────┘ └─────────┘ │
  │    │                     │                    │
  │    ▼                     ▼                    │
  │  ┌──────────┐      ┌──────────┐              │
  │  │OpenRouter│      │  Qdrant  │              │
  │  │LLM API   │      │  (Cloud) │              │
  │  └──────────┘      └──────────┘              │
  │                          ▲                    │
  │                     ┌──────────┐              │
  │                     │  Cohere  │              │
  │                     │ (API v2) │              │
  │                     └──────────┘              │
  └──────────────────────────────────────────────┘

Data Flow (chat):
  User -> ChatKitWidget -> chatkit-fetch.ts (inject pageContext)
    -> /chatkit (FastAPI) -> CustomChatKitServer.respond()
      -> load thread history from SQLiteStore
        -> get_relevant_chunks(query + page title)
          -> Cohere embed -> Qdrant search
        -> book_knowledge_agent (OpenRouter LLM + chunks as context)
          -> guardrail check (Judge agent)
          -> stream_agent_response (SSE to ChatKit)
    -> SQLiteStore.save_item (persist conversation)

Data Flow (ingestion):
  MDX files -> read_mdx_file() -> convert_mdx_to_text()
    -> chunk_text (tiktoken, 512 tokens, 50 overlap)
      -> prepare_chunks_for_embedding()
        -> cohere.embed() -> batch store in Qdrant (100/batch)
          -> verify_stored_vectors()
```

## Non-Goals & Out of Scope

- **User authentication system**: ChatKit `X-User-ID` is a simple header-based identity. No OAuth, no SSO
- **Multi-modal RAG**: Images in textbook are not embedded or retrieved; only text chunks
- **Citation tracking**: `AgentResponse.citations` field is defined but never populated with meaningful data (only `source_file` is provided)
- **Load balancing / horizontal scaling**: SQLite is single-process; embedding cache is process-local; no distributed state
- **Structured logging (JSON)**: Logging uses plain-text format, not structured JSON
- **API documentation**: No auto-generated OpenAPI/Swagger documentation exposed
- **Monitoring / alerting**: No metrics collection (Prometheus), no tracing (OpenTelemetry), no alerts
- **Connection lifecycle management**: Cohere and Qdrant clients initialized at module level with no explicit close/shutdown in lifespan

## Known Gaps & Technical Debt

### Gap 1: Live API Keys Committed to Repo
- **Issue**: `my_project/.env` contains live Cohere, Qdrant, OpenRouter, and Gemini API keys in git history
- **Evidence**: `git log` shows `.env` was committed before `.gitignore` rule took effect
- **Impact**: Anyone with repo access can use these keys; keys are not revocable if exposed
- **Recommendation**: Revoke keys, `git filter-branch`/BFG to remove from history, add as GitHub secrets + HF Space secrets

### Gap 2: No `.env.example` File
- **Issue**: No example env file for new contributors
- **Impact**: Difficult onboarding; contributors don't know which env vars are required or their formats
- **Recommendation**: Create `.env.example` with documented placeholders for all env vars

### Gap 3: Unused `initialize_agent()` Function
- **Issue**: `agent.py:113-124` defines `initialize_agent()` but it is never called anywhere in the codebase
- **Impact**: Dead code causing confusion for maintainers
- **Recommendation**: Remove the function

### Gap 4: Missing `__init__.py` in Backend Packages
- **Issue**: `backend/models/` and `backend/utils/` directories lack `__init__.py` files
- **Impact**: Works via implicit namespace packages in Python 3.13, but may break with some tooling and is non-standard
- **Recommendation**: Add `__init__.py` to both directories

### Gap 5: ChatKit Session Management Lacks Auth
- **Issue**: `/api/chatkit/session` creates client secrets via `secrets.token_urlsafe(32)` but these secrets are used only for the session lifetime; no actual authentication or token validation is enforced
- **Impact**: Any user can create a session without authorization
- **Recommendation**: Add optional rate limiting or user identity validation at session creation

### Gap 6: Embedding Cache is Process-Local
- **Issue**: `retrieval.py` has an in-memory dict cache (`_embed_cache`) with 300s TTL; cache is lost on server restart
- **Impact**: First request after restart always incurs embedding latency; cache does not survive deployment
- **Recommendation**: Add optional Redis-based cache for embedding results

### Gap 7: Chunking Overlap May Lose Context
- **Issue**: Current chunk overlap is 50 characters/tokens; this may be insufficient for preserving context across chunks, especially for paragraphs referencing earlier content
- **Impact**: Chunks split mid-paragraph may lose semantic continuity
- **Recommendation**: Increase overlap to 100-150 tokens, or implement semantic chunking that respects paragraph/section boundaries

### Gap 8: Guardrail Agent Runs on Every Query
- **Issue**: The Judge agent makes an additional LLM call for every query, doubling API cost and latency
- **Impact**: Every user query costs 2x (guardrail + main response) with ~2x latency
- **Recommendation**: Consider keyword-based pre-filtering before the guardrail LLM call, or embedding-based classification

## Success Criteria

### Functional Success
- [ ] All MDX chapters render without broken links in Docusaurus build
- [ ] `POST /chat` with valid query returns SSE stream with tokens
- [ ] `POST /chatkit` with ChatKit payload creates thread and streams agent response
- [ ] Off-topic queries return guardrail error; on-topic queries pass through
- [ ] Text selection >10 chars triggers "Ask AI" button on all pages
- [ ] Ingestion pipeline processes all MDX files into Qdrant vectors
- [ ] Conversation history persists across page reloads (SQLite)

### Non-Functional Success
- [ ] Frontend: `npm run typecheck` passes with 0 errors
- [ ] Frontend: `npm run build` produces `build/` directory
- [ ] Backend: `uv run pytest tests/ -v` — 99/99 tests pass
- [ ] Ingestion: `uv run pytest tests/ -v` — 79/79 tests pass
- [ ] Backend: `uv sync --frozen --no-group dev` resolves without errors
- [ ] Backend: Docker build succeeds with `docker build .`
- [ ] Zero hardcoded secrets in source code
- [ ] All API endpoints return properly structured JSON/SSE responses

## Acceptance Tests

### Test 1: Valid Chat Query
**Given**: Backend is running with valid API keys
**When**: POST to `/chat` with `{query: "What is ROS 2?", user_id: "test", session_id: "sess1"}`
**Then**: Response is SSE stream; first event has `type: "token"`; final event has `type: "final"` with `content.answer` containing ROS 2 information

### Test 2: Off-Topic Rejection
**Given**: Backend is running
**When**: POST to `/chat` with `{query: "What is the best pizza topping?", user_id: "test", session_id: "sess1"}`
**Then**: SSE stream yields `type: "error"` with guardrail message

### Test 3: Empty Response Handling
**Given**: Backend is running
**When**: POST to `/chat` with a query that retrieves no chunks and the LLM produces no output
**Then**: SSE stream yields `type: "error"` with "empty response" message

### Test 4: Ingestion Completeness
**Given**: Ingestion script is run against `frontend/docs/`
**When**: `uv run python ingest_book.py --docs-dir=./my_project/frontend/docs`
**Then**: All 7 MDX files processed; Qdrant collection `book_vectors` has vectors for each chunk; `verify_stored_vectors()` returns True

### Test 5: ChatKit Thread Persistence
**Given**: ChatKit widget sends a message to `/chatkit`
**When**: Thread ID is captured and later queried via `load_thread_items`
**Then**: Thread exists in SQLite with the user message; subsequent messages are appended with correct ordering

### Test 6: Frontend Build
**Given**: Frontend dependencies installed
**When**: `npm run build`
**Then**: Build succeeds; `build/` directory contains `index.html` and all assets
