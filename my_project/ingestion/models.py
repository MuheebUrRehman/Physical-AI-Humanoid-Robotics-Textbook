import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional


class VectorRecord:
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
        return {
            "content": self.content,
            "source_file": self.source_file,
            "module": self.module,
            "chapter": self.chapter,
            "chunk_index": self.chunk_index,
            "created_at": self.created_at.isoformat()
        }

    def to_qdrant_point(self) -> Dict:
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
        record_id = str(uuid.uuid4())
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
