# Tasks: RAG Performance & Frontend Robustness Refactor

**Input**: Design documents from `/specs/004-rag-performance-robustness/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Performance benchmark and stability tests are included to verify measurable outcomes.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Paths assume the structure `my_project/` as defined in the implementation plan.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 [P] Ensure `httpx` and `pytest-asyncio` are available in `my_project/backend/pyproject.toml`
- [x] T002 Update environment using `uv sync` in `my_project/backend/`
- [x] T003 [P] Create performance test file `my_project/backend/tests/test_performance.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T004 [P] Update `my_project/backend/config.py` to include `GEMINI_31_LITE_MODEL` setting
- [x] T005 [P] Implement `SSEBuffer` logic container or utility in `my_project/frontend/src/components/FloatingChat.tsx` (prepare the buffer variable)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Stable Real-time Chat (Priority: P1) 🎯 MVP

**Goal**: Implement a robust frontend SSE buffer to handle fragmented packets and prevent JSON errors.

**Independent Test**: Simulate fragmented SSE chunks in a local test script or via manual network throttling and verify no parsing errors.

### Implementation for User Story 1

- [x] T006 [US1] Refactor `handleSubmit` stream reader in `my_project/frontend/src/components/FloatingChat.tsx` to use a string buffer
- [x] T007 [US1] Implement chunk accumulation and `\n\n` delimiter detection in `my_project/frontend/src/components/FloatingChat.tsx`
- [x] T008 [US1] Update parsing logic to only process complete event frames from the buffer in `my_project/frontend/src/components/FloatingChat.tsx`
- [x] T009 [US1] Add buffer reset logic after successful event processing in `my_project/frontend/src/components/FloatingChat.tsx`

**Checkpoint**: User Story 1 functional - Chat is stable against network fragmentation.

---

## Phase 4: User Story 2 - High-Concurrency Textbook Retrieval (Priority: P2)

**Goal**: Transition retrieval to non-blocking async clients to improve system scaling.

**Independent Test**: Run `test_performance.py` to verify that concurrent requests don't block each other.

### Implementation for User Story 2

- [x] T010 [P] [US2] Update `my_project/backend/retrieval.py` imports to use `AsyncClient` and `AsyncQdrantClient`
- [x] T011 [US2] Refactor `embed_query` in `my_project/backend/retrieval.py` to be fully asynchronous
- [x] T012 [US2] Refactor `get_relevant_chunks` in `my_project/backend/retrieval.py` to use `await` for all search operations
- [x] T013 [US2] Ensure error handling and retries in `my_project/backend/retrieval.py` use `asyncio.sleep`
- [x] T014 [US2] Verify `my_project/backend/app.py` properly awaits `get_relevant_chunks` calls

**Checkpoint**: User Story 2 functional - Retrieval is non-blocking.

---

## Phase 5: User Story 3 - Instant Query Validation (Priority: P3)

**Goal**: Optimize guardrail latency by switching to a singleton judge agent and a lighter model.

**Independent Test**: Measure TTFT for relevance validation and verify >200ms reduction.

### Implementation for User Story 3

- [x] T015 [P] [US3] Move `judge_agent` initialization to the module level in `my_project/backend/agent.py`
- [x] T016 [P] [US3] Update `judge_agent` model to `gemini-3.1-flash-lite` in `my_project/backend/agent.py`
- [x] T017 [US3] Refactor `check_query_relevance` guardrail to use the global `judge_agent` instance in `my_project/backend/agent.py`

**Checkpoint**: User Story 3 functional - Guardrail overhead is eliminated.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and documentation

- [x] T018 [P] Update `my_project/backend/docs/api.md` with async retrieval notes
- [x] T019 Run full test suite: `uv run pytest my_project/backend/tests/`
- [x] T020 Validate `quickstart.md` performance benchmarks
- [x] T021 Perform manual "Slow 3G" network verification in Docusaurus chat

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Phase 1 completion
- **User Stories (Phase 3+)**: All depend on Phase 2 completion
  - US1 (Frontend) can proceed independently of US2/US3 (Backend)
- **Polish (Phase 6)**: Depends on all stories being complete

### Parallel Opportunities

- T001, T003 (Phase 1)
- T004, T005 (Phase 2)
- US1 (Frontend) and US2/US3 (Backend) can run in parallel
- T010, T015, T016 (Implementation starts)
- T018 (Documentation)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2
2. Implement Phase 3 (US1) - This fixes the immediate crashing bugs
3. **VALIDATE**: Ensure "Unexpected token" errors are gone

### Incremental Delivery

1. Foundation ready
2. Add Robust Buffering (US1) -> Stability MVP
3. Add Async Retrieval (US2) -> Scalability Upgrade
4. Add Singleton Guardrail (US3) -> Latency Optimization
5. Final Polish

---

## Notes

- All tasks follow the required format.
- Focus on `\n\n` as the reliable delimiter for SSE events.
- Singleton pattern in Python achieved via module-level object creation.
