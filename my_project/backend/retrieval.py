import asyncio
import logging
import time
from typing import List, Dict

import cohere
from qdrant_client import AsyncQdrantClient

from config import Config

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Cohere async client v2
co = cohere.AsyncClientV2(api_key=Config.COHERE_API_KEY)

# Initialize Qdrant async client
qdrant_client = AsyncQdrantClient(
    url=Config.QDRANT_HOST,
    api_key=Config.QDRANT_API_KEY,
    port=Config.QDRANT_PORT,
    timeout=Config.QUERY_TIMEOUT
)


async def get_relevant_chunks(query: str, max_retries: int = 3) -> List[Dict[str, str]]:
    """
    Retrieve relevant book chunks from Qdrant based on the user query.

    Args:
        query: The user's query string
        max_retries: Maximum number of retry attempts

    Returns:
        List of relevant text chunks from the book content
    """
    for attempt in range(max_retries):
        try:
            # Generate embedding for the query using Cohere v2 API with timeout
            start_time = time.time()
            response = await co.embed(
                texts=[query],
                model="embed-multilingual-v3.0",
                input_type="search_query"
            )
            embedding_time = time.time() - start_time

            if embedding_time > Config.QUERY_TIMEOUT:
                logger.warning(f"Embedding generation took {embedding_time:.2f}s, exceeding timeout of {Config.QUERY_TIMEOUT}s")
                continue  # Retry if timeout exceeded


            # v2 response has embeddings under the float_ key
            query_embedding = response.embeddings.float_[0]

            # Perform similarity search in Qdrant with timeout
            start_time = time.time()
            search_results = await qdrant_client.query_points(
                collection_name=Config.QDRANT_COLLECTION_NAME,
                query=query_embedding,
                limit=Config.TOP_K,
                with_payload=True
            )
            search_time = time.time() - start_time

            if search_time > Config.QUERY_TIMEOUT:
                logger.warning(f"Qdrant search took {search_time:.2f}s, exceeding timeout of {Config.QUERY_TIMEOUT}s")
                continue  # Retry if timeout exceeded

            # Extract text chunks with source metadata from search results
            relevant_chunks = []
            for result in search_results.points:
                if result.payload and "text" in result.payload:
                    relevant_chunks.append({
                        "text": result.payload["text"],
                        "source": result.payload.get("source_file", ""),
                        "module": result.payload.get("module", ""),
                        "chapter": result.payload.get("chapter", "")
                    })
                elif result.payload:
                    relevant_chunks.append({
                        "text": str(result.payload),
                        "source": ""
                    })

            return relevant_chunks

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed in get_relevant_chunks: {e}")
            if attempt == max_retries - 1:
                # If this was the last attempt, return empty list
                logger.error("All retry attempts failed in get_relevant_chunks")
                return []

            # Wait before retrying (exponential backoff)
            await asyncio.sleep(2 ** attempt)

    # This should not be reached, but included for safety
    return []


async def embed_query(query: str, max_retries: int = 3) -> List[float]:
    """
    Generate embedding for a query using Cohere.

    Args:
        query: The query string to embed
        max_retries: Maximum number of retry attempts

    Returns:
        List of floats representing the embedding vector
    """
    for attempt in range(max_retries):
        try:
            response = await co.embed(
                texts=[query],
                model="embed-multilingual-v3.0",
                input_type="search_query"
            )
            return response.embeddings.float_[0]
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed in embed_query: {e}")
            if attempt == max_retries - 1:

                # If this was the last attempt, re-raise the exception
                raise

            # Wait before retrying (exponential backoff)
            await asyncio.sleep(2 ** attempt)