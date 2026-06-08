# Feature Specification: RAG Performance & Frontend Robustness Refactor

**Feature Branch**: `004-rag-performance-robustness`  
**Created**: June 8, 2026  
**Status**: Draft  
**Input**: User description: "Refactor the backend retrieval and frontend streaming layers to improve concurrency, reduce latency, and ensure stream stability. Include guardrail latency optimization using gemini-3.1-flash-lite, non-blocking async retrieval, and robust SSE event parsing."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stable Real-time Chat (Priority: P1)

As a student, I want to see the AI response stream perfectly word-by-word even on unreliable network connections, so that I don't see technical JSON errors mid-conversation.

**Why this priority**: Stability is the foundation of user trust. Currently, fragmented network packets can break the JSON parser, leading to a complete failure of the chat interface.

**Independent Test**: Can be tested by simulating network fragmentation (e.g., using Chrome DevTools "Slow 3G" or "Custom" throttling) and verifying that the chat remains functional without "Unexpected token" errors.

**Acceptance Scenarios**:

1. **Given** a user is receiving a streaming response, **When** network packets are fragmented or delayed, **Then** the UI MUST wait for complete SSE events and display them correctly without error.
2. **Given** an incoming stream of data, **When** a partial JSON chunk is received, **Then** the system MUST buffer it until the complete event is available.

---

### User Story 2 - High-Concurrency Textbook Retrieval (Priority: P2)

As a student, I want my questions to be answered quickly even when many other students are using the system simultaneously, so that the textbook feels responsive at all times.

**Why this priority**: Scaling. Synchronous retrieval blocks the entire server loop, meaning one slow vector search can freeze the experience for all other active users.

**Independent Test**: Can be tested by initiating multiple concurrent chat requests and verifying that they process in parallel without blocking each other.

**Acceptance Scenarios**:

1. **Given** multiple simultaneous users, **When** they ask questions at the same time, **Then** the backend MUST handle retrievals asynchronously without causing queueing delays for other users.

---

### User Story 3 - Instant Query Validation (Priority: P3)

As a student, I want my questions to be validated for relevance instantly, so that the AI feels like it's thinking about my specific question rather than setting up its own system.

**Why this priority**: User experience/Latency. Re-initializing the "judge" agent on every request adds unnecessary overhead (hundreds of milliseconds) before the actual answer generation starts.

**Independent Test**: Can be tested by measuring the time from "Send" to the first token appearing (TTFT) and verifying a significant reduction compared to the previous implementation.

**Acceptance Scenarios**:

1. **Given** a new user query, **When** it is sent to the guardrail, **Then** the system MUST use a pre-initialized (singleton) judge agent to validate the query instantly.

---

### Edge Cases

- What happens if the network connection is dropped entirely during a buffered SSE stream?
- How does the system handle extremely large vector chunks that might exceed default async timeouts?
- What happens if the `gemini-3.1-flash-lite` model for the guardrail is temporarily rate-limited?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement a frontend SSE buffer that only parses data upon detecting the standard `\n\n` event delimiter.
- **FR-002**: System MUST transition all backend retrieval logic (Cohere & Qdrant) to non-blocking asynchronous clients.
- **FR-003**: System MUST use a singleton pattern for the `judge_agent` to eliminate per-request initialization latency.
- **FR-004**: System MUST use the `gemini-3.1-flash-lite` model for guardrail checks to minimize cost and maximize speed.
- **FR-005**: System MUST maintain the existing `gemini-3.5-flash` model for the primary knowledge agent.
- **FR-006**: System MUST ensure that all async operations include appropriate timeout and retry mechanisms.

### Key Entities *(include if feature involves data)*

- **SSEBuffer**: A client-side data structure that accumulates raw string chunks until a valid SSE event frame is complete.
- **AsyncRetrievalPipeline**: A backend workflow where embedding generation and vector search run in non-blocking tasks.
- **GlobalJudgeAgent**: A singleton instance of the guardrail agent configured with the lightweight model.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero "Unexpected token" errors recorded during 100 simulated fragmented network runs.
- **SC-002**: Backend can handle at least 5x more concurrent retrieval requests without an increase in average response time compared to the synchronous implementation.
- **SC-003**: Time to First Token (TTFT) for relevance validation is reduced by at least 200ms.
- **SC-004**: Guardrail API costs are reduced by switching to the `flash-lite` model for classification tasks.
