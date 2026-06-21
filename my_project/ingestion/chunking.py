import logging
from typing import List

import tiktoken


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50, encoding_name: str = "cl100k_base") -> List[str]:
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
        if para_tokens > chunk_size:
            if current_chunk_parts:
                chunk = flush_chunk()
                if chunk:
                    chunks.append(chunk)
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
        if current_tokens + para_tokens > chunk_size and current_chunk_parts:
            chunk = flush_chunk()
            if chunk:
                chunks.append(chunk)
        current_chunk_parts.append(para)
        current_tokens += para_tokens

    if current_chunk_parts:
        chunk = flush_chunk()
        if chunk:
            chunks.append(chunk)

    logger.info(f"Text chunked into {len(chunks)} token-aware chunks")
    return chunks


def process_large_mdx_file(file_path: str, chunk_size: int = 8192) -> str:
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
