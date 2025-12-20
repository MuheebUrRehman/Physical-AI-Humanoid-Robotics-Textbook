# Implementation Plan: Book Vector Ingestion System

**Feature**: 1-vector-db-storage
**Created**: 2025-12-16
**Status**: Draft
**Branch**: 1-vector-db-storage

## Technical Context

This feature implements a book vector ingestion system that processes MDX files from the Physical AI & Humanoid Robotics textbook, converts them to vector embeddings using Cohere, and stores them in Qdrant vector database. The system will be implemented in Python with a single ingestion script at ingestion/ingest_book.py.

**Technologies**:
- Python 3.13 (use all compatible versions of the other packages)
- Cohere API for embeddings
- Qdrant vector database
- Python libraries for MDX processing

**Unknowns**:
- Cohere API key and endpoint details
- Qdrant connection parameters
- Specific MDX processing requirements

## Constitution Check

Based on .specify/memory/constitution.md, this implementation will:
- Follow security-first principles by storing API keys in .env files
- Maintain code quality with proper error handling
- Use industry-standard libraries for vector processing
- Follow clean architecture principles

**Potential violations**:
- Need to ensure proper data validation when processing MDX files
- Must implement proper error handling for API calls

## Gates

- [ ] Cohere API access is available
- [ ] Qdrant database is accessible
- [ ] Python environment supports required libraries
- [ ] MDX processing libraries are compatible

## Phase 0: Research

### Research Tasks

1. **MDX Processing Research**
   - Decision: Use `markdown` and `mistune` libraries to parse MDX content to plain text
   - Rationale: These libraries can handle MDX syntax and extract content effectively
   - Alternatives considered: Custom regex parsing, full React-like MDX parser

2. **Cohere Embedding Research**
   - Decision: Use Cohere's embed API with multilingual v3 embedding model
   - Rationale: Provides high-quality embeddings suitable for semantic search
   - Alternatives considered: OpenAI embeddings, Hugging Face models

3. **Qdrant Integration Research**
   - Decision: Use Qdrant's Python client library for vector storage
   - Rationale: Official client provides reliable integration with proper error handling
   - Alternatives considered: Direct HTTP API calls, other vector databases

4. **Chunking Strategy Research**
   - Decision: Use 512-token chunks with 50-token overlap to maintain context
   - Rationale: Balances retrieval quality with processing efficiency
   - Alternatives considered: Fixed character chunks, sentence-based chunks

## Phase 1: Design

### Data Model

**Vector Record**:
- `id`: Unique identifier (UUID)
- `vector`: Embedding vector from Cohere
- `payload`: Dictionary containing
  - `content`: Original text chunk
  - `source_file`: File path (e.g., "docs/module1/chapter1.mdx")
  - `module`: Module identifier (e.g., "module1")
  - `chapter`: Chapter identifier (e.g., "chapter1")
  - `chunk_index`: Position of chunk within document
  - `created_at`: Timestamp

### API Contracts

**Ingestion Process**:
- Input: Directory path containing MDX files
- Process: Read files → Extract content → Chunk → Embed → Store
- Output: Success/failure status with metrics

## Phase 2: Implementation Plan

### Step 1: Setup Project Structure
- Create `ingestion/` directory at project root
- Create `ingestion/ingest_book.py` main script
- Create `ingestion/requirements.txt` with dependencies
- Create `.env` file for API keys

### Step 2: Implement MDX Processing
- Create function to recursively scan `my-website/docs/` directory
- Implement MDX to plain text conversion
- Handle special MDX syntax and components

### Step 3: Implement Chunking Logic
- Create text chunking function with configurable size
- Implement overlap logic to maintain context
- Add metadata tracking for each chunk

### Step 4: Implement Cohere Integration
- Add Cohere API client setup
- Implement embedding function with error handling
- Handle API rate limiting and retries

### Step 5: Implement Qdrant Integration
- Set up Qdrant client connection
- Create collection for storing vectors
- Implement vector storage with metadata

### Step 6: Create Configuration System
- Load API keys from .env file
- Add configuration options for chunk size, etc.
- Implement logging and progress tracking

## Phase 3: Implementation Details

### Dependencies (requirements.txt)
- cohere (latest version)
- qdrant-client (latest version)
- python-dotenv (latest version)
- PyMDX (latest version, or appropriate MDX parser)

### File Structure
```
/
├── .env (API keys)
├── ingestion/
│   ├── ingest_book.py (main script)
│   └── requirements.txt
└── my-website/docs/ (source files)
```

### Error Handling Strategy
- File read errors: Log and continue with other files
- API errors: Implement retry with exponential backoff
- Database errors: Batch retry mechanism
- Validation errors: Skip invalid chunks with logging

### Performance Considerations
- Process files in batches to manage memory usage
- Implement parallel processing for embedding calls
- Use Qdrant batch insert for efficiency
- Add progress tracking for large datasets