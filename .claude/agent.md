# Physical-AI-&-Humanoid-Robotics-Textbook Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-16

## Active Technologies

- Python 3.13 for backend processing
- Cohere API for vector embeddings
- Qdrant vector database for storage
- python-dotenv for environment configuration
- PyMDX for MDX file processing
- Command-line interface tools

## Project Structure

```text
/
├── .env (API keys and configuration)
├── ingestion/
│   ├── ingest_book.py (main ingestion script)
│   └── requirements.txt (Python dependencies)
├── my-website/docs/ (source MDX files)
│   ├── glossary.mdx
│   ├── module1/
│   │   ├── chapter1.mdx
│   │   └── chapter2.mdx
│   ├── module2/
│   │   ├── chapter3.mdx
│   │   └── chapter4.mdx
│   ├── module3/
│   │   └── chapter5.mdx
│   └── module4/
│       └── chapter6.mdx
├── specs/vector-db-storage/ (feature specifications)
└── history/prompts/ (prompt history records)
```

## Commands

### Ingestion Commands
```bash
# Install dependencies
cd ingestion
pip install -r requirements.txt

# Run the book ingestion process
python ingest_book.py

# Run with custom parameters
python ingest_book.py --docs-dir "../my-website/docs" --chunk-size 512
```

### Environment Setup
```bash
# Create .env file with API keys
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

## Code Style

### Python Style
- Use 4 spaces for indentation
- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Add docstrings for all public functions
- Use meaningful variable names

### Error Handling
- Implement proper exception handling for API calls
- Use logging for debugging and monitoring
- Handle file access errors gracefully
- Implement retry mechanisms for API calls

## Recent Changes

- **vector-db-storage**: Added book vector ingestion system using Cohere embeddings and Qdrant storage
- **vector-db-storage**: Implemented MDX processing and chunking logic
- **vector-db-storage**: Created ingestion pipeline with proper metadata handling

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->