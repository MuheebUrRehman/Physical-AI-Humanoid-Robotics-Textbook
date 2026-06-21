---
name: chatkit-integration
description: Integrates OpenAI ChatKit framework with custom backend and AI agents. This skill should be used when building conversational AI interfaces that need authentication, context injection, conversation persistence, or text selection &quot;Ask&quot; functionality, or when integrating ChatKit with any custom backend, frontend framework, or agent framework.
---

# ChatKit Integration Skill

## Persona

You are a full-stack engineer integrating OpenAI ChatKit framework with a custom backend and AI agents. You understand that ChatKit provides standardized conversation UI/UX, but requires custom integration to work with domain-specific agents and context.

## Required Clarifications

1. **Backend Framework** — What framework is the backend using? (FastAPI, Flask, Express, Next.js API routes, etc.)
2. **Agent Framework** — What agent SDK is being used? (OpenAI Agents SDK, LangChain, custom, or none)
3. **Frontend Framework** — What frontend framework renders the ChatKit widget? (React, Next.js, Docusaurus, Vue, etc.)
4. **Authentication** — How is user authentication handled? (OAuth, JWT, session cookies, Clerk, Auth0, custom)

## Optional Clarifications

5. **Database / Persistence** — What database is used for conversation history? (only if persistence is needed)
6. **Deployment Environment** — Where will this be deployed? (serverless, container, VPS — affects connection pooling strategy)
7. **Custom UI Features** — Does the UI need text selection &quot;Ask&quot; feature, personalization menu, or other custom interactions?

Note: Avoid asking too many questions in a single message. Start with Required questions, follow up with Optional as needed.

## Principles

### Backend Principles

1. **Extend ChatKit Server, Don't Replace**
   - Inherit from `ChatKitServer[RequestContext]`
   - Override only `respond()` method for agent execution
   - Let base class handle read-only operations (threads.list, items.list)
   - **Rationale**: ChatKit handles protocol, you handle agent logic

2. **Context Injection in Prompt**
   - Include conversation history as string in system prompt (CarFixer pattern)
   - Include user context (name, profile) in system prompt
   - Include page context (current page) in system prompt
   - **Rationale**: Agent SDK receives single prompt, history must be in prompt

3. **User Isolation via RequestContext**
   - All operations scoped by `user_id` in `RequestContext`
   - Store operations filter by `user_id` automatically
   - Never expose data across users
   - **Rationale**: Multi-tenant safety, data privacy

4. **Graceful Degradation**
   - System starts even if database unavailable (ChatKit disabled)
   - RAG search can fail without blocking ChatKit
   - Log warnings but don't crash
   - **Rationale**: Partial functionality better than no functionality

5. **Connection Pool Warmup**
   - Pre-warm database connections on startup
   - Avoids 7+ second first-request delay
   - Test connections before use (`pool_pre_ping=True`)
   - **Rationale**: Production-ready performance

### Frontend Principles

1. **Custom Fetch Interceptor**
   - Provide custom `fetch` function to `useChatKit` config
   - Intercept all ChatKit requests
   - Add authentication headers (`X-User-ID`)
   - Add metadata (userInfo, pageContext) to request body
   - **Rationale**: ChatKit doesn't handle auth natively, you must inject it

2. **Script Loading Detection**
   - Check for ChatKit custom element before rendering
   - Listen for script load events
   - Only render ChatKit component when script ready
   - Handle script load failures gracefully
   - **Rationale**: External script required, component fails without it

3. **Page Context Extraction**
   - Extract client-side (DOM, window.location)
   - Include: URL, title, path, headings, meta description
   - Send with every message (in metadata)
   - **Rationale**: Agent needs to know what user is viewing

4. **Build-Time Configuration**
   - Read env vars in `docusaurus.config.ts` (build-time)
   - Add to `customFields` for client-side access
   - Don't use `process.env` in browser code
   - **Rationale**: Static sites bake config at build time

5. **Authentication Gate**
   - Require login before allowing chat access
   - Show login prompt if not authenticated
   - Redirect to OAuth flow
   - **Rationale**: User ID required for conversation persistence

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing backend framework, frontend framework, auth system, database setup, agent SDK |
| **Conversation** | User&#x27;s specific integration requirements, tech stack choices, auth method, persistence needs |
| **Skill References** | ChatKit patterns from this skill — server integration, context injection, fetch interception |
| **User Guidelines** | Project-specific conventions, deployment constraints, security requirements |

Ensure all required context is gathered before implementing. Only ask user for THEIR specific requirements.

## Implementation Patterns

&gt; **Note**: The code examples below are conceptual patterns showing ChatKit integration architecture. Adapt types, imports, and framework-specific details to your project&#x27;s tech stack. The patterns demonstrate the approach, not a copy-paste solution.

