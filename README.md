# Physical AI & Humanoid Robotics Textbook

A comprehensive textbook on Physical AI and Humanoid Robotics with an integrated RAG (Retrieval-Augmented Generation) chatbot system for interactive learning.

## Project Structure

```
.
├── AGENTS.md                          # Agent instructions, commands, quirks
├── opencode.md                        # opencode configuration
├── project_context.md                 # Project context for AI agents
├── skills-lock.json                   # Installed agent skills lockfile
│
├── .agents/                           # Agent skills
│   └── skills/
│       ├── chatkit-integration/       # ChatKit framework integration skill
│       ├── frontend-design/           # UI/UX design guidance skill
│       ├── openai-agents-sdk/         # OpenAI Agents SDK skill
│       │   └── references/           # SDK reference docs (guardrails,
│       │                               # handoffs, sessions, streaming, etc.)
│       ├── ui-ux-futuristic-designer/ # 2026 futuristic design skill
│       │   └── references/           # Color systems, design patterns
│       └── ui-ux-pro-max/            # UI/UX Pro Max design skill
│
├── .opencode/                         # opencode command definitions
│   └── command/
│       ├── sp.adr.md                 # Create Architecture Decision Record
│       ├── sp.analyze.md             # Analyze codebase or feature design
│       ├── sp.checklist.md           # Quality checklist review
│       ├── sp.clarify.md             # Clarify ambiguous requirements
│       ├── sp.constitution.md        # Project constitution
│       ├── sp.implement.md           # Implement from spec/plan/tasks
│       ├── sp.phr.md                 # Create Prompt History Record
│       ├── sp.plan.md                # Architecture plan
│       ├── sp.reverse-engineer.md    # Reverse-engineer existing code
│       ├── sp.specify.md             # Write feature specification
│       ├── sp.tasks.md               # Task breakdown
│       └── sp.taskstoissues.md       # Convert tasks to GitHub issues
│
├── .specify/                          # SDD (Spec-Driven Development) templates
│   ├── memory/
│   │   └── constitution.md           # Project constitution (template)
│   ├── scripts/
│   │   └── bash/                     # Helper scripts
│   └── templates/
│       ├── adr-template.md           # ADR document template
│       ├── agent-file-template.md    # Agent file template
│       ├── checklist-template.md     # Quality checklist template
│       ├── phr-template.prompt.md    # Prompt History Record template
│       ├── plan-template.md          # Architecture plan template
│       ├── spec-template.md          # Specification template
│       └── tasks-template.md         # Tasks breakdown template
│
├── docs/                              # Project documentation
│   └── reverse-engineered/           # Reverse-engineered artifacts
│       ├── intelligence-object.md    # Reusable patterns & skills
│       ├── plan.md                   # Architecture plan
│       ├── spec.md                   # System specification
│       └── tasks.md                  # Implementation tasks
│
├── history/                           # Prompt history records
│   └── prompts/
│       └── reverse-engineered/       # Reverse engineering session PHRs
│
├── my_project/                        # Main project code
│   │
│   ├── .env                          # Environment variables (gitignored)
│   ├── .env.example                  # Environment variable template
│   │
│   ├── backend/                      # FastAPI + OpenAI Agents SDK RAG chatbot
│   │   ├── .dockerignore
│   │   ├── .python-version           # Python 3.13
│   │   ├── Dockerfile                # python:3.13-alpine container
│   │   ├── pyproject.toml            # Python dependencies (uv)
│   │   ├── uv.lock                   # Locked dependency versions
│   │   ├── app.py                    # FastAPI application, routes, CORS, lifespan
│   │   ├── agent.py                  # OpenAI Agents SDK agents & guardrails
│   │   ├── config.py                 # Environment configuration + validation
│   │   ├── retrieval.py              # Cohere embedding + Qdrant vector search
│   │   ├── store.py                  # SQLite persistence for ChatKit threads
│   │   ├── chatkit_server.py         # ChatKit protocol bridge (extends ChatKitServer)
│   │   ├── chatkit.db                # SQLite database (auto-created, gitignored)
│   │   ├── models/
│   │   │   └── chat.py              # Pydantic schemas (ChatRequest, AgentResponse, etc.)
│   │   ├── utils/
│   │   │   └── validation.py        # Input sanitization (XSS, SQLi, path traversal)
│   │   ├── scripts/
│   │   │   └── read_db.py           # Debug utility to inspect chatkit.db
│   │   └── tests/                    # pytest test suite (15 tests)
│   │       ├── conftest.py           # Pytest fixtures + dummy env vars
│   │       ├── test_retrieval.py     # 4 retrieval integration tests
│   │       ├── test_agent_integration.py  # 8 agent pipeline tests
│   │       ├── test_agent_v2.py      # 1 agent response validation test
│   │       ├── test_streaming.py     # 1 SSE streaming endpoint test
│   │       └── test_performance.py   # 1 performance placeholder test
│   │
│   ├── frontend/                     # Docusaurus textbook site + ChatKit widget
│   │   ├── package.json             # npm dependencies (React 19, Docusaurus 3.9)
│   │   ├── tsconfig.json            # TypeScript configuration
│   │   ├── pyrightconfig.json       # Python type-checking for code examples
│   │   ├── docusaurus.config.ts     # Site config, navbar, footer, plugins
│   │   ├── sidebars.ts              # Documentation sidebar structure
│   │   ├── vercel.json              # Vercel deployment configuration
│   │   ├── docs/                    # Textbook content (MDX)
│   │   │   ├── glossary.mdx        # Key terms glossary
│   │   │   ├── module1/
│   │   │   │   ├── chapter1.mdx    # Foundations of Physical AI
│   │   │   │   └── chapter2.mdx    # ROS 2, The Robotic Nervous System
│   │   │   ├── module2/
│   │   │   │   ├── chapter3.mdx    # Gazebo, Your First Digital Twin
│   │   │   │   └── chapter4.mdx    # Unity, High-Fidelity Simulation
│   │   │   ├── module3/
│   │   │   │   └── chapter5.mdx    # Isaac Sim, Isaac ROS, VSLAM, Navigation
│   │   │   └── module4/
│   │   │       └── chapter6.mdx    # Voice-to-Action, LLM Planning & Capstone
│   │   ├── src/                    # React source code
│   │   │   ├── css/
│   │   │   │   └── custom.css     # Global styles (futuristic dark theme)
│   │   │   ├── pages/
│   │   │   │   ├── index.tsx       # Homepage with hero + module cards
│   │   │   │   └── index.module.css # Hero section styles
│   │   │   ├── components/
│   │   │   │   ├── ChatKitWidget.tsx        # Floating chat widget
│   │   │   │   ├── ChatKitWidget.module.css # Widget styles
│   │   │   │   └── HomepageFeatures/
│   │   │   │       ├── index.tsx            # Clickable module cards
│   │   │   │       └── styles.module.css    # Card grid styles
│   │   │   ├── theme/
│   │   │   │   └── Root.tsx        # Global wrapper (includes ChatKitWidget)
│   │   │   └── utils/
│   │   │       ├── chatkit-fetch.ts        # Fetch interceptor (injects page context)
│   │   │       └── context-extractor.ts    # Extracts URL, title, headings
│   │   ├── static/                 # Static assets
│   │   │   ├── .nojekyll
│   │   │   └── img/
│   │   │       ├── logo.svg               # Site logo
│   │   │       ├── favicon.ico            # Favicon
│   │   │       ├── docusaurus.png         # Social preview image
│   │   │       └── docusaurus-social-card.jpg
│   │   └── code/                   # Code examples for textbook
│   │       ├── gazebo_worlds/
│   │       │   └── empty.world           # Gazebo simulation world
│   │       ├── isaac_sim_assets/
│   │       │   └── README.md
│   │       ├── ros2_ws/
│   │       │   ├── pyrightconfig.json
│   │       │   └── src/
│   │       │       ├── humanoid_control_pkg/
│   │       │       │   ├── CMakeLists.txt
│   │       │       │   ├── package.xml
│   │       │       │   ├── scripts/
│   │       │       │   │   └── heartbeat_publisher.py
│   │       │       │   └── urdf/
│   │       │       │       └── simple_humanoid.urdf
│   │       │       └── isaac_ros_pkg/
│   │       │           └── README.md
│   │       ├── unity_projects/
│   │       │   └── PlaceholderJointController.cs
│   │       └── vla_scripts/
│   │           └── README.md
│   │
│   └── ingestion/                   # MDX → Cohere embeddings → Qdrant
│       ├── requirements.txt         # Python dependencies (pip)
│       ├── ingest_book.py           # Full ingestion pipeline script
│       ├── test_ingest_book.py      # Unit tests (unittest)
│       └── e2e_test.py              # End-to-end ingestion test
│
└── .github/
    └── workflows/
        └── deploy.yml               # CI/CD: deploys backend to HF Spaces
```

