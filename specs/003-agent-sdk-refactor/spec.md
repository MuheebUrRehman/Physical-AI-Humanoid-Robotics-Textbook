# Feature Specification: OpenAI Agents SDK Compliance & Streaming Refactor

**Feature Branch**: `003-agent-sdk-refactor`  
**Created**: June 8, 2026  
**Status**: Draft  
**Input**: User description: "Refactor the AI orchestration layer in my_project/backend/agent.py and app.py to align with native OpenAI Agents SDK (v0.6.x) patterns including Native Input Guardrails, Structured Output Schema, Dynamic Context Injection, and Streaming Integration."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Interactive RAG Learning (Priority: P1)

As a student reading the textbook, I want to ask questions and see the answer appear as it's being generated (streaming) so I don't have to wait for the entire response to load, and I want to be confident that the answer is strictly based on the book content.

**Why this priority**: Streaming significantly improves the perceived performance and user experience. Grounding the answer in the book is the core value proposition of the RAG system.

**Independent Test**: Can be tested by asking a question in the chat and observing tokens arriving one by one, followed by a final verified JSON structure containing citations.

**Acceptance Scenarios**:

1. **Given** the user is on a chapter page, **When** they ask a technical question about the content, **Then** they see the response streaming in real-time.
2. **Given** a generated response, **When** the response is complete, **Then** it must include a confidence score and a list of citations from the book.

---

### User Story 2 - Off-topic Query Prevention (Priority: P2)

As a project maintainer, I want the AI to strictly ignore non-technical or off-topic questions using native SDK guardrails so that the system remains a dedicated educational tool.

**Why this priority**: Ensures the AI doesn't hallucinate or provide information outside its intended scope, protecting the integrity of the educational content.

**Independent Test**: Can be tested by asking "How to bake a cake" and verifying the SDK tripwire is triggered, resulting in a polite refusal.

**Acceptance Scenarios**:

1. **Given** an off-topic query, **When** the system processes it, **Then** the native input guardrail MUST trigger and block the generation.
2. **Given** a blocked query, **When** the guardrail triggers, **Then** the user receives a standardized message explaining why the query was not processed.

---

### User Story 3 - Personalized Contextual Answers (Priority: P3)

As a student, I want the AI to use the specific context of the chapter I am currently reading to provide more relevant answers.

**Why this priority**: Enhances the relevance of the RAG system by focusing the AI's attention on the immediate learning context.

**Independent Test**: Can be tested by asking "What is the key takeaway here?" while on different chapters and verifying the response changes based on the chapter chunks injected.

**Acceptance Scenarios**:

1. **Given** a user on Module 1, **When** they ask a question, **Then** the system MUST pull relevant chunks for Module 1 and inject them dynamically into the prompt.

---

### Edge Cases

- What happens when the streaming connection is interrupted mid-response?
- How does the system handle queries where no relevant chunks are found in the vector database?
- What happens if the agent generates a response that fails the structured JSON validation?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST use native `@input_guardrail` to validate query relevance before processing.
- **FR-002**: System MUST return structured JSON responses containing `answer`, `confidence`, and `citations`.
- **FR-003**: System MUST inject book chunks into the agent's instructions dynamically via `RunContextWrapper`.
- **FR-004**: System MUST support Server-Sent Events (SSE) for streaming agent responses to the frontend.
- **FR-005**: System MUST maintain compatibility with the existing Qdrant-based retrieval logic.
- **FR-006**: System MUST ensure that the stream correctly handles both the structured output tokens and the final JSON validation.

### Key Entities *(include if feature involves data)*

- **AgentResponse**: Structured output containing the AI's answer, a confidence score (0-1), and a list of source citations.
- **RunContext**: Dynamic execution context containing `book_chunks` retrieved from the vector store.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Perceived latency (time to first token) is reduced by at least 50% compared to non-streaming responses.
- **SC-002**: 100% of responses follow the defined JSON schema with confidence scores and citations.
- **SC-003**: Off-topic queries are blocked with a success rate of at least 95% using native guardrails.
- **SC-004**: System successfully parses and formats 100% of retrieved chunks into the dynamic system prompt without truncation issues.
