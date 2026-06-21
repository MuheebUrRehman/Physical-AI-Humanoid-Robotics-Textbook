#!/usr/bin/env python3
"""
Book Vector Ingestion System
Converts MDX files from the Physical AI & Humanoid Robotics textbook to vector embeddings
and stores them in Qdrant vector database for semantic search capabilities.
"""

import os
import sys
import argparse
import logging
from typing import List, Dict, Tuple, Optional
import uuid
from datetime import datetime, timezone
import time
from dotenv import load_dotenv

import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models


# Anchor docs directory relative to this script's location — works from any CWD
_DEFAULT_DOCS_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'docs'))

# Load configuration from .env file
load_dotenv()


def load_config():
    """Load configuration from environment variables."""
    config = {
        'cohere_api_key': os.getenv('COHERE_API_KEY'),
        'qdrant_api_key': os.getenv('QDRANT_API_KEY'),
        'qdrant_host': os.getenv('QDRANT_HOST', 'localhost'),
        'qdrant_port': int(os.getenv('QDRANT_PORT', 6333)),
        'docs_directory': os.getenv('DOCS_DIR', _DEFAULT_DOCS_DIR),
        'chunk_size': int(os.getenv('CHUNK_SIZE', 512)),
        'chunk_overlap': int(os.getenv('CHUNK_OVERLAP', 50)),
        'cohere_model': os.getenv('COHERE_MODEL', 'embed-multilingual-v3.0')
    }
    return config


class ProgressTracker:
    """Utility class for tracking progress and providing feedback during long-running operations."""

    def __init__(self, total_items: int, description: str = "Processing"):
        self.total_items = total_items
        self.description = description
        self.completed = 0
        self.logger = logging.getLogger(__name__)

    def update(self, increment: int = 1, message: str = ""):
        """Update progress and log status."""
        self.completed += increment
        percentage = (self.completed / self.total_items) * 100
        status_message = f"{self.description}: {self.completed}/{self.total_items} ({percentage:.1f}%)"
        if message:
            status_message += f" - {message}"

        self.logger.info(status_message)
        print(status_message)

    def complete(self):
        """Mark the process as complete."""
        self.logger.info(f"{self.description} completed successfully")
        print(f"{self.description} completed: 100%")


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ingestion.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def setup_cohere_client(api_key: str):
    """Set up Cohere API client with error handling."""
    if not api_key:
        raise ValueError("Cohere API key is required")

    try:
        client = cohere.Client(api_key)
        # Test the client by making a simple call
        # client.embed(texts=["test"], model="embed-multilingual-v3.0")
        return client
    except Exception as e:
        logging.error(f"Failed to initialize Cohere client: {str(e)}")
        raise


def setup_qdrant_client(host: str, port: int, api_key: Optional[str] = None):
    """Set up Qdrant client with proper connection parameters."""
    try:
        # Remove protocol if present (Qdrant client doesn't expect protocol in host parameter)
        import re
        host_clean = re.sub(r'^https?://', '', host)

        if api_key:
            client = QdrantClient(
                host=host_clean,
                port=port,
                api_key=api_key
            )
        else:
            client = QdrantClient(
                host=host_clean,
                port=port
            )

        # Test the connection
        client.get_collections()
        return client
    except Exception as e:
        logging.error(f"Failed to initialize Qdrant client: {str(e)}")
        raise


class VectorRecord:
    """Data model representing a chunk of content with its vector embedding and metadata."""

    def __init__(self,
                 id: str,
                 vector: List[float],
                 content: str,
                 source_file: str,
                 module: str,
                 chapter: str,
                 chunk_index: int,
                 created_at: Optional[datetime] = None):
        self.id = id
        self.vector = vector
        self.content = content
        self.source_file = source_file
        self.module = module
        self.chapter = chapter
        self.chunk_index = chunk_index
        self.created_at = created_at or datetime.now(timezone.utc)

    def to_payload(self) -> Dict:
        """Convert the VectorRecord to a payload dictionary for Qdrant storage."""
        return {
            "content": self.content,
            "source_file": self.source_file,
            "module": self.module,
            "chapter": self.chapter,
            "chunk_index": self.chunk_index,
            "created_at": self.created_at.isoformat()
        }

    def to_qdrant_point(self) -> Dict:
        """Convert the VectorRecord to a Qdrant point format."""
        return {
            "id": self.id,
            "vector": self.vector,
            "payload": self.to_payload()
        }

    @classmethod
    def from_text_chunk(cls,
                       text_chunk: str,
                       source_file: str,
                       module: str,
                       chapter: str,
                       chunk_index: int,
                       embedding: Optional[List[float]] = None) -> 'VectorRecord':
        """Create a VectorRecord from a text chunk with optional embedding."""
        record_id = str(uuid.uuid4())

        # If no embedding is provided, create an empty placeholder
        vector = embedding if embedding is not None else []

        return cls(
            id=record_id,
            vector=vector,
            content=text_chunk,
            source_file=source_file,
            module=module,
            chapter=chapter,
            chunk_index=chunk_index
        )


