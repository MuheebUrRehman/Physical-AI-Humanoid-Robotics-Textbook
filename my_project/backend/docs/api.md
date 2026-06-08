# RAG Chatbot Backend API Documentation

## Overview
The RAG Chatbot Backend provides a Retrieval-Augmented Generation chat interface for technical book content. The system uses Cohere for embeddings, Qdrant for vector storage, and Gemini for response generation.

## Architecture & Performance
The backend utilizes a non-blocking asynchronous architecture:
- **Async Retrieval**: Cohere embeddings and Qdrant searches are performed using asynchronous clients to prevent event loop blocking.
- **Guardrail Singleton**: The input guardrail uses a pre-initialized singleton agent with `gemini-3.1-flash-lite` for ultra-fast validation.
- **Streaming**: Responses are delivered word-by-word via Server-Sent Events (SSE).

## Base URL
```
http://localhost:8000
```

## Endpoints

### Health Check
```
GET /health
```

**Description**: Check the health status of the service.

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-12-17T10:30:00.123456"
}
```

### Chat
```
POST /chat
```

**Description**: Submit a query and receive a response grounded in book content.

**Headers**:
- `Content-Type: application/json`

**Request Body**:
```json
{
  "query": "string (required, 3-2000 characters)",
  "user_id": "string (optional, max 100 characters)",
  "session_id": "string (optional, max 100 characters)"
}
```

**Response**:
```json
{
  "response": "Generated response text",
  "source_chunks": ["List of source chunks used"],
  "confidence": 0.8,
  "query_id": "Optional query identifier"
}
```

**Response Headers**:
- `X-Response-Time`: Total response time in seconds
- `X-Retrieval-Time`: Time spent on retrieval in seconds
- `X-Agent-Time`: Time spent on agent processing in seconds
- `X-Total-Time`: Total processing time in seconds

**Example Request**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is physical AI?",
    "user_id": "user123",
    "session_id": "session456"
  }'
```

## Error Handling

### HTTP Status Codes
- `200`: Success
- `400`: Bad request (invalid input)
- `500`: Internal server error

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "query_id": "Optional query identifier"
}
```

## Configuration
The service uses the following environment variables:

- `COHERE_API_KEY`: API key for Cohere embeddings
- `QDRANT_API_KEY`: API key for Qdrant vector store
- `GEMINI_API_KEY`: API key for Gemini
- `QDRANT_HOST`: Host URL for Qdrant
- `QDRANT_PORT`: Port for Qdrant (default: 6333)
- `QDRANT_COLLECTION_NAME`: Name of the collection (default: book_chunks)
- `TOP_K`: Number of chunks to retrieve (default: 5)
- `QUERY_TIMEOUT`: Timeout for queries in seconds (default: 30)