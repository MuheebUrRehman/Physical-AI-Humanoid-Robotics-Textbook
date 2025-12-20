# Research Document: Book Vector Ingestion System

**Feature**: 1-vector-db-storage
**Created**: 2025-12-16
**Researcher**: Claude

## MDX Processing Research

### Decision: Use `markdown` and custom parsing for MDX content extraction
- **Rationale**: MDX files contain JSX components that need to be stripped while preserving the actual text content. We'll use a combination of regex and markdown parsing to extract plain text.
- **Implementation**: Use regex to remove JSX tags and then process the remaining markdown content
- **Alternatives considered**:
  - Full React-like MDX parser: Too heavy and complex for simple text extraction
  - Custom regex only: Might miss some edge cases
  - `remark` and `rehype` via Py libraries: Limited Python support

## Cohere Embedding Research

### Decision: Use Cohere's embed-multilingual-v3.0 model
- **Rationale**: This model provides high-quality embeddings with good performance for technical content like textbooks. It supports multiple languages and handles domain-specific text well.
- **Implementation**: Use Cohere's Python client with proper error handling and rate limiting
- **Alternatives considered**:
  - OpenAI embeddings: Would require different API key and pricing model
  - Hugging Face models: Would require local model hosting and more computational resources
  - Sentence Transformers: Local models but require more setup and maintenance

## Qdrant Integration Research

### Decision: Use Qdrant's Python client with gRPC
- **Rationale**: The official Python client provides the most reliable and feature-complete integration with Qdrant. It handles connection pooling, retries, and serialization automatically.
- **Implementation**: Use `qdrant-client` library with batch operations for efficiency
- **Alternatives considered**:
  - Direct HTTP API calls: More manual work and error handling required
  - Other vector databases (Pinecone, Weaviate): Would require different implementation approach

## Chunking Strategy Research

### Decision: 512-token chunks with 50-token overlap
- **Rationale**: This size provides a good balance between context preservation and embedding quality. The overlap helps maintain semantic connections across chunk boundaries.
- **Implementation**: Use a simple token counter based on word/sentence boundaries rather than exact tokenization to keep it lightweight
- **Alternatives considered**:
  - Fixed character chunks: Might break semantic meaning
  - Sentence-based chunks: Could result in very uneven chunk sizes
  - Exact tokenization: Would require additional dependencies and processing time

## Environment Configuration Research

### Decision: Use python-dotenv with standard .env file
- **Rationale**: The python-dotenv library is the standard way to handle environment variables in Python applications. It's lightweight and secure.
- **Implementation**: Create .env file at project root with COHERE_API_KEY and QDRANT_API_KEY
- **Alternatives considered**:
  - Hardcoded values: Insecure and not recommended
  - Command-line arguments: Less secure and harder to manage
  - Configuration files: More complex than needed for just API keys

## File Processing Strategy Research

### Decision: Recursive directory traversal with .mdx filtering
- **Rationale**: The most straightforward approach to find all MDX files in the docs directory structure, including nested modules.
- **Implementation**: Use Python's os.walk() to recursively find all .mdx files
- **Alternatives considered**:
  - Glob patterns: Might miss nested directories
  - Manual file listing: Not scalable when new files are added