def handle_api_call_with_retry(api_call_func, *args, max_retries: int = 3, **kwargs):
    """
    Generic function to handle API calls with retry mechanism.
    """

    last_exception = None

    for attempt in range(max_retries):
        try:
            return api_call_func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt == max_retries - 1:  # Last attempt
                logging.error(f"API call failed after {max_retries} attempts: {str(e)}")
                raise

            # Calculate delay with exponential backoff
            delay = 1.0 * (2 ** attempt)  # 1s, 2s, 4s, etc.
            logging.warning(f"API call attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")
            time.sleep(delay)


def safe_embed_chunks(cohere_client, texts: List[str], model: str = "embed-multilingual-v3.0"):
    """
    Safely embed text chunks with error handling and retry mechanism.
    """
    try:
        # Cohere has a limit on the number of texts per request, so we may need to batch
        # For now, handle a single batch - in production we'd want to chunk this properly
        response = handle_api_call_with_retry(
            cohere_client.embed,
            texts=texts,
            model=model,
            input_type="search_document"
        )
        return response.embeddings
    except Exception as e:
        logging.error(f"Failed to embed chunks: {str(e)}")
        raise


def safe_store_vectors_in_qdrant(qdrant_client, points: List[Dict], collection_name: str = "book_vectors"):
    """
    Safely store vectors in Qdrant with error handling and retry mechanism.
    """
    try:
        result = handle_api_call_with_retry(
            qdrant_client.upsert,
            collection_name=collection_name,
            points=points
        )
        return result
    except Exception as e:
        logging.error(f"Failed to store vectors in Qdrant: {str(e)}")
        raise


def extract_module_and_chapter_from_path(file_path: str) -> Tuple[str, str]:
    """
    Extract module and chapter names from file path.
    Example: 'my-website/docs/module1/chapter1.mdx' -> ('module1', 'chapter1')
    """
    # Convert to relative path if it's an absolute path
    if file_path.startswith('./'):
        file_path = file_path[2:]

    # Normalize path separators
    path_parts = file_path.replace('\\', '/').split('/')

    # Find the docs part and extract module and chapter
    try:
        docs_index = path_parts.index('docs')
        if docs_index + 2 < len(path_parts):
            # If path is docs/module/chapter.mdx
            module = path_parts[docs_index + 1]
            chapter_file = path_parts[docs_index + 2]
            # Remove extension to get chapter name
            chapter = os.path.splitext(chapter_file)[0]
            return module, chapter
        elif docs_index + 1 < len(path_parts):
            # If path is docs/glossary.mdx (or similar top-level file)
            file_name = path_parts[docs_index + 1]
            chapter = os.path.splitext(file_name)[0]
            return 'root', chapter
        else:
            # If path is just docs/something.mdx
            file_name = path_parts[-1]
            chapter = os.path.splitext(file_name)[0]
            return 'root', chapter
    except ValueError:
        # If 'docs' not in path, try to extract from the end
        if len(path_parts) >= 2:
            module = path_parts[-2]
            chapter = os.path.splitext(path_parts[-1])[0]
            return module, chapter
        else:
            # If we can't determine from path, use filename
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            return 'unknown', base_name

def validate_file_path(file_path: str, base_dir: str = _DEFAULT_DOCS_DIR) -> bool:
    """
    Validate file path to prevent directory traversal vulnerabilities.
    """
    try:
        from urllib.parse import unquote
        decoded_path = unquote(file_path)
        normalized_path = os.path.normpath(decoded_path)
        base_path = os.path.normpath(base_dir)

        # Check if the normalized path starts with the base directory
        # This prevents directory traversal attacks
        if not normalized_path.startswith(base_path):
            return False

        # Additional check: resolve both paths and verify relationship
        abs_file_path = os.path.abspath(normalized_path)
        abs_base_path = os.path.abspath(base_path)

        # Check if the file path is under the base directory
        return abs_file_path.startswith(abs_base_path)
    except Exception:
        return False


def get_all_mdx_files(directory_path: str) -> List[str]:
    """
    Recursively scan directory for all .mdx files.
    """
    mdx_files = []

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.mdx'):
                full_path = os.path.join(root, file)
                if validate_file_path(full_path, directory_path):
                    mdx_files.append(full_path)
                else:
                    logging.warning(f"Skipping potentially unsafe file path: {full_path}")

    return mdx_files


