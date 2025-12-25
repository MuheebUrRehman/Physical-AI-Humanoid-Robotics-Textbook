# OpenAI ChatKit Integration Plan

## 1. Overview

This plan outlines the implementation of OpenAI ChatKit into the existing Docusaurus-based website. The goal is to replace the current custom FloatingChat component with the official `@openai/chatkit-react` package, creating a floating chat widget that appears on every page of the website and connects to the existing FastAPI backend.

## 2. Current State Analysis

### 2.1 Existing Implementation
- Current chat component: `FloatingChat.tsx` (custom implementation)
- Backend: FastAPI with `/chat`, `/api/chatkit/session`, and `/api/chatkit/refresh` endpoints
- Frontend: React-based Docusaurus site
- Dependencies: `@openai/chatkit-react` already installed (v1.4.0)

### 2.2 Architecture
- Frontend: Docusaurus React application
- Backend: FastAPI server with RAG functionality
- API endpoints already exist for ChatKit session management

## 3. Implementation Approach

### 3.1 Component Replacement Strategy
1. Create a new ChatKit-based floating chat component
2. Replace the existing FloatingChat component
3. Maintain the floating UI pattern while using ChatKit's UI components
4. Ensure compatibility with existing backend API

### 3.2 Integration Points
- Use existing `/api/chatkit/session` endpoint for session creation
- Use existing `/api/chatkit/refresh` endpoint for session refresh
- Connect to existing `/chat` endpoint for message processing
- Maintain existing proxy configuration in docusaurus.config.ts

## 4. React Component Structure

### 4.1 New ChatKit Component
Create `src/components/ChatKitWidget.tsx` with the following structure:

```typescript
import React, { useState } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import clsx from 'clsx';
import styles from './ChatKitWidget.module.css';

export interface ChatKitWidgetProps {
  initialOpen?: boolean;
}

const ChatKitWidget: React.FC<ChatKitWidgetProps> = ({ initialOpen = false }) => {
  const [isOpen, setIsOpen] = useState(initialOpen);

  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        if (existing) {
          // Refresh expired token
          const res = await fetch('/api/chatkit/refresh', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
          });
          const { client_secret } = await res.json();
          return client_secret;
        }

        // Create new session
        const res = await fetch('/api/chatkit/session', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        const { client_secret } = await res.json();
        return client_secret;
      },
    },
    // Optional: Add theme configuration to match existing styling
    theme: {
      colorScheme: 'light', // or 'dark' based on site theme
    },
  });

  return (
    <div className={clsx(styles.chatkitContainer, !isOpen && styles.minimized)}>
      {isOpen ? (
        <div className={styles.chatkitWidget}>
          <div className={styles.chatkitHeader}>
            <h3>AI Assistant</h3>
            <button
              className={styles.closeButton}
              onClick={() => setIsOpen(false)}
              aria-label="Close chat"
            >
              ×
            </button>
          </div>
          <div className={styles.chatkitBody}>
            <ChatKit
              control={control}
              className={styles.chatkitComponent}
            />
          </div>
        </div>
      ) : (
        <button
          className={styles.floatingButton}
          onClick={() => setIsOpen(true)}
          aria-label="Open chat"
        >
          🤖
        </button>
      )}
    </div>
  );
};

export default ChatKitWidget;
```

### 4.2 CSS Styling
Create `src/components/ChatKitWidget.module.css` with styles to maintain the floating chat appearance:

```css
.chatkitContainer {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  font-family: inherit;
}

.minimized {
  display: flex;
  align-items: center;
  justify-content: center;
}

.chatkitWidget {
  width: 380px;
  height: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  background: white;
}

.chatkitHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.chatkitHeader h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.closeButton {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.closeButton:hover {
  background-color: #e9ecef;
}

.chatkitBody {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chatkitComponent {
  flex: 1;
  height: 100%;
  width: 100%;
}

.floatingButton {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #007bff;
  color: white;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.floatingButton:hover {
  transform: scale(1.05);
  background-color: #0056b3;
}
```

## 5. Backend Integration

### 5.1 FastAPI Endpoints
The existing backend endpoints need to be enhanced to properly support ChatKit frontend requirements:
- `/api/chatkit/session` - Creates ChatKit sessions with proper client secrets
- `/api/chatkit/refresh` - Refreshes ChatKit sessions with valid tokens
- `/api/chatkit/user` - Provides user information for ChatKit frontend
- `/chat` - Processes chat messages with RAG functionality

### 5.2 Session Management
The session endpoints need to be updated to return valid credentials that the ChatKit frontend can use:
- Generate proper client_secret that follows ChatKit protocol expectations
- Implement thread management for conversation continuity
- Ensure session tokens are compatible with ChatKit frontend requirements
- Maintain compatibility with the RAG system

