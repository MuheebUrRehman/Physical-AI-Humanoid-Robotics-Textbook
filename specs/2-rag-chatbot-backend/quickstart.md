# RAG Chatbot Backend with ChatKit Integration Development Guidelines

Auto-generated from feature plan. Last updated: 2025-12-23

## Active Technologies

- Python 3.13
- FastAPI (https://fastapi.tiangolo.com/)
- Cohere API for embeddings
- Qdrant Cloud for vector storage
- OpenAI Agents SDK v0.6 (https://openai.github.io/openai-agents-python/) with Gemini backend
- ChatKit (https://platform.openai.com/docs/guides/chatkit)
- python-dotenv for environment management
- pydantic for data validation

## Project Structure

```text
project-root/
├── .env                    # API keys and secrets at project root
├── backend/
│   ├── app.py
│   ├── retrieval.py
│   ├── agent.py
│   ├── config.py
│   ├── models/
│   │   └── chat.py
│   ├── utils/
│   │   └── validation.py
│   └── tests/
│       ├── test_app.py
│       ├── test_retrieval.py
│       └── test_agent.py
```

## Commands

- `uv run uvicorn backend.app:app --reload` - Start the FastAPI development server
- `uv run pytest` - Run tests
- `uv run python -m backend.agent` - Test agent functionality

## Code Style

- Use async/await for all I/O operations
- Follow the OpenAI Agents SDK v0.6 documentation for agent implementation
- Use context management with the OpenAI Agents SDK via the context property in runner.run
- Implement Input Guardrail agent to validate query relevance before processing
- Remove hard-coded lists that restrict user input to book-related content
- Follow FastAPI best practices for request/response handling

## Recent Changes

- Implemented Input Guardrail agent for query validation
- Added context management using OpenAI Agents SDK
- Removed hard-coded restriction lists for query validation
- Updated API contracts for ChatKit integration

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->