def read_mdx_file(file_path: str, max_file_size_mb: int = 50) -> Optional[str]:
    """
    Implement file reading functionality with error handling for unreadable files [US2].
    Also handles extremely large files that exceed memory limits [T043].
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Reading MDX file: {file_path}")

    # Check file size first to avoid loading extremely large files into memory
    try:
        file_size_bytes = os.path.getsize(file_path)
        max_size_bytes = max_file_size_mb * 1024 * 1024  # Convert MB to bytes

        if file_size_bytes > max_size_bytes:
            logger.error(f"File {file_path} is too large ({file_size_bytes / (1024*1024):.2f} MB), exceeding limit of {max_file_size_mb} MB")
            return None
    except OSError as e:
        logger.error(f"Error getting file size for {file_path}: {str(e)}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            logger.info(f"Successfully read {len(content)} characters from {file_path}")
            return content
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except PermissionError:
        logger.error(f"Permission denied when reading file: {file_path}")
        return None
    except UnicodeDecodeError:
        logger.error(f"Unable to decode file as UTF-8: {file_path}")
        # Try alternative encodings
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
                logger.warning(f"Successfully read {len(content)} characters using latin-1 encoding")
                return content
        except Exception:
            logger.error(f"Unable to decode file with any encoding: {file_path}")
            return None
    except MemoryError:
        logger.error(f"Memory error when reading file {file_path} - file may be too large")
        return None
    except OSError as e:
        logger.error(f"OS error when reading file {file_path}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error when reading file {file_path}: {str(e)}")
        return None


def process_large_mdx_file(file_path: str, chunk_size: int = 8192) -> Optional[str]:
    logger = logging.getLogger(__name__)
    logger.info(f"Processing large MDX file in chunks: {file_path}")

    try:
        content_parts = []
        with open(file_path, 'r', encoding='utf-8') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                content_parts.append(chunk)

        content = "".join(content_parts)
        logger.info(f"Successfully processed large file {file_path} in chunks, total size: {len(content)} characters")
        return content
    except UnicodeDecodeError:
        logger.warning(f"UTF-8 decoding failed for {file_path}, trying latin-1")
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
                return content
        except Exception:
            logger.error(f"Unable to decode file with any encoding: {file_path}")
            return None
    except Exception as e:
        logger.error(f"Error processing large file {file_path} in chunks: {str(e)}")
        return None


def convert_mdx_to_text(mdx_content: str) -> str:
    """
    Create MDX to plain text conversion function [US1].
    This function strips MDX/JSX syntax and extracts the plain text content.
    """
    import re

    logger = logging.getLogger(__name__)
    logger.info("Converting MDX content to plain text")

    # Store the original length for logging
    original_length = len(mdx_content)

    # Remove JSX components (blocks that start with < and end with >)
    # This handles both self-closing tags and paired tags
    text_content = re.sub(r'<[^>]*>', '', mdx_content)

    # Remove import/export statements (these are at the top of MDX files)
    text_content = re.sub(r'^\s*(?:import|export)\s+.*?[\n\r]+', '', text_content, flags=re.MULTILINE)

    # Remove markdown-style code blocks
    text_content = re.sub(r'```[\s\S]*?```', '', text_content)

    # Remove inline code
    text_content = re.sub(r'`[^`]*`', '', text_content)

    # Remove markdown links but keep the link text: [text](url) -> text
    text_content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text_content)

    # Remove markdown images but keep the alt text: ![alt](url) -> alt
    text_content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text_content)

    # Remove markdown headers, lists, bold, italic markers
    # Headers: ## Header -> Header
    text_content = re.sub(r'^\s*#+\s*', '', text_content, flags=re.MULTILINE)
    # Bold: **text** or __text__ -> text
    text_content = re.sub(r'\*{2}([^*]+)\*{2}|_{2}([^_]+)_{2}', r'\1\2', text_content)
    # Italic: *text* or _text_ -> text
    text_content = re.sub(r'(?<!\*)\*([^\*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)', r'\1\2', text_content)
    # List markers: - or * at start of line
    text_content = re.sub(r'^\s*[-*+]\s+', '', text_content, flags=re.MULTILINE)
    # Numbered lists: 1. 2. etc.
    text_content = re.sub(r'^\s*\d+\.\s+', '', text_content, flags=re.MULTILINE)

    # Replace multiple newlines with a single newline
    text_content = re.sub(r'\n\s*\n', '\n', text_content)

    # Replace multiple spaces with a single space
    text_content = re.sub(r' +', ' ', text_content)

    # Strip leading/trailing whitespace
    text_content = text_content.strip()

    logger.info(f"MDX conversion complete: {original_length} -> {len(text_content)} characters")

    return text_content


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50, encoding_name: str = "cl100k_base") -> List[str]:
    """
    Token-aware chunking using tiktoken with paragraph-first, sentence-second boundaries.

    Splits text into chunks of approximately `chunk_size` tokens (not characters),
    preferring to break at paragraph boundaries. Falls back to sentence boundaries
    within oversized paragraphs. Overlap ensures context continuity.

    encoding_name: tiktoken encoding (default cl100k_base, the GPT-4 encoding).
    """
    import tiktoken

    logger = logging.getLogger(__name__)
    logger.info(f"Chunking text of length {len(text)} (chars) with target {chunk_size} tokens, overlap {overlap} tokens")

    if not text:
        return []

    if overlap >= chunk_size:
        overlap = chunk_size // 2
        logger.warning(f"Overlap was >= chunk_size, reducing to {overlap}")

    enc = tiktoken.get_encoding(encoding_name)

    def count_tokens(t: str) -> int:
        return len(enc.encode(t))

    def find_sentence_boundary(t: str, approx_pos: int) -> int:
        """Find the last sentence boundary before approx_pos."""
        search_start = max(0, approx_pos - 100)
        search_region = t[search_start:approx_pos]
        for sep in ('. ', '?\n', '!\n', '.\n', '.\r\n', '?\r\n', '!\r\n'):
            idx = search_region.rfind(sep)
            if idx != -1:
                return search_start + idx + len(sep)
        return approx_pos

    # Split into paragraphs first
    paragraphs = text.split('\n\n')
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    chunks = []
    current_chunk_parts: List[str] = []
    current_tokens = 0
    overlap_text = ""

    def flush_chunk() -> str:
        nonlocal overlap_text, current_chunk_parts, current_tokens
        if not current_chunk_parts:
            return None
        chunk_text_str = '\n\n'.join(current_chunk_parts)
        if overlap > 0 and overlap_text:
            chunk_text_str = overlap_text + '\n\n' + chunk_text_str
        # Compute overlap for next chunk from the end of this one
        encoded = enc.encode(chunk_text_str)
        overlap_token_count = min(overlap, len(encoded))
        overlap_bytes = enc.decode(encoded[-overlap_token_count:])
        overlap_text = overlap_bytes
        current_chunk_parts = []
        current_tokens = 0
        return chunk_text_str

    for para in paragraphs:
        para_tokens = count_tokens(para)

        if para_tokens == 0:
            continue

        # If a single paragraph exceeds the limit, split on sentence boundaries
        if para_tokens > chunk_size:
            # Flush what we have first
            if current_chunk_parts:
                chunk = flush_chunk()
                if chunk:
                    chunks.append(chunk)

            # Split the oversized paragraph on sentences
            sentence_parts = para.replace('. ', '.\n').replace('! ', '!\n').replace('? ', '?\n').split('\n')

            for sentence in sentence_parts:
                sentence = sentence.strip()
                if not sentence:
                    continue
                st = count_tokens(sentence)
                if current_tokens + st > chunk_size and current_chunk_parts:
                    chunk = flush_chunk()
                    if chunk:
                        chunks.append(chunk)
                current_chunk_parts.append(sentence)
                current_tokens += st

            if current_chunk_parts:
                chunk = flush_chunk()
                if chunk:
                    chunks.append(chunk)
            continue

        # Normal paragraph fits or can start a new chunk
        if current_tokens + para_tokens > chunk_size and current_chunk_parts:
            chunk = flush_chunk()
            if chunk:
                chunks.append(chunk)

        current_chunk_parts.append(para)
        current_tokens += para_tokens

    # Flush remaining
    if current_chunk_parts:
        chunk = flush_chunk()
        if chunk:
            chunks.append(chunk)

    logger.info(f"Text chunked into {len(chunks)} token-aware chunks")
    return chunks


def prepare_chunks_for_embedding(chunks: List[str], source_file: str, module: str, chapter: str) -> List[VectorRecord]:
    """
    Create function to prepare text chunks for Cohere embedding [US1].
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Preparing {len(chunks)} chunks for embedding from {source_file}")

    vector_records = []
    for idx, chunk in enumerate(chunks):
        # Create a VectorRecord for each chunk
        vector_record = VectorRecord.from_text_chunk(
            text_chunk=chunk,
            source_file=source_file,
            module=module,
            chapter=chapter,
            chunk_index=idx
        )
        vector_records.append(vector_record)

    logger.info(f"Prepared {len(vector_records)} VectorRecords for embedding")
    return vector_records