### 5.3 Message Flow Integration
Since ChatKit expects a specific message handling pattern but our backend uses a different approach, we need to create a bridge:
- Implement message routing between ChatKit frontend and our `/chat` endpoint
- Handle message format conversion between ChatKit format and our RAG system
- Ensure real-time message delivery works properly
- Maintain conversation context between sessions

### 5.4 Backend Modifications Required
The existing endpoints need significant updates to work with the ChatKit frontend:

```python
# Enhanced session endpoint with proper ChatKit compatibility
@app.post("/api/chatkit/session", response_model=ChatKitSessionResponse)
async def create_chatkit_session(request: ChatKitSessionRequest):
    """
    Create a ChatKit session with proper client secret format.
    This endpoint creates a session that the ChatKit frontend can use
    while maintaining integration with our RAG system.
    """
    import uuid
    # Generate a client secret that follows ChatKit expectations
    client_secret = f"chatkit_{uuid.uuid4().hex}"

    # Create or retrieve user information
    user_id = f"user_{uuid.uuid4().hex[:8]}"

    # Return session information with default thread
    return ChatKitSessionResponse(
        client_secret=client_secret,
        thread_id="default_rag_thread"  # Use consistent thread for RAG interactions
    )

# Enhanced refresh endpoint
@app.post("/api/chatkit/refresh", response_model=ChatKitSessionResponse)
async def refresh_chatkit_session():
    """
    Refresh ChatKit session with new valid credentials.
    """
    import uuid
    client_secret = f"chatkit_{uuid.uuid4().hex}"

    return ChatKitSessionResponse(
        client_secret=client_secret,
        thread_id="default_rag_thread"
    )

# Add user endpoint for ChatKit frontend
@app.get("/api/chatkit/user")
async def get_chatkit_user():
    """
    Return user information that ChatKit frontend expects.
    """
    return {
        "id": "default_user",
        "name": "AI Assistant User",
        "avatar_url": None,
        "custom_data": {}
    }
```

### 5.5 Chat Message Processing Bridge
To connect the ChatKit frontend with our existing RAG system, implement a message processing bridge:

```python
# Enhanced chat endpoint that can work with ChatKit message format
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, response: Response):
    """
    Main chat endpoint that processes requests from ChatKit frontend.
    This endpoint maintains compatibility with our existing RAG functionality
    while working with the ChatKit frontend's message format expectations.
    """
    start_time = time.time()

    try:
        # Validate the request from ChatKit frontend
        from utils.validation import validate_query, validate_user_id, validate_session_id

        is_valid, error_msg = validate_query(request.query)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Process the query using existing RAG functionality
        # Retrieve relevant chunks from vector store
        retrieval_start = time.time()
        logger.info(f"Retrieving relevant chunks for query: {request.query[:50]}...")
        relevant_chunks = await get_relevant_chunks(request.query)
        retrieval_time = time.time() - retrieval_start

        # Generate response using the agent
        agent_start = time.time()
        logger.info("Generating response with agent...")
        response_text = await get_agent_response(request.query, relevant_chunks)
        agent_time = time.time() - agent_start

        # Determine confidence based on response content
        is_off_topic = "only answer questions related to the technical book content" in response_text.lower()
        confidence = 0.3 if is_off_topic else 0.8

        total_time = time.time() - start_time
        logger.info(f"Request completed in {total_time:.2f}s (retrieval: {retrieval_time:.2f}s, agent: {agent_time:.2f}s)")

        # Add performance metrics to response headers
        response.headers["X-Response-Time"] = f"{total_time:.3f}"
        response.headers["X-Retrieval-Time"] = f"{retrieval_time:.3f}"
        response.headers["X-Agent-Time"] = f"{agent_time:.3f}"
        response.headers["X-Total-Time"] = f"{total_time:.3f}"

        return ChatResponse(
            response=response_text,
            source_chunks=relevant_chunks if not is_off_topic else [],
            confidence=confidence
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"Error in chat endpoint after {total_time:.2f}s: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )
```

## 6. Docusaurus Integration

### 6.1 Root Component Integration
To make the chat widget appear on every page, we'll integrate it into the Docusaurus root component:

1. Create a plugin or modify the Root component in Docusaurus
2. Add the ChatKitWidget to the root layout so it appears on all pages

### 6.2 Plugin Approach
Create a Docusaurus plugin in `src/plugins/ChatKitPlugin`:

```typescript
// src/plugins/ChatKitPlugin/index.js
import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';

const ChatKitWidget = React.lazy(() => import('../../components/ChatKitWidget'));

export default function ChatKitPlugin() {
  return (
    <BrowserOnly fallback={<></>}>
      {() => <ChatKitWidget />}
    </BrowserOnly>
  );
}
```

