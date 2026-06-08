# API Contract: Streaming Chat (v2)

## POST /chat

Starts a streaming RAG session grounded in the textbook content.

### Request
- **Headers**: `Content-Type: application/json`
- **Body**:
  ```json
  {
    "query": "What is URDF?",
    "user_id": "student_123",
    "session_id": "thread_abc"
  }
  ```

### Response
- **Headers**: `Content-Type: text/event-stream`, `Cache-Control: no-cache`
- **Body**: A stream of Server-Sent Events.

#### Event: Token
Sent repeatedly during generation.
```text
data: {"type": "token", "content": "UR"}
data: {"type": "token", "content": "DF stands for..."}
```

#### Event: Final
Sent once when generation is complete and validated against the schema.
```text
data: {
  "type": "final",
  "content": {
    "answer": "URDF stands for Unified Robot Description Format.",
    "confidence": 0.98,
    "citations": ["module1/urdf.md"]
  }
}
```

#### Event: Error
Sent if a guardrail is triggered or an internal error occurs.
```text
data: {
  "type": "error",
  "content": "I can only answer questions related to the technical book content."
}
```
