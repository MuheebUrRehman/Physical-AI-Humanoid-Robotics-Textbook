# Data Model: Book Vector Ingestion System

**Feature**: 1-vector-db-storage
**Created**: 2025-12-16
**Model**: Vector Record Schema

## Vector Record Entity

### Fields
- **id** (string, required)
  - Type: UUID string
  - Description: Unique identifier for the vector record
  - Format: Standard UUID4 format

- **vector** (array of numbers, required)
  - Type: Array of floats
  - Description: The embedding vector from Cohere
  - Length: Depends on Cohere model (typically 1024 dimensions for multilingual-v3.0)

- **payload** (object, required)
  - Type: JSON object
  - Description: Metadata associated with the vector

### Payload Sub-fields
- **content** (string, required)
  - Type: String
  - Description: The original text content of the chunk
  - Max length: Appropriate for Cohere model limits

- **source_file** (string, required)
  - Type: String
  - Description: Full path to the source MDX file
  - Format: Relative path from docs directory (e.g., "module1/chapter1.mdx")

- **module** (string, required)
  - Type: String
  - Description: Module identifier extracted from file path
  - Format: Alphanumeric with hyphens (e.g., "module1", "module-advanced-topics")

- **chapter** (string, required)
  - Type: String
  - Description: Chapter identifier extracted from file path
  - Format: Alphanumeric with hyphens (e.g., "chapter1", "introduction")

- **chunk_index** (integer, required)
  - Type: Integer
  - Description: Sequential index of this chunk within the source document
  - Range: 0 to N-1 where N is total chunks in document

- **created_at** (string, required)
  - Type: ISO 8601 timestamp
  - Description: Time when the vector was created
  - Format: YYYY-MM-DDTHH:MM:SS.sssZ

## Processing Data Structures

### MDX Document
- **file_path**: Absolute path to the MDX file
- **content**: Raw content of the MDX file
- **module_name**: Module extracted from directory path
- **chapter_name**: Chapter name derived from file name
- **chunks**: Array of text chunks extracted from document

### Text Chunk
- **text**: The actual text content of the chunk
- **start_pos**: Starting position in the original document
- **end_pos**: Ending position in the original document
- **chunk_number**: Sequential number of this chunk

## Validation Rules

1. **Vector Length**: All vectors must have consistent dimensionality based on the Cohere model used
2. **Content Length**: Content should not exceed Cohere's input token limit
3. **Required Fields**: All required fields must be present before storing in Qdrant
4. **File Path Format**: Source file paths must be relative to the docs directory
5. **Chunk Index**: Must be sequential starting from 0 for each document

## Relationships

- Each MDX document produces multiple Vector Records (1-to-many)
- Each Vector Record maps to exactly one Cohere embedding
- All Vector Records are stored in a single Qdrant collection