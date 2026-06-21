---
name: openai-agents-sdk
argument-hint: "[question or feature]"
description: |
  OpenAI Agents SDK (Python) development with support for agents, multi-agent handoffs, function tools,
  guardrails, sessions, streaming, and tracing via the `openai-agents` Python package — including
  Azure OpenAI through LiteLLM. This skill should be used when building AI agents with the
  openai-agents SDK, implementing multi-agent handoffs, creating function tools, setting up guardrails,
  managing conversation sessions, streaming agent responses, or integrating Azure OpenAI via LiteLLM.
  Triggers on imports from `agents`, `Runner.run_sync`/`Runner.run_streamed`, `@function_tool`,
  `AgentOutputSchema`, `SQLiteSession`, or questions about the openai-agents-python SDK.
---

# OpenAI Agents SDK (Python)

Use this skill when developing AI agents using OpenAI Agents SDK (`openai-agents` package).

## Quick Reference

### Installation

```bash
pip install openai-agents
```

### Environment Variables

```bash
# OpenAI (direct)
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai

# Azure OpenAI (via LiteLLM)
LLM_PROVIDER=azure
AZURE_API_KEY=...
AZURE_API_BASE=https://your-resource.openai.azure.com
AZURE_API_VERSION=2024-12-01-preview
```

### Basic Agent

```python
from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    model="gpt-4o",  # or "gpt-4o-mini", "o4-mini"
)

# Synchronous
result = Runner.run_sync(agent, "Tell me a joke")
print(result.final_output)

# Asynchronous
result = await Runner.run(agent, "Tell me a joke")
```

### Key Patterns

| Pattern | Purpose |
|---------|---------|
| Basic Agent | Simple Q&A with instructions |
| Azure/LiteLLM | Azure OpenAI integration |
| AgentOutputSchema | Strict JSON validation with Pydantic |
| Function Tools | External actions (@function_tool) |
| Streaming | Real-time UI (Runner.run_streamed) |
| Handoffs | Specialized agents, delegation |
| Agents as Tools | Orchestration (agent.as_tool) |
| LLM as Judge | Iterative improvement loop |
| Guardrails | Input/output validation |
| Sessions | Automatic conversation history |
| Multi-Agent Pipeline | Multi-step workflows |
| Sandboxing | Isolated execution environment for agents |
| Subagents | Spawn specialized subordinate agents (Python + TS) |
| Observability | Built-in execution graph recording |

## Required Clarifications

1. **Agent Purpose** — What is the agent supposed to do? (Q&A, tool-use, multi-step workflow, classification)
2. **LLM Provider** — Are you using OpenAI directly or Azure OpenAI via LiteLLM? (affects env vars and setup)
3. **Features Needed** — Which SDK features are required? (basic agent, function tools, handoffs, guardrails, streaming, sessions, structured output)

## Optional Clarifications

4. **Deployment Environment** — Where will this agent run? (serverless, container, long-running service — affects session storage choice)
5. **Observability Requirements** — Do you need tracing/monitoring? (for debugging or production monitoring)
6. **Existing Infrastructure** — Any existing agent framework or tooling this needs to integrate with?

Note: Avoid asking too many questions in a single message. Start with Required, follow up with Optional as needed.

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing project structure, dependencies, Python version, async framework in use |
| **Conversation** | User's specific agent requirements, model preferences, deployment constraints |
| **Skill References** | SDK patterns from `references/` — agent creation, tools, guardrails, sessions, handoffs, streaming |
| **User Guidelines** | Project-specific conventions, API key management, security requirements |

Ensure all required context is gathered before implementing. Only ask user for THEIR specific requirements.

## Preferred: Live Docs via MCP

Model names and API details change frequently. When available, consult the **OpenAI Developer Docs MCP server** (`openaiDeveloperDocs`) before relying on the static references below.

Setup (your CLI tool):
```bash
# Example MCP CLI: your-cli-tool mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp
# Or configure in your editor's MCP settings (see alternative config below)
```

Or config (VS Code `.vscode/mcp.json`, Cursor `~/.cursor/mcp.json`):
```toml
[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
```

Key tools: `mcp__openaiDeveloperDocs__search_openai_docs`, `fetch_openai_doc`, `list_api_endpoints`, `get_openapi_spec`.

**Rules:** Cite fetched docs. Never speculate on field names, defaults, or current model IDs — fetch first. Keep quotes under 125 chars.

Fallback when MCP is unavailable: `https://developers.openai.com/api/docs/llms.txt` (plain-text index of all API docs; each entry has a `.md` twin at `/api/docs/<slug>.md`).

## Reference Documentation

Offline/quick-lookup snippets. Verify model names and API signatures against the MCP or docs when accuracy matters.

- [agents.md](references/agents.md) - Agent creation, Azure/LiteLLM integration
- [tools.md](references/tools.md) - Function tools, hosted tools, agents as tools
- [structured-output.md](references/structured-output.md) - Pydantic output, AgentOutputSchema
- [streaming.md](references/streaming.md) - Streaming patterns, SSE with FastAPI
- [handoffs.md](references/handoffs.md) - Agent delegation
- [guardrails.md](references/guardrails.md) - Input/output validation
- [sessions.md](references/sessions.md) - Sessions, conversation history
- [patterns.md](references/patterns.md) - Multi-agent workflows, LLM as judge, tracing

## Official Documentation

- **Docs:** https://openai.github.io/openai-agents-python/
- **Examples:** https://github.com/openai/openai-agents-python/tree/main/examples
- **Major update:** https://openai.com/index/the-next-evolution-of-the-agents-sdk/
- **Docs MCP setup:** https://developers.openai.com/learn/docs-mcp
- **Docs index (llms.txt):** https://developers.openai.com/api/docs/llms.txt
- **Current model IDs:** https://platform.openai.com/docs/models

## Output Specification

Deliver agents with:

1. **Agent Definition** — Properly configured Agent instance with instructions, model, tools
2. **Tool Implementations** — Function tools or hosted tools as required
3. **Runner Integration** — Sync or async runner usage with proper error handling
4. **Configuration** — Environment variables for LLM provider, model selection
5. **Streaming** (if needed) — Streaming response handling with SSE or async generators
6. **Session Management** (if needed) — Conversation history and persistence configuration
