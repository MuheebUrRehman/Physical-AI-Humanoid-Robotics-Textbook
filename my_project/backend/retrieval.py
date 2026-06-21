import asyncio
import logging
import time
from typing import List, Dict, Optional, Tuple

from config import Config

logger = logging.getLogger(__name__)

_cohere_client: object | None = None
_qdrant_client: object | None = None

def _get_cohere_client():
    global _cohere_client
    if _cohere_client is None:
        import cohere
        _cohere_client = cohere.AsyncClientV2(api_key=Config.COHERE_API_KEY)
    return _cohere_client

def _get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is None:
        from qdrant_client import AsyncQdrantClient
        _qdrant_client = AsyncQdrantClient(
            url=Config.QDRANT_HOST,
            api_key=Config.QDRANT_API_KEY,
            port=Config.QDRANT_PORT,
            timeout=Config.QUERY_TIMEOUT
        )
    return _qdrant_client

# In-memory embedding cache: {query: (embedding, timestamp)}
_embed_cache: Dict[str, Tuple[List[float], float]] = {}
_EMBED_CACHE_TTL: int = 300  # 5 minutes


async def embed_query(query: str, max_retries: int = 3) -> List[float]:
    """Generate embedding for a query using Cohere with in-memory caching.

    Checks the TTL cache before calling the API. Cache entries expire
    after _EMBED_CACHE_TTL seconds to handle model/configuration changes.
    """
    now = time.time()
    cached = _embed_cache.get(query)
    if cached is not None and (now - cached[1]) < _EMBED_CACHE_TTL:
        logger.debug(f"Cache hit for query: {query[:50]}...")
        return cached[0]

    for attempt in range(max_retries):
        try:
            co = _get_cohere_client()
            response = await co.embed(
                texts=[query],
                model=Config.COHERE_MODEL,
                input_type="search_query"
            )
            embedding = response.embeddings.float_[0]
            _embed_cache[query] = (embedding, time.time())
            return embedding
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed in embed_query: {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)


async def get_relevant_chunks(query: str, max_retries: int = 3) -> List[Dict[str, str]]:
    """Retrieve relevant book chunks from Qdrant based on user query.

    Returns chunks with text, source, module, chapter, and score.
    Chunks below RELEVANCE_THRESHOLD are filtered out.
    Delegates embedding to embed_query() to avoid code duplication
    and leverage its caching layer.
    """
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            query_embedding = await embed_query(query)
            embedding_time = time.time() - start_time

            if embedding_time > Config.QUERY_TIMEOUT:
                logger.warning(f"Embedding took {embedding_time:.2f}s, exceeding timeout")
                continue

            start_time = time.time()
            qdrant = _get_qdrant_client()
            search_results = await qdrant.query_points(
                collection_name=Config.QDRANT_COLLECTION_NAME,
                query=query_embedding,
                limit=Config.TOP_K,
                with_payload=True
            )
            search_time = time.time() - start_time

            if search_time > Config.QUERY_TIMEOUT:
                logger.warning(f"Qdrant search took {search_time:.2f}s, exceeding timeout")
                continue

            relevant_chunks = []
            for result in search_results.points:
                score = result.score if hasattr(result, 'score') else 0.0
                if score < Config.RELEVANCE_THRESHOLD:
                    logger.debug(f"Skipping chunk with low relevance score: {score:.3f}")
                    continue

                if result.payload and "content" in result.payload:
                    relevant_chunks.append({
                        "text": result.payload["content"],
                        "source": result.payload.get("source_file", ""),
                        "module": result.payload.get("module", ""),
                        "chapter": result.payload.get("chapter", ""),
                        "score": score
                    })

            return relevant_chunks

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed in get_relevant_chunks: {e}")
            if attempt == max_retries - 1:
                return []
            await asyncio.sleep(2 ** attempt)

    return []
