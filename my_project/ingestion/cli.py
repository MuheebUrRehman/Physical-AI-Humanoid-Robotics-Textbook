import argparse
import logging
import os
import re
import sys
import time

from config import load_config, setup_logging
from pipeline import process_file_for_vectorization, scan_mdx_files, track_performance
from embedding import setup_cohere_client
from qdrant_store import setup_qdrant_client, create_qdrant_collection, batch_store_vectors_in_qdrant, verify_stored_vectors, validate_all_files_processed
from models import VectorRecord

_DEFAULT_DOCS_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'docs'))


def validate_input_parameters(args, skip_dir_check: bool = False):
    logger = logging.getLogger(__name__)

    if not args.docs_dir or not isinstance(args.docs_dir, str):
        raise ValueError("Docs directory must be a non-empty string")
    if not skip_dir_check:
        if not os.path.exists(args.docs_dir):
            raise ValueError(f"Docs directory does not exist: {args.docs_dir}")
        if not os.path.isdir(args.docs_dir):
            raise ValueError(f"Docs directory path is not a directory: {args.docs_dir}")

    if not isinstance(args.chunk_size, int) or args.chunk_size <= 0:
        raise ValueError("Chunk size must be a positive integer")
    if args.chunk_size > 10000:
        logger.warning(f"Chunk size {args.chunk_size} is very large, this may cause performance issues")

    if not isinstance(args.chunk_overlap, int) or args.chunk_overlap < 0:
        raise ValueError("Chunk overlap must be a non-negative integer")
    if args.chunk_overlap >= args.chunk_size:
        raise ValueError("Chunk overlap must be less than chunk size")

    if not args.qdrant_host or not isinstance(args.qdrant_host, str):
        raise ValueError("Qdrant host must be a non-empty string")
    host_pattern = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9\-_.]*$')
    if not host_pattern.match(args.qdrant_host):
        logger.warning(f"Qdrant host '{args.qdrant_host}' may not be a valid format, but proceeding anyway")

    if not isinstance(args.qdrant_port, int) or args.qdrant_port < 1 or args.qdrant_port > 65535:
        raise ValueError("Qdrant port must be an integer between 1 and 65535")

    if not args.cohere_model or not isinstance(args.cohere_model, str):
        raise ValueError("Cohere model must be a non-empty string")

    if not args.collection_name or not isinstance(args.collection_name, str):
        raise ValueError("Collection name must be a non-empty string")
    collection_pattern = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9\-_]*[a-zA-Z0-9]$|^[_a-zA-Z0-9]+$')
    if not collection_pattern.match(args.collection_name):
        logger.warning(f"Collection name '{args.collection_name}' may not follow Qdrant naming conventions")

    if not isinstance(args.batch_size, int) or args.batch_size <= 0:
        raise ValueError("Batch size must be a positive integer")
    if args.batch_size > 1000:
        logger.warning(f"Batch size {args.batch_size} is very large, this may cause memory issues")

    logger.info("All input parameters validated successfully")
    return True


def create_cli_parser():
    parser = argparse.ArgumentParser(
        description="Book Vector Ingestion System - Convert MDX files to vector embeddings and store in Qdrant"
    )
    parser.add_argument('--docs-dir', type=str, default=_DEFAULT_DOCS_DIR,
                        help='Directory containing MDX files (default: ../frontend/docs relative to script)')
    parser.add_argument('--chunk-size', type=int, default=512,
                        help='Target chunk size in tokens (default: 512)')
    parser.add_argument('--chunk-overlap', type=int, default=50,
                        help='Token overlap between chunks (default: 50)')
    parser.add_argument('--qdrant-host', type=str, default='localhost',
                        help='Qdrant host (default: localhost)')
    parser.add_argument('--qdrant-port', type=int, default=6333,
                        help='Qdrant port (default: 6333)')
    parser.add_argument('--cohere-model', type=str, default='embed-multilingual-v3.0',
                        help='Cohere model to use for embeddings (default: embed-multilingual-v3.0)')
    parser.add_argument('--vector-size', type=int, default=1024,
                        help='Dimension of the embedding vectors (default: 1024)')
    parser.add_argument('--collection-name', type=str, default='book_vectors',
                        help='Qdrant collection name (default: book_vectors)')
    parser.add_argument('--batch-size', type=int, default=100,
                        help='Batch size for vector storage (default: 100)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--force-recreate', action='store_true',
                        help='Drop and recreate the Qdrant collection if it already exists')
    return parser