Then add this plugin to the docusaurus.config.ts:

```typescript
// In the plugins array of docusaurus.config.ts
plugins: [
  // ... existing plugins
  async function myPlugin(context, options) {
    return {
      name: 'chatkit-plugin',
      async loadContent() {
        // nothing to load
      },
      async contentLoaded({content, actions}) {
        const {setGlobalData} = actions;
        setGlobalData({hasChatkit: true});
      },
      configureWebpack(config, isServer) {
        // Add any webpack configuration if needed
      }
    };
  },
  // ... rest of plugins
],
```

Alternatively, we can add it directly to the Root export in a file like `src/pages/Root.tsx`:

```typescript
// src/pages/Root.tsx
import React from 'react';
import ChatKitWidget from '../components/ChatKitWidget';

export default function Root({children}) {
  return (
    <>
      {children}
      <ChatKitWidget />
    </>
  );
}
```

## 7. Testing Strategy

### 7.1 Frontend Testing
- Test the ChatKit component rendering in isolation
- Verify the floating UI behavior (open/close functionality)
- Test session creation and refresh functionality with updated endpoints
- Verify message sending and receiving through the ChatKit bridge

### 7.2 Backend Connectivity Testing
- Test the `/api/chatkit/session` endpoint with proper client secret generation
- Test the `/api/chatkit/refresh` endpoint with valid token renewal
- Test the new `/api/chatkit/user` endpoint for user information
- Verify the `/chat` endpoint still works with the new frontend integration
- Test error handling for failed API calls
- Validate session token compatibility with ChatKit frontend

### 7.3 Integration Testing
- Test end-to-end chat functionality from ChatKit UI to backend RAG system
- Verify session management works correctly with the new backend implementation
- Test the message processing bridge between ChatKit and RAG system
- Test the widget appears on all pages as expected
- Test compatibility with different screen sizes
- Validate thread management and conversation continuity

### 7.4 Specific Test Cases
1. Session creation: Verify a new session is created with valid client secret when the chat is opened
2. Session refresh: Test token refresh with new valid credentials when existing token is provided
3. User endpoint: Verify the user endpoint returns proper information for ChatKit frontend
4. Message flow: Send a message through ChatKit and verify it goes to RAG backend and returns
5. Thread management: Test conversation continuity using the default thread
6. Error handling: Test behavior when API calls fail or return invalid responses
7. UI behavior: Verify the floating widget opens/closes correctly with ChatKit integration
8. Format compatibility: Test that message formats are properly handled between systems

## 8. Implementation Steps

### Phase 1: Setup and Component Creation
1. Create the new ChatKitWidget component with the structure outlined above
2. Create appropriate CSS modules for styling
3. Test the component in isolation

### Phase 2: Backend Integration
1. Update `/api/chatkit/session` endpoint with proper client secret generation
2. Update `/api/chatkit/refresh` endpoint with valid token renewal
3. Create new `/api/chatkit/user` endpoint for user information
4. Verify message processing bridge between ChatKit and RAG system
5. Test API connectivity end-to-end with updated endpoints

### Phase 3: Docusaurus Integration
1. Integrate the component into the Docusaurus root
2. Ensure it appears on all pages
3. Test the integration across different page types

### Phase 4: Testing and Validation
1. Perform comprehensive testing of all functionality
2. Validate that existing features still work
3. Verify performance and accessibility
4. Test ChatKit-specific functionality and compatibility

## 9. Risks and Mitigation

### 9.1 Risks
- OpenAI ChatKit may require different backend structure than current implementation
- Styling may not match existing design without customization
- Session management might not work as expected with existing endpoints
- Performance issues with the new component

### 9.2 Mitigation Strategies
- Thoroughly test backend compatibility before full implementation
- Configure theme options to match existing styling
- Have fallback plan to use custom session management if needed
- Monitor performance metrics during testing

## 10. Success Criteria

- [ ] ChatKit widget appears as a floating element on all pages
- [ ] Widget opens and closes with proper UI behavior
- [ ] Session creation works with valid client secrets from updated endpoint
- [ ] Session refresh works with valid token renewal
- [ ] User endpoint returns proper information for ChatKit frontend
- [ ] Messages are sent through ChatKit frontend and processed by RAG backend
- [ ] Message processing bridge correctly handles format conversion
- [ ] Thread management maintains conversation continuity
- [ ] Existing RAG functionality is preserved and enhanced
- [ ] All existing features continue to work
- [ ] Performance is equal to or better than current implementation
- [ ] Accessibility standards are maintained
- [ ] ChatKit frontend successfully connects to backend endpoints