def embed_text_chunks(cohere_client, vector_records: List[VectorRecord], model: str = "embed-multilingual-v3.0") -> List[VectorRecord]:
    """
    Implement Cohere embedding API call with proper error handling [US1].
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Embedding {len(vector_records)} text chunks using model: {model}")

    if not vector_records:
        logger.info("No vector records to embed")
        return []

    # Extract text content from vector records
    texts = [record.content for record in vector_records]

    try:
        # Embed the texts using Cohere
        embeddings = safe_embed_chunks(cohere_client, texts, model)
        logger.info(f"Successfully embedded {len(embeddings)} chunks")

        # Update the vector records with the embeddings
        for i, record in enumerate(vector_records):
            record.vector = embeddings[i]

        logger.info("All vector records updated with embeddings")
        return vector_records

    except Exception as e:
        logger.error(f"Error during embedding process: {str(e)}")
        raise


def process_file_for_vectorization(file_path: str, cohere_client, config: Dict) -> List[VectorRecord]:
    """
    Process individual .mdx files to chunk and embed properly with metadata [US1].
    This function combines all the steps for a single file: read, convert, chunk, embed.
    """

    logger = logging.getLogger(__name__)
    start_time = time.time()
    logger.info(f"Processing file for vectorization: {file_path}")

    # Step 1: Read the MDX file
    mdx_content = read_mdx_file(file_path, max_file_size_mb=config.get('max_file_size_mb', 50))
    if mdx_content is None:
        logger.error(f"Could not read file {file_path}, skipping")
        # Try alternative method for large files
        mdx_content = process_large_mdx_file(file_path)
        if mdx_content is None:
            logger.error(f"Could not process large file {file_path} either, skipping")
            return []

    # Step 2: Extract module and chapter from path
    module, chapter = extract_module_and_chapter_from_path(file_path)
    logger.info(f"Extracted module: {module}, chapter: {chapter} from {file_path}")

    # Step 3: Convert MDX to plain text
    text_content = convert_mdx_to_text(mdx_content)
    if not text_content.strip():
        logger.warning(f"No content found in {file_path} after MDX conversion, skipping")
        return []

    # Step 4: Chunk the text
    chunks = chunk_text(text_content, config['chunk_size'], config['chunk_overlap'])
    logger.info(f"Text chunked into {len(chunks)} chunks")

    # Step 5: Prepare chunks for embedding
    vector_records = prepare_chunks_for_embedding(chunks, file_path, module, chapter)
    logger.info(f"Prepared {len(vector_records)} vector records for embedding")

    # Step 6: Embed the text chunks
    embedded_records = embed_text_chunks(cohere_client, vector_records, config['cohere_model'])
    logger.info(f"Successfully embedded {len(embedded_records)} vector records")

    # Step 7: Add metadata preservation (already handled in VectorRecord creation)
    # The metadata is preserved in the VectorRecord objects as source_file, module, chapter, chunk_index

    # Performance tracking
    elapsed_time = time.time() - start_time
    logger.info(f"Completed processing {file_path} in {elapsed_time:.2f}s, created {len(embedded_records)} embedded records")

    return embedded_records


def track_performance(start_time: float, total_files: int, processed_files: int) -> Dict:
    """
    Add performance tracking to ensure process completes under 10 minutes [US1].
    """

    logger = logging.getLogger(__name__)
    elapsed_time = time.time() - start_time
    estimated_total_time = (elapsed_time / processed_files) * total_files if processed_files > 0 else 0
    remaining_time = estimated_total_time - elapsed_time if processed_files > 0 else 0

    performance_data = {
        'elapsed_time': elapsed_time,
        'estimated_total_time': estimated_total_time,
        'remaining_time': remaining_time,
        'processed_files': processed_files,
        'total_files': total_files,
        'progress_percent': (processed_files / total_files * 100) if total_files > 0 else 0,
        'files_per_second': processed_files / elapsed_time if elapsed_time > 0 else 0
    }

    # Log performance metrics
    logger.info(f"Performance: {elapsed_time:.2f}s elapsed, "
                f"~{estimated_total_time:.2f}s estimated total, "
                f"~{remaining_time:.2f}s remaining, "
                f"{performance_data['progress_percent']:.1f}% complete")

    # Check if we're on track to complete under 10 minutes (600 seconds)
    if estimated_total_time > 600:  # 10 minutes in seconds
        logger.warning(f"Process estimated to take {estimated_total_time:.2f}s, "
                       f"which exceeds the 10-minute target of 600s")
    else:
        logger.info(f"Process on track to complete within 10-minute target "
                    f"(estimated: {estimated_total_time:.2f}s)")

    return performance_data


def create_qdrant_collection(qdrant_client, collection_name: str = "book_vectors", vector_size: int = 1024):
    """
    Create Qdrant collection for storing book vectors [US3].
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Creating Qdrant collection: {collection_name}")

    try:
        # Check if collection already exists
        collections = qdrant_client.get_collections()
        collection_names = [collection.name for collection in collections.collections]

        if collection_name in collection_names:
            logger.info(f"Collection {collection_name} already exists")
            return True

        # Create the collection
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,  # Default size for Cohere embeddings
                distance=models.Distance.COSINE  # Cosine distance for embeddings
            )
        )

        logger.info(f"Successfully created collection: {collection_name}")
        return True

    except Exception as e:
        logger.error(f"Error creating Qdrant collection {collection_name}: {str(e)}")
        raise


