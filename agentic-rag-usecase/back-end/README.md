# Agentic RAG REST API

Convert the agentic RAG notebook into a production-ready REST API with multiple tools (Wikipedia, ArXiv, DuckDuckGo, CRM database, Music database, and custom RAG).

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- Git

### Installation

1. **Clone the repository** (if not already cloned)
   ```bash
   cd agentic-rag-usecase/back-end
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env and add your OPENAI_API_KEY
   # Required: OPENAI_API_KEY=sk-proj-xxxxx
   ```

5. **Initialize databases**
   ```bash
   python db/init_databases.py
   ```

6. **Run the development server**
   ```bash
   # Option 1: Using Python directly
   python main.py
   
   # Option 2: Using uvicorn
   uvicorn main:app --reload --host 0.0.0.0 --port 9080
   
   # Option 3: Using Docker (recommended for production)
   docker-compose up -d
   ```

7. **Access the API**
   - **Swagger UI**: http://localhost:9080/docs
   - **ReDoc**: http://localhost:9080/redoc
   - **Health Check**: http://localhost:9080/health

## 📁 Project Structure

```
back-end/
├── main.py                 # FastAPI application entry point ✅
├── requirements.txt        # Python dependencies ✅
├── .env                    # Environment configuration (create from .env.example)
├── .env.example           # Environment template ✅
├── .env.production        # Production environment template ✅
├── Dockerfile             # Multi-stage Docker container ✅
├── docker-compose.yml     # Docker Compose configuration ✅
├── .dockerignore          # Docker build exclusions ✅
├── urls.txt               # URLs for FAISS indexing
│
├── api/                   # REST API layer (Phase 3) ✅
│   ├── __init__.py
│   ├── routes.py          # Endpoint definitions
│   ├── models.py          # Pydantic request/response models
│   ├── dependencies.py    # Dependency injection
│   └── middleware.py      # Error handling middleware (Phase 4) ✅
│
├── services/              # Business logic (Phase 2) ✅
│   ├── __init__.py
│   ├── agent_service.py   # Agent executor management
│   └── faiss_service.py   # FAISS vector store
│
├── tools/                 # LangChain tools (Phase 2) ✅
│   ├── __init__.py
│   ├── search_tools.py    # Wikipedia, ArXiv, DuckDuckGo
│   ├── crm_tools.py       # Business client database
│   └── sql_tools.py       # Chinook music database
│
├── config/                # Configuration (Phase 1) ✅
│   ├── __init__.py
│   ├── settings.py        # Pydantic settings
│   └── logging_config.py  # Logging setup
│
├── db/                    # Databases (Phase 2)
│   ├── crm.db            # CRM database (SQLite ✅
│   ├── __init__.py
│   ├── models.py          # SQLAlchemy models
│   ├── manager.py         # Database manager
│   ├── init_databases.py  # Database initialization
│   ├── crm.db            # CRM database (SQLi4) ✅
│   ├── __init__.py
│   └── helpers.py        # Helper functions (timestamp, validation, etc.)
│
├── tests/                 # Test files ✅
│   ├── __init__.py
│   ├── test_phase1.py     # Phase 1: Configuration validation
│   ├── test_phase2.py     # Phase 2: Services & tools
│   ├── test_phase3.py     # Phase 3: API layer
│   ├── test_phase4.py     # Phase 4: Error handling validation
│   ├── test_integration.py  # Integration tests (full workflow)
│   └── test_api.py        # API endpoint tests (mocked)
│   ├── __init__.py
│   └── test_phase1.py    # Phase 1 verification
│
├── logs/                  # Log files (auto-created)
├── faiss_cache/           # FAISS vector store cache (auto-created)
└── docs/                  # Documentation ✅
    ├── AGENTIC_RAG_API_IMPLEMENTATION_GUIDE.md
    ├── DEPLOYMENT_GUIDE.md          # Production deployment guide ✅
    ├── PRODUCTION_CHECKLIST.md      # Pre-deployment checklist ✅
    └── API_GUIDE.md
```

## ⚙️ Configuration

All configuration is managed through environment variables in `.env` file.

### Key Configuration Options

```env
# OpenAI (Required)
OPENAI_API_KEY=sk-proj-xxxxx

# API Server
API_PORT=9080
API_ENV=development
API_RELOAD=true

# Rate Limiting (disabled by default)
RATE_LIMIT_ENABLED=false

# Documentation (enabled for development)
DOCS_ENABLED=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=text
```

See `.env.example` for complete configuration options.

## 🔧 Development✅ COMPLETE
- [x] FAISS service
- [x] Search tools (Wikipedia, ArXiv, DuckDuckGo)
- [x] Database tools (CRM, Chinook)
- [x] Agent service

### Phase 3: API Endpoints ✅ COMPLETE
- [x] `/chat` - Blocking chat endpoint
- [x] `/chat-stream` - Streaming chat (SSE)
- [x] `/health` - Health check
- [x] `/tools` - List available tools

