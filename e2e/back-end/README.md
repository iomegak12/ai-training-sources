# Agent Query API

A FastAPI-based REST service that provides intelligent query responses using LangChain agents with multiple data sources including Wikipedia, Google Search, Arxiv, and RAG (Retrieval-Augmented Generation).

## Features

- 🤖 **Multi-Source Agent**: Queries Wikipedia, Google Search, Arxiv, and custom RAG retriever
- 🚀 **FastAPI**: High-performance async API with automatic OpenAPI documentation
- 🌐 **CORS Enabled**: Allows requests from all origins
- 📚 **Swagger UI**: Interactive API documentation at `/docs`
- 🏥 **Health Check**: Monitoring endpoint at `/health`
- 🐳 **Docker Support**: Fully containerized with Docker and Docker Compose
- 📝 **Type Safety**: Pydantic models for request/response validation

## Technologies

- **FastAPI**: Modern web framework for building APIs
- **LangChain**: Framework for developing LLM applications
- **LangGraph**: State management for agent workflows
- **OpenAI**: GPT-4 for intelligent responses
- **FAISS**: Vector database for similarity search
- **Uvicorn**: ASGI server for production

## Prerequisites

- Python 3.11+
- OpenAI API Key
- Google Serper API Key (for Google Search)

## Installation

### Local Development

1. **Clone the repository**
   ```bash
   cd back-end
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     env\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source env/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create `.env` file**
   ```bash
   cp .env.example .env
   ```
   
   Add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SERPER_API_KEY=your_google_serper_api_key_here
   ```

6. **Run the application**
   ```bash
   cd src
   python main.py
   ```

   The API will be available at `http://localhost:8000`

### Docker Deployment

1. **Create `.env` file** with your API keys (same as above)

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Run in detached mode**
   ```bash
   docker-compose up -d
   ```

4. **Stop the service**
   ```bash
   docker-compose down
   ```

## API Documentation

### Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

#### Query Agent
```http
POST /query
```

**Request Body:**
```json
{
  "query": "What is LangSmith?"
}
```

**Response:**
```json
{
  "answer": "LangSmith is a platform for building, debugging, and monitoring LLM applications..."
}
```

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
back-end/
├── src/
│   ├── main.py              # FastAPI application and endpoints
│   ├── query_handler.py     # Query handler function
│   └── agent.py             # LangChain agent configuration
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image configuration
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore          # Docker ignore patterns
├── .gitignore             # Git ignore patterns
├── LICENSE                # MIT License
└── README.md              # This file
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | Yes |
| `SERPER_API_KEY` | Google Serper API key for search | Yes |

## Agent Tools

The agent has access to the following tools:

1. **Google Search**: Real-time web search using Google Serper API
2. **Wikipedia Search**: Encyclopedia queries with Wikipedia API
3. **Arxiv Search**: Academic paper search
4. **LangSmith RAG**: Custom retriever for LangSmith documentation

## Error Handling

The API includes error handling for:
- Empty queries (400 Bad Request)
- Invalid input (400 Bad Request)
- Server errors (500 Internal Server Error)

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black src/
```

### Linting
```bash
flake8 src/
```

## Docker Commands

```bash
# Build the image
docker-compose build

# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build
```

## Production Considerations

- Set appropriate CORS origins instead of allowing all
- Add rate limiting
- Implement authentication/authorization
- Use environment-specific configurations
- Set up logging and monitoring
- Configure SSL/TLS certificates
- Use a production-grade ASGI server configuration

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues and questions, please open an issue in the repository.

## Acknowledgments

- LangChain team for the amazing framework
- OpenAI for GPT-4
- FastAPI team for the excellent web framework