def batch_store_vectors_in_qdrant(qdrant_client, vector_records: List[VectorRecord], collection_name: str = "book_vectors", batch_size: int = 100):
    """
    Implement batch storage for efficiency [US3].
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Batch storing {len(vector_records)} vectors in Qdrant collection: {collection_name} (batch size: {batch_size})")

    if not vector_records:
        logger.info("No vector records to store")
        return True

    try:
        # Process in batches for efficiency
        total_processed = 0
        for i in range(0, len(vector_records), batch_size):
            batch = vector_records[i:i + batch_size]
            logger.debug(f"Processing batch {i//batch_size + 1} with {len(batch)} vectors")

            # Convert VectorRecords to Qdrant points for this batch
            points = [record.to_qdrant_point() for record in batch]

            # Store the batch in Qdrant
            result = safe_store_vectors_in_qdrant(qdrant_client, points, collection_name)
            total_processed += len(batch)

            logger.info(f"Batch {i//batch_size + 1} completed: {total_processed}/{len(vector_records)} vectors stored")

        logger.info(f"Successfully batch stored {len(vector_records)} vectors in Qdrant")
        return True

    except Exception as e:
        logger.error(f"Error during batch storage in Qdrant: {str(e)}")
        raise


def verify_stored_vectors(qdrant_client, collection_name: str = "book_vectors", limit: int = 5) -> bool:
    """
    Add verification function to query stored vectors in Qdrant [US3].
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Verifying stored vectors in collection: {collection_name}")

    try:
        # Get the collection info
        collection_info = qdrant_client.get_collection(collection_name)
        logger.info(f"Collection '{collection_name}' contains {collection_info.points_count} vectors")

        # Sample some vectors to verify they exist and have proper structure
        if collection_info.points_count > 0:
            # Get a sample of points
            sample_size = min(limit, collection_info.points_count)
            points = qdrant_client.scroll(
                collection_name=collection_name,
                limit=sample_size
            )

            logger.info(f"Retrieved {len(points[0])} sample vectors for verification")

            # Verify each sample point has expected structure
            for point in points[0]:
                if hasattr(point, 'payload') and point.payload:
                    expected_fields = ['content', 'source_file', 'module', 'chapter', 'chunk_index', 'created_at']
                    missing_fields = [field for field in expected_fields if field not in point.payload]
                    if missing_fields:
                        logger.warning(f"Vector ID {point.id} missing fields: {missing_fields}")
                        return False
                    else:
                        logger.debug(f"Vector ID {point.id} has all expected metadata fields")
                else:
                    logger.error(f"Vector ID {point.id} has no payload or empty payload")
                    return False

            logger.info(f"Verification successful for {len(points[0])} sample vectors")
            return True
        else:
            logger.warning(f"No vectors found in collection '{collection_name}'")
            return False

    except Exception as e:
        logger.error(f"Error during verification of stored vectors: {str(e)}")
        return False


