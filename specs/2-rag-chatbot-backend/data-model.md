# Data Model: RAG Chatbot Backend with ChatKit Integration

## Entities

### Query
**Description**: A user's text input requesting information from the book content
**Fields**:
- text: str - The user's query text
- metadata: dict - Additional metadata about the query (timestamp, user ID, etc.)
- embedding: list[float] - Vector representation of the query for similarity matching

### Embedding
**Description**: A numerical representation of the query text for semantic similarity matching
**Fields**:
- vector: list[float] - The numerical vector representation
- model: str - The embedding model used to generate the vector
- created_at: datetime - Timestamp of when the embedding was created

### Book Chunk
**Description**: A segment of book content retrieved from the vector store
**Fields**:
- text: str - The actual text content of the chunk
- relevance_score: float - Score indicating similarity to the query
- source_document: str - Reference to the original document
- chunk_id: str - Unique identifier for the chunk
- metadata: dict - Additional metadata about the chunk

### Response
**Description**: The system-generated answer to the user's query
**Fields**:
- text: str - The response text
- confidence: float - Confidence score of the response
- sources: list[str] - List of source chunks used to generate the response
- timestamp: datetime - When the response was generated
- query_relevance: bool - Whether the original query was relevant to book content

### Context
**Description**: Context object for the OpenAI Agents SDK
**Fields**:
- book_chunks: list[Book Chunk] - List of relevant book chunks to be used as context
- query: Query - The original user query
- metadata: dict - Additional context metadata

## State Transitions

### Query Processing Flow
1. **Query Received** → **Embedding Generated** (when user submits query)
2. **Embedding Generated** → **Similarity Search** (when embedding is created)
3. **Similarity Search** → **Context Created** (when relevant chunks are found)
4. **Context Created** → **Response Generated** (when agent processes query with context)
5. **Response Generated** → **Response Returned** (when response is formatted for client)

### Guardrail Flow
1. **Query Received** → **Relevance Check** (when user submits query)
2. **Relevance Check** → **Query Processed** (if query is relevant to book content)
3. **Relevance Check** → **Rejection Response** (if query is off-topic)
4. **Rejection Response** → **Response Returned** (when rejection is sent to client)

## Validation Rules

### Query Validation
- Must be non-empty string
- Must be less than 1000 characters
- Must not contain excessive special characters or potential injection attempts

### Book Chunk Validation
- Text must be non-empty
- Relevance score must be between 0 and 1
- Chunk must have a valid source document reference

### Response Validation
- Text must be non-empty
- Must reference at least one source chunk
- Confidence score must be between 0 and 1

### Context Validation
- Must contain at least one book chunk when query is relevant
- Book chunks must have valid relevance scores
- Query must be properly associated with the context