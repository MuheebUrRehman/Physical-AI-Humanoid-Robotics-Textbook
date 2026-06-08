# Data Model: RAG Performance & Robustness

## Core Entities

### SSEBuffer (Frontend)
- `buffer`: `string` - Raw accumulated stream content.
- `delimiter`: `string` - The `\n\n` sequence used to identify complete events.

### AsyncRetrievalPipeline (Backend)
- `embedding_client`: `AsyncClient` (Cohere)
- `vector_client`: `AsyncQdrantClient` (Qdrant)

### GlobalJudgeAgent (Backend)
- `instance`: `Agent` - Singleton instance initialized at startup.
- `model`: `gemini-3.1-flash-lite` - Optimized for speed.

## State Transitions
1. **Raw Chunk Received** (Frontend): Append to `SSEBuffer`.
2. **Frame Detected**: Check for `\n\n`.
3. **Parse Event**: Extract JSON from `data: ` and reset buffer for processed parts.
4. **Async Retrieval Initiated** (Backend): Concurrent embedding and search operations.
5. **Non-blocking Wait**: Event loop yields while waiting for I/O.
6. **Concurrent Processing**: Other requests (streaming) proceed.
