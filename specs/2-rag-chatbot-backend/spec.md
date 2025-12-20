# Feature Specification: RAG Chatbot Backend with ChatKit Integration for Technical Book Website

**Feature Branch**: `2-rag-chatbot-backend`
**Created**: 2025-12-18
**Status**: Draft
**Input**: User description: "Update the specs at /2-rag-chatbot-backend/spec.md and the prompt with this information; follow the instructions carefully, focus on the main goal, use context7 documentation for coding, and avoid changing anything that's working fine or wasn't asked to change.
Hard constraints:
- The chat user interface MUST use the official ChatKit package according to the official docs [https://platform.openai.com/docs/guides/chatkit]
- No custom chat UI components are allowed
- No alternative chat libraries are allowed
- ChatKit is only responsible for UI and message transport
- The ChatKit chatbot will be a floating widget on all web pages
- ChatKit MUST send user messages to a FastAPI POST endpoint, as before
- Use context7 MCP for documentation access
Non-negotiable rules:
- ChatKit MUST be the only chat UI
- The frontend must not implement custom chat state, rendering, or transport
- Backend responses must strictly follow ChatKit's expected API schema
- Do not change the backend unless necessary
ChatKit flow:
- Remove any chat UI currently integrated on the frontend (in the my-website folder)
- Integrate the ChatKit chat UI as a floating widget at the bottom right corner only; do not create a new page. It should receive a FastAPI POST endpoint as before."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask Book-Related Questions via Floating Chat Widget (Priority: P1)

A user visits any page of the technical book website and interacts with the floating chat widget to ask questions about the book content. The system processes the query, retrieves relevant book passages, and generates accurate answers based solely on the book's content.

**Why this priority**: This is the core functionality that delivers value to users seeking information from the book content through an accessible, always-available interface.

**Independent Test**: Can be fully tested by submitting book-related queries via the floating chat widget on any page and verifying that the system returns accurate, contextually relevant answers based on the book content.

**Acceptance Scenarios**:

1. **Given** a user has accessed any page of the book website with an active floating chat widget, **When** the user submits a question about the book content, **Then** the system returns an accurate answer grounded in the book's text.
2. **Given** a user submits a technical question related to the book topic via the floating chat widget, **When** the query is processed by the RAG system, **Then** the response contains information that is directly sourced from the book content.

---

### User Story 2 - Receive Appropriate Response to Off-Topic Queries (Priority: P2)

A user submits a query unrelated to the book content, and the system appropriately declines to answer, directing them to relevant book topics instead.

**Why this priority**: Critical for maintaining the integrity of the book-focused service and preventing misuse.

**Independent Test**: Can be tested by submitting off-topic queries and verifying that the system refuses to answer while explaining the scope limitation.

**Acceptance Scenarios**:

1. **Given** a user submits a query unrelated to the book content, **When** the system detects the off-topic nature, **Then** it responds with an appropriate refusal message explaining the scope.

---

### User Story 3 - Experience Consistent Chat Performance via Floating Widget (Priority: P3)

A user engages in a multi-turn conversation with the floating chat widget, experiencing consistent response times and quality across all website pages.

**Why this priority**: Enhances user experience and engagement with the system through a consistently available interface.

**Independent Test**: Can be tested by measuring response times and quality across multiple queries submitted via the floating widget on different pages.

**Acceptance Scenarios**:

1. **Given** a user is engaged in a conversation via the floating chat widget, **When** they submit follow-up questions on any website page, **Then** the system maintains consistent performance and context awareness.

---

### Edge Cases

- What happens when the vector store is temporarily unavailable?
- How does the system handle extremely long or malformed user queries?
- What occurs when no relevant book content is found for a query?
- How does the system handle simultaneous high-volume traffic?
- What happens when the existing chat UI is removed from the my-website folder?
- How does the system handle ChatKit widget positioning conflicts with existing UI elements?
- What occurs when ChatKit fails to load on certain pages or browsers?
- How does the system ensure backward compatibility during the transition?

## Requirements *(mandatory)*

### Hard Constraints

- **HC-001**: Chat user interface MUST use the official ChatKit package exclusively
- **HC-002**: No custom chat UI components are allowed
- **HC-003**: No alternative chat libraries are allowed
- **HC-004**: ChatKit is responsible only for UI and message transport
- **HC-005**: Chat UI: ChatKit (official package only)

### Functional Requirements

- **FR-001**: System MUST expose a single POST endpoint for chat interactions compatible with ChatKit
- **FR-002**: System MUST embed user queries using Cohere embedding services
- **FR-003**: System MUST retrieve top-K relevant book chunks from Qdrant Cloud vector store
- **FR-004**: System MUST provide retrieved book chunks as context to the OpenAI Agents SDK
- **FR-005**: System MUST pass user queries through the Agent runner to generate responses
- **FR-006**: System MUST generate answers that are grounded only in the book content
- **FR-007**: System MUST enforce guardrails to detect and reject non-book-related queries
- **FR-008**: System MUST load all required secrets from the root-level `.env` file
- **FR-009**: System MUST use Python 3.13 runtime environment
- **FR-010**: System MUST use OpenAI Agents SDK with Gemini as the underlying LLM
- **FR-011**: System MUST use ONLY the official `openai-agents` Python package (version 0.6)
- **FR-012**: System MUST NOT use the legacy `openai` Python package
- **FR-013**: System MUST follow the official `openai-agents` v0.6 documentation for all agent operations
- **FR-014**: System MUST handle errors gracefully and return appropriate error responses to the client
- **FR-015**: System MUST implement timeout mechanisms for external API calls to prevent hanging requests
- **FR-016**: ChatKit chatbot MUST be implemented as a floating widget on all web pages
- **FR-017**: ChatKit MUST send user messages to a FastAPI POST endpoint as specified
- **FR-018**: Frontend MUST remove any existing chat UI components currently integrated in the my-website folder
- **FR-019**: ChatKit floating widget MUST appear at the bottom right corner of all web pages
- **FR-020**: ChatKit widget MUST NOT create a new page but integrate as an overlay/widget only
- **FR-021**: Backend responses MUST strictly follow ChatKit's expected API schema
- **FR-022**: Frontend MUST NOT implement custom chat state, rendering, or transport logic
- **FR-023**: System MUST use context7 MCP for documentation access during development

### Key Entities *(include if feature involves data)*

- **Query**: A user's text input requesting information from the book content, containing text and metadata
- **Embedding**: A numerical representation of the query text for semantic similarity matching
- **Book Chunk**: A segment of book content retrieved from the vector store, containing text and relevance score
- **Response**: The system-generated answer to the user's query, containing text and confidence indicators

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of book-related questions return accurate, grounded answers within 5 seconds
- **SC-002**: 100% of off-topic questions are appropriately declined with a helpful response
- **SC-003**: Users rate the relevance and accuracy of answers with an average satisfaction score of 4.0/5.0
- **SC-004**: System maintains 99% uptime during peak usage hours
- **SC-005**: Response time stays under 5 seconds for 95% of queries even under load