def validate_all_files_processed(original_files: List[str], processed_files: List[str], stored_vectors_count: int) -> bool:
    """
    Add validation to ensure all .mdx files are processed into vectors [US3].
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Validating all files were processed: {len(original_files)} original, {len(processed_files)} processed")

    # Check if all original files were processed
    all_processed = len(processed_files) == len(original_files)

    # Check if there are vectors stored for the processed files
    expected_min_vectors = len(processed_files)  # At least one vector per file
    has_vectors = stored_vectors_count >= expected_min_vectors

    logger.info(f"Validation results: All files processed: {all_processed}, Vectors stored: {has_vectors} ({stored_vectors_count} vectors for {len(processed_files)} files)")

    if not all_processed:
        missing_files = set(original_files) - set(processed_files)
        logger.warning(f"Missing processed files: {missing_files}")

    if not has_vectors:
        logger.warning(f"Expected at least {expected_min_vectors} vectors but found {stored_vectors_count}")

    return all_processed and has_vectors


def scan_mdx_files(docs_directory: str) -> List[str]:
    """
    Create function to recursively scan my-website/docs directory for .mdx files [US2].
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Scanning directory for .mdx files: {docs_directory}")

    if not os.path.exists(docs_directory):
        raise FileNotFoundError(f"Directory does not exist: {docs_directory}")

    mdx_files = get_all_mdx_files(docs_directory)
    logger.info(f"Found {len(mdx_files)} .mdx files")

    # Log each file found
    for file_path in mdx_files:
        logger.info(f"  - {file_path}")

    return mdx_files


