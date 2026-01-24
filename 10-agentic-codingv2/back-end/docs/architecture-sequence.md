# Agentic RAG - Architecture Sequence Diagram

This document illustrates the sequence of interactions between the main entry point and various components in the Agentic RAG system.

## System Flow

The following Mermaid diagram shows how the `main.py` module interacts with agents, tools, and configuration components during both direct and streaming query modes.

```mermaid
sequenceDiagram
    actor User
    participant Main as main.py
    participant Agent as agents/agentic_rag.py
    participant Config as config/settings.py
    participant LLM as ChatOpenAI
    participant Tools as tools/*
    participant GoogleTool as tools/google_search.py
    participant WikiTool as tools/wikipedia.py
    participant ArxivTool as tools/arxiv.py
    participant RetrieverTool as tools/retriever.py
    participant ReactAgent as LangGraph ReactAgent
    
    %% Direct Query Flow
    rect rgb(200, 220, 250)
        Note over User,ReactAgent: Direct Query Mode
        User->>Main: query_agent_direct("question")
        Main->>Agent: create_agent()
        
        Agent->>Config: validate()
        Config-->>Agent: settings validated
        
        Agent->>Config: get OPENAI settings
        Config-->>Agent: model, temperature, tokens, api_key
        
        Agent->>LLM: ChatOpenAI(settings)
        LLM-->>Agent: llm instance
        
        Agent->>GoogleTool: create_google_search_tool()
        GoogleTool-->>Agent: google_search tool
        
        Agent->>WikiTool: create_wikipedia_tool()
        WikiTool->>Config: get WIKIPEDIA settings
        WikiTool-->>Agent: wikipedia tool
        
        Agent->>ArxivTool: create_arxiv_tool()
        ArxivTool->>Config: get ARXIV settings
        ArxivTool-->>Agent: arxiv tool
        
        Agent->>RetrieverTool: create_retriever_tool()
        RetrieverTool->>Config: get CHUNK_SIZE, CHUNK_OVERLAP
        RetrieverTool-->>Agent: retriever tool
        
        Agent->>ReactAgent: create_react_agent(llm, tools)
        ReactAgent-->>Agent: agent_executor
        
        Agent-->>Main: agent_executor
        
        Main->>ReactAgent: invoke({"messages": [HumanMessage]})
        
        ReactAgent->>LLM: process question
        LLM-->>ReactAgent: determine which tools to use
        
        alt Tool: Google Search
            ReactAgent->>GoogleTool: execute search
            GoogleTool-->>ReactAgent: search results
        else Tool: Wikipedia
            ReactAgent->>WikiTool: execute search
            WikiTool-->>ReactAgent: wiki results
        else Tool: ArXiv
            ReactAgent->>ArxivTool: execute search
            ArxivTool-->>ReactAgent: paper results
        else Tool: Retriever
            ReactAgent->>RetrieverTool: execute retrieval
            RetrieverTool-->>ReactAgent: document results
        end
        
        ReactAgent->>LLM: synthesize answer with tool results
        LLM-->>ReactAgent: final answer
        
        ReactAgent-->>Main: complete response
        Main-->>User: return response
    end
    
    %% Streaming Query Flow
    rect rgb(250, 220, 200)
        Note over User,ReactAgent: Streaming Query Mode
        User->>Main: query_agent_streaming("question")
        Main->>Agent: create_agent()
        
        Note over Agent,RetrieverTool: (Same initialization as above)
        Agent-->>Main: agent_executor
        
        Main->>ReactAgent: stream({"messages": [HumanMessage]})
        
        loop For each chunk
            ReactAgent->>LLM: process next chunk
            
            opt Tool needed
                ReactAgent->>Tools: execute tool
                Tools-->>ReactAgent: tool result
            end
            
            LLM-->>ReactAgent: response chunk
            ReactAgent-->>Main: yield chunk
            Main-->>User: yield chunk
        end
    end
```

## Component Responsibilities

### main.py
- Entry point for the application
- Provides two query interfaces: `query_agent_direct()` and `query_agent_streaming()`
- Manages user interaction and response formatting

### agents/agentic_rag.py
- Creates and configures the React agent
- Initializes the LLM with settings from config
- Orchestrates tool creation and registration
- Returns configured agent executor

### config/settings.py
- Loads environment variables from `.env` file
- Provides centralized configuration for all components
- Validates required settings (e.g., API keys)

### tools/*
Individual tool modules that provide specialized search capabilities:
- **google_search.py**: Real-time web search via Serper API
- **wikipedia.py**: Encyclopedia search
- **arxiv.py**: Academic paper search
- **retriever.py**: Custom document retrieval (LangSmith docs)

### LangGraph ReactAgent
- Orchestrates the conversation flow
- Decides which tools to call based on the question
- Synthesizes final answers using LLM and tool results
- Supports both direct invocation and streaming

## Query Modes

### Direct Mode
1. User calls `query_agent_direct()`
2. Agent is created with all tools
3. Question is sent via `invoke()`
4. Complete response is returned at once

### Streaming Mode
1. User calls `query_agent_streaming()`
2. Agent is created with all tools
3. Question is sent via `stream()`
4. Response chunks are yielded as they're generated
5. User can process each chunk in real-time

## Tool Selection

The ReactAgent automatically selects appropriate tools based on the question:
- **Current events/real-time info** → Google Search
- **General knowledge/topics** → Wikipedia
- **Academic papers** → ArXiv
- **LangSmith questions** → Retriever Tool

Multiple tools can be used in a single query if needed.
