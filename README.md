# Physical AI & Humanoid Robotics Textbook

A comprehensive textbook on Physical AI and Humanoid Robotics with an integrated RAG (Retrieval-Augmented Generation) chatbot system for interactive learning.

## Project Structure

```
.
├── AGENTS.md                          # Agent instructions, commands, quirks
├── opencode.md                        # opencode configuration
├── project_context.md                 # Project context for AI agents
├── skills-lock.json                   # Installed agent skills lockfile
├── .agents/                           # Agent skills
│   └── skills/
│       ├── chatkit-integration/       # ChatKit framework integration skill
│       ├── frontend-design/           # UI/UX design guidance skill
│       ├── openai-agents-sdk/         # OpenAI Agents SDK skill
│       │   └── references/           # SDK reference docs
│       ├── ui-ux-futuristic-designer/ # 2026 futuristic design skill
│       │   └── references/           # Color systems, design patterns
│       └── ui-ux-pro-max/            # UI/UX Pro Max design skill
├── .opencode/                         # opencode command definitions
├── .specify/                          # SDD templates
├── docs/                              # Project documentation
├── history/                           # Prompt history records
├── my_project/                        # Main project code
│   ├── .env                          # Environment variables (gitignored)
│   ├── .env.example                  # Environment variable template
│   ├── backend/                      # FastAPI + OpenAI Agents SDK RAG chatbot
│   │   ├── Dockerfile                # python:3.13-alpine container
│   │   ├── pyproject.toml            # Python dependencies (uv)
│   │   ├── uv.lock                   # Locked dependency versions
│   │   ├── app.py                    # FastAPI app, routes, CORS, rate limit, lifespan
│   │   ├── agent.py                  # OpenAI Agents SDK agents & guardrails
│   │   ├── config.py                 # Environment configuration + validation
│   │   ├── retrieval.py              # Cohere embedding + Qdrant vector search (with in-memory cache)
│   │   ├── store.py                  # SQLite persistence for ChatKit threads
│   │   ├── chatkit_server.py         # ChatKit protocol bridge (with guardrail handling)
│   │   ├── models/
│   │   │   └── chat.py              # Pydantic schemas
│   │   ├── utils/
│   │   │   └── validation.py        # Input sanitization
│   │   ├── scripts/
│   │   │   └── read_db.py           # Debug utility
│   │   └── tests/                    # pytest test suite (99 tests)
│   │       ├── conftest.py           # Fixtures + dummy env vars
│   │       ├── test_validation.py    # Input validation (17 tests)
│   │       ├── test_models.py        # Pydantic model tests (16 tests)
│   │       ├── test_agent_instructions.py  # Prompt construction (5 tests)
│   │       ├── test_guardrail.py     # Guardrail logic (3 tests)
│   │       ├── test_retrieval.py     # Retrieval pipeline (7 tests)
│   │       ├── test_chat_endpoint.py # /chat API endpoint (5 tests)
│   │       ├── test_chatkit_protocol.py  # ChatKit endpoints (5 tests)
│   │       ├── test_chatkit_server.py    # CustomChatKitServer (5 tests)
│   │       ├── test_config.py        # Config validation (4 tests)
│   │       ├── test_middleware.py    # CORS, rate limit, health (7 tests)
│   │       └── test_store.py         # SQLiteStore CRUD (9 tests)
│   ├── frontend/                     # Docusaurus textbook site + ChatKit widget
│   │   ├── package.json             # npm dependencies (React 19, Docusaurus 3.9)
│   │   ├── docusaurus.config.ts     # Site config, navbar, footer, plugins
│   │   ├── sidebars.ts              # Documentation sidebar structure
│   │   ├── docs/                    # Textbook content (MDX), 6 chapters + glossary
│   │   ├── src/                     # React source code
│   │   │   ├── css/                 # Global styles (futuristic dark theme)
│   │   │   ├── pages/               # Homepage with hero + module cards
│   │   │   ├── components/          # ChatKitWidget, HomepageFeatures
│   │   │   ├── theme/               # Root.tsx global wrapper
│   │   │   └── utils/               # chatkit-fetch, context-extractor
│   │   ├── static/                  # Static assets (logo, favicon)
│   │   └── code/                    # Code examples (ROS2, Unity, Gazebo, Isaac Sim)
│   └── ingestion/                   # MDX → Cohere embeddings → Qdrant (uv project)
│       ├── pyproject.toml            # Python dependencies (uv, includes tiktoken)
│       ├── uv.lock                   # Locked dependency versions
│       ├── ingest_book.py           # Full ingestion pipeline (token-aware chunking)
│       └── tests/                    # pytest test suite (79 tests)
│           ├── conftest.py           # Shared fixtures
│           ├── test_path_utils.py    # Path extraction & validation
│           ├── test_mdx_conversion.py # MDX → plain text
│           ├── test_chunking.py      # Text chunking with overlap
│           ├── test_vector_record.py # VectorRecord data model
│           ├── test_cli_validation.py # CLI args + input validation
│           ├── test_file_operations.py # File read/scan
│           ├── test_qdrant_operations.py # Qdrant CRUD
│           ├── test_embedding.py     # Embedding pipeline
│           ├── test_retry_utils.py   # Retry with backoff
│           ├── test_progress_tracker.py # ProgressTracker
│           ├── test_main_pipeline.py # process_file_for_vectorization
│           └── test_e2e.py          # Full pipeline E2E
└── .github/
    └── workflows/
        └── deploy.yml               # CI/CD: deploys backend to HF Spaces
```

## Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (Modern Python package manager)
- Node.js v20+

## Backend Setup and Run

```bash
cd my_project/backend
uv sync
```

Configure environment variables in `.env` file (see `.env.example`):

```env
COHERE_API_KEY=your_cohere_api_key_here
COHERE_MODEL=embed-multilingual-v3.0
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_HOST=your_qdrant_host_here
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=book_vectors
LLM_API_KEY=sk-or-v1-your_openrouter_key_here
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=qwen/qwen3-coder
TOP_K=3
RELEVANCE_THRESHOLD=0.0
```

Start the backend:
```bash
uv run uvicorn app:app --reload --port 8000
```

## Frontend Setup and Run

```bash
cd my_project/frontend
npm install
npm run start
```

Frontend at `http://localhost:3000`, backend at `http://localhost:8000`.

## Content Ingestion

```bash
cd my_project/ingestion
uv sync
uv run python ingest_book.py --docs-dir=../frontend/docs
```

## Running Tests

All test suites use **pytest** for consistency.

### Backend tests (one command)
```bash
cd my_project/backend
uv run pytest tests/ -v
```

### Ingestion tests (one command)
```bash
cd my_project/ingestion
uv run pytest tests/ -v
```

### Frontend typecheck
```bash
cd my_project/frontend
npm run typecheck
```

## Deployment Environment Variables

- Frontend: `API_BASE_URL=https://<your-hf-space-domain>`
- Backend: `ALLOWED_ORIGINS=https://<your-vercel-domain>,http://localhost:3000`
