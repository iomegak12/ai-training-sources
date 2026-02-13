# Agentic RAG REST API - Implementation Guide

**Project**: Convert `agentic-rag.ipynb` notebook into production REST API  
**Target Location**: `agentic-rag-usecase/back-end/`  
**Framework**: FastAPI with async support  
**Date**: February 13, 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Folder Structure](#folder-structure)
4. [Components Design](#components-design)
5. [API Endpoints Specification](#api-endpoints-specification)
6. [FAISS Initialization Strategy](#faiss-initialization-strategy)
7. [Configuration Management](#configuration-management)
8. [Implementation Steps](#implementation-steps)
9. [Dependencies](#dependencies)
10. [Testing Strategy](#testing-strategy)

---

## Overview

### Objectives

- **Modularize** notebook code into reusable service layer
- **Expose** agent functionality via REST API endpoints
- **Maintain** exact behavior of `agent_executor.invoke()` and `agent_executor.stream()`
- **Optimize** FAISS vector store initialization (one-time on startup)
- **Support** both blocking and streaming response modes

### Key Requirements

| Requirement | Approach |
|------------|----------|
| **Endpoints** | `/chat` (blocking), `/chat-stream` (SSE streaming) |
| **Agent Behavior** | Preserve notebook's multi-tool orchestration |
| **FAISS Setup** | Load URLs from `.env` + `urls.txt`, embed once at startup |
| **Tools** | All 10+ tools from notebook (ArXiv, Wiki, DDG, CRM, SQL, etc.) |
| **Authentication** | None (future enhancement) |

---

## Architecture

### High-Level Design

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP POST
       ▼
┌─────────────────────────────────────┐
│      FastAPI Application            │
│  ┌─────────────────────────────┐   │
│  │  API Router (/chat, /stream)│   │
│  └────────────┬────────────────┘   │
│               ▼                     │
│  ┌─────────────────────────────┐   │
│  │   AgentService (Singleton)  │   │
│  │  - agent_executor           │   │
│  │  - tool initialization      │   │
│  └────────────┬────────────────┘   │
│               │                     │
│     ┌─────────┴─────────┐          │
│     ▼                   ▼          │
│  ToolManager      ConfigManager    │
└─────────────────────────────────────┘
       │
       ├─> External APIs (Wikipedia, ArXiv, DDG)
       ├─> FAISS Vector Store (LangSmith docs)
       ├─> CRM Database (business_client_tools)
       └─> Chinook SQL Database
```

### Request Flow

#### `/chat` (Blocking)
```
POST /chat {"message": "..."}
   ↓
API handler validates request
   ↓
agent_service.invoke(message)
   ↓
agent_executor.invoke() - waits for completion
   ↓
Return full JSON response
```

#### `/chat-stream` (SSE)
```
POST /chat-stream {"message": "..."}
   ↓
API handler sets SSE headers
   ↓
agent_service.stream(message)
   ↓
for chunk in agent_executor.stream():
   yield chunk as SSE event
   ↓
Client receives real-time updates
```

---

## Folder Structure

```
agentic-rag-usecase/
├── back-end/
│   ├── main.py                    # FastAPI app entry point
│   ├── requirements.txt           # Python dependencies
│   ├── .env                       # Environment variables (ALL configuration here)
│   ├── .env.example               # Template for environment variables
│   ├── urls.txt                   # List of URLs for FAISS embedding (one per line)
│   ├── Dockerfile                 # Container configuration (optional)
│   ├── docker-compose.yml         # Multi-service orchestration (optional)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py              # API endpoint definitions
│   │   ├── models.py              # Pydantic request/response models
│   │   └── dependencies.py        # Dependency injection (get_agent_service)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agent_service.py       # Core agent executor management
│   │   └── faiss_service.py       # FAISS vector store singleton
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search_tools.py        # DuckDuckGo, Wikipedia, ArXiv
│   │   ├── rag_tools.py           # FAISS retriever tool
│   │   ├── crm_tools.py           # Business client/CRM database tools
│   │   └── sql_tools.py           # Chinook music database SQL tools
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py            # Pydantic Settings (load from .env)
│   │   └── logging_config.py      # Structured logging setup
│   │
│   ├── db/
│   │   ├── crm.db                 # SQLite CRM database (business clients)
│   │   ├── chinook.db             # SQLite Chinook music database
│   │   └── init_databases.py      # Database initialization script
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py             # Common utilities (URL validation, etc.)
│   │
│   └── docs/
│       └── API_GUIDE.md           # API usage documentation
│
├── notebooks/                     # Original notebook
└── docs/                          # This guide (project documentation)
```

**Key Changes**:
- ✅ **No external dependencies**: CRM & SQL tools moved into `back-end/tools/`
- ✅ **Local databases**: All databases in `back-end/db/` folder
- ✅ **Self-contained**: Entire API is portable with no parent directory dependencies

---

## Components Design

### 1. `main.py` - Application Entry Point

**Purpose**: Initialize FastAPI app, register routes, setup lifespan events

**Key Responsibilities**:
- Create FastAPI application instance
- Register API routers
- Handle startup event (initialize FAISS, tools, agent)
- Handle shutdown event (cleanup resources)
- Configure CORS, logging, middleware

**Pseudocode**:
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize FAISS and agent
    await initialize_services()
    yield
    # Shutdown: Cleanup
    await cleanup_services()

app = FastAPI(lifespan=lifespan)
app.include_router(chat_router)
```

---

### 2. `api/routes.py` - Endpoint Handlers

**Purpose**: Define HTTP endpoints and handle requests

**Endpoints**:

#### `POST /chat`
- **Input**: `{"message": str, "metadata": dict (optional)}`
- **Output**: `{"response": str, "tools_used": list, "execution_time": float}`
- **Behavior**: Calls `agent_executor.invoke()`, waits for full response

#### `POST /chat-stream`
- **Input**: `{"message": str}`
- **Output**: SSE stream with events: `data: {"type": "chunk", "content": "..."}`
- **Behavior**: Calls `agent_executor.stream()`, yields chunks in real-time

#### `GET /health`
- **Output**: `{"status": "healthy", "tools_loaded": int, "faiss_ready": bool}`

#### `GET /tools`
- **Output**: `{"tools": [{"name": str, "description": str}, ...]}`

**Key Implementation Notes**:
- Use `StreamingResponse` for `/chat-stream` with `text/event-stream` media type
- Wrap streaming generator in try/except for error handling
- Add request validation using Pydantic models

---

### 3. `api/models.py` - Request/Response Schemas

**Purpose**: Define Pydantic models for type safety and validation

**Models**:
```python
class ChatRequest(BaseModel):
    message: str
    metadata: Optional[dict] = None
    
class ChatResponse(BaseModel):
    response: str
    tools_used: List[str]
    execution_time: float
    metadata: Optional[dict] = None

class ToolInfo(BaseModel):
    name: str
    description: str
    
class HealthResponse(BaseModel):
    status: str
    tools_loaded: int
    faiss_ready: bool
```

---

### 4. `services/agent_service.py` - Agent Orchestrator

**Purpose**: Singleton service managing agent_executor lifecycle

**Key Methods**:

```python
class AgentService:
    def __init__(self):
        self.agent_executor = None
        self.tools = []
        self.llm = None
        
    async def initialize(self):
        """Called once at startup"""
        # 1. Load configuration
        # 2. Initialize LLM (ChatOpenAI)
        # 3. Load all tools (via ToolManager)
        # 4. Create agent_executor
        
    def invoke(self, message: str) -> dict:
        """Blocking call - mirrors notebook's invoke()"""
        response = self.agent_executor.invoke({
            "messages": [HumanMessage(content=message)]
        })
        return self._format_response(response)
        
    async def stream(self, message: str):
        """Async generator - mirrors notebook's stream()"""
        for chunk in self.agent_executor.stream({
            "messages": [HumanMessage(content=message)]
        }):
            yield self._format_chunk(chunk)
            
    def get_tools_info(self) -> List[dict]:
        """Return metadata about loaded tools"""
```

**Design Pattern**: Singleton (only one instance per API server)

---

### 5. `services/faiss_service.py` - Vector Store Manager

**Purpose**: Initialize and manage FAISS vector database

**FAISS Initialization Flow**:
```
Startup
  ↓
Read urls.txt (line-by-line)
  ↓
Read .env for additional URLs (comma-separated)
  ↓
Merge & deduplicate URLs
  ↓
WebBaseLoader.load_many(urls)
  ↓
RecursiveCharacterTextSplitter (chunk_size=1000, overlap=200)
  ↓
OpenAIEmbeddings (batch all chunks)
  ↓
FAISS.from_documents()
  ↓
Store in singleton instance
  ↓
Create retriever tool
```

**Key Methods**:
```python
class FAISSService:
    def __init__(self):
        self.vectorstore = None
        self.retriever = None
        
    async def initialize(self, urls: List[str]):
        """One-time initialization on startup"""
        # Load documents from URLs
        # Chunk text
        # Embed with OpenAI
        # Build FAISS index
        
    def get_retriever_tool(self):
        """Return LangChain retriever tool"""
        return create_retriever_tool(
            self.retriever,
            "langsmith_search",
            "Search LangSmith documentation"
        )
        
    def is_ready(self) -> bool:
        return self.vectorstore is not None
```

**Optimization**:
- Optional: Cache FAISS index to disk after first build
- Load from cache on subsequent restarts (faster startup)

---

### 6. `tools/search_tools.py` - External Search Tools

**Purpose**: Initialize Wikipedia, DuckDuckGo, ArXiv tools

**Implementation**:
```python
def get_wikipedia_tool():
    api_wrapper = WikipediaAPIWrapper(
        top_k_results=1, 
        doc_content_chars_max=3000  # Increased from 1000
    )
    return WikipediaQueryRun(
        name="WikipediaSearch",  # Fixed typo
        description="...",
        api_wrapper=api_wrapper
    )

def get_duckduckgo_tool():
    @tool("DuckDuckGoSearch")
    def duckduckgo_search(query_string: str):
        """..."""
        return DuckDuckGoSearchAPIWrapper().run(query_string)
    return duckduckgo_search

def get_arxiv_tool():
    # Similar pattern
```

---

### 7. `tools/crm_tools.py` & `tools/sql_tools.py` - Database Integration

**Purpose**: Provide CRM and SQL query tools using local databases

**Location**: All database files in `back-end/db/` folder

#### `tools/crm_tools.py` - CRM Business Client Tools
```python
from langchain_core.tools import tool
from pathlib import Path
import sqlite3
from config.settings import settings

DB_PATH = Path(__file__).parent.parent / settings.crm_database_path

@tool("get_business_client_count")
def get_business_client_count() -> str:
    """Get total count of business clients in CRM database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    count = cursor.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    conn.close()
    return f"Total business clients: {count}"

@tool("search_business_clients")
def search_business_clients(name: str) -> str:
    """Search for business clients by name."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    results = cursor.execute(
        "SELECT * FROM clients WHERE name LIKE ?", 
        (f"%{name}%",)
    ).fetchall()
    conn.close()
    return str(results)

@tool("get_business_client_by_id")
def get_business_client_by_id(client_id: int) -> str:
    """Get business client details by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    result = cursor.execute(
        "SELECT * FROM clients WHERE id = ?", 
        (client_id,)
    ).fetchone()
    conn.close()
    return str(result)

@tool("get_business_client_by_email")
def get_business_client_by_email(email: str) -> str:
    """Get business client details by email address."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    result = cursor.execute(
        "SELECT * FROM clients WHERE email = ?", 
        (email,)
    ).fetchone()
    conn.close()
    return str(result)

@tool("get_active_business_clients")
def get_active_business_clients() -> str:
    """Get all active business clients."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    results = cursor.execute(
        "SELECT * FROM clients WHERE status = 'active'"
    ).fetchall()
    conn.close()
    return str(results)

def get_crm_tools():
    """Return list of all CRM tools."""
    return [
        get_business_client_count,
        search_business_clients,
        get_business_client_by_id,
        get_business_client_by_email,
        get_active_business_clients
    ]
```

#### `tools/sql_tools.py` - Chinook Music Database Tool
```python
from langchain_core.tools import tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from pathlib import Path
from config.settings import settings

DB_PATH = Path(__file__).parent.parent / settings.chinook_database_path

@tool("query_music_database")
def query_music_database(question: str) -> str:
    """
    Query the Chinook music database to answer questions about artists,
    albums, tracks, customers, sales, genres, etc.
    
    Examples:
    - "How many artists are in the database?"
    - "Which artist has the most albums?"
    - "What are the most popular genres?"
    - "Which country's customers have spent the most?"
    
    Args:
        question: Natural language question about the music database
    
    Returns:
        Answer based on database query results with explanatory context
    """
    db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
    llm = ChatOpenAI(model=settings.openai_model, temperature=0)
    
    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=False
    )
    
    try:
        result = agent.invoke({"input": question})
        return result["output"]
    except Exception as e:
        return f"Error querying database: {str(e)}"

def get_sql_tool():
    """Return the SQL query tool."""
    return query_music_database
```

**Database Schema**:
- **CRM Database** (`db/crm.db`):  
  `clients` table: id, name, email, phone, status, created_at
  
- **Chinook Database** (`db/chinook.db`):  
  Standard Chinook schema: artists, albums, tracks, customers, invoices, invoice_items, genres, media_types, playlists, employees

---

### 8. `config/settings.py` - Configuration Management

**Purpose**: Centralized configuration using Pydantic Settings

**Implementation**:
```python
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # ============================================
    # OpenAI Configuration
    # ============================================
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 2000
    
    # ============================================
    # FAISS Configuration
    # ============================================
    faiss_urls_file: str = "urls.txt"
    faiss_additional_urls: str = ""  # Comma-separated
    faiss_chunk_size: int = 1000
    faiss_chunk_overlap: int = 200
    faiss_cache_enabled: bool = True
    faiss_cache_ttl_days: int = 7
    
    # ============================================
    # API Server Configuration
    # ============================================
    api_host: str = "0.0.0.0"
    api_port: int = 9080
    api_env: str = "development"
    api_reload: bool = True
    api_workers: int = 1
    
    # ============================================
    # Database Configuration  
    # ============================================
    crm_database_path: str = "db/crm.db"
    chinook_database_path: str = "db/chinook.db"
    
    # ============================================
    # Rate Limiting (Disabled by Default)
    # ============================================
    rate_limit_enabled: bool = False
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # ============================================
    # CORS Configuration
    # ============================================
    cors_enabled: bool = True
    cors_allow_origins: str = "http://localhost:3000,http://localhost:8080"
    
    # ============================================
    # API Documentation (OpenAPI/Swagger)
    # ============================================
    docs_enabled: bool = True
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # ============================================
    # Logging Configuration
    # ============================================
    log_level: str = "INFO"
    log_format: str = "text"  # "text" or "json"
    log_file_enabled: bool = False
    log_file_path: str = "logs/api.log"
    
    # ============================================
    # LangSmith (Optional)
    # ============================================
    langchain_tracing_v2: bool = False
    langchain_api_key: Optional[str] = None
    langchain_project: str = "agentic-rag-api"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [
            origin.strip() 
            for origin in self.cors_allow_origins.split(",") 
            if origin.strip()
        ]
    
    @property
    def faiss_urls_list(self) -> List[str]:
        """Parse FAISS additional URLs from comma-separated string."""
        if not self.faiss_additional_urls:
            return []
        return [
            url.strip() 
            for url in self.faiss_additional_urls.split(",") 
            if url.strip()
        ]

# Global settings instance
settings = Settings()
```

**`.env` Example**:
```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o
FAISS_ADDITIONAL_URLS=https://docs.smith.langchain.com,https://python.langchain.com/docs
```

**`urls.txt` Example**:
```
https://docs.smith.langchain.com
https://python.langchain.com/docs/get_started
https://api.python.langchain.com
```

---

## API Endpoints Specification

### Endpoint: `POST /chat`

**Description**: Blocking chat endpoint that waits for complete agent response

**Request**:
```json
POST /chat HTTP/1.1
Content-Type: application/json

{
  "message": "How many business clients are in the CRM database?",
  "metadata": {
    "user_id": "optional",
    "session_id": "optional"
  }
}
```

**Response** (Success - 200):
```json
{
  "response": "There are 127 business clients in the CRM database.",
  "tools_used": ["get_business_client_count"],
  "execution_time": 1.23,
  "metadata": {
    "model": "gpt-4o",
    "tokens_used": 156
  }
}
```

**Response** (Error - 500):
```json
{
  "error": "Agent execution failed",
  "details": "Tool 'get_business_client_count' encountered database connection error"
}
```

---

### Endpoint: `POST /chat-stream`

**Description**: Streaming chat endpoint using Server-Sent Events (SSE)

**Request**:
```json
POST /chat-stream HTTP/1.1
Content-Type: application/json

{
  "message": "Tell me about the top selling artist in the music database"
}
```

**Response** (Success - 200):
```http
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: {"type": "start", "timestamp": "2026-02-13T10:30:00Z"}

data: {"type": "tool_call", "tool": "chinook_sql_query", "input": "SELECT artist..."}

data: {"type": "tool_result", "tool": "chinook_sql_query", "output": "Iron Maiden"}

data: {"type": "chunk", "content": "The top selling artist is Iron Maiden"}

data: {"type": "chunk", "content": " with 21 albums sold."}

data: {"type": "end", "execution_time": 2.45}
```

**Client-side handling**:
```javascript
const eventSource = new EventSource('/chat-stream');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'chunk') {
    appendToChat(data.content);
  }
};
```

---

### Endpoint: `GET /health`

**Description**: Health check and service status

**Response** (200):
```json
{
  "status": "healthy",
  "tools_loaded": 11,
  "faiss_ready": true,
  "uptime_seconds": 3600,
  "version": "1.0.0"
}
```

---

### Endpoint: `GET /tools`

**Description**: List all available tools

**Response** (200):
```json
{
  "tools": [
    {
      "name": "arxiv",
      "description": "Search academic papers on ArXiv"
    },
    {
      "name": "DuckDuckGoSearch",
      "description": "Search the internet for information"
    },
    {
      "name": "WikipediaSearch",
      "description": "Search Wikipedia for topics"
    },
    {
      "name": "langsmith_search",
      "description": "Search LangSmith documentation"
    },
    {
      "name": "get_business_client_count",
      "description": "Count business clients in CRM"
    },
    {
      "name": "chinook_sql_query",
      "description": "Query Chinook music database"
    }
  ],
  "total": 11
}
```

---

## Response Structure Analysis

### Understanding Agent Executor Outputs

Based on notebook testing (`streamed-response.py` and `direct-response.py`), the agent executor returns different structures for streaming vs blocking calls.

### Streaming Response Structure (`agent_executor.stream()`)

**Raw Stream Output** (from notebook):
Each chunk from `stream()` contains either agent reasoning or tool execution:

```python
# Chunk 1: Agent decides to call a tool
{'agent': {'messages': [AIMessage(
    content='',
    tool_calls=[{
        'name': 'query_music_database',
        'args': {'question': 'Who is the top selling artist?'},
        'id': 'call_xxx',
        'type': 'tool_call'
    }],
    usage_metadata={'input_tokens': 1213, 'output_tokens': 25}
)]}}

# Chunk 2: Tool execution result
{'tools': {'messages': [ToolMessage(
    content='The top selling artist is Iron Maiden, with 140 sales...',
    name='query_music_database',
    tool_call_id='call_xxx'
)]}}

# Chunk 3: Agent calls another tool
{'agent': {'messages': [AIMessage(
    tool_calls=[{
        'name': 'WikipediaSearch',
        'args': {'query': 'Iron Maiden'},
        'id': 'call_yyy'
    }]
)]}}

# Chunk 4: Second tool result
{'tools': {'messages': [ToolMessage(
    content='Page: Iron Maiden\\nSummary: Iron Maiden are an English heavy metal band...',
    name='WikipediaSearch',
    tool_call_id='call_yyy'
)]}}

# Chunk 5: Final answer
{'agent': {'messages': [AIMessage(
    content='The top selling artist is Iron Maiden, with 140 sales. Here\\\'s their history: ...',
    response_metadata={
        'finish_reason': 'stop',  # ← Indicates completion
        'token_usage': {...},
        'model_name': 'gpt-4o-2024-08-06'
    }
)]}}
```

**SSE Transformation for API**:
```python
# Pseudocode for stream endpoint
async def stream_agent_response(message: str):
    for chunk in agent_executor.stream({"messages": [HumanMessage(content=message)]}):
        if 'agent' in chunk:
            ai_message = chunk['agent']['messages'][0]
            
            # Tool call event
            if ai_message.tool_calls:
                for tool_call in ai_message.tool_calls:
                    yield {
                        "type": "tool_call",
                        "tool": tool_call['name'],
                        "args": tool_call['args']
                    }
            
            # Final answer (has content and finish_reason='stop')
            elif ai_message.content and ai_message.response_metadata.get('finish_reason') == 'stop':
                # Stream content in chunks or all at once
                yield {
                    "type": "answer",
                    "content": ai_message.content,
                    "metadata": {
                        "tokens": ai_message.usage_metadata,
                        "model": ai_message.response_metadata.get('model_name')
                    }
                }
        
        elif 'tools' in chunk:
            tool_message = chunk['tools']['messages'][0]
            yield {
                "type": "tool_result",
                "tool": tool_message.name,
                "result": tool_message.content[:200]  # Truncate for streaming
            }
```

---

### Blocking Response Structure (`agent_executor.invoke()`)

**Raw Invoke Output** (from notebook):
Returns complete conversation history:

```python
{
  'messages': [
    HumanMessage(content='Tell me about the top selling artist...'),
    
    AIMessage(tool_calls=[{
        'name': 'query_music_database',
        'args': {'question': 'Who is the top selling artist?'}
    }]),
    
    ToolMessage(
        content='The top selling artist is Iron Maiden, with 140 sales...',
        name='query_music_database'
    ),
    
    AIMessage(tool_calls=[{
        'name': 'WikipediaSearch',
        'args': {'query': 'Iron Maiden band history'}
    }]),
    
    ToolMessage(
        content='Page: Iron Maiden discography...', 
        name='WikipediaSearch'
    ),
    
    AIMessage(
        content='The top selling artist is Iron Maiden, with 140 sales. Here\\'s a brief history: ...',
        response_metadata={'finish_reason': 'stop', 'token_usage': {...}}
    )
  ]
}
```

**API Response Transformation**:
```python
# Pseudocode for /chat endpoint
def format_invoke_response(result: dict) -> ChatResponse:
    messages = result['messages']
    
    # Extract final answer (last AIMessage with content)
    final_message = None
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            final_message = msg
            break
    
    # Extract tool usage
    tools_used = [
        msg.name for msg in messages 
        if isinstance(msg, ToolMessage)
    ]
    
    # Extract token usage
    total_tokens = sum(
        msg.usage_metadata.get('total_tokens', 0) 
        for msg in messages 
        if isinstance(msg, AIMessage) and hasattr(msg, 'usage_metadata')
    )
    
    return ChatResponse(
        response=final_message.content if final_message else "No answer generated",
        tools_used=list(set(tools_used)),
        metadata={
            "total_tokens": total_tokens,
            "model": final_message.response_metadata.get('model_name'),
            "steps": len([m for m in messages if isinstance(m, AIMessage)])
        }
    )
```

---

### Key Observations

**Streaming Behavior**:
- Chunks arrive in real-time as agent thinks and executes tools
- `finish_reason='stop'` indicates final answer is ready
- `finish_reason='tool_calls'` means agent wants to execute a tool
- Tool results are in separate chunks from agent reasoning

**Invoke Behavior**:
- Returns complete history after all execution finishes
- Last `AIMessage` with content contains the final answer
- `ToolMessage` objects show which tools were actually invoked
- Token usage is cumulative across all LLM calls

**Error Handling**:
- Streaming: Catch exceptions per-chunk, yield error event
- Invoke: Catch at endpoint level, return error response

---

## FAISS Initialization Strategy

### Problem Statement

The notebook rebuilds FAISS index on every execution:
- Slow startup (web scraping + embedding takes 10-30 seconds)
- Expensive (OpenAI embedding API calls cost money)
- Unreliable (network failures during scraping)

### Solution: Startup-Once Pattern

```
┌─────────────────────────────────────────────────────┐
│              FastAPI Startup Event                  │
└─────────────────┬───────────────────────────────────┘
                  ▼
         ┌────────────────────┐
         │ Read urls.txt      │
         │ Read .env          │
         └────────┬───────────┘
                  ▼
         ┌────────────────────┐
         │ Merge & Dedupe URLs│
         └────────┬───────────┘
                  ▼
    ┌─────────────────────────────┐
    │ Check if cached index exists│
    └─────────┬──────────┬────────┘
              │          │
         YES  │          │ NO
              ▼          ▼
      ┌────────────┐  ┌──────────────────┐
      │ Load cache │  │ Scrape web pages │
      └────────────┘  │ Chunk text       │
                      │ Embed with OpenAI│
                      │ Build FAISS      │
                      │ Save cache       │
                      └──────────────────┘
                              │
                 ┌────────────┴────────────┐
                 │ Store in singleton      │
                 │ FAISSService.vectorstore│
                 └─────────────────────────┘
                              │
                 ┌────────────┴────────────┐
                 │ Create retriever tool   │
                 └─────────────────────────┘
                              │
                 ┌────────────┴────────────┐
                 │ Add to agent tools list │
                 └─────────────────────────┘
```

### Configuration Files

**`urls.txt`** (one URL per line):
```
https://docs.smith.langchain.com
https://python.langchain.com/docs/get_started
https://api.python.langchain.com/en/latest
```

**`.env`** (optional additional URLs):
```
FAISS_ADDITIONAL_URLS=https://example.com,https://another-site.com
```

### Implementation Pseudocode

```python
async def initialize_faiss():
    # 1. Read URLs
    urls_from_file = read_urls_from_file("urls.txt")
    urls_from_env = os.getenv("FAISS_ADDITIONAL_URLS", "").split(",")
    all_urls = list(set(urls_from_file + urls_from_env))
    
    # 2. Check cache
    if faiss_cache_exists():
        vectorstore = load_faiss_cache()
    else:
        # 3. Build from scratch
        docs = WebBaseLoader.load_many(all_urls)
        chunks = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        ).split_documents(docs)
        
        vectorstore = FAISS.from_documents(
            chunks,
            OpenAIEmbeddings()
        )
        
        # 4. Save cache
        save_faiss_cache(vectorstore)
    
    # 5. Create retriever
    return vectorstore.as_retriever()
```

### Cache Strategy (Optional Enhancement)

**Location**: `back-end/.faiss_cache/`  
**Files**:
- `index.faiss` - FAISS index binary
- `metadata.json` - URLs and timestamp
- `docstore.pkl` - Document store

**Benefits**:
- Subsequent restarts load in <1 second
- No API calls unless URLs change
- Predictable startup time

**Implementation**:
```python
def should_rebuild_cache(urls: List[str]) -> bool:
    if not cache_exists():
        return True
    
    cached_metadata = load_cache_metadata()
    if set(cached_metadata['urls']) != set(urls):
        return True  # URLs changed
    
    cache_age = now() - cached_metadata['timestamp']
    if cache_age > timedelta(days=7):
        return True  # Cache too old
    
    return False
```

---

## Configuration Management

### Environment Variables (`.env`)

**ALL configuration centralized in `.env` file**:

```env
# ============================================
# OpenAI Configuration
# ============================================
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=2000

# ============================================
# FAISS Vector Store Configuration
# ============================================
FAISS_ADDITIONAL_URLS=https://docs.smith.langchain.com
FAISS_CHUNK_SIZE=1000
FAISS_CHUNK_OVERLAP=200
FAISS_CACHE_ENABLED=true
FAISS_CACHE_TTL_DAYS=7

# ============================================
# API Server Configuration (Development)
# ============================================
API_HOST=0.0.0.0
API_PORT=9080
API_ENV=development
API_RELOAD=true
API_WORKERS=1

# ============================================
# Database Configuration
# ============================================
CRM_DATABASE_PATH=db/crm.db
CHINOOK_DATABASE_PATH=db/chinook.db

# ============================================
# Rate Limiting (DISABLED by default)
# ============================================
RATE_LIMIT_ENABLED=false
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# ============================================
# Logging Configuration
# ============================================
LOG_LEVEL=INFO
LOG_FORMAT=text
LOG_FILE_ENABLED=false
LOG_FILE_PATH=logs/api.log

# ============================================
# CORS Configuration (Development)
# ============================================
CORS_ENABLED=true
CORS_ALLOW_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:5173

# ============================================
# API Documentation (OpenAPI/Swagger)
# ============================================
DOCS_ENABLED=true
DOCS_URL=/docs
REDOC_URL=/redoc
OPENAPI_URL=/openapi.json

# ============================================
# LangSmith (Optional - for tracing)
# ============================================
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=lsv2_xxxxx
LANGCHAIN_PROJECT=agentic-rag-api
```

**`.env.example`** template (committed to git):
```env
# ============================================
# Agentic RAG API - Environment Configuration
# Copy this file to .env and fill in your values
# ============================================

# OpenAI (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=2000

# API Server (Development)
API_HOST=0.0.0.0
API_PORT=9080
API_ENV=development
API_RELOAD=true

# Databases (auto-created if not exist)
CRM_DATABASE_PATH=db/crm.db
CHINOOK_DATABASE_PATH=db/chinook.db

# Rate Limiting (disabled for development)
RATE_LIMIT_ENABLED=false

# CORS (allow all localhost ports in dev)
CORS_ENABLED=true
CORS_ALLOW_ORIGINS=http://localhost:3000,http://localhost:8080

# Documentation (OpenAPI/Swagger)
DOCS_ENABLED=true
DOCS_URL=/docs

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=text
```

### URL Configuration (`urls.txt`)

```
# LangChain Documentation
https://docs.smith.langchain.com
https://python.langchain.com/docs/get_started
https://python.langchain.com/docs/modules

# Custom Knowledge Base (add your own)
https://your-company-docs.com/api
https://your-company-docs.com/guides
```

**Rules**:
- One URL per line
- Lines starting with `#` are ignored (comments)
- Empty lines are ignored
- URLs are validated before loading

---

## Implementation Steps

### Phase 1: Project Setup (Day 1)

1. **Create folder structure**
   ```bash
   cd agentic-rag-usecase
   mkdir -p back-end/{api,services,tools,config,utils}
   touch back-end/{main.py,requirements.txt,.env,urls.txt}
   ```

2. **Setup dependencies** (`requirements.txt`)
   ```
   fastapi==0.109.0
   uvicorn[standard]==0.27.0
   langchain==0.1.0
   langchain-openai==0.0.5
   langchain-community==0.0.20
   langgraph==0.0.20
   faiss-cpu==1.7.4
   pydantic-settings==2.1.0
   python-dotenv==1.0.0
   ```

3. **Initialize configuration files**
   - Copy `.env.example` template
   - Create `urls.txt` with initial URLs
   - Setup `config/settings.py`

### Phase 2: Core Services (Day 2)

4. **Implement FAISSService**
   - `services/faiss_service.py`
   - URL loading from file + env
   - Singleton pattern
   - Optional caching

5. **Implement ToolManager**
   - `tools/search_tools.py` - Wikipedia, DDG, ArXiv
   - `tools/rag_tools.py` - FAISS retriever wrapper
   - `tools/business_tools.py` - Import CRM/SQL tools

6. **Implement AgentService**
   - `services/agent_service.py`
   - Initialize LLM (ChatOpenAI)
   - Combine all tools
   - Create `agent_executor` with `create_react_agent`

### Phase 3: API Layer (Day 3)

7. **Create Pydantic models**
   - `api/models.py`
   - ChatRequest, ChatResponse, StreamEvent, HealthResponse

8. **Implement route handlers**
   - `api/routes.py`
   - `POST /chat` - blocking endpoint
   - `POST /chat-stream` - SSE streaming endpoint
   - `GET /health` - health check
   - `GET /tools` - list tools

9. **Setup main application**
   - `main.py`
   - Lifespan events (startup/shutdown)
   - Router registration
   - Error handling middleware

### Phase 4: Testing & Refinement (Day 4)

10. **Manual testing**
    - Test each endpoint with curl/Postman
    - Verify streaming works correctly
    - Test error scenarios

11. **Performance optimization**
    - Add response caching if needed
    - Optimize FAISS retrieval parameters
    - Configure uvicorn workers

12. **Documentation**
    - OpenAPI/Swagger docs (auto-generated)
    - Update README with API usage examples
    - Add example requests/responses

### Phase 5: Deployment Prep (Day 5)

13. **Containerization** (optional)
    - Create `Dockerfile`
    - `docker-compose.yml` for multi-service setup
    - Health check configuration

14. **Environment validation**
    - Startup checks for required env vars
    - Graceful error messages for missing config
    - Tool initialization status logging

15. **Production readiness**
    - Add request logging
    - Setup error monitoring
    - Configure rate limiting (if needed)

---

## Dependencies

### Core Framework
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
```

### LangChain Ecosystem
```
langchain==0.1.0
langchain-openai==0.0.5
langchain-community==0.0.20
langchain-core==0.1.10
langgraph==0.0.20
langsmith==0.0.77
```

### Vector Store & Embeddings
```
faiss-cpu==1.7.4
openai==1.10.0
tiktoken==0.5.2
```

### Tools & Utilities
```
duckduckgo-search==4.1.0
wikipedia==1.4.0
arxiv==2.1.0
beautifulsoup4==4.12.3
lxml==5.1.0
```

### Configuration & Utils
```
python-dotenv==1.0.0
python-multipart==0.0.6
aiofiles==23.2.1
```

### Development
```
pytest==7.4.4
pytest-asyncio==0.21.1
httpx==0.26.0
black==24.1.1
ruff==0.1.14
```

---

## Testing Strategy

### Unit Tests

**Target**: Individual components in isolation

**Tools**:
- `pytest` for test framework
- `unittest.mock` for mocking external dependencies
- `pytest-asyncio` for async tests

**Test Files**:
```
back-end/tests/
├── test_services/
│   ├── test_agent_service.py
│   └── test_faiss_service.py
├── test_tools/
│   ├── test_search_tools.py
│   └── test_business_tools.py
└── test_api/
    └── test_routes.py
```

**Example Test**:
```python
@pytest.mark.asyncio
async def test_faiss_service_initialization():
    service = FAISSService()
    urls = ["https://example.com"]
    
    await service.initialize(urls)
    
    assert service.is_ready() == True
    assert service.retriever is not None
```

### Integration Tests

**Target**: API endpoints end-to-end

**Example**:
```python
def test_chat_endpoint(test_client):
    response = test_client.post("/chat", json={
        "message": "How many artists in the database?"
    })
    
    assert response.status_code == 200
    assert "response" in response.json()
    assert "tools_used" in response.json()
```

### Manual Testing Checklist

- [ ] `/chat` endpoint returns complete response
- [ ] `/chat-stream` endpoint streams SSE events
- [ ] `/health` endpoint shows all tools loaded
- [ ] `/tools` endpoint lists all 11 tools
- [ ] FAISS retriever works for LangSmith questions
- [ ] CRM tools retrieve business clients
- [ ] SQL tool queries Chinook database
- [ ] Wikipedia/ArXiv/DDG tools work correctly
- [ ] Error handling for invalid requests
- [ ] Error handling for tool failures

---

## Error Handling Strategy

### Levels of Error Handling

1. **Request Validation** (API Layer)
   - Pydantic models validate input
   - Return 422 for validation errors

2. **Tool Execution** (Service Layer)
   - Catch tool-specific exceptions
   - Log error details
   - Return graceful error message to user

3. **Agent Execution** (Service Layer)
   - Timeout protection (max 60 seconds)
   - Fallback response on failure
   - Log full trace for debugging

4. **System Errors** (Global)
   - Catch unhandled exceptions
   - Return 500 with sanitized message
   - Log full stack trace

### Example Error Response Format

```json
{
  "error": {
    "type": "ToolExecutionError",
    "message": "Failed to retrieve business clients from CRM",
    "details": "Database connection timeout after 30 seconds",
    "timestamp": "2026-02-13T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

---

## Logging Strategy

### Log Levels

- **DEBUG**: Tool selection, intermediate reasoning steps
- **INFO**: Request received, response sent, tool execution started/completed
- **WARNING**: Tool fallback, degraded performance, retry attempts
- **ERROR**: Tool failures, agent errors, validation errors
- **CRITICAL**: Service initialization failures, unrecoverable errors

### Structured Logging Format

```json
{
  "timestamp": "2026-02-13T10:30:00.123Z",
  "level": "INFO",
  "logger": "agent_service",
  "message": "Agent execution completed",
  "context": {
    "request_id": "req_abc123",
    "user_message": "How many clients?",
    "tools_used": ["get_business_client_count"],
    "execution_time_ms": 1234,
    "tokens_used": 156
  }
}
```

### Key Events to Log

- API request received (with message hash for privacy)
- Agent execution started
- Each tool call (name, input, output length)
- Agent execution completed (total time, tokens)
- Errors at any level (with full context)
- FAISS initialization (URLs loaded, documents embedded)

---

## Performance Considerations

### Optimization Targets

| Metric | Target | Strategy |
|--------|--------|----------|
| **Startup Time** | < 5 seconds | FAISS cache, lazy loading |
| **Response Time (blocking)** | < 3 seconds | Efficient tools, timeout limits |
| **Memory Usage** | < 500 MB | Limit FAISS index size, cleanup |
| **Concurrent Requests** | 10+ | Async handlers, worker processes |

### Bottlenecks & Solutions

1. **FAISS Initialization**
   - Problem: Slow web scraping + embedding
   - Solution: Cache to disk, load on startup

2. **LLM API Calls**
   - Problem: 1-2 second latency per call
   - Solution: Use streaming, optimize prompts, reduce tokens

3. **Tool Execution**
   - Problem: External API timeouts
   - Solution: Parallel tool calls (if possible), timeout limits

4. **Concurrent Requests**
   - Problem: Single-threaded blocking
   - Solution: Uvicorn workers, async handlers

---

## Security Considerations (Future Enhancement)

### Current State: No Authentication

**Risk**: API is publicly accessible

### Future Enhancements

1. **API Key Authentication**
   - Add `X-API-Key` header validation
   - Store keys in database with rate limits

2. **Input Sanitization**
   - Already handled by Pydantic validation
   - Additional checks for SQL injection in CRM/SQL tools

3. **CORS Configuration**
   - Restrict origins in production
   - Currently allows all localhost ports in development

---

## Rate Limiting Implementation

### Configuration (Disabled by Default)

Rate limiting is **disabled by default** for development. Enable via `.env`:

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### Implementation with SlowAPI

**Install dependency**:
```bash
pip install slowapi
```

**`main.py` integration**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from config.settings import settings

# Initialize limiter (only if enabled)
limiter = None
if settings.rate_limit_enabled:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[
            f"{settings.rate_limit_per_minute}/minute",
            f"{settings.rate_limit_per_hour}/hour"
        ]
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to specific endpoints
@app.post("/chat")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute") if limiter else lambda f: f
async def chat_endpoint(request: ChatRequest):
    # ...endpoint logic
```

**Rate limit response** (429):
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Limit: 60 per minute",
  "retry_after": 30
}
```

**Development Note**: Keep `RATE_LIMIT_ENABLED=false` during development to avoid interruptions during testing.

---

## Deployment Options

### Option 1: Development (Uvicorn - Recommended)

```bash
cd agentic-rag-usecase/back-end

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Initialize databases (creates db/crm.db and db/chinook.db)
python db/init_databases.py

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 9080
```

**Access points**:
- API: http://localhost:9080
- Swagger docs: http://localhost:9080/docs
- ReDoc: http://localhost:9080/redoc
- Health check: http://localhost:9080/health

**Development features**:
- Auto-reload on code changes (`API_RELOAD=true`)
- Detailed logging (`LOG_LEVEL=INFO`, `LOG_FORMAT=text`)
- CORS enabled for local frontends
- Rate limiting disabled
- Full Swagger/OpenAPI documentation

---

### Option 2: Production (Uvicorn + Gunicorn)

```bash
# Update .env for production
API_ENV=production
API_RELOAD=false
API_WORKERS=4
LOG_FORMAT=json
DOCS_ENABLED=false  # Disable in production for security

# Run with Gunicorn
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:9080 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

---

### Option 3: Docker

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create db directory
RUN mkdir -p db logs

# Expose port
EXPOSE 9080

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9080", "--workers", "1"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "9080:9080"
    env_file:
      - .env
    volumes:
      - ./db:/app/db
      - ./logs:/app/logs
      - ./.faiss_cache:/app/.faiss_cache
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
```

**Build and run**:
```bash
docker-compose up -d
docker-compose logs -f  # View logs
```

### Option 4: Cloud Deployment

**AWS**:
- Elastic Beanstalk (easiest)
- ECS/Fargate (containerized)
- Lambda + API Gateway (serverless, requires cold start optimization)

**Azure**:
- App Service (PaaS)
- Container Instances
- Functions (serverless)

**GCP**:
- Cloud Run (serverless containers)
- App Engine
- Compute Engine

---

## Monitoring & Observability

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if agent_service.is_ready() else "degraded",
        "checks": {
            "agent": agent_service.is_ready(),
            "faiss": faiss_service.is_ready(),
            "llm": await check_openai_connection(),
            "crm_db": await check_crm_connection(),
            "sql_db": await check_chinook_connection()
        }
    }
```

### Metrics to Track

- Request count by endpoint
- Average response time by endpoint
- Tool usage frequency
- Error rate by tool
- Token consumption
- Active connections (streaming)

### LangSmith Integration (Optional)

- Already in notebook (pulls prompt)
- Enable tracing in production:
  ```env
  LANGCHAIN_TRACING_V2=true
  LANGCHAIN_API_KEY=lsv2_xxxxx
  LANGCHAIN_PROJECT=agentic-rag-api
  ```

- Benefits:
  - Trace every agent execution
  - Debug tool selection
  - Monitor LLM performance
  - Analyze failure patterns

---

## Migration from Notebook

### Code Transformation Map

| Notebook Cell | API Component | Changes |
|---------------|---------------|---------|
| Imports (cell 2) | `tools/search_tools.py` | Modularized |
| Import CRM tools (cell 4) | `tools/business_tools.py` | Wrapped in functions |
| DuckDuckGo tool (cell 5) | `tools/search_tools.py` | Extracted as function |
| Wikipedia tool (cell 6) | `tools/search_tools.py` | Extracted, fixed typo |
| FAISS setup (cells 7-9) | `services/faiss_service.py` | Singleton, cached |
| ArXiv tool (cells 10-11) | `tools/search_tools.py` | Extracted as function |
| Tools list (cell 12) | `services/agent_service.py` | Aggregated in `initialize()` |
| LLM setup (cell 13) | `services/agent_service.py` | From config |
| Prompt pull (cell 14) | REMOVED | Unused in notebook |
| Agent creation (cell 15) | `services/agent_service.py` | In `initialize()` |
| Test queries (cells 16+) | NOT MIGRATED | Replaced by API endpoints |

### Behavior Preservation

✅ **Preserved**:
- Exact same tools with same configurations
- Same LLM (GPT-4o, temp=0.1, max_tokens=2000)
- Same agent type (ReAct via `create_react_agent`)
- Same streaming behavior (chunk-by-chunk)
- Same blocking behavior (full response wait)

⚠️ **Changed**:
- FAISS built once instead of per-query
- Tools initialized as singletons
- Added error handling and logging
- Wrapped in HTTP layer

---

## Success Criteria

### Functional Requirements

- [ ] API starts successfully with all tools loaded
- [ ] `/chat` endpoint produces same responses as notebook `invoke()`
- [ ] `/chat-stream` endpoint streams same chunks as notebook `stream()`
- [ ] All 11 tools are accessible and functional
- [ ] FAISS retriever works for LangSmith questions
- [ ] CRM tools access business client database
- [ ] SQL tool queries Chinook database
- [ ] External tools (Wikipedia, ArXiv, DDG) work

### Non-Functional Requirements

- [ ] Startup time < 5 seconds (with FAISS cache)
- [ ] Response time < 3 seconds for simple queries
- [ ] Memory usage < 500 MB
- [ ] Handles 10+ concurrent requests
- [ ] Error handling for all failure modes
- [ ] Structured logging for debugging
- [ ] OpenAPI documentation auto-generated

### Documentation Requirements

- [ ] README with setup instructions
- [ ] API usage examples (curl, Python client)
- [ ] Environment variable reference
- [ ] Troubleshooting guide
- [ ] Architecture diagram

---

## Next Steps

1. **Review this guide** - Confirm architecture and approach
2. **Approve folder structure** - Any changes needed?
3. **Confirm configuration approach** - `.env` + `urls.txt` acceptable?
4. **Begin implementation** - Start with Phase 1 (project setup)
5. **Iterate** - Build incrementally, test each phase

---

## Questions for Review

~~Before implementation, please confirm:~~

### ✅ **CONFIRMED Requirements** (Updated Feb 13, 2026)

1. ✅ **Folder structure**: Layered architecture (api/, services/, tools/, config/, db/)
2. ✅ **FAISS caching**: Implement with cache-to-disk, load on startup
3. ✅ **Endpoints**: Both `/chat` (blocking) and `/chat-stream` (SSE streaming)
4. ✅ **Port**: 9080 (not 8000)
5. ✅ **Environment**: Development build with uvicorn
6. ✅ **Configuration**: All settings in `.env` file
7. ✅ **Dependencies**: No external folder dependencies - CRM/SQL tools local in `tools/`
8. ✅ **Databases**: Local SQLite databases in `back-end/db/` folder
9. ✅ **Rate limiting**: Disabled by default, configurable via `.env`
10. ✅ **Documentation**: OpenAPI/Swagger enabled at `/docs`
11. ✅ **Response structure**: Based on analyzed `streamed-response.py` and `direct-response.py`

---

## Summary of Changes from Original Guide

### ✨ **New Requirements Incorporated**

| Category | Change | Rationale |
|----------|--------|-----------|
| **Dependencies** | CRM/SQL tools moved to `back-end/tools/` | Self-contained API, no parent folder dependencies |
| **Databases** | SQLite DBs in `back-end/db/` folder | Portable, included with API deployment |
| **Port** | Changed from 8000 → 9080 | User preference |
| **Environment** | All config in `.env`, development mode | Easier configuration management |
| **Rate Limiting** | Disabled by default | Development-friendly, opt-in for production |
| **Response Analysis** | Added section analyzing actual notebook outputs | Based on `streamed-response.py` & `direct-response.py` |
| **Documentation** | OpenAPI/Swagger at `/docs` (enabled) | Auto-generated, already built into FastAPI |
| **Tool Files** | Split into `crm_tools.py` and `sql_tools.py` | Clear separation of concerns |

### 📋 **Configuration Highlights**

```env
# Key development settings
API_PORT=9080
API_ENV=development
API_RELOAD=true
RATE_LIMIT_ENABLED=false
DOCS_ENABLED=true
LOG_FORMAT=text

# Database paths (relative to back-end/)
CRM_DATABASE_PATH=db/crm.db
CHINOOK_DATABASE_PATH=db/chinook.db
```

### 🚀 **Quick Start Command**

```bash
cd agentic-rag-usecase/back-end
cp .env.example .env  # Edit and add OPENAI_API_KEY
python db/init_databases.py
uvicorn main:app --reload --host 0.0.0.0 --port 9080

# Access at: http://localhost:9080/docs
```

---

**Document Status**: ✅ **Updated & Ready for Implementation**  
**Last Updated**: February 13, 2026  
**Next Action**: Begin Phase 1 implementation  
**Estimated Implementation Time**: 3-5 days (based on 5-phase plan)
