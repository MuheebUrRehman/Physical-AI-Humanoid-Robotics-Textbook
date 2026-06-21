import logging
import os
import re
from typing import Optional


def read_mdx_file(file_path: str, max_file_size_mb: int = 50) -> Optional[str]:
    logger = logging.getLogger(__name__)
    logger.info(f"Reading MDX file: {file_path}")
    try:
        file_size_bytes = os.path.getsize(file_path)
        max_size_bytes = max_file_size_mb * 1024 * 1024
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


def convert_mdx_to_text(mdx_content: str) -> str:
    logger = logging.getLogger(__name__)
    logger.info("Converting MDX content to plain text")
    original_length = len(mdx_content)

    text_content = re.sub(r'<[^>]*>', '', mdx_content)
    text_content = re.sub(r'^\s*(?:import|export)\s+.*?[\n\r]+', '', text_content, flags=re.MULTILINE)
    text_content = re.sub(r'```[\s\S]*?```', '', text_content)
    text_content = re.sub(r'`[^`]*`', '', text_content)
    text_content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text_content)
    text_content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text_content)
    text_content = re.sub(r'^\s*#+\s*', '', text_content, flags=re.MULTILINE)
    text_content = re.sub(r'\*{2}([^*]+)\*{2}|_{2}([^_]+)_{2}', r'\1\2', text_content)
    text_content = re.sub(r'(?<!\*)\*([^\*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)', r'\1\2', text_content)
    text_content = re.sub(r'^\s*[-*+]\s+', '', text_content, flags=re.MULTILINE)
    text_content = re.sub(r'^\s*\d+\.\s+', '', text_content, flags=re.MULTILINE)
    text_content = re.sub(r'\n\s*\n', '\n', text_content)
    text_content = re.sub(r' +', ' ', text_content)
    text_content = text_content.strip()

    logger.info(f"MDX conversion complete: {original_length} -> {len(text_content)} characters")
    return text_content
