import logging
from typing import List, Optional

import cohere

from config import load_config
from retry import handle_api_call_with_retry


def setup_cohere_client(api_key: str):
    if not api_key:
        raise ValueError("Cohere API key is required")
    try:
        client = cohere.Client(api_key)
        return client
    except Exception as e:
        logging.error(f"Failed to initialize Cohere client: {str(e)}")
        raise


def safe_embed_chunks(cohere_client, texts: List[str], model: str = "embed-multilingual-v3.0"):
    try:
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


def embed_text_chunks(cohere_client, vector_records, model: str = "embed-multilingual-v3.0"):
    logger = logging.getLogger(__name__)
    logger.info(f"Embedding {len(vector_records)} text chunks using model: {model}")
    if not vector_records:
        logger.info("No vector records to embed")
        return []
    texts = [record.content for record in vector_records]
    try:
        embeddings = safe_embed_chunks(cohere_client, texts, model)
        logger.info(f"Successfully embedded {len(embeddings)} chunks")
        for i, record in enumerate(vector_records):
            record.vector = embeddings[i]
        logger.info("All vector records updated with embeddings")
        return vector_records
    except Exception as e:
        logging.error(f"Error during embedding process: {str(e)}")
        raise
