# Quickstart: Performance Refactor Verification

## Manual Stability Verification

1. **Open Frontend**: Open the Docusaurus site in Chrome.
2. **Network Throttling**: 
    - Open DevTools -> Network Tab.
    - Change "No throttling" to "Slow 3G" (or a custom slow profile).
3. **Trigger Stream**: Ask a question in the chat.
4. **Validation**: Ensure no red error boxes appear and the text streams smoothly.

## Backend Concurrency Benchmark

1. **Start Server**: `uv run uvicorn app:app`.
2. **Run Stress Script**:
   ```python
   # tests/test_performance.py snippet
   async with httpx.AsyncClient() as client:
       responses = await asyncio.gather(*[client.post(url, json=payload) for _ in range(10)])
   ```
3. **Validation**: All 10 requests should complete in roughly the same time as a single request (showing non-blocking I/O).

## Key Files
- `backend/retrieval.py`: Now uses `AsyncClient` and `AsyncQdrantClient`.
- `backend/agent.py`: `judge_agent` is initialized at the top level.
- `frontend/src/components/FloatingChat.tsx`: Implementation of the `while` loop with `accumulatedBuffer`.
