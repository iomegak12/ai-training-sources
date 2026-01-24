# Agentic RAG Backend

A production-ready REST API for an Agentic RAG (Retrieval-Augmented Generation) system using LangChain, LangGraph, and FastAPI.

## 🚀 Features

- **RESTful API** with FastAPI
- **Multiple AI-Powered Search Tools**:
  - Google Search (real-time web search)
  - Wikipedia Search (encyclopedic knowledge)
  - ArXiv Search (academic papers)
  - Custom Document Retriever (LangSmith docs)
- **OpenAPI/Swagger Documentation** at `/api-docs`
- **Health Check Endpoint** at `/health`
- **Rate Limiting** (configurable via .env)
- **CORS Support** (configurable)
- **Docker Support** with Docker Compose
- **Modular Architecture** for easy extension
- **Colorful Console Output** during startup
- **Vector Database Initialization** at startup

## 📁 Project Structure

```
back-end/
│
├── agents/
│   ├── __init__.py
│   └── agentic_rag.py          # Agent creation and configuration
│
├── api/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py          # Request models (Pydantic)
│   │   └── response.py         # Response models (Pydantic)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py           # Health check endpoint
│   │   ├── query.py            # Query endpoint
│   │   └── tools.py            # Tools listing endpoint
│   ├── __init__.py
│   └── dependencies.py         # Dependency injection
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Environment-based configuration
│
├── tools/
│   ├── __init__.py
│   ├── google_search.py        # Google search tool
│   ├── wikipedia.py            # Wikipedia tool
│   ├── arxiv.py                # ArXiv tool
│   └── retriever.py            # Document retriever tool
│
├── docs/
│   └── architecture-sequence.md # System architecture documentation
│
├── app.py                       # FastAPI application
├── main.py                      # CLI entry point (optional)
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker Compose configuration
├── .env.example                 # Environment variables template
├── .dockerignore                # Docker ignore rules
├── .gitignore                   # Git ignore rules
├── LICENSE                      # MIT License
└── README.md                    # This file
```

## 🛠️ Setup

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (optional)
- OpenAI API key
- Google Serper API key (optional, for web search)

### Local Development Setup

1. **Clone the repository**
   ```bash
   cd back-end
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   OPENAI_API_KEY=your-openai-api-key-here
   SERPER_API_KEY=your-serper-api-key-here  # Optional
   ```

5. **Run the application**
   ```bash
   python app.py
   ```
   
   Or with uvicorn:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 9090 --reload
   ```

6. **Access the API**
   - API Docs: http://localhost:9090/api-docs
   - Health Check: http://localhost:9090/health
   - OpenAPI Schema: http://localhost:9090/api-docs.json

### Docker Setup

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the API**
   - API: http://localhost:9090
   - API Docs: http://localhost:9090/api-docs
   - Health: http://localhost:9090/health

4. **Stop the service**
   ```bash
   docker-compose down
   ```

## 📡 API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-13T12:00:00.000000",
  "version": "1.0.0",
  "vector_db_initialized": true
}
```

### Query Agent
```http
POST /query
Content-Type: application/json

{
  "question": "What is LangSmith?",
  "max_tokens": 2000,
  "temperature": 0.1
}
```

**Response:**
```json
{
  "question": "What is LangSmith?",
  "answer": "LangSmith is a platform for building production-grade LLM applications...",
  "tools_used": ["langsmith_search"],
  "timestamp": "2025-11-13T12:00:00.000000"
}
```

### List Tools
```http
GET /tools
```

**Response:**
```json
{
  "tools": [
    {
      "name": "GoogleSearch",
      "description": "Search the internet for real-time information"
    },
    {
      "name": "WikipediaSearch",
      "description": "Search Wikipedia for encyclopedic information"
    },
    {
      "name": "ArxivQueryRun",
      "description": "Search ArXiv for academic papers"
    },
    {
      "name": "langsmith_search",
      "description": "Search LangSmith documentation"
    }
  ],
  "count": 4
}
```

## 🔧 Configuration

All configuration is managed through environment variables in the `.env` file:

### Required Settings
| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | **Required** |

### Optional API Settings
| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | API host address | 0.0.0.0 |
| `API_PORT` | API port number | 9090 |
| `API_TITLE` | API title | Agentic RAG API |
| `API_VERSION` | API version | 1.0.0 |
| `OPENAI_MODEL` | OpenAI model | gpt-4o |
| `OPENAI_MAX_TOKENS` | Max response tokens | 2000 |
| `OPENAI_TEMPERATURE` | Response temperature | 0.1 |
| `SERPER_API_KEY` | Google Serper API key | Optional |

### Rate Limiting (Disabled by Default)
| Variable | Description | Default |
|----------|-------------|---------|
| `RATE_LIMIT_ENABLED` | Enable rate limiting | false |
| `RATE_LIMIT_REQUESTS` | Requests allowed | 10 |
| `RATE_LIMIT_PERIOD` | Time period (seconds) | 60 |

### CORS Settings
| Variable | Description | Default |
|----------|-------------|---------|
| `CORS_ENABLED` | Enable CORS | true |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | * |

### Document Processing
| Variable | Description | Default |
|----------|-------------|---------|
| `CHUNK_SIZE` | Document chunk size | 1000 |
| `CHUNK_OVERLAP` | Chunk overlap size | 200 |
| `LANGSMITH_DOCS_URL` | LangSmith docs URL | https://docs.smith.langchain.com |

## 🐳 Docker

### Build Image
```bash
docker build -t agentic-rag-api .
```

### Run Container
```bash
docker run -p 9090:9090 --env-file .env agentic-rag-api
```

### Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d
```

## 📚 Usage Examples

### Using cURL

**Health Check:**
```bash
curl http://localhost:9090/health
```

**Query Agent:**
```bash
curl -X POST http://localhost:9090/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is LangSmith?"}'
```

**List Tools:**
```bash
curl http://localhost:9090/tools
```

### Using Python

```python
import requests

# Query the agent
response = requests.post(
    "http://localhost:9090/query",
    json={"question": "Tell me about quantum computing"}
)
print(response.json())

# List available tools
tools = requests.get("http://localhost:9090/tools")
print(tools.json())
```

### Using JavaScript/Node.js

```javascript
// Query the agent
const response = await fetch('http://localhost:9090/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: 'What is machine learning?' })
});
const data = await response.json();
console.log(data);
```

## 🎨 Startup Display

When the application starts, you'll see a colorful console output showing:
- ✅ Configuration settings
- ✅ Vector database initialization status
- ✅ AI agent creation status
- ✅ Available tools count
- ✅ API endpoint URLs

## 🧪 Testing

### Manual Testing
1. Start the server
2. Visit http://localhost:9090/api-docs
3. Use the interactive Swagger UI to test endpoints

### Automated Testing
```bash
# Install pytest
pip install pytest pytest-asyncio httpx

# Run tests (when test files are created)
pytest tests/
```

## 🔒 Security Notes

- ⚠️ Never commit your `.env` file with real API keys
- ⚠️ Use environment variables for all sensitive data
- ⚠️ Enable rate limiting in production
- ⚠️ Configure CORS properly for production use
- ⚠️ Consider adding authentication/authorization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- Agent framework by [LangGraph](https://langchain-ai.github.io/langgraph/)

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the API documentation at `/api-docs`
- Review the architecture documentation in `docs/`

---

**Built with ❤️ using LangChain, FastAPI, and Python**

