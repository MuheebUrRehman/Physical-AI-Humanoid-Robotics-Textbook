# Research: RAG Performance & Robustness

## Decision 1: `cohere.AsyncClient` Integration
- **Decision**: Migrate `retrieval.py` to use `AsyncClient`.
- **Rationale**: The current synchronous `co.embed` blocks the FastAPI event loop. In high-traffic scenarios, this leads to request queueing. Asynchronous clients allow the server to process other requests (like streaming tokens) while waiting for embeddings.
- **Alternatives Considered**: `run_in_executor` - Rejected as more complex to manage than using the native async SDK provided by Cohere.

## Decision 2: `AsyncQdrantClient` Migration
- **Decision**: Replace `QdrantClient` with `AsyncQdrantClient`.
- **Rationale**: Similar to embeddings, vector search is a network-bound I/O operation. Using the async client ensures the server remains non-blocking during the top-K retrieval phase.

## Decision 3: Global Singleton Judge Agent
- **Decision**: Initialize the `judge_agent` at the module level in `agent.py`.
- **Rationale**: Re-initializing an `Agent` object on every request introduces significant overhead (>200ms) due to SDK internal setups. A singleton pattern ensures the agent is ready immediately.
- **Impact**: Instant query validation before retrieval begins.

## Decision 4: `gemini-3.1-flash-lite` for Guardrails
- **Decision**: Standardize on the `flash-lite` model for classification tasks.
- **Rationale**: Classification (Yes/No relevance) is a low-complexity task. The "flash-lite" model provides the fastest possible inference at the lowest cost, making it the ideal choice for a high-frequency guardrail.

## Decision 5: Client-Side SSE Buffer
- **Decision**: Implement a string accumulation buffer in `FloatingChat.tsx` using `\n\n` as the frame delimiter.
- **Rationale**: Network fragmentation often splits a single `data: {...}` line into multiple packets. The current implementation tries to parse partial JSON, causing technical errors. Buffering until the official SSE separator (`\n\n`) is reached guarantees data integrity.
