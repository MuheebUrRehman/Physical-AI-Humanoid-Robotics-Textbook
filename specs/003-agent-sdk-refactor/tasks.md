# Tasks: OpenAI Agents SDK Compliance & Streaming Refactor

**Input**: Design documents from `/specs/003-agent-sdk-refactor/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included as requested in the verification strategy of the implementation plan.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Paths assume the structure `my_project/backend/` as defined in the implementation plan.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Update `my_project/backend/pyproject.toml` dependencies to include `openai-agents>=0.6.3`
- [x] T002 Initialize the new environment using `uv sync` in `my_project/backend/`
- [x] T003 [P] Create the directory structure for new tests in `my_project/backend/tests/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T004 [P] Define `AgentResponse` Pydantic model in `my_project/backend/models/chat.py`
- [x] T005 [P] Implement `ChatRequest` and SSE event schemas in `my_project/backend/models/chat.py`
- [x] T006 Configure `Config` to handle any new timeout or streaming settings in `my_project/backend/config.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Interactive RAG Learning (Priority: P1) 🎯 MVP

**Goal**: Implement E2E streaming and structured output for grounded RAG answers.

**Independent Test**: Verify streaming tokens and final JSON response via `curl` or a test client.

### Tests for User Story 1

- [x] T007 [P] [US1] Create integration test for SSE streaming in `my_project/backend/tests/test_streaming.py`
- [x] T008 [P] [US1] Create unit test for `AgentResponse` schema validation in `my_project/backend/tests/test_agent_v2.py`

### Implementation for User Story 1

- [x] T009 [P] [US1] Apply `AgentOutputSchema(AgentResponse)` to `BookKnowledgeAgent` in `my_project/backend/agent.py`
- [x] T010 [US1] Implement async generator for SSE events in `my_project/backend/app.py`
- [x] T011 [US1] Refactor `/chat` endpoint to use `Runner.run_streamed` and return `StreamingResponse` in `my_project/backend/app.py`
- [x] T012 [US1] Ensure the stream handles both token events and the final validated JSON in `my_project/backend/app.py`

**Checkpoint**: User Story 1 functional - Streaming RAG is live.

---

## Phase 4: User Story 2 - Off-topic Query Prevention (Priority: P2)

**Goal**: Use native SDK guardrails to block off-topic queries.

**Independent Test**: Ask an off-topic question and verify the SDK tripwire triggers and returns an error event.

### Tests for User Story 2

- [x] T013 [P] [US2] Create unit test for the native guardrail function in `my_project/backend/tests/test_agent_v2.py`

### Implementation for User Story 2

- [x] T014 [P] [US2] Implement `@input_guardrail` function `check_query_relevance` in `my_project/backend/agent.py`
- [x] T015 [US2] Register `check_query_relevance` in the `input_guardrails` list of `BookKnowledgeAgent` in `my_project/backend/agent.py`
- [x] T016 [US2] Remove the old manual guardrail logic from the chat workflow in `my_project/backend/app.py`

**Checkpoint**: User Story 2 functional - Off-topic queries are blocked via native SDK logic.

---

## Phase 5: User Story 3 - Personalized Contextual Answers (Priority: P3)

**Goal**: Inject book chunks dynamically using `RunContextWrapper`.

**Independent Test**: Verify that the agent instructions reflect the injected chunks using SDK tracing or log inspection.

### Tests for User Story 3

- [x] T017 [P] [US3] Create test case for dynamic instruction generation in `my_project/backend/tests/test_agent_v2.py`

### Implementation for User Story 3

- [x] T018 [US3] Convert `BookKnowledgeAgent` instructions to a callable that accepts `RunContextWrapper` in `my_project/backend/agent.py`
- [x] T019 [US3] Update the instruction function to pull `book_chunks` from the context in `my_project/backend/agent.py`
- [x] T020 [US3] Pass the retrieved chunks into the `Runner.run_streamed` context parameter in `my_project/backend/app.py`

**Checkpoint**: User Story 3 functional - Context is injected dynamically per request.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T021 [P] Update `my_project/backend/docs/api.md` with the new SSE contract
- [x] T022 [P] Clean up unused imports and old RAG orchestration code in `my_project/backend/app.py`
- [x] T023 Run `quickstart.md` validation using `curl` and `pytest`
- [x] T024 Perform a final check of the TTFT (Time To First Token) to verify SC-001

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Phase 2 - Independent of US1/US3
- **User Story 3 (P3)**: Can start after Phase 2 - Independent of US1/US2

### Parallel Opportunities

- T001, T003 (Phase 1)
- T004, T005 (Phase 2)
- T007, T008, T009 (Phase 3) - Test creation and Schema application
- T013, T014 (Phase 4)
- T017 (Phase 5)
- T021, T022 (Phase 6)

---

## Parallel Example: User Story 1

```bash
# Prepare tests and schema in parallel:
Task: "Create integration test for SSE streaming in my_project/backend/tests/test_streaming.py"
Task: "Create unit test for AgentResponse schema validation in my_project/backend/tests/test_agent_v2.py"
Task: "Apply AgentOutputSchema(AgentResponse) to BookKnowledgeAgent in my_project/backend/agent.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (Defines models)
3. Complete Phase 3: User Story 1 (Enables core streaming)
4. **STOP and VALIDATE**: Verify streaming RAG works.

### Incremental Delivery

1. Foundation ready (Phase 1 & 2)
2. Add Streaming & Grounding (US1) -> MVP Ready
3. Add SDK Guardrails (US2) -> Improved Safety
4. Add Dynamic Context (US3) -> Improved Relevance
5. Polish & Documentation

---

## Notes

- All tasks follow the `- [ ] [TaskID] [P?] [Story?]` format.
- File paths are specific to `my_project/backend/`.
- TTFT (Time To First Token) is the primary performance metric.
