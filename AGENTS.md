# AGENTS.md — Physical AI & Humanoid Robotics Textbook

## Repo layout

```
AGENTS.md               ← this file
opencode.md              ← OpenCode agent rules (SDD methodology)
my_project/
  backend/               ← FastAPI + OpenAI Agents SDK RAG chatbot (uv, Python 3.13+)
  frontend/              ← Docusaurus 3.9 textbook site + ChatKit widget (npm, React 19)
  ingestion/             ← MDX → Cohere embeddings → Qdrant pipeline (uv, Python 3.13+)
  .env                   ← shared env (gitignored); template at .env.example
.specify/                ← SDD templates & constitution (constitution.md is an unfilled template)
.opencode/command/       ← sp.* custom commands (sp.phr, sp.adr, sp.plan, etc.)
.agents/skills/          ← 5 installable agent skills (chatkit-integration, openai-agents-sdk, etc.)
.github/workflows/       ← CI/CD deploys only backend to HF Spaces on main
docs/reverse-engineered/ ← SDD artifacts from reverse-engineering phase
history/prompts/         ← PHR records (auto-created per opencode.md)
```

## Commands (run from each subdirectory, no root-level scripts)

| Package | Install | Dev server | Test | Typecheck | Build |
|---|---|---|---|---|---|
| `my_project/backend` | `uv sync` | `uv run uvicorn app:app --reload --port 8000` | `uv run pytest tests/ -v` | — | Docker: `uv sync --frozen --no-group dev` |
| `my_project/frontend` | `npm install` | `npm run start` (port 3000) | `npm test` (vitest); `npm run test:watch` | `npm run typecheck` (tsc) | `npm run build` |
| `my_project/ingestion` | `uv sync` | `uv run python ingest_book.py --docs-dir=../frontend/docs` | `uv run pytest tests/ -v` | — | — |

## Testing quirks

- **Backend** (94 tests): conftest.py sets dummy env var defaults so tests pass without `.env`.
- **Ingestion** (79 tests): same pattern — conftest.py sets dummy COHERE/QDRANT vars.
- **Frontend** (31 tests): vitest with jsdom; mocks Docusaurus modules in `src/__mocks__/docusaurus/`; vitest.config.ts has custom resolve aliases for those mocks.

## Env & config

- `.env` lives at `my_project/.env` — both backend and ingestion read it (config.py calls `load_dotenv()`).
- Required: `COHERE_API_KEY`, `QDRANT_API_KEY`, `QDRANT_HOST`, `LLM_API_KEY`.
- `LLM_API_KEY` defaults to `GEMINI_API_KEY` as fallback in config.py.
- Backend port: 8000 (dev) / 7860 (Docker/Spaces).
- Docker: `python:3.13-alpine`, excludes dev deps (`--no-group dev`).

## CI/CD

- `.github/workflows/deploy.yml`: runs backend + ingestion tests, then copies `my_project/backend/` files to Hugging Face Spaces. Triggered on push to `main` changing `my_project/backend/**`.
- Frontend is deployed **separately** to Vercel (not in this repo's CI).

## SDD workflow (opencode.md)

- After every task, create a PHR in `history/prompts/<category>/` using `.specify/templates/phr-template.prompt.md`.
- Custom commands: `sp.phr`, `sp.adr`, `sp.plan`, `sp.tasks`, `sp.implement`, etc. (defined in `.opencode/command/`).
- Constitution at `.specify/memory/constitution.md` is an **unfilled template** — populate it before relying on SDD governance rules.

## Agent skills

Five skills in `.agents/skills/` can be loaded: `chatkit-integration`, `frontend-design`, `openai-agents-sdk`, `ui-ux-futuristic-designer`, `ui-ux-pro-max`. Load via the skill tool when the task matches.
