---
description: "Task list for RAG Chatbot Backend with ChatKit Integration implementation"
---

# Tasks: RAG Chatbot Backend with ChatKit Integration for Technical Book Website

**Input**: Design documents from `/specs/2-rag-chatbot-backend/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Documentation Resources**: context7 MCP, ChatKit official documentation

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend directory structure in backend/
- [X] T002 [P] Create .env template file at project root with API key placeholders
- [X] T003 Create config.py module for environment variable management in backend/config.py
- [X] T004 Create models/chat.py with request/response models for chat interactions ensuring compatibility with ChatKit's expected API schema
- [X] T005 [P] Create utils/validation.py for input validation utilities
- [X] T006 Setup myproject.toml/pyproject.toml with dependencies: FastAPI, Cohere, qdrant-client, openai-agents==0.6, python-dotenv, pydantic, uvicorn

---
## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Setup FastAPI application structure in backend/app.py
- [X] T008 Configure error handling and logging infrastructure in backend/app.py
- [X] T009 Setup basic API routing structure in backend/app.py ensuring ChatKit compatibility
- [X] T010 [P] Create retrieval.py module with Cohere embedding functionality in backend/retrieval.py
- [X] T011 Create Qdrant client setup and similarity search in backend/retrieval.py
- [X] T012 [P] Create agent.py module with OpenAI Agent initialization using openai-agents==0.6 in backend/agent.py
- [X] T013 Implement context injection into Agent class `context` property exactly as documented in backend/agent.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Ask Book-Related Questions via Floating Chat Widget (Priority: P1) 🎯 MVP

**Goal**: A user can submit book-related questions via the floating chat widget and receive accurate answers grounded in book content.

**Independent Test**: Submit book-related queries via the floating chat widget on any page and verify that the system returns accurate, contextually relevant answers based on the book content.

### Implementation for User Story 1

- [X] T014 [P] [US1] Implement text chunk extraction from Qdrant payloads in backend/retrieval.py
- [X] T015 [US1] Implement query processing through documented runner class in backend/agent.py
- [X] T016 [US1] Integrate retrieval and agent modules in backend/app.py
- [X] T017 [US1] Implement POST chat endpoint compatible with ChatKit in backend/app.py ensuring ChatKit is the exclusive UI and responses follow ChatKit's expected API schema
- [X] T018 [US1] Add request/response validation for chat endpoint in backend/app.py to strictly follow ChatKit's expected API schema
- [X] T019 [P] [US1] Remove any existing chat UI components currently integrated in the my-website folder
- [X] T020 [P] [US1] Integrate ChatKit floating widget at bottom right corner in my-website/src/ (appropriate file)
- [X] T021 [US1] Ensure ChatKit widget integrates as an overlay/widget only, not creating a new page

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Receive Appropriate Response to Off-Topic Queries (Priority: P2)

**Goal**: System appropriately declines to answer queries unrelated to book content and explains the scope limitation.

**Independent Test**: Submit off-topic queries and verify that the system refuses to answer while explaining the scope limitation.

### Implementation for User Story 2

- [X] T022 [P] [US2] Implement content classification logic in backend/agent.py
- [X] T023 [US2] Add documented guardrail mechanisms to restrict answers to book content in backend/agent.py
- [X] T024 [US2] Implement appropriate refusal messages for off-topic queries in backend/agent.py
- [X] T025 [US2] Update chat endpoint to handle off-topic queries in backend/app.py ensuring responses follow ChatKit's expected API schema

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Experience Consistent Chat Performance via Floating Widget (Priority: P3)

**Goal**: System maintains consistent response times and quality across multiple queries via the floating widget.

**Independent Test**: Measure response times and quality across multiple queries submitted via the floating widget on different pages to ensure consistent performance.

### Implementation for User Story 3

- [X] T026 [P] [US3] Implement timeout mechanisms for external API calls in backend/retrieval.py
- [X] T027 [P] [US3] Add retry logic for resilience in backend/retrieval.py
- [X] T028 [US3] Implement error handling for external API failures in backend/retrieval.py
- [X] T029 [US3] Add performance monitoring and metrics in backend/app.py ensuring ChatKit API schema compliance
- [X] T030 [US3] Optimize response time under load in backend/app.py while maintaining ChatKit API schema compliance

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T031 [P] Add comprehensive error handling across all modules ensuring ChatKit compatibility
- [X] T032 Add logging for all major operations across modules with ChatKit API compliance
- [X] T033 [P] Create unit tests for retrieval.py in backend/tests/test_retrieval.py
- [X] T034 [P] Create unit tests for agent.py in backend/tests/test_agent.py
- [X] T035 [P] Create unit tests for app.py in backend/tests/test_app.py
- [X] T036 Documentation updates for the API endpoints ensuring ChatKit schema compliance
- [X] T037 Security hardening and input validation improvements maintaining ChatKit compatibility
- [X] T038 Performance optimization across all components
- [X] T039 Ensure frontend does not implement custom chat state, rendering, or transport logic

---
## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 components
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Builds on US1/US2 components

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---
## Parallel Example: User Story 1

```bash
# Launch all parallel tasks for User Story 1 together:
T014 [P] [US1] Implement text chunk extraction from Qdrant payloads in backend/retrieval.py
T019 [P] [US1] Remove any existing chat UI components currently integrated in the my-website folder
T020 [P] [US1] Integrate ChatKit floating widget at bottom right corner in my-website/src/ (appropriate file)
```

---
## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

### Non-Negotiable Rules Compliance

All implementation must strictly adhere to the following non-negotiable rules:
- ChatKit MUST be the only chat UI (no custom chat components)
- Frontend must not implement custom chat state, rendering, or transport
- Backend responses must strictly follow ChatKit's expected API schema
- Don't change backend if it isn't necessary (only implement required functionality)
- Use context7 MCP for documentation access during development

---
## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence