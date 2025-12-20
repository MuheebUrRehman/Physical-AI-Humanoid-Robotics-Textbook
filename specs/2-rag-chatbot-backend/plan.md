# Implementation Plan: RAG Chatbot Backend with ChatKit Integration for Technical Book Website

**Branch**: `2-rag-chatbot-backend` | **Date**: 2025-12-18 | **Spec**: [link to specs/2-rag-chatbot-backend/spec.md]
**Input**: Feature specification from `/specs/2-rag-chatbot-backend/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of a RAG (Retrieval-Augmented Generation) chatbot backend that integrates with a Docusaurus frontend via ChatKit (https://platform.openai.com/docs/guides/chatkit). The system will use FastAPI (https://fastapi.tiangolo.com/) to expose a chat endpoint, Cohere for query embeddings, Qdrant Cloud for vector similarity search, and OpenAI Agents SDK v0.6 (https://openai.github.io/openai-agents-python/) with Gemini as the LLM to generate responses grounded in book content. The architecture is modular with clear separation of concerns between API routing (app.py), retrieval logic (retrieval.py), and agent processing (agent.py). The implementation will strictly follow the official OpenAI Agents SDK documentation and use only the `openai-agents==0.6` package without any legacy `openai` package dependencies. The backend will ensure strict compliance with ChatKit's API schema and requirements, with ChatKit being the exclusive chat UI component. The frontend will remove any existing chat UI components and integrate ChatKit as a floating widget at the bottom right corner of all web pages, with no custom chat state, rendering, or transport implemented on the frontend.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: FastAPI (https://fastapi.tiangolo.com/), Cohere, Qdrant, OpenAI Agents SDK v0.6 (https://openai.github.io/openai-agents-python/), uv (UV-managed project)
**Storage**: Qdrant Cloud (vector store), .env for secrets at project root
**Testing**: pytest (recommended for FastAPI applications)
**Target Platform**: Linux server (backend service)
**Project Type**: web (backend service for Docusaurus frontend)
**Performance Goals**: <5 second response time for 95% of queries, handle book content retrieval efficiently
**Constraints**: Stateless, single-turn interactions, no runtime ingestion or vector writes, no streaming responses, use `openai-agents==0.6` exclusively, follow official SDK documentation verbatim, do not generate legacy `openai` code or patterns, Gemini API key used by OpenAI Agents SDK
**ChatKit Requirements**: ChatKit MUST be the only chat UI; Frontend must not implement custom chat state, rendering, or transport; Backend responses must strictly follow ChatKit's expected API schema; ChatKit floating widget MUST appear at the bottom right corner of all web pages; ChatKit widget MUST integrate as an overlay/widget only
**Frontend Requirements**: Remove any existing chat UI components currently integrated in the my-website folder
**Documentation**: Use context7 MCP for documentation access during development
**Scale/Scope**: Technical book website with grounded responses based on book content only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Operational Guidelines Compliance:
- Follow Explicit Instructions: Ensure implementation aligns only with explicitly defined requirements
- Consult Primary Sources: Reference user prompts and project files for technical decisions
- Verify Information: Use researched data and verified sources for technical implementations
- Strict Course Alignment: Align with "Physical AI & Humanoid Robotics" course modules
- Academic Reliability: Maintain technical writing with verified robotics sources
- Consistent Terminology: Ensure consistent use of ROS 2, URDF/Xacro, controllers, etc.
- Verified & Precise Citations: Cite official robotics manuals and peer-reviewed papers
- Reproducible & Accurate Examples: Provide clean, reproducible examples
- Factual Integrity: Exclude speculation or untested workflows
- Docusaurus Adherence: Follow official Docusaurus documentation
- Modular Independence: Guarantee chapters can be generated independently

## Project Structure

### Documentation (this feature)

```text
specs/2-rag-chatbot-backend/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
project-root/
├── .env                    # API keys and secrets at project root
├── backend/
│   ├── app.py
│   ├── retrieval.py
│   ├── agent.py
│   ├── config.py
│   ├── models/
│   │   └── chat.py
│   ├── utils/
│   │   └── validation.py
│   └── tests/
│       ├── test_app.py
│       ├── test_retrieval.py
│       └── test_agent.py
```

**Structure Decision**: Web application with dedicated backend service. The backend contains three main modules as specified: app.py for API routing and orchestration, retrieval.py for embeddings and Qdrant search, and agent.py for agent configuration and context injection with guardrails.

## Architecture

### Module Responsibilities

1. **app.py** - API routing and orchestration
   - Exposes POST endpoint for ChatKit integration
   - Extracts query from request and validates input
   - Orchestrates execution flow between modules
   - Handles response formatting to strictly follow ChatKit's expected API schema
   - Ensures backend responses comply with ChatKit requirements
   - Implements error handling and logging

2. **retrieval.py** - Embeddings and Qdrant search
   - Generates query embedding using Cohere API
   - Performs vector similarity search in Qdrant Cloud
   - Extracts text chunks from search result payloads
   - Returns list of relevant book content chunks
   - Handles connection pooling and retries for Qdrant

3. **agent.py** - Agent configuration, context injection, and guardrails
   - Initializes an Agent using `openai-agents` v0.6 following official SDK documentation
   - Injects retrieved chunks into the Agent class `context` property exactly as documented
   - Passes the user query via the documented runner class
   - Applies documented guardrail mechanisms to restrict answers to book content
   - Implements content validation and filtering

### Data Flow

1. ChatKit floating widget (at bottom right corner) sends user query to FastAPI endpoint in app.py (ChatKit is the exclusive UI after removing existing chat UI components)
2. app.py validates input and passes query to retrieval.py
3. retrieval.py:
   - Calls Cohere API to generate query embedding
   - Performs similarity search in Qdrant Cloud
   - Returns top-K relevant book chunks
4. app.py passes retrieved chunks to agent.py
5. agent.py:
   - Initializes agent with Gemini backend
   - Injects book chunks as context
   - Processes user query through agent
   - Applies content guardrails
6. agent.py returns response to app.py
7. app.py formats response to strictly follow ChatKit's expected API schema and returns to client

### Interfaces

- **app.py → retrieval.py**: `get_relevant_chunks(query: str) -> List[str]`
- **app.py → agent.py**: `get_agent_response(query: str, context_chunks: List[str]) -> str`
- **retrieval.py → Cohere API**: Query embedding request
- **retrieval.py → Qdrant Cloud**: Vector similarity search request
- **agent.py → OpenAI Agents SDK**: Agent initialization and query processing

## Implementation Steps

### Phase 1: Project Setup and Configuration

1. **Setup project structure**
   - Create backend directory structure
   - Create config.py for environment variables and settings
   - Create models/chat.py for request/response models
   - Set up myproject.toml with dependencies

2. **Configure environment and dependencies**
   - Define environment variables in .env template
   - Install FastAPI, Cohere, Qdrant, OpenAI Agents SDK
   - Set up UV project management

3. **Create configuration module**
   - Load secrets from .env file at project root
   - Define API keys for Cohere, Qdrant, and Gemini
   - Set up configuration constants (top-K value, timeout settings)

4. **Frontend preparation**
   - Remove any existing chat UI components currently integrated in the my-website folder
   - Prepare for ChatKit floating widget integration at bottom right corner
   - Ensure no custom chat state, rendering, or transport logic is implemented on frontend

### Phase 2: Core Module Implementation

5. **Implement retrieval.py module**
   - Create Cohere embedding client and embedding function
   - Implement Qdrant client setup and similarity search
   - Extract text chunks from Qdrant payloads
   - Add error handling for external API calls
   - Implement retry logic for resilience

6. **Implement agent.py module**
   - Initialize an Agent using `openai-agents` v0.6 as per official documentation
   - Inject retrieved chunks into the Agent class `context` property exactly as documented
   - Pass the user query via the documented runner class
   - Apply documented guardrail mechanisms to restrict answers to book content
   - Add content validation and filtering

7. **Implement app.py module**
   - Create FastAPI application instance
   - Define POST endpoint for ChatKit (ensuring ChatKit is the exclusive UI)
   - Implement request/response validation
   - Integrate retrieval and agent modules
   - Format responses to strictly follow ChatKit's expected API schema
   - Add error handling and logging

### Phase 3: Testing and Validation

8. **Create unit tests**
   - Test retrieval.py functions independently
   - Test agent.py processing logic
   - Test app.py endpoint functionality
   - Mock external API calls for testing

9. **Implement integration tests**
   - Test full RAG flow from query to response
   - Validate guardrail functionality
   - Test error handling scenarios

10. **Performance and security validation**
    - Test response time under load
    - Validate that off-topic queries are properly rejected
    - Ensure no sensitive information is exposed

## Architecture Decisions

### Decision 1: Modular Architecture Pattern
**Context**: Need to separate concerns between API handling, retrieval logic, and agent processing
**Options Considered**:
- Single monolithic file vs. modular approach
- Different module boundaries (e.g., feature-based vs. technical responsibility)
**Chosen Option**: Three-module approach (app.py, retrieval.py, agent.py) with clear responsibilities
**Rationale**: Follows Single Responsibility Principle, improves maintainability, enables independent testing
**Consequences**:
- Positive: Easier to test, maintain, and understand
- Negative: Slightly more complex inter-module communication

### Decision 2: Direct API Integration vs. Abstraction Layer
**Context**: How to integrate with external services (Cohere, Qdrant, OpenAI)
**Options Considered**:
- Direct API calls in business logic vs. abstraction layer
- SDK usage vs. HTTP client implementation
**Chosen Option**: Use official SDKs with minimal abstraction layer
**Rationale**: Leverages maintained libraries, reduces custom code, follows best practices
**Consequences**:
- Positive: Less custom code, better maintained dependencies
- Negative: Tight coupling to specific SDKs, potential vendor lock-in

### Decision 3: Stateless vs. Stateful Interaction
**Context**: Whether to maintain conversation context across requests
**Options Considered**:
- Single-turn interactions vs. multi-turn conversations
- Server-side session storage vs. client-side context passing
**Chosen Option**: Stateless, single-turn interactions as specified
**Rationale**: Matches requirements, simpler implementation, more scalable
**Consequences**:
- Positive: Simpler architecture, easier to scale
- Negative: No conversation history, less contextual responses

## Dependencies & Resources

### Required Libraries
- FastAPI (https://fastapi.tiangolo.com/): Web framework for API creation
- Cohere: For text embeddings
- qdrant-client: For Qdrant Cloud integration
- openai-agents==0.6 (https://openai.github.io/openai-agents-python/): For OpenAI Agents SDK with Gemini (specifically version 0.6)
- python-dotenv: For environment variable management
- pydantic: For request/response validation
- uvicorn: ASGI server for FastAPI

### External Services
- Cohere API: For generating query embeddings
- Qdrant Cloud: Vector similarity search for book content
- Gemini API: Through OpenAI Agents SDK for response generation

### Configuration Requirements
- .env file at project root with API keys for Cohere, Qdrant, and Gemini
- Qdrant Cloud endpoint and collection name
- Cohere embedding model specification
- Top-K retrieval parameter (default: 5)
- Query timeout settings (default: 30 seconds)

### Documentation Resources
- context7 MCP: For documentation access during development
- ChatKit official documentation: https://platform.openai.com/docs/guides/chatkit

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Multiple external dependencies | Required by specification | Specification mandates use of Cohere, Qdrant, and OpenAI Agents SDK |
| Multi-module architecture | Required by specification | Specification defines clear module responsibilities for app.py, retrieval.py, and agent.py |
| Constraint to use openai-agents==0.6 only | Required by specification | Requirement mandates using only openai-agents v0.6 without legacy openai package |
| Frontend changes required | Required by specification | Requirement mandates removing existing chat UI components and integrating ChatKit floating widget |
| Documentation access requirement | Required by specification | Requirement mandates using context7 MCP for documentation access |