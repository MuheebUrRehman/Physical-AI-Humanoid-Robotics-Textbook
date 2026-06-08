# Data Model: Agent SDK Refactor

## Core Entities

### AgentResponse (Structured Output)
- `answer`: `str` - The grounded response based on book content.
- `confidence`: `float` - Confidence score (0.0 to 1.0).
- `citations`: `List[str]` - List of source file paths or chapter titles referenced.

### ChatRequest (Incoming)
- `query`: `str` - User's natural language question.
- `user_id`: `str` - Unique identifier for the student.
- `session_id`: `str` - Unique identifier for the conversation thread.

### SSE Message (Outgoing)
- `type`: `str` - Either "token" or "final".
- `content`: `str | AgentResponse` - Partial token or final structured object.

## State Transitions
1. **Query Input** (ChatRequest)
2. **Retrieval** (retrieval.py -> list of chunks)
3. **Guardrail Check** (Agent.input_guardrails)
4. **Streaming Generation** (Runner.run_streamed)
5. **Final Output** (AgentResponse validation)
