# Agentic RAG Use Case

A comprehensive agentic RAG (Retrieval-Augmented Generation) system demonstrating multi-database querying, business intelligence, and intelligent tool orchestration using LangChain and LangGraph.

## 🎯 Overview

This project showcases an advanced AI agent that can:
- Query and analyze **business client data** from a CRM database
- Perform **complex SQL analytics** on a music store database (Chinook)
- Search the web using **DuckDuckGo**
- Access **Wikipedia** for general knowledge
- Search **academic papers** via ArXiv
- Retrieve information from **LangSmith documentation**

The agent intelligently selects and combines the right tools to answer complex, multi-faceted questions.

## 🏗️ Project Structure

```
agentic-rag-usecase/
│
├── customers_management/          # Business Client & Database Tools
│   ├── __init__.py               # Package initialization
│   ├── models.py                 # SQLAlchemy Customer model
│   ├── manager.py                # CustomerManager (CRUD operations)
│   ├── customer_tools.py         # 6 Business Client retrieval tools
│   ├── sql_query_tool.py         # Chinook SQL query tool (Complex Answer Chain)
│   ├── sample_data.py            # India-based sample data generator
│   ├── demo.py                   # Standalone demo script
│   ├── requirements.txt          # Dependencies
│   └── README.md                 # Library documentation
│
├── notebooks/                    # Jupyter Notebooks
│   └── agentic-rag.ipynb        # Main agentic RAG demonstration
│
├── tests/                        # Test Suite
│   ├── __init__.py
│   └── test_customer_management.py  # Comprehensive tests (14 test cases)
│
├── db/                           # Databases
│   ├── customers.db             # Business client database (25 India-based records)
│   └── chinook.db               # Music store database (Artists, Albums, Sales)
│
├── .env                         # Environment configuration (not in repo)
├── CUSTOMER_LIBRARY_OVERVIEW.md # Customer management library overview
└── README.md                    # This file
```

## 🔧 Components

### 1. Business Client Management (CRM)

**Database**: `customers.db` (SQLite)  
**Tools**: 6 read-only retrieval tools

- `get_business_client_by_id` - Retrieve client by ID
- `get_business_client_by_email` - Find client by email
- `get_all_business_clients` - List all clients
- `get_active_business_clients` - Filter active clients only
- `search_business_clients` - Search by name/email
- `get_business_client_count` - Get statistics

**Schema**:
- customer_id (primary key)
- name, address, email, phone
- credit (rupee balance)
- active_status (active/inactive)

**Sample Data**: 25 India-based business clients with realistic data

### 2. Music Store Analytics (Chinook Database)

**Database**: `chinook.db` (SQLite)  
**Tool**: `query_music_database` - Complex Answer Chain pattern

**Capabilities**:
- Converts natural language → SQL queries
- Executes against music store database
- Returns professional, business-formatted answers

**Schema**: Artists, Albums, Tracks, Genres, Customers, Invoices, Employees, Playlists

**Example Queries**:
- "Which artist has the most albums?"
- "Which country's customers have spent the most?"
- "What are the most popular genres?"

### 3. External Knowledge Tools

- **Wikipedia** - General knowledge and historical information
- **DuckDuckGo** - Web search for current information
- **ArXiv** - Academic paper search by ID or topic
- **LangSmith Docs** - Framework documentation retrieval

### 4. Agentic Orchestration

**Framework**: LangGraph (ReAct agent)  
**LLM**: GPT-4o  
**Total Tools**: 11 (4 external + 6 business client + 1 SQL)

The agent intelligently:
- Selects appropriate tools based on user questions
- Combines multiple tools for complex queries
- Provides coherent, professional answers

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Virtual environment (recommended)
- OpenAI API key

### Installation

1. **Clone/Navigate to the project**:
   ```bash
   cd agentic-rag-usecase
   ```

2. **Install dependencies**:
   ```bash
   pip install sqlalchemy langchain langchain-community langchain-openai langgraph
   ```

