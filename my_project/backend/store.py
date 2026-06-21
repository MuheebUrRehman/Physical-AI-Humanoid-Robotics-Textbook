import aiosqlite
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional
from pydantic import TypeAdapter
from chatkit.store import Store, NotFoundError
from chatkit.types import ThreadMetadata, ThreadItem, Page, Attachment, ActiveStatus

# ThreadItem is a discriminated union (Annotated type), not a direct Pydantic model.
# Use TypeAdapter for deserialization.
thread_item_adapter = TypeAdapter(ThreadItem)

logger = logging.getLogger(__name__)

class SQLiteStore(Store[Any]):
    """
    Asynchronous SQLite store implementation for OpenAI ChatKit Server.
    Uses aiosqlite to manage data persistence.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Create tables if they don't exist yet. Idempotent — safe to call repeatedly."""
        if self._initialized:
            return
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS threads (
                    id TEXT PRIMARY KEY,
                    metadata TEXT,
                    created_at REAL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id TEXT PRIMARY KEY,
                    thread_id TEXT,
                    item_data TEXT,
                    created_at REAL,
                    FOREIGN KEY (thread_id) REFERENCES threads (id) ON DELETE CASCADE
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS attachments (
                    id TEXT PRIMARY KEY,
                    attachment_data TEXT
                )
            """)
            await db.commit()
        self._initialized = True
        logger.info(f"SQLiteStore initialized at {self.db_path}")

    async def initialize(self) -> None:
        """Public alias for _ensure_initialized — called during lifespan."""
        await self._ensure_initialized()

    async def load_thread(self, thread_id: str, context: Any) -> ThreadMetadata:
        await self._ensure_initialized()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT metadata FROM threads WHERE id = ?", (thread_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise NotFoundError(f"Thread {thread_id} not found")
                return ThreadMetadata.model_validate_json(row[0])

    async def create_thread(
        self,
        user_id: str,
        metadata: dict | None = None,
        context: Any = None,
    ) -> ThreadMetadata:
        await self._ensure_initialized()
        thread = ThreadMetadata(
            title=f"Chat with {user_id}",
            id=str(uuid.uuid4()),
            created_at=datetime.now(timezone.utc),
            status=ActiveStatus(),
            allowed_image_domains=[],
            metadata=metadata or {},
        )
        await self.save_thread(thread, context)
        return thread

    async def save_thread(self, thread: ThreadMetadata, context: Any) -> None:
        await self._ensure_initialized()
        thread_json = thread.model_dump_json()
        created_at = datetime.now(timezone.utc).timestamp()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO threads (id, metadata, created_at) VALUES (?, ?, ?)",
                (thread.id, thread_json, created_at)
            )
            await db.commit()

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: Any,
    ) -> Page[ThreadItem]:
        await self._ensure_initialized()

        ORDER_SQL = {"asc": "ASC", "desc": "DESC"}
        sql_order = ORDER_SQL.get(order, "DESC")

        comparator = "<" if order == "desc" else ">"
        async with aiosqlite.connect(self.db_path) as db:
            if after:
                cursor = await db.execute(
                    f"SELECT created_at FROM items WHERE id = ?",
                    (after,)
                )
                row = await cursor.fetchone()
                if row:
                    after_ts = row[0]
                    items_cursor = await db.execute(
                        f"SELECT item_data FROM items WHERE thread_id = ? AND created_at {comparator} ? ORDER BY created_at {sql_order} LIMIT ?",
                        (thread_id, after_ts, limit)
                    )
                else:
                    items_cursor = await db.execute(
                        f"SELECT item_data FROM items WHERE thread_id = ? ORDER BY created_at {sql_order} LIMIT ?",
                        (thread_id, limit)
                    )
            else:
                items_cursor = await db.execute(
                    f"SELECT item_data FROM items WHERE thread_id = ? ORDER BY created_at {sql_order} LIMIT ?",
                    (thread_id, limit)
                )

            rows = await items_cursor.fetchall()
            items = [thread_item_adapter.validate_json(row[0]) for row in rows]

            has_more = len(items) >= limit
            return Page(data=items, has_more=has_more)

    async def save_attachment(self, attachment: Attachment, context: Any) -> None:
        await self._ensure_initialized()
        attachment_json = attachment.model_dump_json()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO attachments (id, attachment_data) VALUES (?, ?)",
                (attachment.id, attachment_json)
            )
            await db.commit()

    async def load_attachment(self, attachment_id: str, context: Any) -> Attachment:
        await self._ensure_initialized()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT attachment_data FROM attachments WHERE id = ?", (attachment_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise NotFoundError(f"Attachment {attachment_id} not found")
                return Attachment.model_validate_json(row[0])

    async def delete_attachment(self, attachment_id: str, context: Any) -> None:
        await self._ensure_initialized()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
            await db.commit()

    async def load_threads(
        self,
        limit: int,
        after: str | None,
        order: str,
        context: Any,
    ) -> Page[ThreadMetadata]:
        await self._ensure_initialized()

        ORDER_SQL = {"asc": "ASC", "desc": "DESC"}
        sql_order = ORDER_SQL.get(order, "DESC")

        comparator = "<" if order == "desc" else ">"
        async with aiosqlite.connect(self.db_path) as db:
            if after:
                cursor = await db.execute(
                    "SELECT created_at FROM threads WHERE id = ?",
                    (after,)
                )
                row = await cursor.fetchone()
                if row:
                    after_ts = row[0]
                    threads_cursor = await db.execute(
                        f"SELECT metadata FROM threads WHERE created_at {comparator} ? ORDER BY created_at {sql_order} LIMIT ?",
                        (after_ts, limit)
                    )
                else:
                    threads_cursor = await db.execute(
                        f"SELECT metadata FROM threads ORDER BY created_at {sql_order} LIMIT ?",
                        (limit,)
                    )
            else:
                threads_cursor = await db.execute(
                    f"SELECT metadata FROM threads ORDER BY created_at {sql_order} LIMIT ?",
                    (limit,)
                )

            rows = await threads_cursor.fetchall()
            threads = [ThreadMetadata.model_validate_json(row[0]) for row in rows]

            has_more = len(threads) >= limit
            return Page(data=threads, has_more=has_more)

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: Any
    ) -> None:
        await self._ensure_initialized()
        item_json = item.model_dump_json()
        created_at = datetime.now(timezone.utc).timestamp()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO items (id, thread_id, item_data, created_at) VALUES (?, ?, ?, ?)",
                (item.id, thread_id, item_json, created_at)
            )
            await db.commit()

    async def save_item(
        self, thread_id: str, item: ThreadItem, context: Any
    ) -> None:
        await self._ensure_initialized()
        item_json = item.model_dump_json()
        created_at = datetime.now(timezone.utc).timestamp()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO items (id, thread_id, item_data, created_at) VALUES (?, ?, ?, ?)",
                (item.id, thread_id, item_json, created_at)
            )
            await db.commit()

    async def load_item(
        self, thread_id: str, item_id: str, context: Any
    ) -> ThreadItem:
        await self._ensure_initialized()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT item_data FROM items WHERE id = ? AND thread_id = ?", (item_id, thread_id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise NotFoundError(f"Item {item_id} not found in thread {thread_id}")
                return thread_item_adapter.validate_json(row[0])

    async def delete_thread(self, thread_id: str, context: Any) -> None:
        await self._ensure_initialized()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
            await db.execute("DELETE FROM items WHERE thread_id = ?", (thread_id,))
            await db.commit()

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: Any
    ) -> None:
        await self._ensure_initialized()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM items WHERE id = ? AND thread_id = ?", (item_id, thread_id))
            await db.commit()