### Pattern 1: ChatKit Server with Custom Agent

**When**: Integrating ChatKit with OpenAI Agents SDK

**Implementation**:
```python
from chatkit.server import ChatKitServer
from agents import Agent, Runner
from chatkit.agents import stream_agent_response

class CustomChatKitServer(ChatKitServer[RequestContext]):
    """Extend ChatKit server with custom agent."""
    
    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        # Only handle user messages (let base class handle read-only ops)
        if not input_user_message:
            return
        
        # Load conversation history
        previous_items = await self.store.load_thread_items(
            thread.id, after=None, limit=10, order="desc", context=context
        )
        
        # Build history string for prompt
        history_str = "\n".join([
            f"{item.role}: {item.content}" 
            for item in reversed(previous_items.data)
        ])
        
        # Extract context from metadata
        user_info = context.metadata.get('userInfo', {})
        page_context = context.metadata.get('pageContext', {})
        
        # Build context strings
        user_context_str = f"\nUser: {user_info.get('name')}\n"
        page_context_str = f"\nPage: {page_context.get('title')}\n"
        
        # Create agent with tools
        agent = Agent(
            name="Assistant",
            tools=[agent_tools],  # Replace with your agent&#x27;s tools (e.g., RAG search, API calls, custom functions)
            instructions=f"{history_str}\n{user_context_str}{page_context_str}\n{system_prompt}",
        )
        
        # Convert message to agent input
        converter = ThreadItemConverter()  # Implement your own converter matching your agent&#x27;s input format
        agent_input = await converter.to_agent_input(input_user_message)
        
        # Run agent with streaming
        agent_context = AgentContext(  # Implement your own context class with thread, store, request_context
            thread=thread,
            store=self.store,
            request_context=context,
        )
        result = Runner.run_streamed(agent, agent_input, context=agent_context)
        
        # Stream results
        async for event in stream_agent_response(agent_context, result):
            yield event
```


### Pattern 2: Custom Fetch Interceptor

**When**: Adding authentication and context to ChatKit requests

**Implementation**:
```typescript
const { control, sendUserMessage } = useChatKit({
  api: {
    url: `${backendUrl}/chatkit`,
    domainKey: domainKey,
    
    // Custom fetch to inject auth and context
    fetch: async (url: string, options: RequestInit) => {
      // Check authentication (replace with your auth implementation)
      if (!isLoggedIn) {
        throw new Error('User must be logged in');
      }
      
      const user = getUser(); // Get current user from your auth system
      const userId = user.id;
      const pageContext = getPageContext();
      const userInfo = {
        id: userId,
        name: user.name,
        email: user.email,
        // ... other user fields
      };
      
      // Modify request body to add metadata
      let modifiedOptions = { ...options };
      if (modifiedOptions.body && typeof modifiedOptions.body === 'string') {
        const parsed = JSON.parse(modifiedOptions.body);
        if (parsed.type === 'threads.create' && parsed.params?.input) {
          parsed.params.input.metadata = {
            userId,
            userInfo,
            pageContext,
            ...parsed.params.input.metadata,
          };
          modifiedOptions.body = JSON.stringify(parsed);
        } else if (parsed.type === 'threads.run' && parsed.params?.input) {
          if (!parsed.params.input.metadata) {
            parsed.params.input.metadata = {};
          }
          parsed.params.input.metadata.userInfo = userInfo;
          parsed.params.input.metadata.pageContext = pageContext;
          modifiedOptions.body = JSON.stringify(parsed);
        }
      }
      
      // Add authentication header
      return fetch(url, {
        ...modifiedOptions,
        headers: {
          ...modifiedOptions.headers,
          'X-User-ID': userId,
          'Content-Type': 'application/json',
        },
      });
    },
  },
});
```


### Pattern 3: Script Loading Detection

**When**: ChatKit requires external script, component must wait

**Implementation**:
```typescript
const [scriptStatus, setScriptStatus] = useState<'pending' | 'ready' | 'error'>(
  isBrowser && window.customElements?.get('openai-chatkit') ? 'ready' : 'pending'
);

useEffect(() => {
  if (scriptStatus !== 'pending') return;
  
  // Check if already loaded
  if (window.customElements?.get('openai-chatkit')) {
    setScriptStatus('ready');
    return;
  }
  
  // Listen for script load events
  const handleLoaded = () => setScriptStatus('ready');
  const handleError = () => setScriptStatus('error');
  
  window.addEventListener('chatkit-script-loaded', handleLoaded);
  window.addEventListener('chatkit-script-error', handleError);
  
  // Timeout after 5 seconds
  const timeoutId = setTimeout(() => {
    if (scriptStatus === 'pending') {
      setScriptStatus('error');
    }
  }, 5000);
  
  return () => {
    window.removeEventListener('chatkit-script-loaded', handleLoaded);
    window.removeEventListener('chatkit-script-error', handleError);
    clearTimeout(timeoutId);
  };
}, [scriptStatus]);

// Only render ChatKit when script ready
{isOpen && scriptStatus === 'ready' && (
  <ChatKit control={control} />
)}
```


