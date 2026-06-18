# AGENTS.md — Physical AI & Humanoid Robotics Textbook

## Project anatomy

```
my_project/
├── backend/          # FastAPI + OpenAI Agents SDK RAG chatbot (Python 3.13, uv)
├── frontend/         # Docusaurus textbook site + ChatKit widget (React 19, npm)
└── ingestion/        # MDX → Cohere embeddings → Qdrant (Python 3.13, pip)
```

## Commands

| Area | Command | Working dir |
|---|---|---|
| Install backend deps | `uv sync` | `my_project/backend` |
| Run backend API | `uv run uvicorn app:app --reload --port 8000` | `my_project/backend` |
| Run ingestion | `python ingest_book.py` (pip deps in `requirements.txt`) | `my_project/ingestion` |
| Install frontend deps | `npm install` | `my_project/frontend` |
| Run frontend dev | `npm run start` | `my_project/frontend` |
| Frontend typecheck | `npm run typecheck` (runs `tsc`) | `my_project/frontend` |
| Frontend build | `npm run build` | `my_project/frontend` |
| Backend tests | `uv run pytest` or `python -m pytest` | `my_project/backend` |
| Ingestion unit tests | `python -m unittest test_ingest_book.py` | `my_project/ingestion` |
| Ingestion E2E test | `python e2e_test.py` | `my_project/ingestion` |

## Entry points and wiring

- **Backend app**: `my_project/backend/app.py:app` — FastAPI instance. Config validation runs at **module import time** (before lifespan).
- **Agent**: `my_project/backend/agent.py` — OpenAI Agents SDK agent. Uses OpenRouter as LLM provider (not direct OpenAI). Requires `HTTP-Referer` + `X-Title` headers in client config.
- **LLM provider fallback** (in `config.py`): `LLM_API_KEY` → `OPENROUTER_API_KEY` → `GEMINI_API_KEY`. Change model via `LLM_MODEL` env var only.
- **ChatKit bridge**: `my_project/backend/chatkit_server.py` — `CustomChatKitServer` extends `ChatKitServer[RequestContext]`. Overrides `respond()`. ChatKit SDK handles thread management; SQLite store persists conversations.
- **Frontend Chat widget**: `my_project/frontend/src/theme/Root.tsx` globally includes `ChatKitWidget`. Uses `@openai/chatkit-react`. Custom fetch interceptor (`chatkit-fetch.ts`) injects page context (`url`, `title`, `headings`) into ChatKit protocol metadata.
- **Ingestion default path gotcha**: `ingest_book.py` defaults to `./my-website/docs` but actual content is at `./my_project/frontend/docs`. Always pass `--docs-dir=./my_project/frontend/docs`.

## Framework/toolchain quirks

- **uv + FastAPI**: Use `uv run uvicorn ...` not raw `uvicorn`. The `uv` venv is managed automatically.
- **ChatKit dev proxy**: `docusaurus.config.ts` has a custom plugin that proxies `/chatkit` and `/api/chatkit` to the backend. No CORS issues in dev.
- **raw-loader plugin**: `.py`, `.cs`, `.world` files are loaded as raw strings for code examples. Don't remove.
- **Agents SDK version**: Uses `openai-agents>=0.17.5`. Guardrails via `@input_guardrail` decorator, not the old `input_guardrail()` function.
- **ChatKit SDK**: `@openai/chatkit-react` is the React wrapper. The `chatkit.js` script tag is loaded from CDN in `docusaurus.config.ts` for the ChatKit React import.
- **No linter/formatter config**: No `ruff`, `black`, `eslint`, or `prettier` config found. Assume none unless added.

## Spec-Driven Development (SDD) workflow

This repo runs on SDD. Every feature goes through: `/sp.specify` → `/sp.plan` → `/sp.tasks` → `/sp.implement`.

Command files at `.opencode/command/sp.*.md` define the full workflow:
- `/sp.specify` — Write feature spec (user stories, acceptance criteria)
- `/sp.plan` — Architecture plan, data model, contracts
- `/sp.tasks` — Task breakdown by user story priority (P1, P2, P3)
- `/sp.implement` — Implement from spec/plan/tasks
- `/sp.adr` — Create Architecture Decision Record
- `/sp.constitution` — Create/edit project constitution
- `/sp.phr` — Create Prompt History Record (also auto-created after every prompt)
- `/sp.reverse-engineer` — Extract spec/plan/tasks from existing code
- `/sp.clarify` — Clarify ambiguous requirements
- `/sp.checklist` — Review against quality checklist
- `/sp.analyze` — Analyze codebase or feature design
- `/sp.git.commit_pr` — Commit + PR creation workflow
- `/sp.taskstoissues` — Convert tasks to GitHub issues

## PHR requirement

After **every user prompt**, create a PHR (Prompt History Record) under `history/prompts/`. Routing:
- `constitution` stage → `history/prompts/constitution/`
- Feature stages (spec/plan/tasks/red/green/refactor/explainer/misc) → `history/prompts/<feature-name>/`
- `general` → `history/prompts/general/`

Template at `.specify/templates/phr-template.prompt.md`. Must fill all YAML placeholders and embed full PROMPT_TEXT verbatim.

## Testing quirks

- **Backend tests use FastAPI TestClient** (`test_streaming.py`). They rely on real API keys if the agent/retrieval actually runs — no mocking currently. Test is contract-only.
- **Ingestion tests use `unittest`** (not pytest). Run with `python -m unittest test_ingest_book.py`.
- **`test_performance.py`** is a placeholder (empty `pass`). Skip in test runs.
- **No CI test execution**: `.github/workflows/deploy.yml` only deploys backend; does not run tests.

## Deployment

- **Backend**: GitHub Actions → Hugging Face Spaces. Pushes `my_project/backend/` files (app.py, agent.py, config.py, retrieval.py, models/, utils/, pyproject.toml, uv.lock, Dockerfile) to HF Space repo.
- **Frontend**: Deployed to Vercel (URL in docusaurus config: `physical-ai-humanoid-robotics-textbook.vercel.app`). Not automated in this repo's CI.
- **CORS**: Configured via `ALLOWED_ORIGINS` env var. No trailing slashes allowed.

## Known constraints

- `.env` file at `my_project/.env` contains **live API keys** committed to the repo. Do not push; do not use in examples.
- `AgentResponse.citations` field is defined but **never populated** — chunks lack citation tracking.
- `config.py:load_dotenv()` loads `my_project/backend/.env` or `my_project/.env` — not root `.env`.
- ChatKit SQLite DB (`chatkit.db`) is gitignored and auto-created at runtime.
- The constitution at `.specify/memory/constitution.md` is an **unfilled template** — all sections are placeholders.
