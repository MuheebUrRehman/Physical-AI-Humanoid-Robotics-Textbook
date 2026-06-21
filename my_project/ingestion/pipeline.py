import logging
import os
import time
from typing import List, Dict, Tuple

from config import load_config
from mdx_utils import read_mdx_file, convert_mdx_to_text
from chunking import chunk_text, process_large_mdx_file
from embedding import embed_text_chunks
from models import VectorRecord


def extract_module_and_chapter_from_path(file_path: str) -> Tuple[str, str]:
    if file_path.startswith('./'):
        file_path = file_path[2:]
    path_parts = file_path.replace('\\', '/').split('/')
    try:
        docs_index = path_parts.index('docs')
        if docs_index + 2 < len(path_parts):
            module = path_parts[docs_index + 1]
            chapter_file = path_parts[docs_index + 2]
            chapter = os.path.splitext(chapter_file)[0]
            return module, chapter
        elif docs_index + 1 < len(path_parts):
            file_name = path_parts[docs_index + 1]
            chapter = os.path.splitext(file_name)[0]
            return 'root', chapter
        else:
            file_name = path_parts[-1]
            chapter = os.path.splitext(file_name)[0]
            return 'root', chapter
    except ValueError:
        if len(path_parts) >= 2:
            module = path_parts[-2]
            chapter = os.path.splitext(path_parts[-1])[0]
            return module, chapter
        else:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            return 'unknown', base_name


def validate_file_path(file_path: str, base_dir: str) -> bool:
    try:
        from urllib.parse import unquote
        decoded_path = unquote(file_path)
        normalized_path = os.path.normpath(decoded_path)
        base_path = os.path.normpath(base_dir)
        if not normalized_path.startswith(base_path):
            return False
        abs_file_path = os.path.abspath(normalized_path)
        abs_base_path = os.path.abspath(base_path)
        return abs_file_path.startswith(abs_base_path)
    except Exception:
        return False


def get_all_mdx_files(directory_path: str) -> List[str]:
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


def scan_mdx_files(docs_directory: str) -> List[str]:
    logger = logging.getLogger(__name__)
    logger.info(f"Scanning directory for .mdx files: {docs_directory}")
    if not os.path.exists(docs_directory):
        raise FileNotFoundError(f"Directory does not exist: {docs_directory}")
    mdx_files = get_all_mdx_files(docs_directory)
    logger.info(f"Found {len(mdx_files)} .mdx files")
    for file_path in mdx_files:
        logger.info(f"  - {file_path}")
    return mdx_files


def prepare_chunks_for_embedding(chunks: List[str], source_file: str, module: str, chapter: str) -> List[VectorRecord]:
    logger = logging.getLogger(__name__)
    logger.info(f"Preparing {len(chunks)} chunks for embedding from {source_file}")
    vector_records = []
    for idx, chunk in enumerate(chunks):
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


def process_file_for_vectorization(file_path: str, cohere_client, config: Dict) -> List[VectorRecord]:
    logger = logging.getLogger(__name__)
    start_time = time.time()
    logger.info(f"Processing file for vectorization: {file_path}")

    mdx_content = read_mdx_file(file_path, max_file_size_mb=config.get('max_file_size_mb', 50))
    if mdx_content is None:
        logger.error(f"Could not read file {file_path}, skipping")
        mdx_content = process_large_mdx_file(file_path)
        if mdx_content is None:
            logger.error(f"Could not process large file {file_path} either, skipping")
            return []

    module, chapter = extract_module_and_chapter_from_path(file_path)
    logger.info(f"Extracted module: {module}, chapter: {chapter} from {file_path}")

    text_content = convert_mdx_to_text(mdx_content)
    if not text_content.strip():
        logger.warning(f"No content found in {file_path} after MDX conversion, skipping")
        return []

    chunks = chunk_text(text_content, config['chunk_size'], config['chunk_overlap'])
    logger.info(f"Text chunked into {len(chunks)} chunks")

    vector_records = prepare_chunks_for_embedding(chunks, file_path, module, chapter)
    logger.info(f"Prepared {len(vector_records)} vector records for embedding")

    embedded_records = embed_text_chunks(cohere_client, vector_records, config['cohere_model'])
    logger.info(f"Successfully embedded {len(embedded_records)} vector records")

    elapsed_time = time.time() - start_time
    logger.info(f"Completed processing {file_path} in {elapsed_time:.2f}s, created {len(embedded_records)} embedded records")
    return embedded_records


def track_performance(start_time: float, total_files: int, processed_files: int) -> Dict:
    logger = logging.getLogger(__name__)
    elapsed_time = time.time() - start_time
    estimated_total_time = (elapsed_time / max(processed_files, 1)) * total_files
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

    logger.info(f"Performance: {elapsed_time:.2f}s elapsed, "
                f"~{estimated_total_time:.2f}s estimated total, "
                f"~{remaining_time:.2f}s remaining, "
                f"{performance_data['progress_percent']:.1f}% complete")

    if estimated_total_time > 600:
        logger.warning(f"Process estimated to take {estimated_total_time:.2f}s, "
                       f"which exceeds the 10-minute target of 600s")
    else:
        logger.info(f"Process on track to complete within 10-minute target "
                    f"(estimated: {estimated_total_time:.2f}s)")
    return performance_data
