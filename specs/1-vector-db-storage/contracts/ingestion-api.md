# API Contracts: Book Vector Ingestion System

**Feature**: 1-vector-db-storage
**Created**: 2025-12-16
**API Type**: Command-line interface

## Main Ingestion Function

### Function: `ingest_books_to_vector_db()`
- **Purpose**: Process all MDX files and store vector embeddings in Qdrant
- **Input**: Configuration parameters (directory path, API keys, chunk size)
- **Output**: Status result with statistics

#### Parameters:
- `docs_directory`: Path to the directory containing MDX files (default: "./my-website/docs")
- `chunk_size`: Maximum number of tokens per chunk (default: 512)
- `chunk_overlap`: Number of tokens to overlap between chunks (default: 50)
- `qdrant_url`: URL for Qdrant database connection (default: "localhost:6333")
- `cohere_model`: Cohere model to use for embeddings (default: "embed-multilingual-v3.0")

#### Return Value:
- **Success**: Dictionary with
  - `status`: "success"
  - `files_processed`: Number of MDX files processed
  - `chunks_created`: Total number of text chunks created
  - `vectors_stored`: Number of vectors successfully stored in Qdrant
  - `processing_time`: Time taken in seconds
- **Error**: Dictionary with
  - `status`: "error"
  - `error_message`: Description of the error
  - `partial_results`: Any partial results if applicable

## Internal Functions

### Function: `extract_text_from_mdx(file_path)`
- **Purpose**: Convert MDX content to plain text
- **Input**: Path to MDX file
- **Output**: Plain text content

#### Parameters:
- `file_path`: Path to the MDX file to process

#### Return Value:
- String containing the extracted text content

### Function: `chunk_text(text, chunk_size, overlap)`
- **Purpose**: Split text into overlapping chunks
- **Input**: Text content, chunk size, and overlap
- **Output**: Array of text chunks with metadata

#### Parameters:
- `text`: The text to chunk
- `chunk_size`: Maximum size of each chunk
- `overlap`: Size of overlap between chunks

#### Return Value:
- Array of objects with:
  - `text`: The chunk text
  - `start_pos`: Start position in original text
  - `end_pos`: End position in original text
  - `chunk_number`: Sequential number

### Function: `embed_chunks(chunks)`
- **Purpose**: Generate vector embeddings for text chunks
- **Input**: Array of text chunks
- **Output**: Array of embedding vectors

#### Parameters:
- `chunks`: Array of text chunk objects

#### Return Value:
- Array of embedding vectors (arrays of floats)

### Function: `store_vectors_in_qdrant(vectors, metadata)`
- **Purpose**: Store embedding vectors with metadata in Qdrant
- **Input**: Array of vectors and corresponding metadata
- **Output**: Success status

#### Parameters:
- `vectors`: Array of embedding vectors
- `metadata`: Array of metadata objects corresponding to each vector

#### Return Value:
- Boolean indicating success or failure

## External API Integration Contracts

### Cohere Embed API
- **Endpoint**: `https://api.cohere.ai/v1/embed`
- **Method**: POST
- **Headers**:
  - `Authorization: Bearer {COHERE_API_KEY}`
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "model": "embed-multilingual-v3.0",
    "texts": ["array", "of", "text", "chunks"],
    "input_type": "search_document"
  }
  ```
- **Response**:
  ```json
  {
    "embeddings": [[...], [...], ...],
    "meta": {...}
  }
  ```

### Qdrant API
- **Endpoint**: `http://{qdrant_host}:{qdrant_port}/collections/{collection_name}/points`
- **Method**: PUT
- **Headers**:
  - `Content-Type: application/json`
  - `api-key: {QDRANT_API_KEY}` (if authentication enabled)
- **Request Body**:
  ```json
  {
    "points": [
      {
        "id": "unique-uuid",
        "vector": [0.1, 0.2, ...],
        "payload": {
          "content": "text content",
          "source_file": "path/to/file.mdx",
          "module": "module1",
          "chapter": "chapter1",
          "chunk_index": 0,
          "created_at": "timestamp"
        }
      }
    ]
  }
  ```
- **Response**: Success confirmation or error details

## Configuration Contract

### Environment Variables
- `COHERE_API_KEY`: API key for Cohere service
- `QDRANT_API_KEY`: API key for Qdrant database (optional if no auth)
- `QDRANT_HOST`: Host for Qdrant database (default: localhost)
- `QDRANT_PORT`: Port for Qdrant database (default: 6333)

### Command Line Interface
- **Script**: `ingestion/ingest_book.py`
- **Usage**: `python ingest_book.py [options]`
- **Options**:
  - `--docs-dir`: Directory containing MDX files (default: "./my-website/docs")
  - `--chunk-size`: Size of text chunks (default: 512)
  - `--chunk-overlap`: Overlap between chunks (default: 50)
  - `--qdrant-host`: Qdrant host (default: "localhost")
  - `--qdrant-port`: Qdrant port (default: 6333)
  - `--cohere-model`: Cohere model to use (default: "embed-multilingual-v3.0")