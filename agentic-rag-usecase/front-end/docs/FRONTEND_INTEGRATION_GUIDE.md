# Front-End Integration Guide
## Agentic RAG REST API - Client Application Development

**Target Stack**: React + Node.js v22 + Express  
**Architecture**: Express serves React build, React calls API directly  
**Purpose**: Technical specification for building a web application that consumes the Agentic RAG API

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Endpoints Specification](#api-endpoints-specification)
4. [Feature Implementation Patterns](#feature-implementation-patterns)
5. [Data Models](#data-models)
6. [Error Handling](#error-handling)
7. [CORS Configuration](#cors-configuration)
8. [State Management Considerations](#state-management-considerations)
9. [Performance Optimization](#performance-optimization)
10. [Security Considerations](#security-considerations)
11. [Testing Recommendations](#testing-recommendations)

---

## Overview

### What This Guide Covers

This guide provides **technical specifications** and **integration patterns** for building a React web application that interfaces with the Agentic RAG REST API. It focuses on:

- ✅ API endpoint specifications
- ✅ Request/response formats
- ✅ Integration patterns
- ✅ Architecture recommendations
- ✅ Best practices

This guide does **NOT** include:

- ❌ HTML/CSS/JavaScript code (handled by your front-end team)
- ❌ UI/UX design specifications
- ❌ Component implementations

### Backend API Capabilities

The Agentic RAG API provides:

- **Multi-Tool Agent**: Access to 11+ tools (Wikipedia, ArXiv, DuckDuckGo, CRM database, SQL analytics, FAISS RAG)
- **Synchronous Chat**: Traditional request/response pattern
- **Streaming Chat**: Real-time Server-Sent Events (SSE) for live agent reasoning
- **Tool Visibility**: See which tools the agent uses during reasoning
- **Health Monitoring**: Multi-component health checks
- **Conversation History**: Maintain context across multiple messages

### Backend Server Details

- **Base URL**: `http://localhost:9080` (development)
- **Protocol**: HTTP/HTTPS
- **Content-Type**: `application/json` (requests), `text/event-stream` (streaming)
- **Authentication**: None (development), configure for production
- **Rate Limiting**: Configurable (60/min, 1000/hour default)

---

## Architecture

### Recommended Front-End Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Browser                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              React Application                         │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐      │   │
│  │  │   Chat     │  │ Streaming  │  │  Health    │      │   │
│  │  │ Component  │  │   Chat     │  │ Dashboard  │      │   │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘      │   │
│  │        │               │               │              │   │
│  │        └───────────────┴───────────────┘              │   │
│  │                        │                              │   │
│  │                ┌───────▼────────┐                     │   │
│  │                │  API Service   │                     │   │
│  │                │  Layer (fetch) │                     │   │
│  │                └───────┬────────┘                     │   │
│  └────────────────────────┼──────────────────────────────┘   │
└─────────────────────────────┼────────────────────────────────┘
                              │
                    HTTP/HTTPS │ (Direct API Calls)
                              │
┌─────────────────────────────▼────────────────────────────────┐
│                   Agentic RAG REST API                        │
│                   http://localhost:9080                       │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐            │
│  │ /chat  │  │/stream │  │/health │  │ /tools │            │
│  └────────┘  └────────┘  └────────┘  └────────┘            │
└───────────────────────────────────────────────────────────────┘
```

### Express Server Role

**Purpose**: Serve the production React build (static files)

```
Express Server (Port 3000)
├── Serves index.html, bundle.js, assets
├── Handles client-side routing (SPA)
└── React app makes direct API calls to backend (port 9080)
```

**Key Points**:
- Express does **NOT** proxy API requests
- React app communicates **directly** with backend API
- CORS must be configured on backend to allow frontend origin
- No server-side rendering (CSR only)

### Project Structure (Recommended)

```
front-end/
├── public/
│   └── index.html
├── src/
│   ├── services/
│   │   ├── api.js              # API client wrapper
│   │   ├── chatService.js      # Chat endpoint handlers
│   │   ├── streamingService.js # SSE streaming handlers
│   │   └── healthService.js    # Health check handlers
│   ├── components/
│   │   ├── Chat/               # Chat interface components
│   │   ├── StreamingChat/      # Streaming chat components
│   │   ├── ToolVisualization/  # Tool usage display
│   │   └── HealthDashboard/    # Health monitoring
│   ├── hooks/
│   │   ├── useChat.js          # Chat state management
│   │   ├── useStreamingChat.js # SSE streaming hook
│   │   └── useHealth.js        # Health monitoring hook
│   ├── utils/
│   │   ├── errorHandler.js     # Error handling utilities
│   │   └── eventParser.js      # SSE event parser
│   └── App.js
├── server.js                    # Express server (serves build)
├── package.json
└── docs/
    └── FRONTEND_INTEGRATION_GUIDE.md  # This file
```

---

## API Endpoints Specification

### Base Configuration

```
API_BASE_URL: http://localhost:9080
HEADERS:
  Content-Type: application/json
  Accept: application/json
```

---

### 1. POST /chat - Synchronous Chat

**Purpose**: Send a message to the agent and receive the complete response after processing.

**Endpoint**: `POST http://localhost:9080/chat`

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "message": "string (required) - User's message to the agent",
  "conversation_history": [
    {
      "role": "string (user|assistant) - Speaker role",
      "content": "string - Message content"
    }
  ]
}
```

**Request Body Validation**:
- `message`: Required, non-empty string
- `conversation_history`: Optional array, defaults to `[]`
- Each history item must have `role` (user|assistant) and `content`

**Example Request**:
```json
{
  "message": "How many active customers do we have?",
  "conversation_history": []
}
```

**Success Response** (200 OK):
```json
{
  "response": "string - Agent's complete response",
  "conversation_history": [
    {
      "role": "user",
      "content": "How many active customers do we have?"
    },
    {
      "role": "assistant",
      "content": "Based on the CRM database, you currently have 25 active customers."
    }
  ],
  "timestamp": "string - ISO 8601 timestamp (e.g., 2026-02-13T10:30:00Z)"
}
```

**Error Responses**:

- **422 Unprocessable Entity** - Validation error
  ```json
  {
    "error": "ValidationError",
    "detail": "Request validation failed",
    "status_code": 422,
    "validation_errors": [
      {
        "field": "message",
        "message": "field required",
        "type": "value_error.missing"
      }
    ]
  }
  ```

- **500 Internal Server Error** - Agent processing failed
  ```json
  {
    "error": "Exception",
    "detail": "Internal server error occurred",
    "status_code": 500,
    "path": "/chat"
  }
  ```

**Integration Pattern**:

1. **Send Request**: POST to `/chat` with message and conversation history
2. **Wait**: This is a blocking call - agent processes completely before responding
3. **Parse Response**: Extract `response` field for agent's answer
4. **Update History**: Use returned `conversation_history` for next request
5. **Handle Errors**: Check for 422 (validation) or 500 (processing) errors

**Expected Response Time**: 2-10 seconds (depends on tool usage and LLM processing)

**Use Cases**:
- Simple question-answer interactions
- When you don't need real-time feedback
- Mobile apps or slower networks
- Showing "thinking..." loader until response arrives

---

### 2. POST /chat-stream - Streaming Chat (SSE)

**Purpose**: Send a message and receive real-time streaming updates as the agent processes.

**Endpoint**: `POST http://localhost:9080/chat-stream`

**Request Headers**:
```
Content-Type: application/json
Accept: text/event-stream
```

**Request Body**: (Same as `/chat`)
```json
{
  "message": "string (required) - User's message",
  "conversation_history": [
    {
      "role": "string (user|assistant)",
      "content": "string"
    }
  ]
}
```

**Response Type**: `text/event-stream` (Server-Sent Events)

**SSE Event Stream Format**:

The response is a continuous stream of events in SSE format:

```
data: {"type": "agent", "content": {...}}

data: {"type": "tool", "content": {...}}

data: {"type": "end", "content": {...}}

```

**Event Types**:

1. **Agent Messages** (`type: "agent"`):
   ```json
   {
     "type": "agent",
     "content": {
       "messages": [
         {
           "type": "ai",
           "content": "Let me search the CRM database for you..."
         }
       ]
     },
     "timestamp": "2026-02-13T10:30:01Z"
   }
   ```

2. **Tool Usage** (`type: "tool"`):
   ```json
   {
     "type": "tool",
     "content": {
       "tool": "crm_count_active_customers",
       "input": {},
       "output": "25"
     },
     "timestamp": "2026-02-13T10:30:02Z"
   }
   ```

3. **Final Response** (`type: "end"`):
   ```json
   {
     "type": "end",
     "content": {
       "response": "You currently have 25 active customers.",
       "conversation_history": [...]
     },
     "timestamp": "2026-02-13T10:30:05Z"
   }
   ```

4. **Error Event** (`type: "error"`):
   ```json
   {
     "type": "error",
     "content": {
       "error": "Agent processing failed",
       "detail": "Tool execution error"
     },
     "timestamp": "2026-02-13T10:30:03Z"
   }
   ```

**SSE Connection Lifecycle**:

```
1. POST Request → Connection Opened
2. Stream Events:
   - Agent thinking messages
   - Tool usage notifications
   - Intermediate results
3. Final Event (type: "end")
4. Connection Closed
```

**Integration Pattern**:

1. **Open SSE Connection**: Use EventSource or fetch with stream reader
2. **Parse Events**: Each line starting with `data:` contains a JSON event
3. **Handle Event Types**:
   - `agent`: Display agent's intermediate thoughts
   - `tool`: Show which tool is being used
   - `end`: Final response, close connection
   - `error`: Display error, close connection
4. **Build UI Updates**: Update UI in real-time as events arrive
5. **Close Connection**: After receiving `end` or `error` event

**Example Event Sequence**:

```
# Event 1 - Agent starts
data: {"type":"agent","content":{"messages":[{"type":"ai","content":"I'll check the CRM database"}]},"timestamp":"2026-02-13T10:30:00Z"}

# Event 2 - Tool usage
data: {"type":"tool","content":{"tool":"crm_count_active_customers","input":{},"output":"25"},"timestamp":"2026-02-13T10:30:01Z"}

# Event 3 - Agent processes result
data: {"type":"agent","content":{"messages":[{"type":"ai","content":"Based on the database query..."}]},"timestamp":"2026-02-13T10:30:02Z"}

# Event 4 - Final response
data: {"type":"end","content":{"response":"You have 25 active customers.","conversation_history":[...]},"timestamp":"2026-02-13T10:30:03Z"}

```

**Error Handling**:

- **Connection Errors**: Network issues, timeout
- **Parse Errors**: Malformed JSON in `data:` field
- **Event Errors**: `type: "error"` event received
- **Timeout**: No events for extended period (implement client-side timeout)

**Use Cases**:
- Real-time chat interfaces
- Showing agent's "thought process"
- Tool usage visualization
- Better UX for long-running queries (SQL, multi-tool searches)

**Browser Compatibility**:
- EventSource API: Supported in all modern browsers
- Fallback: Use fetch with ReadableStream for more control

---

### 3. GET /health - Health Check

**Purpose**: Check the operational status of all backend components.

**Endpoint**: `GET http://localhost:9080/health`

**Request Headers**: None required

**Query Parameters**: None

**Success Response** (200 OK) - All Healthy:
```json
{
  "status": "healthy",
  "components": {
    "agent_service": {
      "status": "healthy",
      "message": "Agent service is initialized and ready"
    },
    "database": {
      "status": "healthy",
      "message": "Database connection is active"
    },
    "faiss_service": {
      "status": "healthy",
      "message": "FAISS vector store is initialized"
    }
  },
  "timestamp": "2026-02-13T10:30:00Z"
}
```

**Degraded Response** (503 Service Unavailable) - Partial Failure:
```json
{
  "status": "unhealthy",
  "components": {
    "agent_service": {
      "status": "unhealthy",
      "message": "Agent service not initialized"
    },
    "database": {
      "status": "healthy",
      "message": "Database connection is active"
    },
    "faiss_service": {
      "status": "unhealthy",
      "message": "FAISS service not initialized (optional)"
    }
  },
  "timestamp": "2026-02-13T10:30:00Z"
}
```

**Component Status Values**:
- `"healthy"`: Component is operational
- `"unhealthy"`: Component is not working
- `"degraded"`: Component is working but with issues (not currently used)

**Overall Status Logic**:
- `"healthy"`: All critical components are healthy (agent_service + database)
- `"unhealthy"`: Any critical component is unhealthy
- **Note**: FAISS is optional - its failure doesn't mark overall status as unhealthy

**Integration Pattern**:

1. **Periodic Polling**:
   - Call `/health` every 30-60 seconds
   - Update UI indicator (green/red/yellow)
   - Alert user if status changes to unhealthy

2. **On Application Load**:
   - Check health before enabling chat features
   - Show maintenance message if unhealthy

3. **Before Critical Operations**:
   - Verify health before sending important requests
   - Provide user feedback if backend is down

**Use Cases**:
- Health status indicator in UI header/footer
- Health dashboard page showing component details
- Automated monitoring/alerting
- Pre-flight checks before user actions

**Recommended Polling Interval**: 30-60 seconds (avoid excessive requests)

---

### 4. GET /tools - List Available Tools

**Purpose**: Retrieve the list of all tools available to the agent.

**Endpoint**: `GET http://localhost:9080/tools`

**Request Headers**: None required

**Query Parameters**: None

**Success Response** (200 OK):
```json
{
  "tools": [
    {
      "name": "wikipedia",
      "description": "Search Wikipedia for information on a topic. Use this for general knowledge, historical facts, and encyclopedic information."
    },
    {
      "name": "arxiv",
      "description": "Search ArXiv for academic papers and research. Use this for scientific, mathematical, and technical research topics."
    },
    {
      "name": "duckduckgo_search",
      "description": "Search the web using DuckDuckGo. Use this for current events, recent information, and general web searches."
    },
    {
      "name": "crm_get_customer_by_id",
      "description": "Retrieve customer information by ID from the CRM database."
    },
    {
      "name": "crm_get_customer_by_email",
      "description": "Retrieve customer information by email address from the CRM database."
    },
    {
      "name": "crm_search_customers",
      "description": "Search for customers by name or company in the CRM database."
    },
    {
      "name": "crm_get_active_customers",
      "description": "Get a list of all active customers from the CRM database."
    },
    {
      "name": "crm_count_active_customers",
      "description": "Count the number of active customers in the CRM database."
    },
    {
      "name": "query_music_database",
      "description": "Query the Chinook music database using natural language. Use this for questions about tracks, albums, artists, genres, customers, invoices, and sales data."
    },
    {
      "name": "langsmith_search",
      "description": "Search LangSmith documentation for information about tracing, monitoring, and debugging LLM applications."
    }
  ],
  "count": 10,
  "timestamp": "2026-02-13T10:30:00Z"
}
```

**Error Response** (503 Service Unavailable):
```json
{
  "error": "ServiceUnavailable",
  "detail": "Agent service not initialized",
  "status_code": 503
}
```

**Tool Categories**:

1. **Search Tools** (3):
   - `wikipedia`: General knowledge
   - `arxiv`: Academic research
   - `duckduckgo_search`: Web search

2. **CRM Tools** (5):
   - `crm_get_customer_by_id`: Fetch by ID
   - `crm_get_customer_by_email`: Fetch by email
   - `crm_search_customers`: Search by name/company
   - `crm_get_active_customers`: List all active
   - `crm_count_active_customers`: Count active

3. **Database Tools** (1):
   - `query_music_database`: Natural language SQL queries

4. **RAG Tools** (1):
   - `langsmith_search`: Vector search documentation

**Integration Pattern**:

1. **Load on Application Start**:
   - Fetch tools list when app initializes
   - Cache in application state/context

2. **Display in UI**:
   - Show available tools in help/info section
   - Create tool category tabs
   - Provide tool descriptions to users

3. **Tool Visualization**:
   - When agent uses a tool (from streaming events)
   - Highlight that tool in UI
   - Show tool name and description

**Use Cases**:
- "Available Tools" page or modal
- Tool usage statistics (track which tools are used most)
- User education (what can the agent do?)
- Dynamic UI updates when backend tools change

---

## Feature Implementation Patterns

### Feature 1: Chat Interface with Conversation History

**Goal**: Implement a traditional chat interface where users can send messages and receive responses while maintaining conversation context.

#### Data Flow

```
User Input
    ↓
[Validate Message]
    ↓
[Build Request with History]
    ↓
POST /chat
    ↓
[Show Loading State]
    ↓
[Receive Response]
    ↓
[Update Conversation History]
    ↓
[Display Response]
```

#### Request/Response Pattern

**Initial Message** (No history):
```
REQUEST:
{
  "message": "What is LangChain?",
  "conversation_history": []
}

RESPONSE:
{
  "response": "LangChain is a framework for developing applications powered by language models...",
  "conversation_history": [
    {
      "role": "user",
      "content": "What is LangChain?"
    },
    {
      "role": "assistant",
      "content": "LangChain is a framework for developing applications powered by language models..."
    }
  ],
  "timestamp": "2026-02-13T10:30:00Z"
}
```

**Follow-up Message** (With history):
```
REQUEST:
{
  "message": "How do I use it?",
  "conversation_history": [
    {
      "role": "user",
      "content": "What is LangChain?"
    },
    {
      "role": "assistant",
      "content": "LangChain is a framework for developing applications powered by language models..."
    }
  ]
}

RESPONSE:
{
  "response": "To use LangChain, you first need to install it via pip...",
  "conversation_history": [
    {
      "role": "user",
      "content": "What is LangChain?"
    },
    {
      "role": "assistant",
      "content": "LangChain is a framework for developing applications powered by language models..."
    },
    {
      "role": "user",
      "content": "How do I use it?"
    },
    {
      "role": "assistant",
      "content": "To use LangChain, you first need to install it via pip..."
    }
  ],
  "timestamp": "2026-02-13T10:30:05Z"
}
```

#### State Management

**Conversation State**:
```javascript
{
  conversationHistory: [
    { role: "user", content: "..." },
    { role: "assistant", content: "..." }
  ],
  isLoading: false,
  error: null,
  currentMessage: ""
}
```

**State Update Flow**:
1. User types message → update `currentMessage`
2. User sends → set `isLoading: true`, clear `currentMessage`
3. Response received → append to `conversationHistory`, set `isLoading: false`
4. Error occurred → set `error`, set `isLoading: false`

#### Key Considerations

1. **History Management**:
   - Always send the **full conversation history** from the response
   - Don't manually construct history (use what backend returns)
   - History can grow large - consider implementing pagination or truncation

2. **Loading States**:
   - Show "thinking..." or loading indicator when `isLoading: true`
   - Disable send button during loading
   - Show typing indicator for better UX

3. **Error Handling**:
   - Display validation errors (422) clearly to user
   - Show user-friendly message for 500 errors
   - Provide retry mechanism

4. **Message Validation**:
   - Trim whitespace from user input
   - Prevent empty messages
   - Consider max length (10,000 characters recommended)

5. **Conversation Reset**:
   - Provide "New Conversation" button
   - Clear `conversationHistory` array
   - Confirm before clearing if history exists

---

### Feature 2: Real-Time Streaming Chat (SSE)

**Goal**: Implement a streaming chat interface that shows the agent's reasoning process and tool usage in real-time.

#### Server-Sent Events (SSE) Basics

**What is SSE?**
- One-way communication from server to client
- Built on HTTP (no WebSocket needed)
- Automatic reconnection
- Text-based protocol

**SSE Format**:
```
data: <JSON payload>

data: <JSON payload>

```
- Each event starts with `data:`
- Events separated by double newline (`\n\n`)
- Payload is typically JSON

#### Integration Pattern

**Connection Flow**:
```
1. POST /chat-stream (with message)
2. Server opens SSE stream
3. Client receives events in real-time:
   - Agent messages
   - Tool usage
   - Results
4. Stream ends with "end" or "error" event
5. Connection closes
```

**Event Types to Handle**:

1. **Agent Thinking** (`type: "agent"`):
   - Agent's intermediate thoughts
   - Reasoning steps
   - Display as chat bubbles in real-time

2. **Tool Usage** (`type: "tool"`):
   - Tool name, input, output
   - Show "Using Wikipedia..." notification
   - Display tool results when available

3. **Final Response** (`type: "end"`):
   - Complete answer
   - Updated conversation history
   - Close connection

4. **Errors** (`type: "error"`):
   - Error message and details
   - Close connection
   - Show error to user

#### Example Event Sequence

**User asks**: "How many tracks are in the database?"

```
Event 1 (Agent):
data: {"type":"agent","content":{"messages":[{"type":"ai","content":"I'll query the music database to find the total number of tracks."}]},"timestamp":"2026-02-13T10:30:00Z"}

Event 2 (Tool):
data: {"type":"tool","content":{"tool":"query_music_database","input":"How many tracks are in the database?","output":"There are 3,503 tracks."},"timestamp":"2026-02-13T10:30:02Z"}

Event 3 (Agent):
data: {"type":"agent","content":{"messages":[{"type":"ai","content":"Based on the database query, I can provide you with the answer."}]},"timestamp":"2026-02-13T10:30:03Z"}

Event 4 (End):
data: {"type":"end","content":{"response":"The database contains 3,503 tracks.","conversation_history":[...]},"timestamp":"2026-02-13T10:30:04Z"}

```

#### UI Update Pattern

**Real-Time Updates**:

1. **Agent Messages**:
   - Append each agent message as it arrives
   - Show as "thinking" bubbles
   - Can update existing bubble or create new ones

2. **Tool Notifications**:
   - Show "🔧 Using query_music_database..." badge
   - Display tool output when available
   - Remove notification when tool completes

3. **Final Response**:
   - Replace all intermediate messages with final response
   - OR keep intermediate messages for transparency
   - Update conversation history

**Example State Updates**:

```javascript
// Initial state
{
  messages: [],
  activeTools: [],
  isStreaming: true
}

// After Event 1 (Agent)
{
  messages: [
    { type: "agent", content: "I'll query the music database..." }
  ],
  activeTools: [],
  isStreaming: true
}

// After Event 2 (Tool)
{
  messages: [
    { type: "agent", content: "I'll query the music database..." }
  ],
  activeTools: [
    { name: "query_music_database", status: "running" }
  ],
  isStreaming: true
}

// After Event 4 (End)
{
  messages: [
    { type: "user", content: "How many tracks..." },
    { type: "assistant", content: "The database contains 3,503 tracks." }
  ],
  activeTools: [],
  isStreaming: false
}
```

#### Key Considerations

1. **Connection Management**:
   - Open connection only when needed
   - Close connection after "end" or "error" event
   - Handle network disconnections gracefully
   - Implement timeout (e.g., 60 seconds of no events)

2. **Event Parsing**:
   - Each SSE message starts with "data:"
   - Parse JSON from the data field
   - Handle malformed JSON gracefully

3. **Memory Management**:
   - Limit number of intermediate messages stored
   - Clear old tool notifications
   - Consider message history size

4. **Error Handling**:
   - Network errors (connection lost)
   - Parse errors (invalid JSON)
   - Application errors (error event)
   - Timeout errors (no events for too long)

5. **UX Enhancements**:
   - Smooth scrolling to latest message
   - Typing indicators during streaming
   - Tool usage animations
   - "Stop" button to cancel stream

#### Fallback Strategy

If SSE is not supported or fails:
- Fall back to synchronous `/chat` endpoint
- Show "Loading..." instead of streaming updates
- Same final result, just without real-time updates

---

### Feature 3: Tool Usage Visualization

**Goal**: Display which tools the agent uses during processing, providing transparency into the agent's decision-making.

#### Data Source

**From Streaming Events** (`/chat-stream`):
```json
{
  "type": "tool",
  "content": {
    "tool": "crm_count_active_customers",
    "input": {},
    "output": "25"
  },
  "timestamp": "2026-02-13T10:30:02Z"
}
```

**Tool Information** (from `/tools`):
```json
{
  "name": "crm_count_active_customers",
  "description": "Count the number of active customers in the CRM database."
}
```

#### Visualization Patterns

**Pattern 1: Tool Timeline**
- Show tools used in chronological order
- Display tool name, input, output, and timestamp
- Indicate which tool is currently running

**Pattern 2: Tool Badges**
- Show small badges/pills for each tool used
- Color-code by tool category (search, database, RAG)
- Click to expand and see details

**Pattern 3: Tool Flow Diagram**
- Visual representation of tool usage flow
- Show dependencies between tools
- Highlight active tool

**Pattern 4: Expandable Details**
- Collapsed: Just tool name
- Expanded: Input parameters and output results

#### Data Structure for Tracking

```javascript
{
  toolsUsed: [
    {
      name: "wikipedia",
      description: "Search Wikipedia...",
      input: "LangChain framework",
      output: "LangChain is...",
      timestamp: "2026-02-13T10:30:01Z",
      status: "completed"  // "pending" | "running" | "completed" | "error"
    },
    {
      name: "crm_search_customers",
      description: "Search for customers...",
      input: { "query": "Acme Corp" },
      output: "[{...}]",
      timestamp: "2026-02-13T10:30:03Z",
      status: "running"
    }
  ]
}
```

#### Integration Pattern

1. **Load Tools on Startup**:
   - Fetch from `/tools` endpoint
   - Store in application state
   - Use for displaying tool descriptions

2. **Track Tool Usage from Stream**:
   - Listen for `type: "tool"` events
   - Extract tool name, input, output
   - Add to `toolsUsed` array

3. **Update Tool Status**:
   - When tool event received → status: "running"
   - When next event arrives → previous tool status: "completed"
   - On error → status: "error"

4. **Display in UI**:
   - Show tool name from event
   - Show description from `/tools` data
   - Format input/output for readability

#### Tool Categories and Icons

**Search Tools**:
- `wikipedia` → 📚 Search
- `arxiv` → 🔬 Research
- `duckduckgo_search` → 🌐 Web

**Database Tools**:
- `crm_*` → 👥 CRM
- `query_music_database` → 🎵 SQL

**RAG Tools**:
- `langsmith_search` → 📖 Docs

#### Key Considerations

1. **Performance**:
   - Limit number of tools displayed (last 10)
   - Lazy load tool details
   - Virtualize long tool lists

2. **Readability**:
   - Format JSON input/output with syntax highlighting
   - Truncate long outputs with "Show more" button
   - Use icons/colors to differentiate tool types

3. **Accessibility**:
   - Provide screen reader descriptions
   - Keyboard navigation support
   - High contrast mode for status indicators

4. **User Value**:
   - Help users understand how agent arrived at answer
   - Build trust through transparency
   - Educational value (see what agent can do)

---

### Feature 4: Health Dashboard / Monitoring

**Goal**: Display the operational status of backend components and provide system health insights.

#### Data Source

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "components": {
    "agent_service": {
      "status": "healthy",
      "message": "Agent service is initialized and ready"
    },
    "database": {
      "status": "healthy",
      "message": "Database connection is active"
    },
    "faiss_service": {
      "status": "healthy",
      "message": "FAISS vector store is initialized"
    }
  },
  "timestamp": "2026-02-13T10:30:00Z"
}
```

#### Dashboard Components

**1. Overall Status Indicator**:
- Large status badge/icon at top
- Green: "All Systems Operational"
- Red: "System Down"
- Yellow: "Degraded Performance" (if implemented)

**2. Component Status Cards**:
- Agent Service: ✅ Healthy / ❌ Unhealthy
- Database: ✅ Healthy / ❌ Unhealthy
- FAISS Service: ✅ Healthy / ⚠️ Optional

**3. Status Details**:
- Component name
- Status (healthy/unhealthy)
- Status message
- Last check timestamp

**4. Historical Status** (Optional):
- Status changes over time
- Uptime percentage
- Downtime incidents

#### Polling Strategy

**Recommended Pattern**:
```javascript
{
  pollingInterval: 30000,  // 30 seconds
  retryOnFailure: true,
  maxRetries: 3,
  backoffMultiplier: 2
}
```

**Polling Flow**:
```
1. Initial check on page load
2. Poll every 30-60 seconds
3. If check fails:
   - Retry with exponential backoff
   - Show "Connection Lost" after max retries
4. Update UI with each successful check
5. Stop polling when leaving page
```

#### State Management

```javascript
{
  health: {
    overall: "healthy",  // "healthy" | "unhealthy" | "unknown"
    components: {
      agent_service: { status: "healthy", message: "..." },
      database: { status: "healthy", message: "..." },
      faiss_service: { status: "healthy", message: "..." }
    },
    lastChecked: "2026-02-13T10:30:00Z",
    isLoading: false,
    error: null
  }
}
```

#### Status Icons and Colors

**Overall Status**:
- ✅ Green: All systems operational
- ❌ Red: Critical failure
- ⚠️ Yellow: Degraded (optional)
- ❓ Gray: Unknown/checking

**Component Status**:
- `healthy` → ✅ Green
- `unhealthy` → ❌ Red
- Loading → ⏳ Spinner

#### User Notifications

**When to Notify**:
1. **Status Change**: healthy → unhealthy
2. **Service Recovery**: unhealthy → healthy
3. **Connection Lost**: Failed to check health

**Notification Types**:
- **Toast/Snackbar**: Brief status updates
- **Banner**: Persistent warning when unhealthy
- **Badge**: Header indicator (red dot when down)

#### Integration Pattern

1. **Page Load**:
   - Fetch initial health status
   - Display results
   - Start polling interval

2. **Continuous Monitoring**:
   - Poll every 30-60 seconds
   - Compare with previous status
   - Notify user if changed

3. **Error Handling**:
   - Network error → Show "Connection Lost"
   - 503 response → Show "Service Unavailable"
   - Timeout → Retry with backoff

4. **User Actions**:
   - "Refresh" button to check immediately
   - "Disable Chat" button if backend unhealthy
   - Link to status page or admin contact

#### Key Considerations

1. **Performance**:
   - Don't poll too frequently (30s minimum)
   - Cancel pending requests when unmounting
   - Use efficient state updates

2. **User Experience**:
   - Don't block UI while checking
   - Show unobtrusive status indicator
   - Provide clear error messages

3. **Reliability**:
   - Handle temporary network blips gracefully
   - Don't assume unhealthy after single failure
   - Implement retry logic

4. **Optional Components**:
   - FAISS failure shouldn't show "System Down"
   - Differentiate critical vs optional components
   - Show degraded mode when optionals fail

---

## Data Models

### Request Models

#### ChatRequest
```json
{
  "message": "string (required, max 10000 chars)",
  "conversation_history": [
    {
      "role": "user | assistant (required)",
      "content": "string (required)"
    }
  ]
}
```

**Validation Rules**:
- `message`: Required, non-empty, max 10,000 characters
- `conversation_history`: Optional, defaults to `[]`
- Each history item must have `role` and `content`
- `role` must be either "user" or "assistant"

---

### Response Models

#### ChatResponse
```json
{
  "response": "string - Agent's complete answer",
  "conversation_history": [
    {
      "role": "user | assistant",
      "content": "string"
    }
  ],
  "timestamp": "string - ISO 8601 format"
}
```

#### StreamEvent
```json
{
  "type": "agent | tool | end | error",
  "content": {
    // Varies by type (see below)
  },
  "timestamp": "string - ISO 8601 format"
}
```

**Event Content by Type**:

**Agent Event**:
```json
{
  "type": "agent",
  "content": {
    "messages": [
      {
        "type": "ai",
        "content": "string - Agent's thought/message"
      }
    ]
  }
}
```

**Tool Event**:
```json
{
  "type": "tool",
  "content": {
    "tool": "string - Tool name",
    "input": "string | object - Tool input parameters",
    "output": "string - Tool output/result"
  }
}
```

**End Event**:
```json
{
  "type": "end",
  "content": {
    "response": "string - Final answer",
    "conversation_history": [...]
  }
}
```

**Error Event**:
```json
{
  "type": "error",
  "content": {
    "error": "string - Error type",
    "detail": "string - Error description"
  }
}
```

#### HealthResponse
```json
{
  "status": "healthy | unhealthy",
  "components": {
    "agent_service": {
      "status": "healthy | unhealthy",
      "message": "string"
    },
    "database": {
      "status": "healthy | unhealthy",
      "message": "string"
    },
    "faiss_service": {
      "status": "healthy | unhealthy",
      "message": "string"
    }
  },
  "timestamp": "string - ISO 8601 format"
}
```

#### ToolsResponse
```json
{
  "tools": [
    {
      "name": "string - Tool identifier",
      "description": "string - What the tool does"
    }
  ],
  "count": "number - Total tools",
  "timestamp": "string - ISO 8601 format"
}
```

#### ErrorResponse
```json
{
  "error": "string - Error type/name",
  "detail": "string - Human-readable error message",
  "status_code": "number - HTTP status code",
  "path": "string - API endpoint where error occurred",
  "validation_errors": [  // Only for 422 errors
    {
      "field": "string - Field name",
      "message": "string - Error message",
      "type": "string - Error type"
    }
  ]
}
```

---

### Conversation History Structure

**Format**:
```json
[
  {
    "role": "user",
    "content": "What is LangChain?"
  },
  {
    "role": "assistant",
    "content": "LangChain is a framework for developing applications powered by language models..."
  },
  {
    "role": "user",
    "content": "How do I use it?"
  },
  {
    "role": "assistant",
    "content": "To use LangChain, you first need to install it..."
  }
]
```

**Rules**:
- Alternating user/assistant messages
- Always starts with "user" role
- Always send full history (not just last N messages)
- Use history returned by backend (don't manually construct)

**History Management**:
- Store in component state or context
- Persist to localStorage for session recovery
- Clear on "New Conversation" action
- Consider truncation for very long conversations (>50 messages)

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | When It Occurs | How to Handle |
|------|---------|----------------|---------------|
| **200** | Success | Request processed successfully | Parse and display response |
| **422** | Validation Error | Invalid request body (missing/invalid fields) | Show field-specific errors to user |
| **404** | Not Found | Invalid endpoint | Check API base URL and endpoint path |
| **405** | Method Not Allowed | Wrong HTTP method (e.g., GET on POST endpoint) | Verify HTTP method |
| **429** | Too Many Requests | Rate limit exceeded | Show "Please wait" message, retry after delay |
| **500** | Server Error | Backend processing failed | Show generic error, provide retry button |
| **503** | Service Unavailable | Backend not ready (unhealthy) | Check `/health`, show maintenance message |

---

### Error Response Formats

#### Validation Error (422)
```json
{
  "error": "ValidationError",
  "detail": "Request validation failed",
  "status_code": 422,
  "validation_errors": [
    {
      "field": "message",
      "message": "field required",
      "type": "value_error.missing"
    },
    {
      "field": "conversation_history -> 0 -> role",
      "message": "unexpected value; permitted: 'user', 'assistant'",
      "type": "value_error.const"
    }
  ]
}
```

**How to Display**:
- Show field-specific errors next to input fields
- Highlight invalid fields in red
- Provide clear instructions on how to fix

#### Server Error (500)
```json
{
  "error": "Exception",
  "detail": "Internal server error occurred",
  "status_code": 500,
  "path": "/chat"
}
```

**How to Display**:
- Generic user-friendly message: "Something went wrong. Please try again."
- Log error details to console for debugging
- Provide "Retry" button
- Don't expose technical details to end users

#### HTTP Error (404)
```json
{
  "error": "HTTPException",
  "detail": "Not Found",
  "status_code": 404,
  "path": "/invalid-endpoint"
}
```

**How to Display**:
- "Feature not available" message
- Check if API base URL is correct
- Verify endpoint path

---

### Client-Side Error Handling

#### Network Errors
- **Connection Timeout**: "Unable to connect to server"
- **Network Offline**: "No internet connection"
- **CORS Error**: "Unable to access API. Check CORS configuration."

#### Validation Errors
- **Empty Message**: "Please enter a message"
- **Invalid History**: "Conversation history is corrupted. Start a new conversation."
- **Message Too Long**: "Message exceeds 10,000 character limit"

#### SSE Streaming Errors
- **Connection Lost**: "Stream interrupted. Please retry."
- **Parse Error**: "Invalid data received. Restarting connection..."
- **Timeout**: "No response for 60 seconds. Connection timeout."

---

### Error Handling Best Practices

1. **User-Friendly Messages**:
   - Don't show technical stack traces
   - Provide clear, actionable error messages
   - Use plain language

2. **Retry Mechanisms**:
   - Automatic retry for transient failures (network issues)
   - Manual retry button for user-initiated retries
   - Exponential backoff for multiple failures

3. **Error Logging**:
   - Log all errors to console (development)
   - Send critical errors to logging service (production)
   - Include context (endpoint, request body, user action)

4. **Fallback Strategies**:
   - SSE fails → Fall back to synchronous chat
   - FAISS unavailable → Continue with other tools
   - Network issues → Show cached/offline content

5. **Graceful Degradation**:
   - Disable features when backend unhealthy
   - Show "Limited Functionality" mode
   - Provide status page link

---

### Error Recovery Patterns

#### Pattern 1: Exponential Backoff
```javascript
Retry Delays: 1s, 2s, 4s, 8s, 16s, give up
Use for: Network errors, temporary server issues
```

#### Pattern 2: Circuit Breaker
```javascript
After 3 consecutive failures:
- Stop trying for 30 seconds
- Show "Service Unavailable" message
- Retry after cooldown period
```

#### Pattern 3: Optimistic Updates
```javascript
1. Update UI immediately (optimistic)
2. Send API request
3. If fails, revert UI changes
4. Show error message
```

---

## CORS Configuration

### What is CORS?

**Cross-Origin Resource Sharing (CORS)** is a security feature that restricts web applications from making requests to a different domain than the one serving the app.

### Your Setup

**Frontend Origin**: `http://localhost:3000` (Express server)  
**Backend Origin**: `http://localhost:9080` (FastAPI server)  
**Cross-Origin Request**: ✅ Yes (different ports)

### Backend CORS Configuration

The backend is already configured to allow CORS. Default settings:

```env
CORS_ENABLED=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

**What This Means**:
- Backend accepts requests from `http://localhost:3000`
- Backend accepts requests from `http://localhost:8080`
- Requests from other origins will be blocked

### Production Configuration

**For Production**, update backend `.env`:

```env
CORS_ENABLED=true
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

Replace with your actual production domain(s).

### Frontend Considerations

**Development**:
- No special configuration needed
- Ensure frontend runs on `http://localhost:3000`
- Backend automatically allows this origin

**Production**:
- Ensure your domain is in backend's `CORS_ORIGINS`
- Use HTTPS in production
- Update API base URL from `localhost:9080` to production URL

### Testing CORS

**Check if CORS is working**:
```
1. Open browser DevTools (F12)
2. Go to Network tab
3. Make API request from frontend
4. Check response headers:
   - Access-Control-Allow-Origin: http://localhost:3000
   - Access-Control-Allow-Credentials: true
```

**Common CORS Errors**:
- **"CORS policy blocked"**: Backend doesn't allow your origin
  - Solution: Add your origin to backend `CORS_ORIGINS`
- **"Preflight request failed"**: OPTIONS request blocked
  - Solution: Ensure backend accepts OPTIONS method (already configured)

### CORS and Authentication

**If you add authentication later**:
```env
# Backend .env
CORS_ALLOW_CREDENTIALS=true
```

**Frontend must include**:
```javascript
fetch(url, {
  credentials: 'include'  // Send cookies/auth headers
})
```

---

## State Management Considerations

### Application State Structure

**Recommended State Organization**:

```javascript
{
  // User/Session
  user: {
    id: null,
    isAuthenticated: false
  },

  // Chat State
  chat: {
    conversations: [
      {
        id: "conv-1",
        history: [...],
        createdAt: "2026-02-13T10:00:00Z"
      }
    ],
    activeConversationId: "conv-1",
    isLoading: false,
    error: null
  },

  // Streaming State
  streaming: {
    isStreaming: false,
    currentMessages: [],
    activeTools: [],
    error: null
  },

  // System State
  system: {
    health: {
      status: "healthy",
      components: {...},
      lastChecked: "2026-02-13T10:30:00Z"
    },
    tools: [
      { name: "wikipedia", description: "..." }
    ]
  },

  // UI State
  ui: {
    sidebarOpen: true,
    activeView: "chat", // "chat" | "streaming" | "health"
    theme: "light"
  }
}
```

### State Management Options

#### Option 1: React Context API (Simple)
**Best for**: Small to medium apps, simple state

**Pros**:
- Built into React
- No external dependencies
- Easy to set up

**Cons**:
- Can cause re-render issues at scale
- No built-in DevTools

#### Option 2: Redux / Redux Toolkit (Complex)
**Best for**: Large apps, complex state interactions

**Pros**:
- Time-travel debugging
- Middleware support (logging, persistence)
- DevTools integration

**Cons**:
- Steeper learning curve
- More boilerplate code

#### Option 3: Zustand (Balanced)
**Best for**: Most applications, balanced complexity

**Pros**:
- Simple API
- Good performance
- Small bundle size
- DevTools support

**Cons**:
- Less ecosystem than Redux

#### Option 4: Local Component State + Custom Hooks
**Best for**: Simple apps, minimal state sharing

**Pros**:
- No setup needed
- Easiest to understand

**Cons**:
- State duplication
- Prop drilling

### Recommended Approach

**For This Application**:
- **Use Zustand or Context API**
- **Separate concerns**:
  - Chat state (conversations, messages)
  - Streaming state (active stream, tools)
  - System state (health, tools list)
  - UI state (sidebar, theme)

### State Persistence

**What to Persist**:
- ✅ Conversation history (localStorage)
- ✅ User preferences (theme, settings)
- ✅ Active conversation ID
- ❌ Loading states
- ❌ Error messages
- ❌ Streaming state

**Persistence Pattern**:
```javascript
// Save to localStorage after each update
localStorage.setItem('chat_history', JSON.stringify(conversationHistory));

// Load on app startup
const savedHistory = JSON.parse(localStorage.getItem('chat_history') || '[]');
```

**Storage Limits**:
- localStorage: ~5-10MB per domain
- Consider IndexedDB for larger datasets

### State Updates for Streaming

**Challenge**: Frequent updates during SSE streaming can cause performance issues

**Solution**: Batch updates

```javascript
// Bad: Update on every event
onEvent((event) => {
  setState({ messages: [...messages, event] })  // Re-render every event
})

// Good: Batch updates
let buffer = []
onEvent((event) => {
  buffer.push(event)
})

setInterval(() => {
  if (buffer.length > 0) {
    setState({ messages: [...messages, ...buffer] })
    buffer = []
  }
}, 100)  // Update every 100ms
```

---

## Performance Optimization

### 1. API Request Optimization

#### Debouncing User Input
**Problem**: User types fast, sends too many requests  
**Solution**: Debounce input

```
User types: "h" "e" "l" "l" "o"
Without debounce: 5 API calls
With debounce (300ms): 1 API call after user stops typing
```

**Use Cases**:
- Search-as-you-type features
- Auto-save functionality

#### Request Caching
**Pattern**: Cache GET requests (health, tools)

```javascript
Cache Strategy:
1. Check cache first
2. If exists and not expired, return cached data
3. If expired or missing, fetch from API
4. Store in cache with timestamp
```

**What to Cache**:
- ✅ Tools list (rarely changes)
- ✅ Health status (30-60s TTL)
- ❌ Chat responses (always unique)
- ❌ Streaming events (real-time)

#### Request Cancellation
**Problem**: User navigates away before request completes  
**Solution**: Cancel in-flight requests

```javascript
Pattern:
1. Create AbortController
2. Pass signal to fetch
3. On unmount, call abort()
```

**Use Cases**:
- User changes pages
- User starts new chat before previous finishes
- User closes modal/dialog

---

### 2. Rendering Performance

#### Message List Virtualization
**Problem**: Long conversation history causes slow rendering  
**Solution**: Virtual scrolling (render only visible messages)

**Libraries**: react-window, react-virtual

**Benefits**:
- Render only 10-20 visible messages
- Handle thousands of messages smoothly
- Smooth scrolling

#### Memoization
**Use Cases**:
- Expensive computations (formatting, parsing)
- Child components that don't need re-render

```javascript
Techniques:
- React.memo(): Prevent component re-render
- useMemo(): Cache computed values
- useCallback(): Cache function references
```

#### Code Splitting
**Pattern**: Load features on demand

```javascript
Split Points:
- Main Chat: Loaded immediately
- Health Dashboard: Lazy loaded
- Admin Panel: Lazy loaded
- Tool Visualization: Lazy loaded
```

**Benefits**:
- Smaller initial bundle
- Faster page load
- Better user experience

---

### 3. Network Performance

#### HTTP/2 Multiplexing
If backend supports HTTP/2:
- Multiple requests over single connection
- Better performance
- Reduced latency

#### Compression
Ensure backend sends compressed responses:
- Gzip or Brotli
- Reduces payload size
- Faster transfers

#### CDN (Production)
For static files:
- Host frontend build on CDN
- Faster global delivery
- Reduced server load

---

### 4. State Management Performance

#### Avoid Unnecessary Re-renders
**Techniques**:
1. Split state into smaller pieces
2. Use selectors to subscribe to specific state
3. Memoize components and values

#### State Structure
**Good Structure** (normalized):
```javascript
{
  conversations: {
    byId: {
      "conv-1": {...},
      "conv-2": {...}
    },
    allIds: ["conv-1", "conv-2"]
  }
}
```

**Bad Structure** (nested):
```javascript
{
  conversations: [
    { id: "conv-1", messages: [...] },
    { id: "conv-2", messages: [...] }
  ]
}
```

---

### 5. SSE Streaming Performance

#### Batch UI Updates
Update UI every 100-200ms instead of every event:
```
Events per second: 10
Without batching: 10 re-renders/sec
With batching (100ms): ~10 re-renders/sec (max)
```

#### Limit Message Buffer
Don't keep all intermediate messages:
```javascript
Keep only:
- Last 5 agent messages
- All tool usage events
- Final response
```

---

### Performance Monitoring

**Metrics to Track**:
- Time to First Byte (TTFB)
- Time to Interactive (TTI)
- First Contentful Paint (FCP)
- API request latency
- Re-render count

**Tools**:
- React DevTools Profiler
- Chrome DevTools Performance tab
- Lighthouse (built into Chrome)

---

## Security Considerations

### 1. API Key Security

**⚠️ NEVER expose backend API keys in frontend**

**Backend API Key**:
- `OPENAI_API_KEY` lives on backend ONLY
- Never send to frontend
- Never include in frontend code
- Backend makes OpenAI calls on behalf of frontend

**Frontend Configuration**:
```javascript
// Good: Only backend URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:9080'

// Bad: NEVER do this
const OPENAI_KEY = process.env.REACT_APP_OPENAI_KEY  // ❌ NEVER!
```

---

### 2. Input Validation

**Always Validate User Input**:

**Message Length**:
```javascript
Max Length: 10,000 characters
Validation: Check before sending to backend
```

**Content Sanitization**:
- Escape HTML to prevent XSS
- Strip dangerous characters
- Use libraries like DOMPurify

**Conversation History**:
- Validate structure before sending
- Ensure role is "user" or "assistant"
- Prevent history injection

---

### 3. XSS Prevention

**Cross-Site Scripting (XSS)**: Malicious scripts in user input

**Prevention**:
1. **Never use `dangerouslySetInnerHTML`** without sanitization
2. **Escape user content** when rendering
3. **Use React's default escaping** (automatic)
4. **Sanitize markdown** if rendering markdown responses

**Safe Rendering**:
```javascript
// React escapes by default - SAFE
<div>{userMessage}</div>

// Dangerous - NEVER do this
<div dangerouslySetInnerHTML={{ __html: userMessage }} />

// If you must render HTML, sanitize first
import DOMPurify from 'dompurify'
<div dangerouslySetInnerHTML={{ 
  __html: DOMPurify.sanitize(userMessage) 
}} />
```

---

### 4. HTTPS in Production

**Development**: HTTP is fine (`http://localhost:3000`)  
**Production**: Always use HTTPS (`https://yourdomain.com`)

**Why HTTPS**:
- Encrypts data in transit
- Protects against man-in-the-middle attacks
- Required for modern browser features
- SEO benefits

**Setup**:
- Get SSL certificate (Let's Encrypt is free)
- Configure nginx/Apache reverse proxy
- Redirect HTTP → HTTPS

---

### 5. Rate Limiting (Client-Side)

**Backend has rate limiting** (60/min, 1000/hour default)

**Client-Side Protection**:
1. **Disable send button during request**
2. **Show cooldown timer if rate limited**
3. **Implement local throttling**

**Handle 429 Response**:
```javascript
if (response.status === 429) {
  // Show: "Too many requests. Please wait 60 seconds."
  // Disable UI for 60 seconds
  // Retry after delay
}
```

---

### 6. Session Security

**If you add authentication**:

**Secure Cookies**:
```javascript
Set-Cookie: sessionId=...; HttpOnly; Secure; SameSite=Strict
```

**Token Storage**:
- ✅ HttpOnly cookies (best)
- ⚠️ sessionStorage (okay)
- ❌ localStorage (vulnerable to XSS)

**CSRF Protection**:
- Use SameSite cookies
- Implement CSRF tokens if needed

---

### 7. Error Message Security

**Don't Expose Sensitive Information**:

**Bad**:
```javascript
Error: "Database connection failed at postgres://user:pass@db:5432"
```

**Good**:
```javascript
Error: "Unable to process request. Please try again."
```

**Logging**:
- Log full errors to console (development)
- Send full errors to logging service (production)
- Show generic errors to users

---

### 8. Content Security Policy (CSP)

**Add CSP headers** to prevent XSS and injection attacks:

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               connect-src 'self' http://localhost:9080; 
               script-src 'self'; 
               style-src 'self' 'unsafe-inline';">
```

**What This Does**:
- Only load scripts from your domain
- Only connect to your API
- Blocks inline scripts (XSS protection)

---

### Security Checklist

Before deploying to production:

- [ ] ✅ No API keys in frontend code
- [ ] ✅ HTTPS enabled
- [ ] ✅ Input validation implemented
- [ ] ✅ XSS protection (sanitize user content)
- [ ] ✅ CORS configured correctly
- [ ] ✅ Rate limiting handled
- [ ] ✅ Error messages don't expose sensitive data
- [ ] ✅ CSP headers configured
- [ ] ✅ Secure session management (if auth added)
- [ ] ✅ Dependencies updated (no known vulnerabilities)

---

## Testing Recommendations

### 1. Unit Testing

**What to Test**:
- API service layer functions
- Utility functions (parsing, formatting)
- Custom hooks
- State management logic

**Tools**: Jest, React Testing Library

**Example Tests**:
- Parse SSE events correctly
- Format conversation history
- Handle API errors
- Validate user input

---

### 2. Integration Testing

**What to Test**:
- API calls with mock server
- Full user flows (send message → receive response)
- Error handling (network failures, 500 errors)
- State updates after API calls

**Tools**: Jest, MSW (Mock Service Worker), React Testing Library

**Example Tests**:
- Send chat message and verify response displayed
- Stream chat and verify real-time updates
- Health check updates status indicator
- Tools list loads and displays

---

### 3. E2E Testing

**What to Test**:
- Complete user journeys
- Real backend integration
- Cross-browser compatibility

**Tools**: Cypress, Playwright

**Example Tests**:
- User opens app → sends message → receives response
- User switches between chat and streaming modes
- User views health dashboard
- User starts new conversation

---

### 4. API Testing

**Test Backend API Separately**:

```bash
# Test health endpoint
curl http://localhost:9080/health

# Test chat endpoint
curl -X POST http://localhost:9080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "conversation_history": []}'

# Test streaming
curl -X POST http://localhost:9080/chat-stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "conversation_history": []}'
```

**Tools**: Postman, Insomnia, curl, HTTPie

---

### 5. Performance Testing

**What to Test**:
- Long conversation history rendering
- Rapid message sending
- Stream with many events
- Large API responses

**Tools**: Chrome DevTools, Lighthouse, WebPageTest

**Metrics**:
- Time to Interactive (TTI)
- First Contentful Paint (FCP)
- API response time
- Memory usage

---

### Testing Best Practices

1. **Mock External Dependencies**:
   - Mock API calls in unit tests
   - Use real API in E2E tests

2. **Test Error States**:
   - Network failures
   - API errors (500, 422)
   - Invalid responses

3. **Accessibility Testing**:
   - Screen reader compatibility
   - Keyboard navigation
   - ARIA labels

4. **Visual Regression Testing**:
   - Screenshot comparison
   - Detect UI changes
   - Tools: Percy, Chromatic

---

## Appendix

### A. Example API Service Implementation Structure

**File**: `src/services/api.js`

```
Purpose: Base API client for all HTTP requests

Responsibilities:
- Set base URL
- Add common headers
- Handle errors globally
- Provide retry logic
```

---

**File**: `src/services/chatService.js`

```
Purpose: Chat endpoint wrapper

Functions:
- sendMessage(message, history) -> POST /chat
- Returns: ChatResponse
- Handles: Validation errors, network errors
```

---

**File**: `src/services/streamingService.js`

```
Purpose: Streaming chat handler

Functions:  
- startStream(message, history) -> POST /chat-stream
- Returns: EventSource or ReadableStream
- Handles: SSE parsing, connection management
```

---

**File**: `src/services/healthService.js`

```
Purpose: Health monitoring

Functions:
- checkHealth() -> GET /health
- Returns: HealthResponse
- Handles: Polling, connection errors
```

---

**File**: `src/services/toolsService.js`

```
Purpose: Tools management

Functions:
- getTools() -> GET /tools
- Returns: ToolsResponse
- Caching: Cache results (rarely changes)
```

---

### B. SSE Client Implementation Notes

**Browser Support**:
- EventSource API: Modern browsers
- Polyfill: Available for older browsers
- Alternative: Fetch with ReadableStream

**EventSource Limitations**:
- Cannot send custom headers (POST body is okay)
- Cannot control reconnection behavior precisely
- No progress events

**Fetch Alternative** (More Control):
```
Advantages:
- Full control over reconnection
- Custom headers support
- Better error handling
- Cancel anytime

Disadvantages:
- More complex implementation
- Manual parsing required
```

**Recommendation**: Use EventSource for simplicity, fallback to Fetch if needed

---

### C. Environment Variables Setup

**Express Server** (`server.js`):
```javascript
// Not needed - Express just serves static files
// API URL is configured in React build
```

**React App** (`.env`):
```
REACT_APP_API_URL=http://localhost:9080
```

**Production** (`.env.production`):
```
REACT_APP_API_URL=https://api.yourdomain.com
```

**Usage in React**:
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:9080'
```

---

### D. TypeScript Definitions (Optional)

If you add TypeScript later, here are the interface definitions:

**ChatRequest**:
```typescript
interface ChatRequest {
  message: string
  conversation_history: ConversationMessage[]
}
```

**ConversationMessage**:
```typescript
interface ConversationMessage {
  role: 'user' | 'assistant'
  content: string
}
```

**ChatResponse**:
```typescript
interface ChatResponse {
  response: string
  conversation_history: ConversationMessage[]
  timestamp: string
}
```

**StreamEvent**:
```typescript
type StreamEventType = 'agent' | 'tool' | 'end' | 'error'

interface StreamEvent {
  type: StreamEventType
  content: AgentContent | ToolContent | EndContent | ErrorContent
  timestamp: string
}
```

**HealthResponse**:
```typescript
interface HealthResponse {
  status: 'healthy' | 'unhealthy'
  components: {
    [key: string]: ComponentHealth
  }
  timestamp: string
}

interface ComponentHealth {
  status: 'healthy' | 'unhealthy'
  message: string
}
```

**ToolsResponse**:
```typescript
interface ToolsResponse {
  tools: Tool[]
  count: number
  timestamp: string
}

interface Tool {
  name: string
  description: string
}
```

---

### E. Useful Resources

**React**:
- React Docs: https://react.dev
- Hooks Reference: https://react.dev/reference/react

**State Management**:
- Zustand: https://github.com/pmndrs/zustand
- Redux Toolkit: https://redux-toolkit.js.org

**SSE**:
- EventSource API: https://developer.mozilla.org/en-US/docs/Web/API/EventSource
- SSE Specification: https://html.spec.whatwg.org/multipage/server-sent-events.html

**Testing**:
- React Testing Library: https://testing-library.com/react
- Jest: https://jestjs.io
- Cypress: https://www.cypress.io

**Performance**:
- Web Vitals: https://web.dev/vitals/
- React DevTools: https://react.dev/learn/react-developer-tools

---

### F. Quick Reference Commands

**Start Backend (Docker)**:
```bash
cd back-end
docker-compose up -d
docker-compose logs -f
```

**Start Frontend (Development)**:
```bash
cd front-end
npm install
npm start
# Runs on http://localhost:3000
```

**Test API Endpoints**:
```bash
# Health check
curl http://localhost:9080/health

# Tools list
curl http://localhost:9080/tools

# Chat
curl -X POST http://localhost:9080/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","conversation_history":[]}'
```

**Build Frontend for Production**:
```bash
npm run build
# Outputs to: build/
```

**Serve Production Build**:
```bash
node server.js
# Serves build on http://localhost:3000
```

---

## Summary

This guide provides everything your front-end team needs to build a React application that integrates with the Agentic RAG REST API:

### Key Takeaways

1. **4 API Endpoints**:
   - POST `/chat` - Synchronous chat
   - POST `/chat-stream` - Real-time streaming (SSE)
   - GET `/health` - Component health checks
   - GET `/tools` - Available tools list

2. **Core Features**:
   - Chat with conversation history
   - Real-time streaming with tool visualization
   - Health monitoring dashboard

3. **Technical Stack**:
   - React for UI
   - Express to serve build
   - Fetch API for HTTP requests
   - EventSource/Fetch for SSE streaming

4. **Best Practices**:
   - Validate input before sending
   - Handle errors gracefully
   - Implement retry logic
   - Optimize for performance
   - Secure API keys (backend only)
   - Test thoroughly

5. **CORS Configuration**:
   - Backend allows `http://localhost:3000`
   - Update for production domains

### Next Steps for Front-End Team

1. **Set up project**:
   - Create React app
   - Install dependencies
   - Configure Express server

2. **Implement API service layer**:
   - Base API client
   - Chat service
   - Streaming service
   - Health service

3. **Build core features**:
   - Chat interface
   - Streaming chat
   - Tool visualization
   - Health dashboard

4. **Test integration**:
   - Test with local backend
   - Handle errors
   - Optimize performance

5. **Deploy**:
   - Build production bundle
   - Configure production API URL
   - Update CORS settings
   - Deploy to hosting

---

**Guide Version**: 1.0  
**Last Updated**: February 13, 2026  
**Backend API Version**: 1.0.0

For backend documentation, see:
- [DEPLOYMENT_GUIDE.md](../../back-end/docs/DEPLOYMENT_GUIDE.md)
- [API_GUIDE.md](../../back-end/docs/API_GUIDE.md)
- [README.md](../../back-end/README.md)