### Phase 4: Testing & Error Handling ✅ COMPLETE
- [x] Error handling middleware
- [x] Global exception handlers
- [x] Utility functions
- [x] Integration tests
- [x] API endpoint tests
- [x] Phase 4 validation testsstream` - Streaming chat (SSE)
- [ ] `/health` - Health check
- [ ] `/tools` - List available tools

### Phase 4: Testing & Error Handling
- [ ] Error handling
- [ ] Request validation
- [ ] Rate limiting
- [ ] Logging

### Phase 5: Documentation & Deployment ✅ COMPLETE
- [x] Docker configuration (Dockerfile, docker-compose.yml)
- [x] Production environment template (.env.production)
- [x] Deployment guide (DEPLOYMENT_GUIDE.md)
- [x] Production readiness checklist (PRODUCTION_CHECKLIST.md)
- [x] .dockerignore configuration

## 📝 Testing Configuration (Phase 1)

Test that configuration loads correctly:

```bash
python tests/test_phase1.py
```

## 🧪 Testing Phase 2

Test database initialization, tools, and services:

```bash
python tests/test_phase2.py
```

## 🧪 Testing Phase 4

Test error handling, middleware, and utilities:

```bash
python tests/test_phase4.py
```

### Integration Tests

Test full workflow from API to agent response:

```bash
python tests/test_integration.py
```

### API Endpoint Tests

Test individual endpoints with mocked services:

```bash
python tests/test_api.py
```

### Run All Tests

```bash
# Run all tests with pytest
pytest tests/ -v

# Run specific test file
pytest tests/test_phase4.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

**Note**: Some tests will be skipped if `OPENAI_API_KEY` is not set in `.env` file.

## 🧪 Testing Phase 3

Test API layer (models, routes, FastAPI app):

```bash
python tests/test_phase3.py
```

## 🚀 Running the API Server

### Development Mode

Start the development server:

```bash
# Using Python directly
python main.py

# Or with uvicorn for auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 9080
```

### Production Mode (Docker)

**Recommended** for production deployment:

```bash
# 1. Configure environment
cp .env.production .env
# Edit .env and set OPENAI_API_KEY

# 2. Start with Docker Compose
docker-compose up -d

# 3. View logs
docker-compose logs -f

# 4. Check health
curl http://localhost:9080/health
```

### Access the API

The server will start on `http://localhost:9080` with:
- **Interactive API docs**: http://localhost:9080/docs (development only)
- **Alternative docs**: http://localhost:9080/redoc (development only)
- **Health check**: http://localhost:9080/health
- **Tools list**: http://localhost:9080/tools

Expected startup output (development mode):
```
======================================================================
AGENTIC RAG API - STARTUP
======================================================================
Validating configuration...
Initializing databases...
Initializing FAISS service...
Initializing agent service...
======================================================================
STARTUP COMPLETE ✓
API Server: http://0.0.0.0:9080
Documentation: http://0.0.0.0:9080/docs
======================================================================
```

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f agentic-rag-api

# Restart after changes
docker-compose up -d --build

# Execute command in container
docker-compose exec agentic-rag-api python db/init_databases.py

# Check resource usage
docker stats agentic-rag-api
```

## 🐛 Troubleshooting

### Configuration Issues

**Problem**: `ValidationError` when loading settings  
**Solution**: Ensure `.env` file exists and contains `OPENAI_API_KEY`

**Problem**: Module import errors  
**Solution**: Ensure virtual environment is activated and dependencies are installed

**Problem**: Docker container won't start  
**Solution**: Check logs with `docker-compose logs`, ensure OPENAI_API_KEY is set

### Dependency Issues

**Problem**: `pip install` fails  
**Solution**: Upgrade pip: `python -m pip install --upgrade pip`

**Problem**: Port 9080 already in use  
**Solution**: Change API_PORT in .env or stop conflicting service

## 📚 API Documentation

Once the server is running (Phase 3), visit:

- **Interactive Swagger UI**: http://localhost:9080/docs
- **Alternative ReDoc**: http://localhost:9080/redoc

## 🔐 Security

- **Development**: No authentication, rate limiting disabled
- **Production**: Enable rate limiting via `RATE_LIMIT_ENABLED=true`
- **API Keys**: Never commit `.env` file to git (already in `.gitignore`)

## 📄 License

See LICENSE file in project root.

## 🤝 Contributing

This is a demonstration project. See main project documentation for contribution guidelines.

---

**Current Status**: Phase 5 Complete ✅ - ALL PHASES COMPLETE! 🎉  
**Project Status**: Production-Ready 🚀

**Deployment**: See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for production setup  
**Checklist**: Review [PRODUCTION_CHECKLIST.md](docs/PRODUCTION_CHECKLIST.md) before deploying