def main():
    parser = create_cli_parser()
    args = parser.parse_args()

    try:
        validate_input_parameters(args)
    except ValueError as e:
        print(f"Input validation error: {str(e)}")
        sys.exit(1)

    config = load_config()
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

    if not config['cohere_api_key']:
        logger.error("COHERE_API_KEY not found in environment. Please set it in .env file.")
        sys.exit(1)
    if not config['qdrant_host']:
        logger.error("QDRANT_HOST not set in environment.")
        sys.exit(1)

    try:
        mdx_files = scan_mdx_files(config['docs_directory'])
        print(f"Successfully found {len(mdx_files)} MDX files to process")
    except Exception as e:
        logger.error(f"Error scanning MDX files: {str(e)}")
        sys.exit(1)

    if not mdx_files:
        logger.warning("No MDX files found to process")
        return

    try:
        cohere_client = setup_cohere_client(config['cohere_api_key'])
        logger.info("Cohere client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Cohere client: {str(e)}")
        sys.exit(1)

    try:
        qdrant_client = setup_qdrant_client(config['qdrant_host'], config['qdrant_port'], config['qdrant_api_key'])
        logger.info("Qdrant client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant client: {str(e)}")
        sys.exit(1)

    try:
        if args.force_recreate:
            logger.warning("Force-recreate requested, dropping existing collection if any")
            try:
                qdrant_client.delete_collection(collection_name=args.collection_name)
            except Exception:
                pass
        create_qdrant_collection(qdrant_client, args.collection_name, vector_size=args.vector_size)
        logger.info("Qdrant collection verified/created")
    except Exception as e:
        logger.error(f"Failed to create Qdrant collection: {str(e)}")
        sys.exit(1)

    all_vector_records = []
    processed_files = []
    start_time = time.time()

    for i, file_path in enumerate(mdx_files):
        try:
            logger.info(f"Processing file {i+1}/{len(mdx_files)}: {file_path}")
            vector_records = process_file_for_vectorization(file_path, cohere_client, config)
            all_vector_records.extend(vector_records)
            if vector_records:
                processed_files.append(file_path)
            perf_data = track_performance(start_time, len(mdx_files), i+1)
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            continue

    logger.info(f"Processed all files, created {len(all_vector_records)} vector records from {len(processed_files)} files")

    if all_vector_records:
        try:
            batch_store_vectors_in_qdrant(qdrant_client, all_vector_records, args.collection_name, args.batch_size)
            logger.info(f"Successfully stored {len(all_vector_records)} vectors in Qdrant")
        except Exception as e:
            logger.error(f"Failed to store vectors in Qdrant: {str(e)}")
            sys.exit(1)

        try:
            verification_success = verify_stored_vectors(qdrant_client, args.collection_name)
            if verification_success:
                logger.info("Vector verification successful")
            else:
                logger.warning("Vector verification failed")
        except Exception as e:
            logger.error(f"Error during vector verification: {str(e)}")

        validation_success = validate_all_files_processed(mdx_files, processed_files, len(all_vector_records))
        logger.info(f"File processing validation: {'PASSED' if validation_success else 'FAILED'}")

    print(f"Ingestion complete! Processed {len(mdx_files)} files and stored {len(all_vector_records)} vectors in Qdrant.")
    print("System is ready for semantic search queries.")


if __name__ == "__main__":
    main()