3. **Set up environment variables**:
   
   Create a `.env` file in the root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   MODEL_NAME=gpt-4o
   
   # Database Paths
   CUSTOMER_DB_PATH=sqlite:///d:/path/to/agentic-rag-usecase/db/customers.db
   CHINOOK_DB_PATH=sqlite:///d:/path/to/agentic-rag-usecase/db/chinook.db
   ```

4. **Initialize sample data** (optional):
   ```bash
   python -m customers_management.sample_data
   ```

### Usage

#### Option 1: Jupyter Notebook (Recommended)

1. Open `notebooks/agentic-rag.ipynb`
2. Run cells sequentially
3. Try the demo queries or create your own

#### Option 2: Standalone Demo

```bash
python -m customers_management.demo
```

#### Option 3: Programmatic Usage

```python
from customers_management import CustomerManager, business_client_tools
from customers_management.sql_query_tool import chinook_sql_tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

# Combine tools
all_tools = business_client_tools + [chinook_sql_tool]

# Create agent
agent = create_react_agent(llm, tools=all_tools)

# Query
response = agent.invoke({
    "messages": [{"role": "user", "content": "How many business clients do we have?"}]
})
```

## 💡 Example Queries

### Business Client Queries (CRM)
```
"How many business clients are in our CRM?"
"Find business clients with name 'Sharma'"
"Show me the details of business client ID 5"
"What's the total credit of all active business clients?"
```

### Music Store Analytics
```
"Which artist has the most albums in the music database?"
"Which country's customers have spent the most? Give top 5"
"What are the most popular music genres?"
"How many tracks are in each genre?"
```

### Multi-Tool Queries
```
"How many active business clients do we have? Also tell me about the Indian Constitution from Wikipedia"
"Tell me about the top selling artist in the music database and search Wikipedia for their history"
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd agentic-rag-usecase
python -m tests.test_customer_management
```

**Test Coverage**:
- 13 functional tests for CustomerManager
- CRUD operations validation
- Edge case handling
- Sample data generation

## 🎓 Key Concepts Demonstrated

### 1. Tool Disambiguation
Clear separation between:
- **Business Clients** (CRM database) - Your business relationships
- **Music Store Customers** (Chinook) - Music purchase data

### 2. Complex Answer Chain Pattern
The SQL query tool implements the sophisticated pattern:
```
Question → SQL Generation → Parsing → Execution → Professional Answer
```

### 3. Agentic RAG
- Agent selects tools dynamically based on user intent
- Combines multiple data sources seamlessly
- Provides coherent answers from disparate sources

### 4. ORM + Tools Integration
- SQLAlchemy for structured database operations
- LangChain tools for AI agent integration
- Best of both worlds: type safety + flexibility

## 📊 Database Details

### Business Clients Database
- **Records**: 25 India-based clients
- **Active**: 20 (80%)
- **Inactive**: 5 (20%)
- **Credit Range**: ₹0 - ₹1,00,000

### Chinook Database
- **Artists**: 275
- **Albums**: 347
- **Tracks**: 3,503
- **Customers**: 59
- **Invoices**: 412

## 🔐 Security Notes

- All tools are **read-only** - no CRUD operations exposed to agent
- No sensitive data in version control (`.env` excluded)
- SQL injection protected by LangChain's query validation

## 📝 Documentation

- [Customer Library Overview](CUSTOMER_LIBRARY_OVERVIEW.md) - Detailed library documentation
- [Customer Management README](customers_management/README.md) - API reference
- [Agentic RAG Notebook](notebooks/agentic-rag.ipynb) - Interactive examples

## 🛠️ Technology Stack

- **AI Framework**: LangChain, LangGraph
- **LLM**: OpenAI GPT-4o
- **Database**: SQLite + SQLAlchemy ORM
- **Tools**: Wikipedia, DuckDuckGo, ArXiv, FAISS
- **Language**: Python 3.12

## 🚧 Future Enhancements

- [ ] Add conversational memory to agent
- [ ] Implement custom business analytics tools
- [ ] Add data visualization capabilities
- [ ] Create REST API wrapper
- [ ] Add authentication/authorization
- [ ] Containerize with Docker

## 📄 License

MIT License

## 🤝 Contributing

This is a demonstration project for training purposes.

---

**Author**: Your Name  
**Created**: February 2026  
**Purpose**: Agentic RAG Training & Demonstration