## Commands to Navigate and Run

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (Modern Python package manager)
- Node.js v20+

### Backend Setup and Run
1. Navigate to the backend directory:
```bash
cd my_project/backend
```

2. Sync dependencies and set up the environment:
```bash
uv sync
```

3. Configure environment variables in `.env` file:
```env
# Required: Cohere + Qdrant for vector search
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_HOST=your_qdrant_host_here
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=book_vectors

# LLM Provider — OpenRouter (recommended) or Gemini fallback
# Switch models by changing LLM_MODEL only; no code changes needed.
LLM_API_KEY=sk-or-v1-your_openrouter_key_here
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=qwen/qwen3-coder
LLM_SITE_URL=https://your-site.com
LLM_APP_NAME=Your App Name

# Fallback: Gemini key used if LLM_API_KEY is not set (backward compat)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional overrides
TOP_K=5
QUERY_TIMEOUT=30
```

4. Start the backend server:
```bash
uv run uvicorn app:app --reload --port 8000
```

### Frontend Setup and Run
1. Navigate to the frontend directory:
```bash
cd my_project/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run start
```

The frontend will be available at `http://localhost:3000` and the backend API at `http://localhost:8000`.

### Deployment Environment Variables

When frontend and backend are deployed on different domains (for example, Vercel + Hugging Face Spaces), configure these variables:

- Frontend (`my_project/frontend` build environment):
  - `API_BASE_URL=https://<your-hf-space-domain>`
- Backend (`my_project/backend` runtime environment):
  - `ALLOWED_ORIGINS=https://<your-vercel-domain>,http://localhost:3000`

Notes:
- Do not include a trailing slash in origins.
- The frontend sends chat requests to `${API_BASE_URL}/chat`.

### Content Ingestion
1. Navigate to the ingestion directory:
```bash
cd my_project/ingestion
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the ingestion script to process book content:
```bash
python ingest_book.py --docs-dir=./my_project/frontend/docs
```

### Running Tests

```bash
# Backend tests (pytest)
cd my_project/backend
uv run pytest tests/ -v

# Ingestion tests (unittest)
cd my_project/ingestion
python -m unittest test_ingest_book.py

# Ingestion E2E test
cd my_project/ingestion
python e2e_test.py

# Frontend typecheck
cd my_project/frontend
npm run typecheck
```

### Full Application Usage
1. Start the backend server first
2. In a separate terminal, start the frontend server
3. Visit `http://localhost:3000` in your browser
4. Use the chat interface to ask questions about the textbook content