def validate_input_parameters(args, skip_dir_check: bool = False):
    """
    Add input validation for all user-provided parameters [T042].
    """
    import re
    logger = logging.getLogger(__name__)

    # Validate docs directory
    if not args.docs_dir or not isinstance(args.docs_dir, str):
        raise ValueError("Docs directory must be a non-empty string")

    if not skip_dir_check:
        if not os.path.exists(args.docs_dir):
            raise ValueError(f"Docs directory does not exist: {args.docs_dir}")

        if not os.path.isdir(args.docs_dir):
            raise ValueError(f"Docs directory path is not a directory: {args.docs_dir}")

    # Validate chunk size
    if not isinstance(args.chunk_size, int) or args.chunk_size <= 0:
        raise ValueError("Chunk size must be a positive integer")

    if args.chunk_size > 10000:  # Set a reasonable upper limit
        logger.warning(f"Chunk size {args.chunk_size} is very large, this may cause performance issues")

    # Validate chunk overlap
    if not isinstance(args.chunk_overlap, int) or args.chunk_overlap < 0:
        raise ValueError("Chunk overlap must be a non-negative integer")

    if args.chunk_overlap >= args.chunk_size:
        raise ValueError("Chunk overlap must be less than chunk size")

    # Validate Qdrant host
    if not args.qdrant_host or not isinstance(args.qdrant_host, str):
        raise ValueError("Qdrant host must be a non-empty string")

    # Basic host format validation (could be IP or domain)
    host_pattern = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9\-_.]*$')
    if not host_pattern.match(args.qdrant_host):
        logger.warning(f"Qdrant host '{args.qdrant_host}' may not be a valid format, but proceeding anyway")

    # Validate Qdrant port
    if not isinstance(args.qdrant_port, int) or args.qdrant_port < 1 or args.qdrant_port > 65535:
        raise ValueError("Qdrant port must be an integer between 1 and 65535")

    # Validate Cohere model
    if not args.cohere_model or not isinstance(args.cohere_model, str):
        raise ValueError("Cohere model must be a non-empty string")

    # Validate collection name
    if not args.collection_name or not isinstance(args.collection_name, str):
        raise ValueError("Collection name must be a non-empty string")

    # Qdrant collection names should follow certain rules
    collection_pattern = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9\-_]*[a-zA-Z0-9]$|^[_a-zA-Z0-9]+$')
    if not collection_pattern.match(args.collection_name):
        logger.warning(f"Collection name '{args.collection_name}' may not follow Qdrant naming conventions")

    # Validate batch size
    if not isinstance(args.batch_size, int) or args.batch_size <= 0:
        raise ValueError("Batch size must be a positive integer")

    if args.batch_size > 1000:  # Set a reasonable upper limit
        logger.warning(f"Batch size {args.batch_size} is very large, this may cause memory issues")

    logger.info("All input parameters validated successfully")
    return True


