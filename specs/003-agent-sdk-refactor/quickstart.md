# Quickstart: Agent SDK Refactor

## Local Development

1. **Setup Environment**:
   ```bash
   cd my_project/backend
   uv sync
   ```

2. **Run Server**:
   ```bash
   uv run uvicorn app:app --reload --port 8000
   ```

3. **Test Streaming with curl**:
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "Explain ROS 2 nodes", "user_id": "test", "session_id": "test"}' \
     -N
   ```

## Key Files
- `agent.py`: Native SDK Agent configuration.
- `app.py`: FastAPI SSE endpoint logic.
- `models/chat.py`: Pydantic schemas for the agent and API.

## Troubleshooting
- **Model Errors**: Ensure `GEMINI_API_KEY` is valid.
- **Validation Errors**: Check `AgentResponse` schema in `models/chat.py` if the agent fails to return the required JSON fields.
