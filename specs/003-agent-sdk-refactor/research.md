# Research: OpenAI Agents SDK Compliance & Streaming Refactor

This document consolidates research findings and technical decisions for the backend refactor.

## Decision 1: Streaming Implementation with FastAPI
- **Choice**: Use `Runner.run_streamed` with a custom async generator yielding Server-Sent Events (SSE).
- **Rationale**: `Runner.run_streamed` provides real-time token access. SSE is natively supported by FastAPI's `StreamingResponse` and is easy to consume on the frontend.
- **Alternatives Considered**: 
    - WebSockets: Overkill for one-way AI streaming.
    - Long Polling: Poor performance for real-time tokens.

## Decision 2: Native Guardrail Pattern
- **Choice**: Implement `@input_guardrail` as an async function returning `GuardrailFunctionOutput`.
- **Rationale**: This is the documented standard in SDK v0.6. It allows the `Runner` to handle exceptions and tripwires automatically, providing better observability in the execution graph.
- **Alternatives Considered**: Manual pre-check (current implementation) - rejected because it's non-standard and less observable.

## Decision 3: Structured Output Schema
- **Choice**: `AgentOutputSchema` wrapping a Pydantic `AgentResponse` model.
- **Rationale**: Ensures the agent's output is always valid JSON. This simplifies frontend logic and enables SC-002 (100% schema compliance).
- **Alternatives Considered**: Raw text with manual regex parsing - rejected as fragile and error-prone.

## Decision 4: Dynamic Instructions for Context Injection
- **Choice**: Define `Agent.instructions` as a callable: `def instructions(ctx: RunContextWrapper, agent: Agent) -> str`.
- **Rationale**: Allows the agent to receive the most relevant book chunks exactly when needed, without pre-filling the entire conversation history. This follows the "Context Injection" pattern in the SDK.
- **Alternatives Considered**: Passing chunks in the user message - rejected as it mixes user input with system context.

## Decision 5: SSE Event Format
- **Choice**: `data: { "token": "..." }` for intermediate chunks and `data: { "final": { ... } }` for the structured result.
- **Rationale**: Provides a clear distinction between raw streaming text and the final structured object. Compatible with `@openai/chatkit-react` expectations if transitioned later.
