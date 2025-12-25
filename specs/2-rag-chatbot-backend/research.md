# Research: RAG Chatbot Backend with Input Guardrails and Context Management

## Decision: Input Guardrail Agent Implementation
**Context**: Need to implement an Input Guardrail agent that triggers when a user asks something not relevant to book content

**Research**: The OpenAI Agents SDK allows for creating specialized agents that can process input before the main agent processes the request. This can be implemented by creating a guardrail agent that evaluates the query relevance before passing it to the BookKnowledgeAgent.

**Rationale**: This approach provides a clean separation of concerns where the guardrail agent handles query validation and the main agent focuses on content generation.

**Alternatives considered**:
- Integrating guardrails directly into the main agent: Less modular and harder to maintain
- Using a simple function call: Doesn't leverage the agent framework as required

**Consequences**:
- Positive: Better separation of concerns, more maintainable code
- Negative: Slightly more complex architecture with additional agent

## Decision: Context Management Using OpenAI Agents SDK
**Context**: Need to implement context (book chunks) using context management in the OpenAI Agents SDK

**Research**: The OpenAI Agents SDK v0.6 provides context management features that allow creating context classes and passing them to the runner.run method via the context property. This is the proper way to manage context instead of embedding it directly in the user message.

**Rationale**: Using the official SDK context management ensures compatibility with the framework and follows best practices as specified in the requirements.

**Alternatives considered**:
- Embedding context directly in the user message: Doesn't use the proper SDK features
- Custom context management: Would not follow the official documentation

**Consequences**:
- Positive: Proper use of SDK features, maintainable code
- Negative: Requires understanding of SDK-specific context management patterns

## Decision: Removal of Hard-Coded Restriction Lists
**Context**: Need to remove hard-coded lists that restrict user input to book-related content

**Research**: The current implementation uses hard-coded lists like BOOK_TOPICS, off_topic_indicators, and technical_indicators. These should be replaced with more sophisticated content analysis approaches that don't rely on predefined keyword lists.

**Rationale**: Removing hard-coded lists makes the system more flexible and less prone to false positives/negatives based on keyword matching.

**Alternatives considered**:
- Keeping the lists but expanding them: Still relies on keyword matching which is limiting
- Using ML-based classification: More complex but potentially more accurate

**Consequences**:
- Positive: More flexible content evaluation
- Negative: May require more sophisticated content analysis techniques

## OpenAI Agents SDK Context Management Implementation
**Key Findings**:
- The SDK supports context classes that can be passed to the runner
- Context management allows for better separation of conversation history, tools, and other contextual information
- The runner.run method accepts a context parameter for proper context handling
- This replaces the current approach of embedding context directly in messages

## Input Guardrail Agent Pattern
**Key Findings**:
- Guardrail agents can be implemented as a preprocessing step
- The guardrail agent should return early if content is off-topic
- Proper logging and metrics should be implemented for guardrail decisions
- Error handling should be robust to prevent bypassing the guardrails