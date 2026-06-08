# API Contract: Chat Endpoint for ChatKit Integration

## Overview
This document defines the API contract for the chat endpoint that integrates with ChatKit. The endpoint accepts user queries, processes them through the RAG system, and returns responses that comply with ChatKit's expected schema.

## Base URL
`/api/chat` (mounted under the main application)

## Endpoint: Process Chat Message

### Request
**Method**: `POST`
**Path**: `/api/chat`
**Content-Type**: `application/json`

#### Request Body
```json
{
  "message": {
    "content": "string - The user's query message",
    "id": "string - Unique message ID from ChatKit",
    "createdAt": "ISO 8601 timestamp - When the message was created"
  },
  "sessionId": "string - Session identifier (optional)",
  "userId": "string - User identifier (optional)"
}
```

#### Example Request
```json
{
  "message": {
    "content": "What are the key principles of embodied AI?",
    "id": "msg-12345",
    "createdAt": "2025-12-23T10:00:00Z"
  },
  "sessionId": "session-67890",
  "userId": "user-abcde"
}
```

### Responses

#### Success Response (200 OK)
```json
{
  "id": "string - Unique response ID",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "string - The assistant's response"
      },
      "finish_reason": "string - Reason the generation stopped (e.g., 'stop')"
    }
  ],
  "created": "integer - Unix timestamp of when the response was created",
  "model": "string - Model identifier used",
  "object": "string - Type of response object",
  "usage": {
    "prompt_tokens": "integer - Number of tokens in the prompt",
    "completion_tokens": "integer - Number of tokens in the completion",
    "total_tokens": "integer - Total number of tokens used"
  }
}
```

#### Example Success Response
```json
{
  "id": "resp-67890",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Embodied AI refers to artificial intelligence systems that interact with the physical world through sensors and actuators. Key principles include sensorimotor learning, environmental interaction, and adaptive behavior based on physical feedback."
      },
      "finish_reason": "stop"
    }
  ],
  "created": 1703325600,
  "model": "gemini-3.5-flash",
  "object": "chat.completion",
  "usage": {
    "prompt_tokens": 120,
    "completion_tokens": 85,
    "total_tokens": 205
  }
}
```

#### Error Response (400 Bad Request)
```json
{
  "error": {
    "type": "string - Type of error",
    "message": "string - Human-readable error message",
    "code": "string - Error code"
  }
}
```

#### Example Error Response
```json
{
  "error": {
    "type": "invalid_request_error",
    "message": "Query is not related to book content. Please ask a question about physical AI, humanoid robotics, or related topics.",
    "code": "off_topic_query"
  }
}
```

### Error Response (500 Internal Server Error)
```json
{
  "error": {
    "type": "server_error",
    "message": "An internal server error occurred",
    "code": "internal_error"
  }
}
```

## Security
- All requests must include proper authentication if required by the deployment
- Input validation must be performed on all request fields
- Rate limiting should be implemented to prevent abuse

## Performance Requirements
- Response time should be under 5 seconds for 95% of requests
- The system should handle up to 100 concurrent requests
- Timeouts should be implemented for external API calls (30 seconds default)

## Validation
- Request body must be valid JSON
- Message content must not exceed 1000 characters
- Message content must not be empty
- The system must validate that the query is related to book content before processing

## Implementation Notes
- The endpoint must strictly follow ChatKit's expected API schema
- Responses must be compatible with ChatKit's client-side processing
- Error handling should be consistent and informative
- The system must implement proper logging for debugging and monitoring