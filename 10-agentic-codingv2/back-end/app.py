"""
FastAPI Application for Agentic RAG API

This module initializes and configures the FastAPI application,
including startup events, middleware, and routing.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import colorama
from colorama import Fore, Back, Style

from config.settings import settings
from api.routers import health_router, query_router, tools_router
from api.dependencies import app_state
from api.models import ToolInfo
from agents import create_agent
from tools import (
    create_google_search_tool,
    create_wikipedia_tool,
    create_arxiv_tool,
    create_retriever_tool
)

# Initialize colorama
colorama.init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print a colorful startup banner."""
    print(f"\n{Fore.CYAN}{'=' * 80}")
    print(f"{Fore.CYAN}{Back.BLUE}{Style.BRIGHT} Agentic RAG API {Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 80}\n")


def print_config():
    """Print configuration settings in a colorful format."""
    print(f"{Fore.GREEN}{Style.BRIGHT}📋 Configuration Settings:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  API Title:        {Fore.WHITE}{settings.API_TITLE}")
    print(f"{Fore.YELLOW}  API Version:      {Fore.WHITE}{settings.API_VERSION}")
    print(f"{Fore.YELLOW}  Host:             {Fore.WHITE}{settings.API_HOST}")
    print(f"{Fore.YELLOW}  Port:             {Fore.WHITE}{settings.API_PORT}")
    print(f"{Fore.YELLOW}  OpenAI Model:     {Fore.WHITE}{settings.OPENAI_MODEL}")
    print(f"{Fore.YELLOW}  Max Tokens:       {Fore.WHITE}{settings.OPENAI_MAX_TOKENS}")
    print(f"{Fore.YELLOW}  Temperature:      {Fore.WHITE}{settings.OPENAI_TEMPERATURE}")
    print(f"{Fore.YELLOW}  Rate Limiting:    {Fore.WHITE}{'Enabled' if settings.RATE_LIMIT_ENABLED else 'Disabled'}")
    if settings.RATE_LIMIT_ENABLED:
        print(f"{Fore.YELLOW}    - Requests:     {Fore.WHITE}{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_PERIOD}s")
    print(f"{Fore.YELLOW}  CORS:             {Fore.WHITE}{'Enabled' if settings.CORS_ENABLED else 'Disabled'}")
    print(f"{Fore.YELLOW}  Chunk Size:       {Fore.WHITE}{settings.CHUNK_SIZE}")
    print(f"{Fore.YELLOW}  Chunk Overlap:    {Fore.WHITE}{settings.CHUNK_OVERLAP}")
    print(f"{Fore.CYAN}{'=' * 80}\n")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print_banner()
    print_config()
    
    logger.info(f"{Fore.GREEN}🚀 Starting up Agentic RAG API...{Style.RESET_ALL}")
    
    try:
        # Validate settings
        logger.info(f"{Fore.YELLOW}🔍 Validating configuration...{Style.RESET_ALL}")
        settings.validate()
        logger.info(f"{Fore.GREEN}✅ Configuration validated{Style.RESET_ALL}")
        
        # Initialize vector database (this happens during retriever tool creation)
        logger.info(f"{Fore.YELLOW}🔄 Initializing vector database...{Style.RESET_ALL}")
        retriever_tool = create_retriever_tool()
        logger.info(f"{Fore.GREEN}✅ Vector database initialized{Style.RESET_ALL}")
        app_state.vector_db_initialized = True
        
        # Create agent
        logger.info(f"{Fore.YELLOW}🤖 Creating AI agent...{Style.RESET_ALL}")
        agent = create_agent()
        app_state.agent = agent
        logger.info(f"{Fore.GREEN}✅ AI agent created successfully{Style.RESET_ALL}")
        
        # Store tools information
        google_search = create_google_search_tool()
        wikipedia = create_wikipedia_tool()
        arxiv = create_arxiv_tool()
        
        app_state.tools_info = [
            ToolInfo(
                name="GoogleSearch",
                description="Search the internet for real-time information using Google Search"
            ),
            ToolInfo(
                name="WikipediaSearch",
                description="Search Wikipedia for encyclopedic information on any topic"
            ),
            ToolInfo(
                name="ArxivQueryRun",
                description="Search ArXiv for academic and research papers"
            ),
            ToolInfo(
                name="langsmith_search",
                description="Search LangSmith documentation for specific information about LangSmith"
            )
        ]
        
        logger.info(f"{Fore.GREEN}✅ {len(app_state.tools_info)} tools loaded{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}{Style.BRIGHT}{'=' * 80}")
        print(f"{Fore.GREEN}{Style.BRIGHT}✨ API is ready to accept requests!")
        print(f"{Fore.GREEN}{Style.BRIGHT}📖 API Documentation: http://{settings.API_HOST}:{settings.API_PORT}/api-docs")
        print(f"{Fore.GREEN}{Style.BRIGHT}📋 OpenAPI Schema: http://{settings.API_HOST}:{settings.API_PORT}/api-docs.json")
        print(f"{Fore.GREEN}{Style.BRIGHT}❤️  Health Check: http://{settings.API_HOST}:{settings.API_PORT}/health")
        print(f"{Fore.GREEN}{Style.BRIGHT}{'=' * 80}\n")
        
    except Exception as e:
        logger.error(f"{Fore.RED}❌ Startup failed: {str(e)}{Style.RESET_ALL}")
        raise
    
    yield
    
    # Shutdown
    logger.info(f"{Fore.YELLOW}🛑 Shutting down Agentic RAG API...{Style.RESET_ALL}")


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/api-docs",
    openapi_url="/api-docs.json",
    redoc_url=None,
    lifespan=lifespan
)

# Add rate limiting middleware if enabled
if settings.RATE_LIMIT_ENABLED:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    logger.info("Rate limiting enabled")

# Add CORS middleware if enabled
if settings.CORS_ENABLED:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS enabled for origins: {settings.CORS_ORIGINS}")


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "ValidationError",
            "message": str(exc),
            "status_code": 400
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An internal server error occurred",
            "status_code": 500
        }
    )


# Include routers
app.include_router(health_router)
app.include_router(query_router)
app.include_router(tools_router)


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint redirects to docs."""
    return {
        "message": "Welcome to Agentic RAG API",
        "version": settings.API_VERSION,
        "docs": "/api-docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
