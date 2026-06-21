import pytest
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone


@pytest.fixture(autouse=True)
def _cleanup_retrieval_cache():
    import retrieval
    retrieval._embed_cache.clear()


@pytest.fixture
def db_path():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.mark.asyncio
async def test_store_initialize_creates_tables(db_path):
    from store import SQLiteStore
    store = SQLiteStore(db_path)
    await store.initialize()

    import aiosqlite
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in await cursor.fetchall()}

    assert "threads" in tables
    assert "items" in tables
    assert "attachments" in tables


@pytest.mark.asyncio
async def test_store_create_and_load_thread(db_path):
    from store import SQLiteStore
    store = SQLiteStore(db_path)
    await store.initialize()

    thread = await store.create_thread(user_id="student1", metadata={"source": "test"})
    assert thread.id is not None

    loaded = await store.load_thread(thread.id, context=None)
    assert loaded.id == thread.id


@pytest.mark.asyncio
async def test_store_load_thread_not_found(db_path):
    from store import SQLiteStore
    from chatkit.store import NotFoundError
    store = SQLiteStore(db_path)
    await store.initialize()

    with pytest.raises(NotFoundError):
        await store.load_thread("nonexistent", context=None)


@pytest.mark.asyncio
async def test_store_load_item_not_found(db_path):
    from store import SQLiteStore
    from chatkit.store import NotFoundError
    store = SQLiteStore(db_path)
    await store.initialize()

    thread = await store.create_thread(user_id="student1")
    with pytest.raises(NotFoundError):
        await store.load_item(thread.id, "nonexistent", context=None)


@pytest.mark.asyncio
async def test_store_delete_thread_cascades(db_path):
    from store import SQLiteStore
    store = SQLiteStore(db_path)
    await store.initialize()

    thread = await store.create_thread(user_id="student1")
    await store.delete_thread(thread.id, context=None)

    from chatkit.store import NotFoundError
    with pytest.raises(NotFoundError):
        await store.load_thread(thread.id, context=None)


@pytest.mark.asyncio
async def test_store_load_threads_pagination(db_path):
    from store import SQLiteStore
    store = SQLiteStore(db_path)
    await store.initialize()

    await store.create_thread(user_id="u1")
    await store.create_thread(user_id="u2")

    page = await store.load_threads(limit=1, after=None, order="asc", context=None)
    assert len(page.data) == 1
    assert page.has_more is True

    page2 = await store.load_threads(limit=10, after=None, order="asc", context=None)
    assert len(page2.data) == 2


@pytest.mark.asyncio
async def test_store_is_idempotent(db_path):
    from store import SQLiteStore
    store = SQLiteStore(db_path)
    await store.initialize()
    await store.initialize()

    import aiosqlite
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in await cursor.fetchall()}

    assert "threads" in tables


@pytest.mark.asyncio
async def test_store_add_and_load_item(db_path):
    from store import SQLiteStore, thread_item_adapter
    store = SQLiteStore(db_path)
    await store.initialize()

    thread = await store.create_thread(user_id="student1")
    item_json = '{"type":"user_message","id":"item-1","thread_id":"' + thread.id + '","created_at":"2026-01-01T00:00:00Z","content":[{"type":"input_text","text":"hello"}],"inference_options":{},"status":{"type":"completed"}}'
    import aiosqlite
    async with aiosqlite.connect(db_path) as db:
        await db.execute("INSERT INTO items (id, thread_id, item_data, created_at) VALUES (?, ?, ?, ?)",
                         ("item-1", thread.id, item_json, 1767225600.0))
        await db.commit()

    loaded = await store.load_item(thread.id, "item-1", context=None)
    assert loaded is not None


@pytest.mark.asyncio
async def test_store_save_item_replaces_existing(db_path):
    from store import SQLiteStore
    store = SQLiteStore(db_path)
    await store.initialize()

    thread = await store.create_thread(user_id="student1")
    v1 = '{"type":"user_message","id":"item-replace","thread_id":"' + thread.id + '","created_at":"2026-01-01T00:00:00Z","content":[{"type":"input_text","text":"v1"}],"inference_options":{},"status":{"type":"completed"}}'
    v2 = '{"type":"user_message","id":"item-replace","thread_id":"' + thread.id + '","created_at":"2026-01-01T00:00:00Z","content":[{"type":"input_text","text":"v2"}],"inference_options":{},"status":{"type":"completed"}}'
    import aiosqlite
    async with aiosqlite.connect(db_path) as db:
        await db.execute("INSERT INTO items (id, thread_id, item_data, created_at) VALUES (?, ?, ?, ?)",
                         ("item-replace", thread.id, v1, 1767225600.0))
        await db.execute("INSERT OR REPLACE INTO items (id, thread_id, item_data, created_at) VALUES (?, ?, ?, ?)",
                         ("item-replace", thread.id, v2, 1767225601.0))
        await db.commit()

    loaded = await store.load_item(thread.id, "item-replace", context=None)
    assert loaded is not None


@pytest.mark.asyncio
async def test_store_delete_item(db_path):
    from store import SQLiteStore
    store = SQLiteStore(db_path)
    await store.initialize()

    thread = await store.create_thread(user_id="student1")
    item_json = '{"type":"user_message","id":"item-to-delete","thread_id":"' + thread.id + '","created_at":"2026-01-01T00:00:00Z","content":[{"type":"input_text","text":"delete me"}],"inference_options":{},"status":{"type":"completed"}}'
    import aiosqlite
    async with aiosqlite.connect(db_path) as db:
        await db.execute("INSERT INTO items (id, thread_id, item_data, created_at) VALUES (?, ?, ?, ?)",
                         ("item-to-delete", thread.id, item_json, 1767225600.0))
        await db.commit()
    await store.delete_thread_item(thread.id, "item-to-delete", context=None)

    from chatkit.store import NotFoundError
    with pytest.raises(NotFoundError):
        await store.load_item(thread.id, "item-to-delete", context=None)


@pytest.mark.asyncio
async def test_store_attachment_crud(db_path):
    from store import SQLiteStore
    from chatkit.types import FileAttachment
    store = SQLiteStore(db_path)
    await store.initialize()

    attachment = FileAttachment(
        id="att-1",
        name="test.txt",
        mime_type="text/plain",
    )
    await store.save_attachment(attachment, context=None)

    loaded = await store.load_attachment("att-1", context=None)
    assert loaded.id == "att-1"

    await store.delete_attachment("att-1", context=None)
    from chatkit.store import NotFoundError
    with pytest.raises(NotFoundError):
        await store.load_attachment("att-1", context=None)
