import pytest
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone


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
