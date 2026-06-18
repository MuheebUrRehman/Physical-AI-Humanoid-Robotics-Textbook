# Physical AI & Humanoid Robotics Textbook — Reusable Intelligence

**Version**: 2.0 (Extracted from Codebase)
**Date**: 2026-06-18

## Overview

This document captures the reusable intelligence embedded in the RAG chatbot textbook codebase — patterns, decisions, and expertise applicable to any project combining LLMs with domain-specific knowledge bases.

---

## Extracted Skills

### Skill 1: RAG Pipeline with Multi-Layer Validation

**Persona**: You are a backend engineer building a Retrieval-Augmented Generation system where the LLM must only answer from provided context, and user input must be validated at every layer.

**Questions to ask before implementing RAG**:
- What are the trust boundaries? (User → API → Guardrail → LLM → Response)
- What happens at each layer when input is invalid?
- How do you prevent prompt injection while preserving legitimate queries?
- What's the fallback behavior when retrieval returns nothing?

**Principles**:
- **Layer 1 — Input Sanitization**: Strip HTML/JS, block SQL patterns, block code execution patterns, block path traversal. Run this on every user input before anything else.
- **Layer 2 — Guardrail**: A lightweight LLM call to classify query relevance. Must fail-open (let query through on error) to avoid blocking due to transient LLM failures.
- **Layer 3 — RAG Grounding**: Only the retrieved chunks + the user query reach the main LLM. The system prompt explicitly instructs the LLM to refuse answering if the answer isn't in the chunks.
- **Layer 4 — Response**: The LLM output is streamed directly to the client. No post-processing (assumes LLM won't produce harmful output when grounded).

**Implementation Pattern** (extracted from codebase):
```python
# Layer 1: Input Validation (app.py: chat_endpoint)
is_valid, error_msg, sanitized_query = validate_query(request.query)
if not is_valid:
    raise HTTPException(status_code=400, detail=error_msg)

# Layer 2: Guardrail (agent.py)
@input_guardrail
async def check_query_relevance(ctx, agent, input_text):
    result = await Runner.run(judge_agent, f"Analyze: {input_text}")
    is_relevant = 'yes' in result.final_output.lower()
    return GuardrailFunctionOutput(
        tripwire_triggered=not is_relevant,
        output_info=None if is_relevant else "Off-topic query detected"
    )

# Layer 3: RAG Grounding (chatkit_server.py + agent.py)
relevant_chunks = await get_relevant_chunks(search_query)
# Dynamic instructions inject chunks into system prompt
def book_knowledge_instructions(ctx, agent):
    chunks_text = format_chunks(ctx.context["book_chunks"])
    return f"You must answer based ONLY on this content:\n{chunks_text}"

# Layer 4: SSE Streaming (app.py)
async for event in stream.stream_events():
    if event.type == "raw_response_event":
        delta = getattr(data, "delta", None)
        if delta:
            yield f"data: {json_event}\n\n"
```

**When to apply**:
- Any RAG system using user-provided queries
- Chatbots over sensitive or proprietary content
- Educational assistants where answer correctness is critical

**Contraindications**:
- Open-domain chatbots (no grounding needed, guardrail would be too restrictive)
- Systems where the LLM needs access to external tools (guardrail may block tool-use queries)

---

### Skill 2: ChatKit Protocol Bridge with Error Isolation

**Persona**: You are integrating the OpenAI ChatKit protocol with a custom AI backend, where conversation persistence and graceful error recovery are required.

**Questions to ask before implementing ChatKit**:
- What's the threading model? (ChatKit manages threads server-side; the `respond()` method is called per user message)
- How does conversation history flow into the LLM context? (ChatKit provides the thread; you load items, format as text, inject into the prompt)
- How do you handle streaming errors without corrupting the conversation state? (Once SSE events are sent to ChatKit, an ErrorEvent would break the conversation)
- What context does the widget provide? (ChatKit protocol carries metadata; your fetch interceptor can inject anything)

**Principles**:
- **Extend ChatKitServer, don't wrap it**: Your custom server inherits from `ChatKitServer[RequestContext]` and overrides `respond().` ChatKit handles thread management; you focus on AI logic.
- **History as prompt prefix**: Load the last N thread items, format with role prefixes (User/Assistant/Tool), prepend to the system prompt. This gives the LLM conversational memory without ChatKit managing it.
- **Transient agent clone**: Don't modify the global singleton agent. Clone it with dynamic instructions per-request to avoid shared state.
- **Error isolation with sentinel flag**: Track `sent_any_event`. If an error occurs before any event was sent, yield `ErrorEvent(code="custom", message=..., allow_retry=True)`. After events are sent, log the error but don't yield — the client has partial output and an ErrorEvent would corrupt the thread state.
- **Page context injection**: The frontend's fetch interceptor injects page metadata into the ChatKit protocol body; you extract it from `params.input.metadata.pageContext` in the `/chatkit` route handler.

**Implementation Pattern** (extracted from codebase):
```python
# ChatKit Server Bridge (chatkit_server.py)
class CustomChatKitServer(ChatKitServer[RequestContext]):
    async def respond(self, thread, input_user_message, context):
        if not input_user_message:
            return

        # 1. Load history
        previous_items = await self.store.load_thread_items(
            thread.id, after=None, limit=10, order="desc", context=context
        )
        history_str = format_history(previous_items)

        # 2. Extract page context + query
        page_context_str = format_page_context(context.page_context)
        user_query = extract_text(input_user_message.content)

        # 3. RAG retrieval with context grounding
        search_query = f"{context.page_context.title}: {user_query}" if context.page_context else user_query
        relevant_chunks = await get_relevant_chunks(search_query)

        # 4. Dynamic instructions with history + page context
        def dynamic_instructions(ctx, agent):
            base = book_knowledge_instructions(ctx, agent)
            return f"{history_str}\n{page_context_str}\n{base}"

        # 5. Clone agent with dynamic instructions
        run_agent = Agent(
            name=book_knowledge_agent.name,
            instructions=dynamic_instructions,
            model=book_knowledge_agent.model,
            model_settings=book_knowledge_agent.model_settings,
            input_guardrails=book_knowledge_agent.input_guardrails
        )

        # 6. Stream with error isolation
        result = Runner.run_streamed(run_agent, user_query, context=agent_run_context)
        sent_any_event = False
        async for event in stream_agent_response(agent_ctx, result):
            yield event
            sent_any_event = True

        # 7. ErrorEvent only if no events streamed yet
        except Exception as e:
            if not sent_any_event:
                yield ErrorEvent(code="custom", message=str(e)[:200], allow_retry=True)
```

**When to apply**:
- Any project using ChatKit protocol for chat UI
- Systems needing persistent conversation threads without managing them manually
- Educational assistants where page context improves answer relevance

**Contraindications**:
- Simple Q&A without conversation history (ChatKit overhead not justified)
- Systems already using a different chat protocol (e.g., plain SSE)

---

### Skill 3: Dynamic LLM Instructions with Context Injection

**Persona**: You are building an LLM application where the system prompt must change per-request based on retrieved context, conversation history, and user state.

**Questions to ask before implementing dynamic instructions**:
- What context changes per request? (Retrieved chunks, history, page being viewed, user identity)
- What context is static? (Base behavior instructions, formatting rules, constraints)
- How do you compose these without redefining the agent for every request?
- How do you keep the prompt within the model's context window?

**Principles**:
- **Static base + dynamic injection**: Define the base agent with static instructions using a function, not a string. The function reads from `RunContextWrapper.context` at call time.
- **Clone agents for per-request customization**: The OpenAI Agents SDK lets you clone an `Agent` with overridden `instructions`. This is safer than mutating the global singleton.
- **Prepend history, not append**: Conversation history goes before the chunk context, so the LLM sees the conversation flow first, then the grounding content.
- **Page context as early priming**: If the user is on a specific page, prepend "STUDENT CONTEXT: Viewing page X" to help the LLM prioritize relevant content before it even sees the chunks.
- **Token budget**: Set `max_tokens` on the output. The input context uses the model's full context window (in this case ~32K for Qwen 3), so ensure your combined history + chunks + instructions fit.

**Implementation Pattern** (extracted from codebase):
```python
# Static base as function (agent.py)
def book_knowledge_instructions(ctx: RunContextWrapper, agent: Agent) -> str:
    """Called by the Agent SDK when the LLM needs instructions.
    ctx.context contains the per-request data."""
    book_chunks = ctx.context.get("book_chunks", [])
    chunks_text = format_chunks(book_chunks)
    return f"""
    You are an AI assistant that answers questions based only on book content.
    ### BOOK CONTENT CONTEXT:
    {chunks_text}
    """

# Dynamic wrapping per-request (chatkit_server.py)
def dynamic_instructions(ctx: RunContextWrapper, agent: Agent) -> str:
    base_instructions = book_knowledge_instructions(ctx, agent)
    return f"{history_str}\n{page_context_str}\n{base_instructions}"

# Clone agent for this request only
run_agent = Agent(
    name=book_knowledge_agent.name,
    instructions=dynamic_instructions,  # ← new function reference
    model=book_knowledge_agent.model,
    model_settings=book_knowledge_agent.model_settings,
    input_guardrails=book_knowledge_agent.input_guardrails
)
```

**When to apply**:
- Any LLM application where the prompt changes per request
- RAG systems where retrieved documents differ per query
- Multi-tenant systems where each tenant has different instructions
- Chatbots with conversation memory

**Contraindications**:
- Simple, stateless Q&A (no context variation needed)
- Systems using models with very small context windows

---

### Skill 4: SSE Streaming with Error Recovery

**Persona**: You are building a streaming API where partial results must be delivered in real-time, and failures must be communicated without corrupting the client state.

**Questions to ask before implementing SSE streaming**:
- What event types are needed? (Token deltas, final result, errors, metadata)
- How does the client handle partial output vs. completed output?
- What happens if the stream disconnects mid-response? (Client should reconnect, server should be idempotent)
- How does SSE interact with your framework? (FastAPI StreamingResponse vs. async generators)

**Principles**:
- **Well-defined event schema**: Use a discriminated union type (`SSEMessage.type = "token" | "final" | "error"`). The client switches behavior based on `type`.
- **One `data:` line per event**: SSE format requires `data: <json>\n\n`. Each yield produces exactly one event.
- **Empty response detection**: Track `tokens_yielded` counter. If zero events were yielded after the stream completes, emit an explicit `type: "error"` event with a user-friendly message. This prevents silent failures.
- **Guardrail errors are user-friendly**: When the guardrail triggers, emit `type: "error"` with "Off-topic query detected" rather than a raw exception message.
- **StreamingResponse for FastAPI**: Return `StreamingResponse(chat_stream_generator(), media_type="text/event-stream")`. FastAPI handles the SSE headers and transfer encoding.
- **Error boundaries**: Wrap the generator in try/except. Catch all exceptions and yield error events instead of crashing the stream. The client always gets a complete SSE stream.

**Implementation Pattern** (extracted from codebase):
```python
# Event schema (models/chat.py)
class SSEMessage(BaseModel):
    type: str  # "token" | "final" | "error"
    content: Union[str, AgentResponse]

# Stream generator (app.py)
async def chat_stream_generator(request: ChatRequest) -> AsyncGenerator[str, None]:
    tokens_yielded = 0
    try:
        relevant_chunks = await get_relevant_chunks(request.query)
        stream = Runner.run_streamed(book_knowledge_agent, request.query, context={...})

        async for event in stream.stream_events():
            if event.type == "raw_response_event":
                delta = getattr(event.data, "delta", None)
                if delta:
                    tokens_yielded += 1
                    message = SSEMessage(type="token", content=delta)
                    yield f"data: {message.model_dump_json()}\n\n"

            elif event.type == "run_item_stream_event":
                # ... handle final output ...

        if tokens_yielded == 0:
            # Empty response — yield error instead of silent failure
            error_message = SSEMessage(type="error", content="The AI generated an empty response.")
            yield f"data: {error_message.model_dump_json()}\n\n"

    except InputGuardrailTripwireTriggered:
        error_message = SSEMessage(type="error", content="Off-topic query detected.")
        yield f"data: {error_message.model_dump_json()}\n\n"
    except Exception as e:
        error_message = SSEMessage(type="error", content=f"Streaming error: {str(e)[:200]}")
        yield f"data: {error_message.model_dump_json()}\n\n"

# FastAPI route
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    return StreamingResponse(
        chat_stream_generator(request),
        media_type="text/event-stream"
    )
```

**When to apply**:
- Any real-time LLM streaming
- Long-running operations where partial progress should be displayed
- Systems requiring graceful error communication to the client

---

### Skill 5: Retry with Exponential Backoff for External APIs

**Persona**: You are integrating with external APIs (Cohere, Qdrant, OpenAI) where transient failures (rate limits, network blips, server errors) must be handled transparently.

**Questions to ask before implementing retry logic**:
- Are the failures transient or permanent? (Rate limit = transient; bad API key = permanent — don't retry)
- What's the retry budget? (Total time the user waits before getting a response)
- Should you fail-fast or degrade gracefully? (RAG can return empty chunks and still produce a response)
- What backoff strategy prevents thundering herd? (Exponential backoff with jitter)

**Principles**:
- **Only retry on transient failures**: Network timeouts, 429 (rate limit), 503 (service unavailable). Don't retry on 4xx client errors.
- **Exponential backoff**: `delay = base * 2^attempt` (1s, 2s, 4s). Add jitter in production to prevent synchronized retries.
- **Graceful degradation**: If retrieval retries are exhausted, return empty results instead of propagating the error. The LLM can still respond (poorly, but it doesn't crash).
- **Max retries = 3**: Balances reliability with latency. Beyond 3 retries (~7s cumulative), the user experience degrades too much.
- **Log every attempt**: Each retry logs a warning with the attempt number and error. Final failure logs an error.

**Implementation Pattern** (extracted from codebase):
```python
# Retrieval with retry (retrieval.py)
async def get_relevant_chunks(query: str, max_retries: int = 3) -> List[Dict[str, str]]:
    for attempt in range(max_retries):
        try:
            # Try the operation
            response = await co.embed(texts=[query], model="embed-multilingual-v3.0", ...)
            search_results = await qdrant_client.query_points(...)
            return relevant_chunks

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error("All retries exhausted")
                return []  # Graceful degradation

            await asyncio.sleep(2 ** attempt)  # 1s, 2s, 4s
```

**When to apply**:
- Any code calling external HTTP APIs
- Database connection retries
- File I/O operations
- Webhook delivery

**Contraindications**:
- Idempotency-critical operations without idempotency keys (retries may cause duplicates)
- Real-time systems where latency budget is <100ms
- Permanent failures (don't retry auth errors)

---

## Architecture Decision Records (Inferred)

### ADR-001: Chosen OpenRouter over Direct OpenAI API

**Status**: Accepted

**Context**:
The system needs LLM access for both the primary RAG agent and the guardrail judge agent. Direct OpenAI API would be the simplest choice, but the project targets a diverse user base with different LLM preferences and budget constraints.

**Decision**: Route all LLM calls through OpenRouter using the OpenAI-compatible v1 API.

**Rationale** (inferred from code):
1. `_build_openai_client()` in `agent.py` sets `base_url=Config.LLM_BASE_URL` which defaults to `https://openrouter.ai/api/v1`
2. `default_headers` includes `HTTP-Referer` and `X-Title`, which are OpenRouter-specific identity headers
3. `Config.LLM_API_KEY` has a fallback chain: `LLM_API_KEY` → `OPENROUTER_API_KEY` → `GEMINI_API_KEY`, suggesting OpenRouter is primary with Gemini as fallback
4. Default model `qwen/qwen3-coder` is a model available through OpenRouter, not directly from OpenAI

**Consequences**:

**Positive**:
- Model flexibility: can switch between 200+ models by changing `LLM_MODEL`
- Cost control: can use cheaper models via OpenRouter's auction pricing
- Single API for all LLM needs (guardrail + main agent)
- No vendor lock-in to OpenAI

**Negative**:
- Additional latency from OpenRouter's routing layer (~50-200ms)
- Dependency on a third-party proxy (OpenRouter availability affects system availability)
- OpenRouter-specific headers required (`HTTP-Referer`, `X-Title`)

### ADR-002: Chosen Character-Based Chunking over Token-Based

**Status**: Accepted

**Context**:
The ingestion pipeline needs to split textbook content into chunks for embedding. Token-based chunking (using a proper tokenizer) would be more accurate but adds a dependency.

**Decision**: Use character-based chunking (512 chars, 50 overlap) with a note that token-based chunking would be better in production.

**Rationale** (inferred from code):
1. `chunk_text()` in `ingest_book.py` uses simple string slicing: `text[start:end]`
2. Comment in code: *"For simplicity, we're using character-based chunking instead of token-based. In a production system, we'd use a proper tokenizer."*
3. The decision prioritizes simplicity and avoiding an additional dependency (tiktoken)

**Consequences**:

**Positive**:
- No additional dependency
- Simple, debuggable logic
- Fast — no tokenization overhead

**Negative**:
- Chunks may break in the middle of words or sentences
- Character count != token count; 512 chars is ~128-200 tokens (varies by language)
- Semantic boundaries (paragraphs, sections) are not respected
- Overlap of 50 chars (~12 tokens) may be insufficient for context preservation

### ADR-003: Chosen SQLite over PostgreSQL for ChatKit Store

**Status**: Accepted

**Context**:
The ChatKit protocol requires persistent storage for conversation threads, items, and attachments. Options include SQLite, PostgreSQL, or in-memory storage.

**Decision**: Use SQLite via aiosqlite for ChatKit conversation persistence.

**Rationale** (inferred from code):
1. Conversation data is single-process and low-volume (one backend instance, moderate number of users)
2. SQLite requires zero configuration — no database server to set up, no connection pooling
3. The ChatKit `Store` interface is simple (CRUD on 3 tables), well within SQLite's capabilities
4. File-based DB (`chatkit.db`) is easy to backup, reset, and inspect (debug script: `scripts/read_db.py`)

**Consequences**:

**Positive**:
- Zero infrastructure: no DB server, no connection pool, no migrations
- Single file: easy to backup, reset, or inspect
- Fast for single-process access
- Automatic deployment: file is created on first use

**Negative**:
- No horizontal scaling: multiple backend instances would need separate DB files
- Write contention under high concurrency (SQLite uses file-level locking)
- No built-in replication or high availability
- Schema changes require manual migration (no Alembic/Flyway)

### ADR-004: Chosen Memory-Based Pagination over SQL OFFSET/LIMIT

**Status**: Accepted

**Context**:
The `load_thread_items()` and `load_threads()` methods need pagination. ChatKit uses a cursor-based pattern with `after` and `limit`.

**Decision**: Load all items into memory, then paginate in Python code.

**Rationale** (inferred from code):
```python
rows = await cursor.fetchall()  # Load ALL items
items = [thread_item_adapter.validate_json(row[0]) for row in rows]
# Memory-based pagination in Python
page_data = items[start_idx:start_idx + limit]
```

1. Conversation threads are typically short (< 100 items per thread)
2. Simpler than implementing cursor-based SQL pagination with `WHERE id > ? LIMIT ?`
3. No SQL complexity for the `after` cursor (ChatKit uses the `item.id` as cursor, which is a UUID, not a sequential integer)

**Consequences**:

**Positive**:
- Simple, bug-free pagination logic
- No complex SQL queries needed
- Always consistent (no phantom reads from concurrent inserts)

**Negative**:
- Won't scale to threads with thousands of items (memory pressure)
- Every pagination request loads the full data set (wasteful for deep pagination)

---

## Code Patterns & Conventions

### Pattern 1: async def + aiosqlite for All Database Operations

**Observed in**: `store.py`

All database methods follow the same pattern:
```python
async with aiosqlite.connect(self.db_path) as db:
    await db.execute("SQL", params)
    await db.commit()
```

**Why**: aiosqlite provides async SQLite access compatible with FastAPI's async event loop. The `async with` context manager handles connection lifecycle.

### Pattern 2: Pydantic BaseModel for All API Schemas

**Observed in**: `models/chat.py`

Every request, response, and internal data structure is a Pydantic BaseModel with:
- Type-annotated fields
- `Field()` with description and validation (`min_length`, `max_length`, `ge`, `le`)
- `model_dump_json()` for serialization
- `model_validate_json()` for deserialization

### Pattern 3: Module-Level Loggers

**Observed in**: `app.py`, `agent.py`, `retrieval.py`, `store.py`, `chatkit_server.py`

Every module creates its own logger:
```python
logger = logging.getLogger(__name__)
```

**Why**: Allows log filtering by module, makes debugging easier (each log message includes the source module).

### Pattern 4: Early Config Validation on Import

**Observed in**: `app.py`

```python
try:
    Config.validate()
except ValueError as e:
    logger.error(f"Configuration validation failed: {e}")
    sys.exit(1)
```

**Why**: Fail fast on startup rather than at first user request. If a required API key is missing, the server crashes immediately with a clear error message.

### Pattern 5: Text Selection UI Pattern

**Observed in**: `ChatKitWidget.tsx`

The `mouseup` event listener captures text selection, gets bounding rect via `Range.getBoundingClientRect()`, and positions a floating button above the selection. On click, it calls `setComposerValue()` to pre-fill the ChatKit composer.

## Lessons Learned

### What Worked Well

1. **Three-layer validation architecture**: Input sanitization → Guardrail → RAG grounding prevented prompt injection, off-topic queries, and hallucinated answers
2. **Dynamic instructions pattern**: Using function-based instructions that read from `RunContextWrapper.context` enabled per-request customization without agent redefinition
3. **Error isolation in ChatKit**: The `sent_any_event` flag pattern prevented corrupted conversation state when errors occurred mid-stream
4. **Lazy SQLite initialization**: `_ensure_initialized()` called at the start of every public method automatically created tables on first use, avoiding the need for explicit initialization in the lifespan
5. **Gradient-based CTA buttons**: The `linear-gradient(135deg, #6366F1, #8B5CF6)` + lift on hover + scale on active created a tactile, premium feel

### What Could Be Improved

1. **No test execution in CI**: The deploy workflow deploys without running any tests — broken code can reach production
2. **Duplicated RAG orchestration**: The agent-streaming pipeline (get_chunks → run_agent → stream_events) is duplicated between `app.py` (chat_stream_generator) and `chatkit_server.py` (respond method). Should be extracted into a shared service
3. **Missing citation tracking**: `AgentResponse.citations` is defined but populated with only `source_file` — no actual citation context (page numbers, section titles)
4. **Connection management**: Cohere and Qdrant clients are initialized at module level with no explicit lifecycle management (open on import, never closed)

### What to Avoid in Future Projects

1. **Committing API keys**: The `.env` file was committed before being gitignored. Always add sensitive files to `.gitignore` before the first commit
2. **Char-based chunking for production**: Character-based chunking doesn't respect sentence boundaries. Use token-based chunking (tiktoken) or semantic chunking in production
3. **Deprecated CLI flags**: The Dockerfile used `--no-dev` which was deprecated in a newer uv version. Pin tool versions or use forward-compatible flags

## Reusability Assessment

### Components Reusable As-Is

1. **`utils/validation.py`**: Input sanitization functions are generic enough for any web API
2. **`config.py` pattern**: Class-based config with classmethod validation is portable to any Python project
3. **`models/chat.py`** schemas: BaseModel types for RAG, SSE, and health check are reusable templates
4. **`retrieval.py` retry pattern**: The exponential backoff + graceful degradation approach is reusable in any async API client

### Patterns Worth Generalizing

1. **Dynamic instructions with context injection**: Create a skill/template for function-based system prompts that vary per-request
2. **ChatKit protocol bridge with error isolation**: Create a skill for the CustomChatKitServer pattern with sentinel flag error handling
3. **Multi-layer RAG validation**: Create a skill documenting the 4-layer validation architecture
4. **SSE streaming with empty response detection**: Create a skill for the SSE event schema + empty response handling pattern

### Domain-Specific (Not Reusable)

1. **MDX chunking pipeline**: Specific to educational content in Docusaurus/MDX format
2. **Module cards content**: The 4 specific modules (ROS 2, Gazebo, Isaac, VLA) are textbook-specific
3. **Futuristic dark theme**: The specific color palette and glassmorphism effects are tied to this project's brand
