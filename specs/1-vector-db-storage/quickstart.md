# Quickstart Guide: Book Vector Ingestion System

**Feature**: 1-vector-db-storage
**Created**: 2025-12-16

## Prerequisites

1. **Python Environment**: Python 3.8 or higher
2. **API Keys**:
   - Cohere API key (sign up at https://cohere.ai)
   - Qdrant database access (local or cloud instance)
3. **System Dependencies**: Git, pip

## Setup Instructions

### 1. Clone and Navigate to Project
```bash
git clone <your-repo-url>
cd <your-project-directory>
```

### 2. Install Python Dependencies
```bash
cd ingestion
pip install -r requirements.txt
```

If requirements.txt doesn't exist yet, install the required packages:
```bash
pip install cohere qdrant-client python-dotenv PyMDX
```

### 3. Configure Environment Variables
Create a `.env` file in the project root directory:

```bash
# .env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here  # Optional if no auth
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 4. Verify Qdrant Connection
Make sure your Qdrant database is running and accessible at the configured host/port.

## Usage Instructions

### Run the Ingestion Process
```bash
cd ingestion
python ingest_book.py
```

### Custom Configuration Options
```bash
# With custom parameters
python ingest_book.py \
  --docs-dir "../my-website/docs" \
  --chunk-size 512 \
  --chunk-overlap 50 \
  --qdrant-host localhost \
  --qdrant-port 6333 \
  --cohere-model embed-multilingual-v3.0
```

## Expected Output
Upon successful execution, you should see:
- Progress indicators as files are processed
- Summary statistics showing:
  - Number of files processed
  - Number of text chunks created
  - Number of vectors stored in Qdrant
  - Total processing time

## Verification Steps

### 1. Check Qdrant Collection
Verify that vectors were stored in Qdrant:
```python
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)
# Check if the collection exists and has points
collection_info = client.get_collection("book_vectors")
print(f"Points in collection: {collection_info.points_count}")
```

### 2. Verify Metadata
Confirm that metadata includes proper source file information:
- Each vector should have `source_file`, `module`, `chapter`, and `chunk_index` fields
- Content should match the original MDX file text

## Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Verify your Cohere and Qdrant API keys are correct
   - Check that your `.env` file is properly formatted

2. **File Access Errors**:
   - Ensure the docs directory path is correct
   - Check that MDX files are readable

3. **Qdrant Connection Issues**:
   - Verify Qdrant is running and accessible
   - Check host and port configuration

4. **Memory Issues with Large Files**:
   - Reduce chunk size if processing very large MDX files
   - Consider processing files in smaller batches

### Error Handling
The ingestion script includes comprehensive error handling:
- Files that fail to process will be logged but won't stop the entire process
- API rate limits are handled with exponential backoff
- Invalid chunks are skipped with appropriate logging

## Next Steps

After successful ingestion:
1. Implement a search function to query the stored vectors
2. Create a user interface to interact with the vector database
3. Add monitoring and logging for production use