### Pattern 4: Page Context Extraction

**When**: Agent needs to know what page user is viewing

**Implementation**:
```typescript
const getPageContext = useCallback(() => {
  if (typeof window === 'undefined') return null;
  
  // Extract meta tags
  const metaDescription = document.querySelector('meta[name="description"]')
    ?.getAttribute('content') || '';
  
  // Find main content
  const mainContent = document.querySelector('article') || 
                     document.querySelector('main') || 
                     document.body;
  
  // Extract headings
  const headings = Array.from(mainContent.querySelectorAll('h1, h2, h3'))
    .slice(0, 5)
    .map(h => h.textContent?.trim())
    .filter(Boolean)
    .join(', ');
  
  return {
    url: window.location.href,
    title: document.title,
    path: window.location.pathname,
    description: metaDescription,
    headings: headings,
    timestamp: new Date().toISOString(),
  };
}, []);
```


### Pattern 5: Text Selection "Ask" Feature

**When**: Users want to ask questions about selected content

**Implementation**:
```typescript
// Detect text selection
useEffect(() => {
  const handleSelection = () => {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) {
      setSelectedText('');
      setSelectionPosition(null);
      return;
    }
    
    const selectedText = selection.toString().trim();
    if (selectedText.length > 0) {
      setSelectedText(selectedText);
      
      // Get selection position
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      setSelectionPosition({
        x: rect.left + rect.width / 2,
        y: rect.top - 10,
      });
    }
  };
  
  document.addEventListener('selectionchange', handleSelection);
  document.addEventListener('mouseup', handleSelection);
  
  return () => {
    document.removeEventListener('selectionchange', handleSelection);
    document.removeEventListener('mouseup', handleSelection);
  };
}, []);

// Send selected text
const handleAskSelectedText = useCallback(async () => {
  const pageContext = getPageContext();
  const messageText = `Can you explain this from "${pageContext.title}":\n\n"${selectedText}"`;
  
  if (!isOpen) {
    setIsOpen(true);
    await new Promise(resolve => setTimeout(resolve, 300));
  }
  
  await sendUserMessage({
    text: messageText,
    newThread: false,
  });
  
  // Clear selection
  window.getSelection()?.removeAllRanges();
  setSelectedText('');
  setSelectionPosition(null);
}, [selectedText, isOpen, sendUserMessage, getPageContext]);
```


## When to Apply

- Integrating ChatKit with custom backend
- Adding authentication to ChatKit
- Injecting context (user, page) into agent prompts
- Implementing text selection "Ask" functionality
- Building conversational AI interfaces

## Contraindications

- **Simple chat without persistence**: ChatKit may be overkill
- **No user authentication**: ChatKit requires user_id for isolation
- **Serverless functions**: Connection pooling doesn't work well
- **Very low traffic**: Overhead not justified

## Common Pitfalls

1. **History Not in Prompt**: Agent doesn't remember conversation
   - **Fix**: Include history as string in system prompt (not as messages)

2. **Context Not Transmitted**: Agent doesn't receive user/page context
   - **Fix**: Add to request metadata, extract in backend, include in prompt

3. **Script Not Loaded**: ChatKit component fails to render
   - **Fix**: Detect script loading, wait before rendering

4. **Auth Headers Missing**: Backend rejects requests
   - **Fix**: Use custom fetch interceptor to add headers

5. **Database Not Warmed**: First request takes 7+ seconds
   - **Fix**: Pre-warm connection pool on startup

## Output Specification

When implementing ChatKit integration, deliver:

1. **Backend Server** — ChatKit-compatible server with:
   - Custom `respond()` method that handles agent execution
   - Context injection (user info, page context) into agent prompts
   - Graceful degradation when services are unavailable
   - Connection pool warmup for production performance

2. **Frontend Widget** — ChatKit component with:
   - Custom fetch interceptor for auth headers and context injection
   - Script loading detection
   - Page context extraction
   - Authentication gate

3. **Configuration** — Environment variables for:
   - Backend URL, domain key, auth tokens
   - Database connection strings
   - API keys for agent services

## References

- **OpenAI ChatKit Documentation**: https://github.com/openai/chatkit
- **ChatKit Server API**: Official ChatKit server package docs
- **OpenAI Agents SDK**: https://openai.github.io/openai-agents-python/


