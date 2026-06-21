import logging
import re
from typing import List, Dict, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models

from retry import handle_api_call_with_retry


def setup_qdrant_client(host: str, port: int, api_key: Optional[str] = None):
    try:
        host_clean = re.sub(r'^https?://', '', host)
        if api_key:
            client = QdrantClient(host=host_clean, port=port, api_key=api_key)
        else:
            client = QdrantClient(host=host_clean, port=port)
        client.get_collections()
        return client
    except Exception as e:
        logging.error(f"Failed to initialize Qdrant client: {str(e)}")
        raise


def safe_store_vectors_in_qdrant(qdrant_client, points: List[Dict], collection_name: str = "book_vectors"):
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


def create_qdrant_collection(qdrant_client, collection_name: str = "book_vectors", vector_size: int = 1024):
    logger = logging.getLogger(__name__)
    logger.info(f"Creating Qdrant collection: {collection_name}")
    try:
        collections = qdrant_client.get_collections()
        collection_names = [collection.name for collection in collections.collections]
        if collection_name in collection_names:
            logger.info(f"Collection {collection_name} already exists")
            return True
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            )
        )
        logger.info(f"Successfully created collection: {collection_name}")
        return True
    except Exception as e:
        logger.error(f"Error creating Qdrant collection {collection_name}: {str(e)}")
        raise


def batch_store_vectors_in_qdrant(qdrant_client, vector_records, collection_name: str = "book_vectors", batch_size: int = 100):
    logger = logging.getLogger(__name__)
    logger.info(f"Batch storing {len(vector_records)} vectors in Qdrant collection: {collection_name} (batch size: {batch_size})")
    if not vector_records:
        logger.info("No vector records to store")
        return True
    try:
        total_processed = 0
        for i in range(0, len(vector_records), batch_size):
            batch = vector_records[i:i + batch_size]
            points = [record.to_qdrant_point() for record in batch]
            result = safe_store_vectors_in_qdrant(qdrant_client, points, collection_name)
            total_processed += len(batch)
            logger.info(f"Batch {i//batch_size + 1} completed: {total_processed}/{len(vector_records)} vectors stored")
        logger.info(f"Successfully batch stored {len(vector_records)} vectors in Qdrant")
        return True
    except Exception as e:
        logger.error(f"Error during batch storage in Qdrant: {str(e)}")
        raise


def verify_stored_vectors(qdrant_client, collection_name: str = "book_vectors", limit: int = 5) -> bool:
    logger = logging.getLogger(__name__)
    logger.info(f"Verifying stored vectors in collection: {collection_name}")
    try:
        collection_info = qdrant_client.get_collection(collection_name)
        logger.info(f"Collection '{collection_name}' contains {collection_info.points_count} vectors")
        if collection_info.points_count > 0:
            sample_size = min(limit, collection_info.points_count)
            points = qdrant_client.scroll(collection_name=collection_name, limit=sample_size)
            logger.info(f"Retrieved {len(points[0])} sample vectors for verification")
            for point in points[0]:
                if hasattr(point, 'payload') and point.payload:
                    expected_fields = ['content', 'source_file', 'module', 'chapter', 'chunk_index', 'created_at']
                    missing_fields = [field for field in expected_fields if field not in point.payload]
                    if missing_fields:
                        logger.warning(f"Vector ID {point.id} missing fields: {missing_fields}")
                        return False
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
    logger = logging.getLogger(__name__)
    logger.info(f"Validating all files were processed: {len(original_files)} original, {len(processed_files)} processed")
    all_processed = len(processed_files) == len(original_files)
    expected_min_vectors = len(processed_files)
    has_vectors = stored_vectors_count >= expected_min_vectors
    logger.info(f"Validation results: All files processed: {all_processed}, Vectors stored: {has_vectors} ({stored_vectors_count} vectors for {len(processed_files)} files)")
    if not all_processed:
        missing_files = set(original_files) - set(processed_files)
        logger.warning(f"Missing processed files: {missing_files}")
    if not has_vectors:
        logger.warning(f"Expected at least {expected_min_vectors} vectors but found {stored_vectors_count}")
    return all_processed and has_vectors