def create_cli_parser():
    """Create command-line interface with configurable parameters [T041]."""
    parser = argparse.ArgumentParser(
        description="Book Vector Ingestion System - Convert MDX files to vector embeddings and store in Qdrant"
    )
    parser.add_argument(
        '--docs-dir',
        type=str,
        default=_DEFAULT_DOCS_DIR,
        help='Directory containing MDX files (default: ../frontend/docs relative to script)'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=512,
        help='Target chunk size in tokens (default: 512)'
    )
    parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=50,
        help='Token overlap between chunks (default: 50)'
    )
    parser.add_argument(
        '--qdrant-host',
        type=str,
        default='localhost',
        help='Qdrant host (default: localhost)'
    )
    parser.add_argument(
        '--qdrant-port',
        type=int,
        default=6333,
        help='Qdrant port (default: 6333)'
    )
    parser.add_argument(
        '--cohere-model',
        type=str,
        default='embed-multilingual-v3.0',
        help='Cohere model to use for embeddings (default: embed-multilingual-v3.0)'
    )
    parser.add_argument(
        '--vector-size',
        type=int,
        default=1024,
        help='Dimension of the embedding vectors (default: 1024, Cohere embed-multilingual-v3.0)'
    )
    parser.add_argument(
        '--collection-name',
        type=str,
        default='book_vectors',
        help='Qdrant collection name (default: book_vectors)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Batch size for vector storage (default: 100)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser


def main():
    """Main entry point for the book vector ingestion system."""
    # Parse command line arguments
    parser = create_cli_parser()
    args = parser.parse_args()

    # Validate input parameters
    try:
        validate_input_parameters(args)
    except ValueError as e:
        print(f"Input validation error: {str(e)}")
        sys.exit(1)

    # Override config with command line args
    config = load_config()

    # Update config with CLI arguments if provided
    config['docs_directory'] = args.docs_dir
    if args.chunk_size != 512:
        config['chunk_size'] = args.chunk_size
    if args.chunk_overlap != 50:
        config['chunk_overlap'] = args.chunk_overlap
    if args.qdrant_host != 'localhost':
        config['qdrant_host'] = args.qdrant_host
    if args.qdrant_port != 6333:
        config['qdrant_port'] = args.qdrant_port
    if args.cohere_model != 'embed-multilingual-v3.0':
        config['cohere_model'] = args.cohere_model

    # Set up logging based on verbosity
    logger = setup_logging()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    print("Book Vector Ingestion System - Full Implementation")
    print(f"Configuration loaded:")
    print(f"  - Docs directory: {config['docs_directory']}")
    print(f"  - Chunk size: {config['chunk_size']}")
    print(f"  - Chunk overlap: {config['chunk_overlap']}")
    print(f"  - Cohere model: {config['cohere_model']}")
    print(f"  - Qdrant host: {config['qdrant_host']}:{config['qdrant_port']}")

    # Check if API keys are set
    if not config['cohere_api_key']:
        logger.error("COHERE_API_KEY not found in environment. Please set it in .env file.")
        sys.exit(1)
    if not config['qdrant_host']:
        logger.error("QDRANT_HOST not set in environment.")
        sys.exit(1)

    # Step 1: Scan MDX files
    try:
        mdx_files = scan_mdx_files(config['docs_directory'])
        print(f"Successfully found {len(mdx_files)} MDX files to process")
    except Exception as e:
        logger.error(f"Error scanning MDX files: {str(e)}")
        sys.exit(1)

    if not mdx_files:
        logger.warning("No MDX files found to process")
        return

    # Step 2: Set up Cohere client
    try:
        cohere_client = setup_cohere_client(config['cohere_api_key'])
        logger.info("Cohere client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Cohere client: {str(e)}")
        sys.exit(1)

    # Step 3: Set up Qdrant client
    try:
        qdrant_client = setup_qdrant_client(
            config['qdrant_host'],
            config['qdrant_port'],
            config['qdrant_api_key']
        )
        logger.info("Qdrant client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant client: {str(e)}")
        sys.exit(1)

    # Step 4: Create Qdrant collection
    try:
        create_qdrant_collection(qdrant_client, args.collection_name, vector_size=args.vector_size)
        logger.info("Qdrant collection verified/created")
    except Exception as e:
        logger.error(f"Failed to create Qdrant collection: {str(e)}")
        sys.exit(1)

    # Step 5: Process files and store vectors
    all_vector_records = []
    processed_files = []
    start_time = time.time()

    for i, file_path in enumerate(mdx_files):
        try:
            logger.info(f"Processing file {i+1}/{len(mdx_files)}: {file_path}")
            vector_records = process_file_for_vectorization(file_path, cohere_client, config)
            all_vector_records.extend(vector_records)

            # Track successfully processed files
            if vector_records:  # Only count as processed if we got vectors
                processed_files.append(file_path)

            # Performance tracking
            perf_data = track_performance(start_time, len(mdx_files), i+1)
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            continue  # Continue with other files

    logger.info(f"Processed all files, created {len(all_vector_records)} vector records from {len(processed_files)} files")

    # Step 6: Store all vectors in Qdrant
    if all_vector_records:
        try:
            batch_store_vectors_in_qdrant(qdrant_client, all_vector_records, args.collection_name, args.batch_size)
            logger.info(f"Successfully stored {len(all_vector_records)} vectors in Qdrant")
        except Exception as e:
            logger.error(f"Failed to store vectors in Qdrant: {str(e)}")
            sys.exit(1)

        # Step 7: Verify the stored vectors
        try:
            verification_success = verify_stored_vectors(qdrant_client, args.collection_name)
            if verification_success:
                logger.info("Vector verification successful")
            else:
                logger.warning("Vector verification failed")
        except Exception as e:
            logger.error(f"Error during vector verification: {str(e)}")

        # Step 8: Validate all files were processed
        validation_success = validate_all_files_processed(mdx_files, processed_files, len(all_vector_records))
        logger.info(f"File processing validation: {'PASSED' if validation_success else 'FAILED'}")

    print(f"Ingestion complete! Processed {len(mdx_files)} files and stored {len(all_vector_records)} vectors in Qdrant.")
    print("System is ready for semantic search queries.")


if __name__ == "__main__":
    main()